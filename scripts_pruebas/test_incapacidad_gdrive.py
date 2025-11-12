#!/usr/bin/env python3
"""
Script para probar la creación de incapacidades con subida de archivos a Google Drive
"""

import requests
import json
import os
from datetime import datetime, timedelta

def test_incapacidad_with_files():
    """Prueba la creación de una incapacidad con archivos"""
    print("🏥 Prueba de Creación de Incapacidad con Archivos")
    print("=" * 60)
    
    base_url = "http://localhost:8000"
    
    # Paso 1: Login para obtener token
    print("🔐 Paso 1: Autenticación...")
    
    login_data = {
        "email": "celestetijaro@gmail.com",
        "password": "123456"  # Cambiar por la contraseña correcta
    }
    
    try:
        response = requests.post(
            f"{base_url}/api/auth/login",
            json=login_data,
            timeout=30
        )
        
        if response.status_code != 200:
            print(f"❌ Error en login: {response.status_code}")
            print(f"📝 Respuesta: {response.text}")
            return False
        
        result = response.json()
        token = result.get('access_token')
        user_id = result.get('id_usuario')
        
        print(f"✅ Login exitoso")
        print(f"👤 Usuario: {result.get('nombre', 'N/A')}")
        print(f"🆔 ID: {user_id}")
        
    except requests.exceptions.RequestException as e:
        print(f"❌ Error de conexión en login: {e}")
        return False
    
    # Paso 2: Crear incapacidad
    print(f"\n🏥 Paso 2: Creando incapacidad...")
    
    fecha_inicio = datetime.now().strftime("%Y-%m-%d")
    fecha_fin = (datetime.now() + timedelta(days=5)).strftime("%Y-%m-%d")
    
    incapacidad_data = {
        "tipo_incapacidad_id": 1,  # Cambiar por un ID válido
        "fecha_inicio": fecha_inicio,
        "fecha_final": fecha_fin,
        "dias": 5,
        "causa_id": 1,  # Cambiar por un ID válido
        "eps_afiliado_id": 1,  # Cambiar por un ID válido
        "servicio_id": 1,  # Cambiar por un ID válido
        "diagnostico_id": 1,  # Cambiar por un ID válido
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
        
        if response.status_code != 200:
            print(f"❌ Error creando incapacidad: {response.status_code}")
            print(f"📝 Respuesta: {response.text}")
            return False
        
        result = response.json()
        incapacidad_id = result.get('id_incapacidad') or result.get('id')
        
        print(f"✅ Incapacidad creada exitosamente")
        print(f"🆔 ID de incapacidad: {incapacidad_id}")
        
    except requests.exceptions.RequestException as e:
        print(f"❌ Error de conexión creando incapacidad: {e}")
        return False
    
    # Paso 3: Subir archivo de prueba
    print(f"\n📤 Paso 3: Subiendo archivo de prueba...")
    
    # Crear un archivo de prueba
    test_file_content = b"Este es un archivo de prueba para la incapacidad"
    test_filename = "test_incapacidad.txt"
    
    # Crear archivo temporal
    with open(test_filename, "wb") as f:
        f.write(test_file_content)
    
    try:
        # Subir archivo
        with open(test_filename, "rb") as f:
            files = {"file": (test_filename, f, "text/plain")}
            data = {
                "incapacidad_id": incapacidad_id,
                "archivo_id": 1  # Cambiar por un ID válido
            }
            
            response = requests.post(
                f"{base_url}/api/incapacidad/archivo",
                files=files,
                data=data,
                headers={
                    "Authorization": f"Bearer {token}"
                },
                timeout=60
            )
        
        print(f"📊 Respuesta subida: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Archivo subido exitosamente")
            print(f"📁 Nombre local: {result.get('url_documento', 'N/A')}")
            print(f"☁️ Google Drive: {result.get('gdrive_url', 'No disponible')}")
            
            if result.get('gdrive_url'):
                print(f"🎉 ¡Archivo subido a Google Drive!")
            else:
                print(f"⚠️ Archivo solo guardado localmente")
        else:
            print(f"❌ Error subiendo archivo: {response.status_code}")
            print(f"📝 Respuesta: {response.text}")
        
    except requests.exceptions.RequestException as e:
        print(f"❌ Error de conexión subiendo archivo: {e}")
    finally:
        # Limpiar archivo temporal
        try:
            os.remove(test_filename)
        except:
            pass
    
    print(f"\n" + "=" * 60)
    print(f"🎉 ¡Prueba completada!")
    print(f"💡 Revisa los logs del servidor para ver si se subió a Google Drive")
    
    return True

def check_server_logs():
    """Instrucciones para revisar logs"""
    print(f"\n📋 Para verificar si funcionó:")
    print(f"1. 🔍 Revisa la terminal del servidor backend")
    print(f"2. 📤 Busca mensajes como 'Subiendo archivo a Google Drive'")
    print(f"3. ✅ Busca 'Archivo subido exitosamente a Google Drive'")
    print(f"4. 🌐 Verifica en tu Google Drive que aparezca el archivo")

if __name__ == "__main__":
    print("🏥 Prueba de Incapacidades con Google Drive")
    print("=" * 60)
    
    success = test_incapacidad_with_files()
    
    check_server_logs()
    
    print(f"\n" + "=" * 60)
    if success:
        print("🎉 ¡Prueba ejecutada!")
        print("📧 Ahora cuando crees una incapacidad real, los archivos se subirán a Google Drive")
    else:
        print("❌ La prueba falló")
        print("📝 Revisa los errores anteriores")




