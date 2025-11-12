#!/usr/bin/env python3
"""
Script de prueba para verificar la configuración de Google Drive
"""

import os
import sys
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

def test_gdrive_config():
    """Prueba la configuración de Google Drive"""
    print("🔍 Verificando configuración de Google Drive...")
    
    # Verificar variables de entorno
    folder_name = os.getenv("GDRIVE_FOLDER_NAME", "")
    folder_id = os.getenv("GDRIVE_FOLDER_ID", "")
    service_account_file = os.getenv("GDRIVE_SERVICE_ACCOUNT_JSON", "google_service_account.json")
    
    print(f"📁 Nombre de carpeta: {folder_name}")
    print(f"🆔 ID de carpeta: {folder_id}")
    print(f"🔑 Archivo Service Account: {service_account_file}")
    
    # Verificar si existe el archivo de Service Account
    if os.path.exists(service_account_file):
        print(f"✅ Archivo Service Account encontrado: {service_account_file}")
        
        # Verificar contenido del archivo
        try:
            import json
            with open(service_account_file, 'r') as f:
                config = json.load(f)
            
            print(f"📧 Email del Service Account: {config.get('client_email', 'No encontrado')}")
            print(f"🆔 Project ID: {config.get('project_id', 'No encontrado')}")
            
        except Exception as e:
            print(f"❌ Error leyendo Service Account: {e}")
            return False
    else:
        print(f"❌ Archivo Service Account no encontrado: {service_account_file}")
        return False
    
    # Verificar librerías de Google Drive
    try:
        from google.oauth2 import service_account
        from googleapiclient.discovery import build
        print("✅ Librerías de Google Drive disponibles")
    except ImportError as e:
        print(f"❌ Librerías de Google Drive no disponibles: {e}")
        return False
    
    # Probar autenticación
    try:
        print("🔑 Probando autenticación...")
        scopes = [
            "https://www.googleapis.com/auth/drive",
            "https://www.googleapis.com/auth/drive.file",
        ]
        
        credentials = service_account.Credentials.from_service_account_file(
            service_account_file, 
            scopes=scopes
        )
        
        service = build("drive", "v3", credentials=credentials)
        
        # Probar acceso a Drive
        results = service.files().list(pageSize=1, fields="files(id,name)").execute()
        files = results.get('files', [])
        
        print(f"✅ Autenticación exitosa! Se encontraron {len(files)} archivos")
        
        # Verificar carpeta específica
        if folder_id:
            try:
                folder_info = service.files().get(fileId=folder_id).execute()
                print(f"✅ Carpeta encontrada: {folder_info.get('name', 'Sin nombre')}")
            except Exception as e:
                print(f"⚠️  No se pudo acceder a la carpeta específica: {e}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error en autenticación: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Iniciando prueba de configuración de Google Drive")
    print("=" * 50)
    
    success = test_gdrive_config()
    
    print("=" * 50)
    if success:
        print("🎉 ¡Configuración de Google Drive correcta!")
        print("📝 Los archivos ahora se subirán a Google Drive automáticamente")
    else:
        print("❌ Configuración de Google Drive incorrecta")
        print("📝 Revisa los errores anteriores y corrige la configuración")
    
    sys.exit(0 if success else 1)
