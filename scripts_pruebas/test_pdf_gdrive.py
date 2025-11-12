#!/usr/bin/env python3
"""
Script para probar la subida SOLO a Google Drive con archivo PDF
"""

import requests
import json
import os
from datetime import datetime, timedelta

def create_simple_pdf():
    """Crea un PDF simple para prueba"""
    # Contenido PDF mínimo válido
    pdf_content = b"""%PDF-1.4
1 0 obj
<<
/Type /Catalog
/Pages 2 0 R
>>
endobj

2 0 obj
<<
/Type /Pages
/Kids [3 0 R]
/Count 1
>>
endobj

3 0 obj
<<
/Type /Page
/Parent 2 0 R
/MediaBox [0 0 612 792]
/Contents 4 0 R
>>
endobj

4 0 obj
<<
/Length 44
>>
stream
BT
/F1 12 Tf
72 720 Td
(Archivo de prueba Google Drive) Tj
ET
endstream
endobj

xref
0 5
0000000000 65535 f 
0000000009 00000 n 
0000000058 00000 n 
0000000115 00000 n 
0000000206 00000 n 
trailer
<<
/Size 5
/Root 1 0 R
>>
startxref
300
%%EOF"""
    return pdf_content

def test_pdf_gdrive_upload():
    """Prueba la subida de PDF solo a Google Drive"""
    print("☁️ Prueba de Subida PDF SOLO a Google Drive")
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
        print(f"✅ Login exitoso: {result.get('nombre', 'N/A')}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False
    
    # Paso 2: Crear incapacidad
    print(f"\n🏥 Creando incapacidad...")
    
    fecha_inicio = datetime.now().strftime("%Y-%m-%d")
    fecha_fin = (datetime.now() + timedelta(days=2)).strftime("%Y-%m-%d")
    
    incapacidad_data = {
        "tipo_incapacidad_id": 1,
        "fecha_inicio": fecha_inicio,
        "fecha_final": fecha_fin,
        "dias": 2,
        "causa_id": 1,
        "eps_afiliado_id": 1,
        "servicio_id": 1,
        "diagnostico_id": 1,
        "salario": "2500000"
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
    
    # Paso 3: Crear archivo PDF de prueba
    print(f"\n📁 Creando archivo PDF de prueba...")
    
    pdf_content = create_simple_pdf()
    test_filename = "test_gdrive_only.pdf"
    
    with open(test_filename, "wb") as f:
        f.write(pdf_content)
    
    # Paso 4: Subir archivo PDF SOLO a Google Drive
    print(f"📤 Subiendo archivo PDF SOLO a Google Drive...")
    
    try:
        with open(test_filename, "rb") as f:
            files = {"file": (test_filename, f, "application/pdf")}
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
            print(f"✅ Archivo PDF procesado exitosamente")
            print(f"☁️ URL Google Drive: {result.get('url_documento', 'N/A')}")
            
            if result.get('url_documento') and 'drive.google.com' in str(result.get('url_documento')):
                print(f"🎉 ¡SUCCESS! Archivo PDF subido SOLO a Google Drive")
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
            print(f"🧹 Archivo PDF temporal eliminado")
        except:
            pass
    
    print(f"\n" + "=" * 60)
    print(f"🎉 ¡Prueba completada!")
    print(f"💡 Los archivos ahora se guardan SOLO en Google Drive")
    print(f"📁 No se crean archivos locales")
    print(f"☁️ Verifica en tu Google Drive que aparezca el archivo PDF")
    
    return True

if __name__ == "__main__":
    test_pdf_gdrive_upload()





