#!/usr/bin/env python3
"""
Script de prueba para subir un archivo y verificar que se guarde en Google Drive
"""

import requests
import json
import os
from datetime import datetime

def test_file_upload():
    """Prueba la subida de un archivo al servidor"""
    print("🚀 Iniciando prueba de subida de archivo...")
    print("=" * 50)
    
    # URL del servidor
    base_url = "http://localhost:8000"
    
    # Crear un archivo de prueba (PNG simple)
    test_file_content = create_test_png()
    test_filename = f"test_upload_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
    
    print(f"📁 Creando archivo de prueba: {test_filename}")
    
    # Preparar los datos para la subida
    files = {
        'file': (test_filename, test_file_content, 'image/png')
    }
    
    data = {
        'incapacidad_id': 1,  # ID de incapacidad de prueba
        'archivo_id': 1       # ID de archivo de prueba
    }
    
    try:
        print("📤 Subiendo archivo al servidor...")
        
        # Hacer la petición POST para subir el archivo
        response = requests.post(
            f"{base_url}/api/incapacidad/archivo",
            files=files,
            data=data,
            timeout=30
        )
        
        print(f"📊 Respuesta del servidor: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Archivo subido exitosamente!")
            print(f"🆔 ID del archivo: {result.get('id_archivo', 'No disponible')}")
            print(f"📝 Descripción: {result.get('descripcion', 'No disponible')}")
            
            # Verificar si hay URL de Google Drive en la respuesta
            if 'url' in result:
                url = result['url']
                if 'drive.google.com' in url:
                    print(f"🎉 ¡ÉXITO! Archivo guardado en Google Drive: {url}")
                else:
                    print(f"⚠️  Archivo guardado localmente: {url}")
            else:
                print("ℹ️  No se encontró URL en la respuesta")
            
            return True
            
        else:
            print(f"❌ Error en la subida: {response.status_code}")
            print(f"📝 Respuesta: {response.text}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Error de conexión: {e}")
        return False
    except Exception as e:
        print(f"❌ Error inesperado: {e}")
        return False

def create_test_png():
    """Crea un PNG simple de prueba"""
    # PNG mínimo válido (1x1 pixel transparente)
    png_data = bytes([
        0x89, 0x50, 0x4E, 0x47, 0x0D, 0x0A, 0x1A, 0x0A,  # PNG signature
        0x00, 0x00, 0x00, 0x0D, 0x49, 0x48, 0x44, 0x52,  # IHDR chunk
        0x00, 0x00, 0x00, 0x01, 0x00, 0x00, 0x00, 0x01,  # 1x1 pixel
        0x08, 0x06, 0x00, 0x00, 0x00, 0x1F, 0x15, 0xC4,  # RGBA, no compression
        0x89, 0x00, 0x00, 0x00, 0x0A, 0x49, 0x44, 0x41,  # IDAT chunk
        0x54, 0x78, 0x9C, 0x63, 0x00, 0x01, 0x00, 0x00,  # Compressed data
        0x05, 0x00, 0x01, 0x0D, 0x0A, 0x2D, 0xB4, 0x00,  # CRC
        0x00, 0x00, 0x00, 0x49, 0x45, 0x4E, 0x44, 0xAE,  # IEND chunk
        0x42, 0x60, 0x82  # CRC and end
    ])
    return png_data

def check_recent_uploads():
    """Verifica los archivos subidos recientemente"""
    print("\n🔍 Verificando archivos subidos recientemente...")
    
    try:
        # Verificar archivos locales
        uploads_dir = "uploads"
        if os.path.exists(uploads_dir):
            files = os.listdir(uploads_dir)
            png_files = [f for f in files if f.endswith('.png')]
            print(f"📁 Archivos PNG locales encontrados: {len(png_files)}")
            
            if png_files:
                print("📋 Archivos locales:")
                for file in png_files[-5:]:  # Mostrar los últimos 5
                    file_path = os.path.join(uploads_dir, file)
                    size = os.path.getsize(file_path)
                    print(f"  - {file} ({size} bytes)")
        
        # Verificar metadatos
        urls_dir = os.path.join(uploads_dir, "urls")
        if os.path.exists(urls_dir):
            json_files = [f for f in os.listdir(urls_dir) if f.endswith('.json')]
            print(f"📄 Archivos de metadatos: {len(json_files)}")
            
            if json_files:
                # Leer el último archivo de metadatos
                latest_json = max(json_files, key=lambda x: os.path.getctime(os.path.join(urls_dir, x)))
                json_path = os.path.join(urls_dir, latest_json)
                
                try:
                    with open(json_path, 'r', encoding='utf-8') as f:
                        metadata = json.load(f)
                    
                    print(f"📋 Último archivo subido:")
                    print(f"  - ID: {metadata.get('archivo_id', 'N/A')}")
                    print(f"  - Usuario: {metadata.get('user_id', 'N/A')}")
                    print(f"  - URL: {metadata.get('url', 'N/A')}")
                    print(f"  - Fecha: {metadata.get('fecha_subida', 'N/A')}")
                    
                    if 'drive.google.com' in metadata.get('url', ''):
                        print("🎉 ¡El archivo está en Google Drive!")
                    else:
                        print("⚠️  El archivo está guardado localmente")
                        
                except Exception as e:
                    print(f"❌ Error leyendo metadatos: {e}")
                    
    except Exception as e:
        print(f"❌ Error verificando archivos: {e}")

if __name__ == "__main__":
    print("🧪 Prueba de Subida de Archivo a Google Drive")
    print("=" * 50)
    
    # Hacer la prueba de subida
    success = test_file_upload()
    
    # Verificar archivos subidos
    check_recent_uploads()
    
    print("=" * 50)
    if success:
        print("🎉 ¡Prueba completada!")
        print("📝 Revisa los logs del servidor para ver más detalles")
    else:
        print("❌ La prueba falló")
        print("📝 Revisa los errores anteriores")
    
    print("\n💡 Consejos:")
    print("- Revisa los logs del servidor para ver mensajes de Google Drive")
    print("- Verifica que el archivo aparezca en la carpeta 'archivos incapacidades' de Google Drive")
    print("- Si ves URLs de drive.google.com, ¡la configuración está funcionando!")
