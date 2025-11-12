#!/usr/bin/env python3

import uvicorn
import sys
import os

# Agregar el directorio raíz al path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    print("Iniciando servidor...")
    uvicorn.run(
        "app.api.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
except Exception as e:
    print(f"Error al iniciar servidor: {e}")
    import traceback
    traceback.print_exc()

