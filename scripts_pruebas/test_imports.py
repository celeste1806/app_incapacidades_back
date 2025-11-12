#!/usr/bin/env python3

print("Probando importaciones...")

try:
    print("1. Importando FastAPI...")
    import fastapi
    print(f"   ✓ FastAPI {fastapi.__version__} importado correctamente")
except Exception as e:
    print(f"   ✗ Error importando FastAPI: {e}")

try:
    print("2. Importando uvicorn...")
    import uvicorn
    print(f"   ✓ uvicorn importado correctamente")
except Exception as e:
    print(f"   ✗ Error importando uvicorn: {e}")

try:
    print("3. Importando app.api.main...")
    from app.api.main import app
    print(f"   ✓ app importado correctamente")
except Exception as e:
    print(f"   ✗ Error importando app: {e}")
    import traceback
    traceback.print_exc()

try:
    print("4. Importando servicios...")
    from app.services.upload_service import UploadService
    from app.services.notification_service import NotificationService
    from app.services.audit_service import AuditService
    print(f"   ✓ Servicios importados correctamente")
except Exception as e:
    print(f"   ✗ Error importando servicios: {e}")
    import traceback
    traceback.print_exc()

try:
    print("5. Importando routers...")
    from app.api.v1.routers.upload_router import router
    print(f"   ✓ Router de upload importado correctamente")
except Exception as e:
    print(f"   ✗ Error importando router: {e}")
    import traceback
    traceback.print_exc()

print("\nTodas las importaciones completadas.")

