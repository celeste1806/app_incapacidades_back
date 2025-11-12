#!/usr/bin/env python3
"""
Script para probar acceso a una Shared Drive específica
"""

import os
import sys
from dotenv import load_dotenv

# Agregar el directorio del proyecto al path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_specific_shared_drive():
    """Prueba acceso a una Shared Drive específica"""
    print("🔍 Probando acceso a Shared Drive específica...")
    
    try:
        from google.oauth2 import service_account
        from googleapiclient.discovery import build
        
        # Cargar configuración
        load_dotenv()
        service_account_file = os.getenv("GDRIVE_SERVICE_ACCOUNT_JSON", "google_service_account.json")
        
        # ID de la Shared Drive específica
        shared_drive_id = "1yx5WXRhebsi3DLw6sT8nAv0hGo_3J7VW"
        
        if not os.path.exists(service_account_file):
            print(f"❌ Archivo Service Account no encontrado: {service_account_file}")
            return False
        
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
        
        print(f"🆔 Probando acceso a Shared Drive: {shared_drive_id}")
        
        # Intentar obtener información de la Shared Drive
        try:
            drive_info = service.drives().get(driveId=shared_drive_id).execute()
            print(f"✅ Acceso exitoso a Shared Drive!")
            print(f"📁 Nombre: {drive_info.get('name', 'Sin nombre')}")
            print(f"🆔 ID: {drive_info.get('id', 'Sin ID')}")
            print(f"🔒 Restricciones: {drive_info.get('restrictions', {})}")
            
            # Intentar listar archivos en la Shared Drive
            print(f"\n📋 Listando archivos en la Shared Drive...")
            results = service.files().list(
                q=f"'{shared_drive_id}' in parents and trashed=false",
                fields="files(id,name,mimeType)",
                supportsAllDrives=True,
                includeItemsFromAllDrives=True
            ).execute()
            
            files = results.get('files', [])
            print(f"📄 Se encontraron {len(files)} archivos:")
            
            for file in files:
                file_type = "📁" if file.get('mimeType') == 'application/vnd.google-apps.folder' else "📄"
                print(f"  {file_type} {file.get('name', 'Sin nombre')} (ID: {file.get('id')})")
            
            return True
            
        except Exception as e:
            print(f"❌ Error accediendo a Shared Drive: {e}")
            
            # Verificar si es un error de permisos
            if "403" in str(e) or "permission" in str(e).lower():
                print("\n💡 SOLUCIÓN:")
                print("1. Ve a Google Drive")
                print("2. Abre la Shared Drive")
                print("3. Clic en 'Compartir'")
                print("4. Invita: incapacidad@vocal-spirit-475714-r8.iam.gserviceaccount.com")
                print("5. Rol: Editor")
                print("6. Clic en 'Enviar'")
            
            return False
        
    except Exception as e:
        print(f"❌ Error general: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("🧪 Prueba de Acceso a Shared Drive Específica")
    print("=" * 60)
    
    success = test_specific_shared_drive()
    
    print("=" * 60)
    if success:
        print("🎉 ¡Acceso exitoso a Shared Drive!")
        print("💡 Ya puedes probar subir archivos")
    else:
        print("❌ No se pudo acceder a la Shared Drive")
        print("📝 Sigue las instrucciones anteriores para invitar al Service Account")

