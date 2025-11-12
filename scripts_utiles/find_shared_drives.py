#!/usr/bin/env python3
"""
Script para encontrar Shared Drives disponibles
"""

import os
import sys
from dotenv import load_dotenv

# Agregar el directorio del proyecto al path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def find_shared_drives():
    """Encuentra Shared Drives disponibles"""
    print("🔍 Buscando Shared Drives disponibles...")
    
    try:
        from google.oauth2 import service_account
        from googleapiclient.discovery import build
        
        # Cargar configuración
        load_dotenv()
        service_account_file = os.getenv("GDRIVE_SERVICE_ACCOUNT_JSON", "google_service_account.json")
        
        if not os.path.exists(service_account_file):
            print(f"❌ Archivo Service Account no encontrado: {service_account_file}")
            return
        
        # Configurar credenciales
        scopes = [
            "https://www.googleapis.com/auth/drive",
            "https://www.googleapis.com/auth/drive.file",
        ]
        
        credentials = service_account.Credentials.from_service_account_file(
            service_account_file, 
            scopes=scopes
        )
        
        # Crear servicio
        service = build("drive", "v3", credentials=credentials)
        
        # Buscar Shared Drives
        print("📋 Listando Shared Drives...")
        results = service.drives().list().execute()
        drives = results.get('drives', [])
        
        if not drives:
            print("❌ No se encontraron Shared Drives")
            print("💡 Necesitas crear una Shared Drive primero")
            return
        
        print(f"✅ Se encontraron {len(drives)} Shared Drive(s):")
        print("=" * 60)
        
        for drive in drives:
            print(f"📁 Nombre: {drive.get('name', 'Sin nombre')}")
            print(f"🆔 ID: {drive.get('id', 'Sin ID')}")
            print(f"🔒 Restricciones: {drive.get('restrictions', {})}")
            print("-" * 40)
        
        # Buscar carpetas dentro de cada Shared Drive
        print("\n🔍 Buscando carpetas dentro de Shared Drives...")
        for drive in drives:
            drive_id = drive.get('id')
            drive_name = drive.get('name', 'Sin nombre')
            
            print(f"\n📁 Buscando en: {drive_name} (ID: {drive_id})")
            
            try:
                # Buscar carpetas
                query = f"'{drive_id}' in parents and mimeType='application/vnd.google-apps.folder' and trashed=false"
                results = service.files().list(
                    q=query,
                    fields="files(id,name)",
                    supportsAllDrives=True,
                    includeItemsFromAllDrives=True
                ).execute()
                
                folders = results.get('files', [])
                
                if folders:
                    print(f"  📂 Carpetas encontradas:")
                    for folder in folders:
                        print(f"    - {folder.get('name')} (ID: {folder.get('id')})")
                else:
                    print(f"  📂 No hay carpetas en esta Shared Drive")
                    
            except Exception as e:
                print(f"  ❌ Error buscando carpetas: {e}")
        
        print("\n" + "=" * 60)
        print("💡 Instrucciones:")
        print("1. Si no hay Shared Drives, crea una nueva")
        print("2. Invita al Service Account como Editor")
        print("3. Copia el ID de la Shared Drive")
        print("4. Actualiza tu .env con el nuevo ID")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    find_shared_drives()

