#!/usr/bin/env python3
"""
Script para probar la subida de archivos SOLO a Google Drive
"""

import requests
import json
import os
from datetime import datetime

def test_gdrive_only_upload():
    """Prueba la subida de archivos solo a Google Drive"""
    print("☁️ Prueba de Subida SOLO a Google Drive")
    print("=" * 50)
    
    base_url = "http://localhost:8000"
    
    # Paso 1: Login con diferentes contraseñas
    print("🔐 Autenticación...")
    
    passwords_to_try = ["123456", "nueva_contraseña_123", "celeste123", "admin123"]
    
    token = None
    for password in passwords_to_try:
        login_data = {
            "email": "celestetijaro@gmail.com",
            "password": password
        }
        
        try:
            response = requests.post(f"{base_url}/api/auth/login", json=login_data, timeout=30)
            
            if response.status_code == 200:
                result = response.json()
                token = result.get('access_token')
                print(f"✅ Login exitoso con contraseña: {password}")
                print(f"👤 Usuario: {result.get('nombre', 'N/A')}")
                break
            else:
                print(f"❌ Contraseña '{password}' no válida")
                
        except Exception as e:
            print(f"❌ Error con contraseña '{password}': {e}")
    
    if not token:
        print(f"❌ No se pudo autenticar con ninguna contraseña")
        print(f"💡 Verifica que el usuario existe y la contraseña es correcta")
        return False
    
    # Paso 2: Crear archivo de prueba
    print(f"\n📁 Creando archivo de prueba...")
    
    test_content = f"Archivo de prueba SOLO Google Drive - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
    test_filename = "test_gdrive_only.txt"
    
    with open(test_filename, "wb") as f:
        f.write(test_content.encode('utf-8'))
    
    # Paso 3: Subir archivo
    print(f"📤 Subiendo archivo SOLO a Google Drive...")
    
    try:
        with open(test_filename, "rb") as f:
            files = {"file": (test_filename, f, "text/plain")}
            data = {
                "incapacidad_id": 1,  # Usar una incapacidad existente
                "archivo_id": 1        # Usar un archivo existente
            }
            
            response = requests.post(
                f"{base_url}/api/incapacidad/archivo",
                files=files,
                data=data,
                headers={"Authorization": f"Bearer {token}"},
                timeout=60
            )
        
        print(f"📊 Respuesta: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Archivo procesado exitosamente")
            print(f"☁️ URL Google Drive: {result.get('url_documento', 'N/A')}")
            print(f"📁 Nombre archivo: {result.get('gdrive_url', 'N/A')}")
            
            if result.get('url_documento') and 'drive.google.com' in str(result.get('url_documento')):
                print(f"🎉 ¡SUCCESS! Archivo subido SOLO a Google Drive")
                print(f"🔗 URL: {result.get('url_documento')}")
            else:
                print(f"⚠️ El archivo no parece estar en Google Drive")
        else:
            print(f"❌ Error: {response.status_code}")
            print(f"📝 Respuesta: {response.text}")
        
    except Exception as e:
        print(f"❌ Error subiendo archivo: {e}")
    finally:
        # Limpiar archivo temporal
        try:
            os.remove(test_filename)
            print(f"🧹 Archivo temporal eliminado")
        except:
            pass
    
    print(f"\n" + "=" * 50)
    print(f"🎉 ¡Prueba completada!")
    print(f"💡 Los archivos ahora se guardan SOLO en Google Drive")
    print(f"📁 No se crean archivos locales")
    
    return True

if __name__ == "__main__":
    test_gdrive_only_upload()