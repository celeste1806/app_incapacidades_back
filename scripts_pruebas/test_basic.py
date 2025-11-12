print("Probando ejecución básica...")

try:
    import fastapi
    print("FastAPI OK")
except Exception as e:
    print(f"FastAPI Error: {e}")

try:
    import uvicorn
    print("Uvicorn OK")
except Exception as e:
    print(f"Uvicorn Error: {e}")

try:
    from app.api.main import app
    print("App OK")
except Exception as e:
    print(f"App Error: {e}")
    import traceback
    traceback.print_exc()

print("Prueba completada.")
