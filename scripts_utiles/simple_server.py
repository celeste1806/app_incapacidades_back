#!/usr/bin/env python3

import sys
import os

# Agregar el directorio raíz al path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    print("Importando FastAPI...")
    from fastapi import FastAPI
    print("✓ FastAPI importado")
    
    print("Importando app...")
    from app.api.main import app
    print("✓ App importado")
    
    print("Iniciando servidor...")
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000, log_level="info")
    
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()

