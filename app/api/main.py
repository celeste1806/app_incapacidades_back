from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from pathlib import Path
from starlette.middleware.cors import CORSMiddleware

from app.db.session import test_connection
from app.models.base import Base
from app.models import parametro as _parametro  # noqa: F401  Ensure model import for metadata
from app.models import tipo_incapacidad as _tipo_incapacidad  # noqa: F401  Ensure model import for metadata
from app.models import archivo as _archivo  # noqa: F401  Ensure model import for metadata
from app.models import relacion as _relacion  # noqa: F401  Ensure model import for metadata
from app.models import password_reset_token as _password_reset_token  # noqa: F401  Ensure model import for metadata
from app.db.session import engine
from app.config.settings import get_env, DATABASE_URL
from app.api.v1.routers.parametro_router import router as parametro_router
from app.api.v1.routers.parametro_hijo_router import router as parametro_hijo_router
from app.api.v1.routers.tipo_incapacidad_router import router as tipo_incapacidad_router
from app.api.v1.routers.relacion_router import router as relacion_router
from app.api.archivo_router import router as archivo_router
from app.api.v1.routers.usuario_router import router as auth_router
from app.api.v1.routers.incapacidad_router import router as incapacidad_router
from app.db.migrate import align_usuario_table, align_incapacidad_table


BASE_DIR = Path(__file__).resolve().parents[2]

app = FastAPI(title="API Incapacidades")


@app.on_event("startup")
def on_startup() -> None:
    print("DEBUG: ===== SERVIDOR INICIANDO =====")
    try:
        test_connection()
        print("[OK] Base de datos conectada correctamente.")
        print(f"[INFO] DATABASE_URL activo: {DATABASE_URL}")
    except Exception as exc:  # noqa: BLE001
        # No abortar la app por fallo de conexión; permitir que /health responda
        print(f"[WARN] Falló la conexión a la base de datos: {exc}")
    # Crear tablas si no existen
    try:
        Base.metadata.create_all(bind=engine)
    except Exception as exc:  # noqa: BLE001
        print(f"[WARN] No fue posible crear/verificar tablas: {exc}")
    # Migraciones ligeras
    try:
        align_usuario_table(engine)
        print("[OK] Migración de tabla Usuario aplicada.")
    except Exception as exc:  # noqa: BLE001
        print(f"[WARN] No fue posible aplicar migración Usuario: {exc}")
    # Alinear incapacidad.fecha_registro sin ON UPDATE
    try:
        align_incapacidad_table(engine)
        print("[OK] Migración de tabla Incapacidad aplicada.")
    except Exception as exc:  # noqa: BLE001
        print(f"[WARN] No fue posible aplicar migración Incapacidad: {exc}")
    print("DEBUG: ===== SERVIDOR INICIADO =====")


@app.get("/health")
def health_check() -> dict[str, str]:
    return {"status": "ok"}

# CORS
# CORS: permite explícitamente el front en 3000
origins_env = get_env("CORS_ORIGINS", "http://localhost:3000,http://127.0.0.1:3000, http://localhost:5173, http://127.0.0.1:5173, *")
origins = [o.strip() for o in origins_env.split(",") if o.strip()] or ["*"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Registrar routers
app.include_router(parametro_router, prefix="/api")
app.include_router(parametro_hijo_router, prefix="/api")
app.include_router(tipo_incapacidad_router, prefix="/api")
app.include_router(archivo_router, prefix ="/api" )
app.include_router(relacion_router, prefix="/api")
app.include_router(auth_router, prefix="/api")
app.include_router(incapacidad_router, prefix="/api")
# Upload deshabilitado



# Exponer carpeta de subidas como estáticos para poder ver/descargar documentos
try:
    uploads_dir = BASE_DIR / "uploads"
    if uploads_dir.is_dir():
        app.mount("/uploads", StaticFiles(directory=str(uploads_dir)), name="uploads")
except Exception:
    # No bloquear si falla el montaje
    pass
