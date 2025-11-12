#!/usr/bin/env python3
"""
Script simple para probar solo la subida de archivos a Google Drive
"""

import requests
import json
import os

def test_file_upload_only():
    """Prueba solo la subida de archivos"""
    print("📤 Prueba de Subida de Archivos a Google Drive")
    print("=" * 50)
    
    base_url = "http://localhost:8000"
    
    # Paso 1: Login
    print("🔐 Autenticación...")
    
    login_data = {
        "email": "celestetijaro@gmail.com",
        "password": "123456"
    }
    
    try:
        response = requests.post(f"{base_url}/api/auth/login", json=login_data, timeout=30)
        
        if response.status_code != 200:
            print(f"❌ Error en login: {response.status_code}")
            print(f"📝 Respuesta: {response.text}")
            return False
        
        result = response.json()
        token = result.get('access_token')
        print(f"✅ Login exitoso: {result.get('nombre', 'N/A')}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False
    
    # Paso 2: Crear archivo de prueba
    print(f"\n📁 Creando archivo de prueba...")
    
    test_content = f"Archivo de prueba creado el {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
    test_filename = "test_gdrive.txt"
    
    with open(test_filename, "wb") as f:
        f.write(test_content.encode('utf-8'))
    
    # Paso 3: Subir archivo usando el endpoint directo
    print(f"📤 Subiendo archivo...")
    
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
            print(f"✅ Archivo subido exitosamente")
            print(f"📁 Nombre: {result.get('url_documento', 'N/A')}")
            print(f"☁️ Google Drive: {result.get('gdrive_url', 'No disponible')}")
            
            if result.get('gdrive_url'):
                print(f"🎉 ¡SUCCESS! Archivo subido a Google Drive")
                print(f"🔗 URL: {result.get('gdrive_url')}")
            else:
                print(f"⚠️ Archivo solo guardado localmente")
        else:
            print(f"❌ Error: {response.status_code}")
            print(f"📝 Respuesta: {response.text}")
        
    except Exception as e:
        print(f"❌ Error subiendo archivo: {e}")
    finally:
        # Limpiar
        try:
            os.remove(test_filename)
        except:
            pass
    
    return True

if __name__ == "__main__":
    from datetime import datetime
    test_file_upload_only()





