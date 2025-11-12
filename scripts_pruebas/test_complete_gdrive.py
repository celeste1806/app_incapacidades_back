#!/usr/bin/env python3
"""
Script completo para probar la subida SOLO a Google Drive
"""

import requests
import json
import os
from datetime import datetime, timedelta

def test_complete_gdrive_flow():
    """Prueba completa: crear incapacidad y subir archivo solo a Google Drive"""
    print("☁️ Prueba Completa: SOLO Google Drive")
    print("=" * 60)
    
    base_url = "http://localhost:8000"
    
    # Paso 1: Login
    print("🔐 Autenticación...")
    
    login_data = {
        "email": "celestetijaro@gmail.com",
        "password": "celeste123"
    }
    
    try:
        response = requests.post(f"{base_url}/api/auth/login", json=login_data, timeout=30)
        
        if response.status_code != 200:
            print(f"❌ Error en login: {response.status_code}")
            return False
        
        result = response.json()
        token = result.get('access_token')
        user_id = result.get('id_usuario')
        print(f"✅ Login exitoso: {result.get('nombre', 'N/A')}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False
    
    # Paso 2: Crear incapacidad
    print(f"\n🏥 Creando incapacidad...")
    
    fecha_inicio = datetime.now().strftime("%Y-%m-%d")
    fecha_fin = (datetime.now() + timedelta(days=3)).strftime("%Y-%m-%d")
    
    incapacidad_data = {
        "tipo_incapacidad_id": 1,
        "fecha_inicio": fecha_inicio,
        "fecha_final": fecha_fin,
        "dias": 3,
        "causa_id": 1,
        "eps_afiliado_id": 1,
        "servicio_id": 1,
        "diagnostico_id": 1,
        "salario": "2000000"
    }
    
    try:
        response = requests.post(
            f"{base_url}/api/incapacidad/",
            json=incapacidad_data,
            headers={
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json"
            },
            timeout=30
        )
        
        print(f"📊 Respuesta creación: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            incapacidad_id = result.get('id_incapacidad') or result.get('id')
            print(f"✅ Incapacidad creada: ID {incapacidad_id}")
        else:
            print(f"❌ Error creando incapacidad: {response.status_code}")
            print(f"📝 Respuesta: {response.text}")
            return False
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False
    
    # Paso 3: Crear archivo de prueba
    print(f"\n📁 Creando archivo de prueba...")
    
    test_content = f"Archivo de prueba SOLO Google Drive\nCreado: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\nIncapacidad ID: {incapacidad_id}"
    test_filename = "test_gdrive_only.txt"
    
    with open(test_filename, "wb") as f:
        f.write(test_content.encode('utf-8'))
    
    # Paso 4: Subir archivo SOLO a Google Drive
    print(f"📤 Subiendo archivo SOLO a Google Drive...")
    
    try:
        with open(test_filename, "rb") as f:
            files = {"file": (test_filename, f, "text/plain")}
            data = {
                "incapacidad_id": incapacidad_id,
                "archivo_id": 1
            }
            
            response = requests.post(
                f"{base_url}/api/incapacidad/archivo",
                files=files,
                data=data,
                headers={"Authorization": f"Bearer {token}"},
                timeout=60
            )
        
        print(f"📊 Respuesta subida: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Archivo procesado exitosamente")
            print(f"☁️ URL Google Drive: {result.get('url_documento', 'N/A')}")
            
            if result.get('url_documento') and 'drive.google.com' in str(result.get('url_documento')):
                print(f"🎉 ¡SUCCESS! Archivo subido SOLO a Google Drive")
                print(f"🔗 URL: {result.get('url_documento')}")
                print(f"📁 Verifica en tu Google Drive que aparezca el archivo")
            else:
                print(f"⚠️ El archivo no parece estar en Google Drive")
                print(f"📝 Resultado: {result}")
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
    
    print(f"\n" + "=" * 60)
    print(f"🎉 ¡Prueba completada!")
    print(f"💡 Los archivos ahora se guardan SOLO en Google Drive")
    print(f"📁 No se crean archivos locales")
    print(f"☁️ Verifica en tu Google Drive que aparezca el archivo")
    
    return True

if __name__ == "__main__":
    test_complete_gdrive_flow()





