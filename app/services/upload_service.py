from __future__ import annotations

import os
import uuid
from typing import List, Optional
from fastapi import UploadFile
from sqlalchemy.orm import Session
from datetime import datetime
from pathlib import Path

from app.repositories.archivo_repository import ArchivoRepository
from app.repositories.incapacidad import IncapacidadRepository
from app.schemas.archivo import ArchivoCreate, ArchivoOut
from app.services.audit_service import AuditService
from app.config.settings import get_env

# Google Drive SDK
try:
    from google.oauth2.credentials import Credentials as OAuthCredentials
    from google_auth_oauthlib.flow import Flow
    from google.auth.transport.requests import Request
    from google.oauth2 import service_account
    from googleapiclient.discovery import build as gbuild
    from googleapiclient.http import MediaInMemoryUpload
except Exception:
    OAuthCredentials = None
    Flow = None
    Request = None
    service_account = None
    gbuild = None
    MediaInMemoryUpload = None


class UploadService:
    def __init__(self, db: Session) -> None:
        self.db = db
        self.archivo_repo = ArchivoRepository(db)
        self.incapacidad_repo = IncapacidadRepository(db)
        self.audit_service = AuditService(db)
        base_uploads_path = Path(__file__).resolve().parents[2] / "uploads"
        self.upload_dir = str(base_uploads_path)
        self.urls_dir = str(base_uploads_path / "urls")
        self.max_file_size = 10 * 1024 * 1024  # 10MB
        # Configuración Drive
        self.gdrive_folder_name = get_env("GDRIVE_FOLDER_NAME", "archivo incapacidad")
        self.gdrive_folder_id = get_env("GDRIVE_FOLDER_ID", "")
        self.gdrive_service_account_json = get_env("GDRIVE_SERVICE_ACCOUNT_JSON", "google_service_account.json")
        self.gdrive_oauth_json = get_env("GDRIVE_OAUTH_JSON", "")
        self.gdrive_token_json = get_env("GDRIVE_TOKEN_JSON", "token.json")
        self._gdrive_service = None
        
        # Crear directorio de uploads si no existe
        os.makedirs(self.upload_dir, exist_ok=True)
        os.makedirs(self.urls_dir, exist_ok=True)

    def upload_pdf(self, *, file: UploadFile, user_id: int, description: str = None) -> int:
        """
        Sube un archivo PDF y retorna el ID del archivo en la base de datos.
        """
        # Validar tamaño del archivo
        if file.size and file.size > self.max_file_size:
            raise ValueError(f"El archivo es demasiado grande. Máximo permitido: {self.max_file_size / (1024*1024):.1f}MB")
        
        # Generar nombre único para el archivo
        file_extension = ".pdf"
        unique_filename = f"{uuid.uuid4()}{file_extension}"
        file_path = os.path.join(self.upload_dir, unique_filename)
        
        try:
            # Leer contenido del archivo
            content = file.file.read()
            
            # Validar que el contenido sea realmente un PDF
            if not self._is_valid_pdf(content):
                raise ValueError("El archivo no es un PDF válido")
            
            # Subir a Google Drive si hay credenciales; si no, guardar local
            public_url = None
            if self._ensure_gdrive():
                try:
                    public_url = self._gdrive_upload(content, original_name=(file.filename or "documento.pdf"), mime_type="application/pdf")
                    if public_url:
                        print(f"✅ Archivo subido a Google Drive: {public_url}")
                    else:
                        print("⚠️  Falló subida a Google Drive, usando almacenamiento local")
                except Exception as e:
                    print(f"⚠️  Error subiendo a Google Drive: {str(e)}")
                    print("📁 Usando almacenamiento local como fallback")
            
            if not public_url:
                with open(file_path, "wb") as f:
                    f.write(content)
            
            # Crear registro en base de datos
            archivo_data = ArchivoCreate(
                nombre=file.filename or f"documento_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf",
                descripcion=description or f"Documento PDF subido por usuario {user_id}",
                estado=True
            )
            
            archivo = self.archivo_repo.create(archivo_data)
            
            # Guardar información adicional del archivo físico
            # Guardar metadatos con URL pública (Drive o local)
            if public_url:
                self._save_file_metadata_with_url(archivo.id_archivo, public_url, file.size, user_id)
            else:
                self._save_file_metadata(archivo.id_archivo, file_path, file.size, user_id)
            
            # Registrar auditoría
            self.audit_service.log_file_upload(
                file_id=archivo.id_archivo,
                user_id=user_id,
                filename=file.filename or "documento.pdf",
                file_size=file.size or 0
            )
            
            return archivo.id_archivo
            
        except Exception as e:
            # Limpiar archivo si hubo error
            if os.path.exists(file_path):
                os.remove(file_path)
            raise ValueError(f"Error al procesar archivo: {str(e)}")

    def link_file_to_incapacidad(self, *, file_id: int, incapacidad_id: int) -> dict | None:
        """
        Crea el vínculo en incapacidad_archivo y retorna la fila creada.
        """
        inserted = self.incapacidad_repo.add_archivos(
            incapacidad_id=incapacidad_id,
            archivo_ids=[file_id],
            url_builder=lambda a_id: f"/uploads/{a_id}"
        )
        return inserted[0] if inserted else None

    def _is_valid_pdf(self, content: bytes) -> bool:
        """
        Valida que el contenido sea realmente un PDF.
        """
        # Verificar firma PDF (debe empezar con %PDF)
        if not content.startswith(b'%PDF'):
            return False
        
        # Verificar que termine con %%EOF o similar
        if not (b'%%EOF' in content[-100:] or b'startxref' in content[-100:]):
            return False
        
        return True

    def upload_image(self, *, file: UploadFile, user_id: int, description: str = None) -> int:
        """
        Sube una imagen PNG y retorna el ID del archivo en la base de datos.
        """
        # Validar tamaño del archivo
        if file.size and file.size > self.max_file_size:
            raise ValueError(f"El archivo es demasiado grande. Máximo permitido: {self.max_file_size / (1024*1024):.1f}MB")

        content_type = (file.content_type or "").lower()
        if not content_type.startswith("image/png"):
            raise ValueError("Solo se permite imagen PNG")

        file_extension = ".png"
        unique_filename = f"{uuid.uuid4()}{file_extension}"
        file_path = os.path.join(self.upload_dir, unique_filename)

        try:
            content = file.file.read()

            if not self._is_valid_png(content):
                raise ValueError("El archivo no es un PNG válido")

            public_url = None
            if self._ensure_gdrive():
                try:
                    public_url = self._gdrive_upload(content, original_name=(file.filename or f"imagen{file_extension}"), mime_type="image/png")
                    if public_url:
                        print(f"✅ Imagen subida a Google Drive: {public_url}")
                    else:
                        print("⚠️  Falló subida a Google Drive, usando almacenamiento local")
                except Exception as e:
                    print(f"⚠️  Error subiendo a Google Drive: {str(e)}")
                    print("📁 Usando almacenamiento local como fallback")
            
            if not public_url:
                with open(file_path, "wb") as f:
                    f.write(content)

            archivo = self.archivo_repo.create(ArchivoCreate(
                nombre=file.filename or f"imagen_{datetime.now().strftime('%Y%m%d_%H%M%S')}{file_extension}",
                descripcion=description or f"Imagen PNG subida por usuario {user_id}",
                estado=True
            ))

            if public_url:
                self._save_file_metadata_with_url(archivo.id_archivo, public_url, file.size, user_id)
            else:
                self._save_file_metadata(archivo.id_archivo, file_path, file.size, user_id)

            self.audit_service.log_file_upload(
                file_id=archivo.id_archivo,
                user_id=user_id,
                filename=file.filename or f"imagen{file_extension}",
                file_size=file.size or 0
            )

            return archivo.id_archivo

        except Exception as e:
            if os.path.exists(file_path):
                os.remove(file_path)
            raise ValueError(f"Error al procesar imagen: {str(e)}")

    def _is_valid_png(self, content: bytes) -> bool:
        """
        Valida que el contenido sea realmente un PNG (firma PNG válida).
        """
        return content.startswith(b"\x89PNG\r\n\x1a\n")

    def _save_file_metadata(self, archivo_id: int, file_path: str, file_size: int, user_id: int):
        """
        Guarda un JSON por archivo en uploads/urls con la URL y metadatos básicos.
        """
        try:
            public_url = f"/uploads/{archivo_id}{os.path.splitext(file_path)[1]}" if os.path.splitext(file_path)[1] else f"/uploads/{archivo_id}"
            metadata = {
                "archivo_id": archivo_id,
                "user_id": user_id,
                "file_path": file_path,
                "file_size": file_size or 0,
                "url": public_url,
                "fecha_subida": datetime.now().isoformat(),
            }
            meta_file = os.path.join(self.urls_dir, f"{archivo_id}.json")
            # Escribir como JSON (sin depender de imports adicionales)
            import json
            with open(meta_file, "w", encoding="utf-8") as f:
                json.dump(metadata, f, ensure_ascii=False, indent=2)
        except Exception:
            # No interrumpir el flujo de subida si falla el guardado de metadatos
            pass

    def _save_file_metadata_with_url(self, archivo_id: int, public_url: str, file_size: int, user_id: int):
        try:
            metadata = {
                "archivo_id": archivo_id,
                "user_id": user_id,
                "file_path": public_url,
                "file_size": file_size or 0,
                "url": public_url,
                "fecha_subida": datetime.now().isoformat(),
            }
            meta_file = os.path.join(self.urls_dir, f"{archivo_id}.json")
            import json
            with open(meta_file, "w", encoding="utf-8") as f:
                json.dump(metadata, f, ensure_ascii=False, indent=2)
        except Exception:
            pass

    # ---------------- Google Drive helpers -----------------
    def _ensure_gdrive(self) -> bool:
        if self._gdrive_service is not None:
            return True
        try:
            if not (service_account and gbuild and MediaInMemoryUpload):
                print("❌ Librerías de Google Drive no disponibles")
                return False
            
            # Intentar usar Service Account primero
            if self.gdrive_service_account_json and os.path.exists(self.gdrive_service_account_json):
                try:
                    print("🔑 Usando Service Account para Google Drive...")
                    scopes = [
                        "https://www.googleapis.com/auth/drive",
                        "https://www.googleapis.com/auth/drive.file",
                    ]
                    
                    credentials = service_account.Credentials.from_service_account_file(
                        self.gdrive_service_account_json, 
                        scopes=scopes
                    )
                    
                    # Crear servicio de Google Drive
                    self._gdrive_service = gbuild("drive", "v3", credentials=credentials)
                    
                    # Asegurar carpeta
                    self._ensure_folder()
                    print("✅ Google Drive configurado correctamente con Service Account")
                    return True
                    
                except Exception as e:
                    print(f"❌ Error con Service Account: {str(e)}")
                    self._gdrive_service = None
            
            # Fallback a OAuth2 si Service Account falla
            if self.gdrive_oauth_json:
                print("🔑 Intentando autenticación OAuth2...")
                if not (OAuthCredentials and Flow and Request):
                    print("❌ Librerías OAuth2 no disponibles")
                    return False
                
                import json
                
                # Leer credenciales OAuth2
                if os.path.exists(self.gdrive_oauth_json):
                    with open(self.gdrive_oauth_json, 'r', encoding='utf-8') as f:
                        client_config = json.load(f)
                else:
                    client_config = json.loads(self.gdrive_oauth_json)
                
                # Configurar scopes
                scopes = [
                    "https://www.googleapis.com/auth/drive",
                    "https://www.googleapis.com/auth/drive.file",
                ]
                
                # Verificar si ya tenemos un token guardado
                creds = None
                if os.path.exists(self.gdrive_token_json):
                    try:
                        creds = OAuthCredentials.from_authorized_user_file(self.gdrive_token_json, scopes)
                    except Exception:
                        creds = None
                
                # Si no hay credenciales válidas, necesitamos autenticación
                if not creds or not creds.valid:
                    if creds and creds.expired and creds.refresh_token:
                        try:
                            creds.refresh(Request())
                        except Exception:
                            creds = None
                    
                    if not creds:
                        print("🔑 Iniciando proceso de autenticación OAuth2...")
                        flow = Flow.from_client_config(client_config, scopes)
                        flow.redirect_uri = 'http://localhost:8000/auth/callback'
                        
                        # Generar URL de autorización
                        auth_url, _ = flow.authorization_url(prompt='consent')
                        print(f"🌐 Abre esta URL en tu navegador: {auth_url}")
                        print("📋 Después de autorizar, copia el código de autorización aquí")
                        
                        # Por ahora, retornar False para evitar bloqueo
                        return False
                
                # Crear servicio de Google Drive
                self._gdrive_service = gbuild("drive", "v3", credentials=creds)
                
                # Guardar token para futuras sesiones
                with open(self.gdrive_token_json, 'w') as token:
                    token.write(creds.to_json())
                
                # Asegurar carpeta
                self._ensure_folder()
                print("✅ Google Drive configurado correctamente con OAuth2")
                return True
            
            print("❌ No se encontraron credenciales válidas para Google Drive")
            return False
            
        except Exception as e:
            print(f"❌ Error inicializando Google Drive: {str(e)}")
            self._gdrive_service = None
            return False

    def _ensure_folder(self) -> None:
        if not self._gdrive_service:
            return
        try:
            if self.gdrive_folder_id:
                return
            # Buscar carpeta por nombre
            q = f"mimeType='application/vnd.google-apps.folder' and name='{self.gdrive_folder_name}' and trashed=false"
            res = self._gdrive_service.files().list(q=q, fields="files(id,name)").execute()
            files = res.get("files", [])
            if files:
                self.gdrive_folder_id = files[0]["id"]
                return
            # Crear si no existe
            file_metadata = {
                'name': self.gdrive_folder_name,
                'mimeType': 'application/vnd.google-apps.folder'
            }
            folder = self._gdrive_service.files().create(body=file_metadata, fields='id').execute()
            self.gdrive_folder_id = folder.get('id')
        except Exception:
            pass

    def _gdrive_upload(self, content: bytes, *, original_name: str, mime_type: str) -> str | None:
        try:
            if not self._gdrive_service:
                return None
            media = MediaInMemoryUpload(content, mimetype=mime_type, resumable=False)
            body = { 'name': original_name }
            if self.gdrive_folder_id:
                body['parents'] = [self.gdrive_folder_id]
            
            # Subir archivo directamente al Drive (o Shared Drive)
            file = self._gdrive_service.files().create(
                body=body, 
                media_body=media, 
                fields='id,webViewLink,webContentLink',
                supportsAllDrives=True  # Habilitar soporte para Shared Drives
            ).execute()
            
            file_id = file.get('id')
            
            # Hacer público con enlace
            try:
                self._gdrive_service.permissions().create(
                    fileId=file_id, 
                    body={'type':'anyone','role':'reader'},
                    supportsAllDrives=True  # Habilitar soporte para Shared Drives
                ).execute()
                print(f"✅ Archivo {original_name} subido a Google Drive exitosamente")
            except Exception as e:
                print(f"⚠️  Archivo subido pero no se pudo hacer público: {str(e)}")
            
            # Preferir webViewLink
            return file.get('webViewLink') or file.get('webContentLink') or f"https://drive.google.com/file/d/{file_id}/view"
        except Exception as e:
            print(f"Error en _gdrive_upload: {str(e)}")
            return None

    def get_file_info(self, file_id: int, user_id: int) -> Optional[dict]:
        """
        Obtiene información de un archivo subido por el usuario.
        """
        archivo = self.archivo_repo.get(file_id)
        if not archivo or not archivo.estado:
            return None
        
        # En un entorno real, aquí buscarías la información del archivo físico
        # Por ahora, retornamos la información básica
        return {
            "id_archivo": archivo.id_archivo,
            "nombre": archivo.nombre,
            "descripcion": archivo.descripcion,
            "estado": archivo.estado,
            "fecha_subida": datetime.now().isoformat(),  # En realidad vendría de la BD
            "tipo": "PDF"
        }

    def list_user_files(self, user_id: int, *, skip: int = 0, limit: int = 100) -> List[dict]:
        """
        Lista archivos subidos por el usuario.
        """
        # En un entorno real, filtrarías por user_id
        # Por ahora, retornamos todos los archivos activos
        archivos = self.archivo_repo.list(skip=skip, limit=limit)
        
        result = []
        for archivo in archivos:
            if archivo.estado:  # Solo archivos activos
                result.append({
                    "id_archivo": archivo.id_archivo,
                    "nombre": archivo.nombre,
                    "descripcion": archivo.descripcion,
                    "estado": archivo.estado,
                    "tipo": "PDF"
                })
        
        return result

    def delete_file(self, file_id: int, user_id: int) -> bool:
        """
        Elimina un archivo (marca como inactivo).
        """
        archivo = self.archivo_repo.get(file_id)
        if not archivo:
            return False
        
        # Marcar como inactivo en lugar de eliminar físicamente
        success = self.archivo_repo.update(
            file_id,
            estado=False
        )
        
        # En un entorno real, también eliminarías el archivo físico
        # self._delete_physical_file(file_id)
        
        return success is not None

    def get_file_path(self, file_id: int, user_id: int) -> Optional[str]:
        """
        Obtiene la ruta del archivo físico.
        """
        archivo = self.archivo_repo.get(file_id)
        if not archivo or not archivo.estado:
            return None
        
        # En un entorno real, buscarías la ruta en la tabla de metadatos
        # Por ahora, retornamos una ruta genérica
        return f"/uploads/{archivo.id_archivo}.pdf"

    def validate_file_ids(self, file_ids: List[int]) -> dict:
        """
        Valida que los IDs de archivos existan y estén activos.
        Retorna información sobre archivos válidos e inválidos.
        """
        valid_files = []
        invalid_files = []
        
        for file_id in file_ids:
            archivo = self.archivo_repo.get(file_id)
            if archivo and archivo.estado:
                valid_files.append(file_id)
            else:
                invalid_files.append(file_id)
        
        return {
            "valid_files": valid_files,
            "invalid_files": invalid_files,
            "all_valid": len(invalid_files) == 0
        }

    # Nuevos helpers para leer metadatos/urls
    def get_file_url_metadata(self, archivo_id: int) -> Optional[dict]:
        meta_file = os.path.join(self.urls_dir, f"{archivo_id}.json")
        if not os.path.exists(meta_file):
            return None
        try:
            import json
            with open(meta_file, "r", encoding="utf-8") as f:
                data = json.load(f)
            return data
        except Exception:
            return None

    def list_user_urls(self, user_id: int) -> List[dict]:
        import json
        results: List[dict] = []
        try:
            for name in os.listdir(self.urls_dir):
                if not name.endswith(".json"):
                    continue
                path = os.path.join(self.urls_dir, name)
                try:
                    with open(path, "r", encoding="utf-8") as f:
                        data = json.load(f)
                    if data.get("user_id") == user_id:
                        results.append(data)
                except Exception:
                    continue
        except FileNotFoundError:
            return []
        return results
