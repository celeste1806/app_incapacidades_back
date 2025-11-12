# Incapacidades Backend

API backend construida con FastAPI y SQLAlchemy para gestionar incapacidades. Este README explica cómo instalar dependencias, configurar variables de entorno y ejecutar el proyecto localmente después de clonar el repositorio.

## Requisitos

- Python 3.10 o 3.11 (recomendado)
- pip actualizado (`pip install --upgrade pip`)
- (Opcional) Git para clonar el repo
- (Opcional) MySQL si usarás una base de datos MySQL; para comenzar puedes usar SQLite sin instalar nada adicional

## Tecnologías principales

- FastAPI
- Uvicorn
- SQLAlchemy 2.x
- Pydantic 2.x
- Passlib + python-jose (JWT)

## Dependencias

Las dependencias mínimas están en `requirements.txt`:

```
fastapi>=0.104.0
uvicorn[standard]>=0.24.0
sqlalchemy>=2.0.0
pydantic>=2.0.0
python-multipart>=0.0.6
python-jose[cryptography]>=3.3.0
passlib[bcrypt]>=1.7.4
```

Notas importantes:
- El proyecto carga variables desde `.env` mediante `python-dotenv`. Si no lo tienes instalado, añádelo: `pip install python-dotenv` (o agréguelo a `requirements.txt`).
- Si vas a usar MySQL, añade e instala un driver compatible con SQLAlchemy, por ejemplo `pymysql`:
  - `pip install pymysql`
  - La URL sería del tipo: `mysql+pymysql://usuario:password@host:puerto/base`
- Para empezar rápido con SQLite no necesitas instalar nada adicional (viene en la stdlib de Python) y la URL sería `sqlite:///./incapacidades.db`.

## Estructura relevante

- `app/api/main.py`: app FastAPI y registro de routers
- `app/config/settings.py`: carga de variables de entorno y configuración de seguridad
- `app/db/session.py`: creación de engine y sesión de BD
- `scripts_utiles/`: utilidades y documentación para configuración (correos, GDrive, inicialización)
- `scripts_pruebas/`: scripts manuales de verificación y pruebas puntuales
- `sql_scripts/`: archivos `.sql` con cargas masivas (diagnósticos, cargos, servicios, etc.)
- `run_server.py`: arranque del servidor con Uvicorn en modo reload
- `start_server.bat`: script Windows para iniciar el servidor

## Configuración de entorno

Crea un archivo `.env` en la raíz del proyecto. Ejemplo sugerido:

```
# Base de datos (elige una opción)
# Opción sencilla (SQLite, recomendado para desarrollo rápido):
DATABASE_URL=sqlite:///./incapacidades.db

# Opción MySQL (requiere instalar un driver, p. ej., pymysql):
# DATABASE_URL=mysql+pymysql://usuario:password@localhost:3306/incapacidades

# Seguridad (JWT)
SECRET_KEY=cambe-esta-clave-secreta
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=1440

# CORS (separados por comas)
CORS_ORIGINS=http://localhost:3000,http://127.0.0.1:3000,http://localhost:5173,http://127.0.0.1:5173,*
```

Variables opcionales relacionadas con integraciones (Google Drive, correos, etc.) existen en este repo; revisa los archivos dentro de `scripts_utiles/` (ej. `CONFIGURACION_CORREOS.md`, `NOTIFICACIONES_CORREO.md`, `configuracion_gdrive.env`) si piensas habilitarlas. No son necesarias para levantar el servidor básico.

## Instalación

1) Clona el repositorio
```
git clone <URL_DE_TU_REPOSITORIO>
cd incapacidades-backend-main
```

2) Crea y activa un entorno virtual
- Windows (PowerShell):
```
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```
- Windows (CMD):
```
python -m venv .venv
.\.venv\Scripts\activate.bat
```
- Linux/Mac:
```
python3 -m venv .venv
source .venv/bin/activate
```

3) Instala dependencias
```
pip install -r requirements.txt
# Si usas .env, instala también python-dotenv si no está incluido:
pip install python-dotenv
# Si usas MySQL, instala un driver, por ejemplo:
pip install pymysql
```

4) Crea el archivo `.env` (usa el ejemplo de arriba).

## Ejecución

- Opción A (recomendada):
```
python run_server.py
```

- Opción B (manual con Uvicorn):
```
uvicorn app.api.main:app --reload --host 0.0.0.0 --port 8000
```

- Opción C (Windows, doble clic):
- Ejecuta `start_server.bat`

La API quedará disponible en:
- Aplicación: `http://localhost:8000`
- Documentación interactiva (Swagger): `http://localhost:8000/docs`
- Endpoint de salud: `http://localhost:8000/health`

## Migraciones y tablas

Al iniciar, la app intentará:
- Probar la conexión a la base de datos
- Crear tablas (si no existen) con SQLAlchemy metadata
- Aplicar pequeñas migraciones internas de alineación (ver `app/db/migrate.py`)

Si usas SQLite con `DATABASE_URL=sqlite:///./incapacidades.db`, el archivo se creará automáticamente en la raíz del proyecto al primer arranque.

## Subidas de archivos

Si existe la carpeta `uploads` en la raíz del proyecto, se expondrá como estático en `/uploads`. Esto permite ver/descargar documentos subidos durante pruebas.

## Problemas comunes

- "DATABASE_URL no está definido en el archivo .env": crea `.env` con una URL válida (ver ejemplos).
- "ModuleNotFoundError: dotenv": instala `python-dotenv` (`pip install python-dotenv`).
- Usando MySQL: instala el driver de tu elección (`pymysql`, `mysqlclient`, etc.) y ajusta el prefijo de la URL (`mysql+pymysql://...`).
- Conflictos de CORS: ajusta `CORS_ORIGINS` en `.env` a los orígenes de tu frontend.

## Tests rápidos (opcional)

En `scripts_pruebas/` hay scripts de verificación manual (por ejemplo `test_*`, `verificar_*`). Puedes ejecutarlos con:
```
python nombre_del_script.py
```

## SQL de apoyo

- Los archivos de cargas masivas (diagnósticos, cargos, servicios, etc.) están en `sql_scripts/`.
- Usa `sql_scripts/insert_diagnosticos_mysql.sql`, `sql_scripts/insert_cargos_mysql.sql`, `sql_scripts/insert_servicios_mysql.sql`, etc., según necesites poblar la base de datos.

## Despliegue (resumen)

- Ejecutar con `uvicorn` o un servidor ASGI de producción (ej. `gunicorn` + `uvicorn.workers.UvicornWorker`).
- Configurar variables de entorno apropiadas (`DATABASE_URL`, `SECRET_KEY`, etc.).
- Usar un motor de base de datos gestionado (MySQL/PostgreSQL) para producción.

---

Si encuentras algo faltante para levantar el proyecto tras clonar, abre un issue o ajusta este README.
