@echo off
echo Iniciando servidor de incapacidades...
python -m uvicorn app.api.main:app --reload --host 0.0.0.0 --port 8000
pause
