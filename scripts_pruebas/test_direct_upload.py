#!/usr/bin/env python3
"""
Script de prueba directo para verificar que Google Drive funciona
"""

import os
import sys
from datetime import datetime

# Agregar el directorio del proyecto al path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.db.session import get_db
from app.services.upload_service import UploadService
from fastapi import UploadFile
from io import BytesIO

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

def test_direct_upload():
    """Prueba la subida directa usando el servicio"""
    print("🚀 Iniciando prueba directa de subida a Google Drive...")
    print("=" * 60)
    
    try:
        # Obtener sesión de base de datos
        db = next(get_db())
        
        # Crear servicio de upload
        upload_service = UploadService(db)
        
        # Crear archivo de prueba
        test_filename = f"test_gdrive_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
        test_content = create_test_png()
        
        print(f"📁 Creando archivo de prueba: {test_filename}")
        print(f"📊 Tamaño del archivo: {len(test_content)} bytes")
        
        # Crear objeto UploadFile simulado
        file_obj = BytesIO(test_content)
        upload_file = UploadFile(
            filename=test_filename,
            file=file_obj,
            size=len(test_content),
            headers={"content-type": "image/png"}
        )
        
        print("🔑 Intentando configurar Google Drive...")
        
        # Intentar subir la imagen
        print("📤 Subiendo imagen...")
        archivo_id = upload_service.upload_image(
            file=upload_file,
            user_id=1,
            description="Archivo de prueba para verificar Google Drive"
        )
        
        print(f"✅ Archivo subido exitosamente!")
        print(f"🆔 ID del archivo: {archivo_id}")
        
        # Verificar metadatos
        metadata = upload_service.get_file_url_metadata(archivo_id)
        if metadata:
            print(f"📋 Metadatos del archivo:")
            print(f"  - URL: {metadata.get('url', 'N/A')}")
            print(f"  - Usuario: {metadata.get('user_id', 'N/A')}")
            print(f"  - Fecha: {metadata.get('fecha_subida', 'N/A')}")
            
            if 'drive.google.com' in metadata.get('url', ''):
                print("🎉 ¡ÉXITO! El archivo se guardó en Google Drive!")
                print(f"🔗 URL de Google Drive: {metadata['url']}")
                return True
            else:
                print("⚠️  El archivo se guardó localmente, no en Google Drive")
                print(f"📁 Ruta local: {metadata.get('file_path', 'N/A')}")
                return False
        else:
            print("❌ No se encontraron metadatos del archivo")
            return False
            
    except Exception as e:
        print(f"❌ Error durante la prueba: {str(e)}")
        import traceback
        print(f"📝 Traceback completo:")
        traceback.print_exc()
        return False
    finally:
        if 'db' in locals():
            db.close()

def check_gdrive_config():
    """Verifica la configuración de Google Drive"""
    print("\n🔍 Verificando configuración de Google Drive...")
    
    try:
        from dotenv import load_dotenv
        load_dotenv()
        
        folder_name = os.getenv("GDRIVE_FOLDER_NAME", "")
        folder_id = os.getenv("GDRIVE_FOLDER_ID", "")
        service_account_file = os.getenv("GDRIVE_SERVICE_ACCOUNT_JSON", "google_service_account.json")
        
        print(f"📁 Nombre de carpeta: {folder_name}")
        print(f"🆔 ID de carpeta: {folder_id}")
        print(f"🔑 Archivo Service Account: {service_account_file}")
        
        if os.path.exists(service_account_file):
            print(f"✅ Archivo Service Account encontrado")
        else:
            print(f"❌ Archivo Service Account no encontrado")
            return False
            
        return True
        
    except Exception as e:
        print(f"❌ Error verificando configuración: {e}")
        return False

if __name__ == "__main__":
    print("🧪 Prueba Directa de Google Drive")
    print("=" * 60)
    
    # Verificar configuración
    config_ok = check_gdrive_config()
    
    if not config_ok:
        print("❌ Configuración incorrecta, abortando prueba")
        sys.exit(1)
    
    # Hacer la prueba de subida
    success = test_direct_upload()
    
    print("=" * 60)
    if success:
        print("🎉 ¡PRUEBA EXITOSA!")
        print("📝 Google Drive está funcionando correctamente")
        print("💡 Los archivos ahora se subirán automáticamente a Google Drive")
    else:
        print("❌ La prueba falló")
        print("📝 Revisa los errores anteriores")
        print("💡 Verifica la configuración de Google Drive")
    
    print("\n🔧 Para verificar manualmente:")
    print("1. Ve a Google Drive")
    print("2. Busca la carpeta 'archivos incapacidades'")
    print("3. Verifica que aparezca el archivo de prueba")

