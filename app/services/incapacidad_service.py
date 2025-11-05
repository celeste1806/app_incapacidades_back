from __future__ import annotations

from typing import List, Optional, Any, Dict
from sqlalchemy.orm import Session
from datetime import datetime
from decimal import Decimal, InvalidOperation

from app.repositories.incapacidad import IncapacidadRepository
from app.repositories.archivo_repository import ArchivoRepository
from app.repositories.relacion_repository import RelacionRepository
from app.repositories.parametro_hijo_repository import ParametroHijoRepository
from app.schemas.incapacidad import IncapacidadCreate, IncapacidadAdministrativaUpdate, IncapacidadFormularioUpdate
from app.services.upload_service import UploadService
from fastapi import UploadFile
import os
import uuid
from app.services.notification_service import NotificationService
from app.services.audit_service import AuditService, AuditAction


class IncapacidadService:
    def __init__(self, db: Session) -> None:
        self.db = db
        self.repo = IncapacidadRepository(db)
        self.archivo_repo = ArchivoRepository(db)
        self.rel_repo = RelacionRepository(db)
        self.param_hijo_repo = ParametroHijoRepository(db)
        self.upload_service = UploadService(db)
        self.notification_service = NotificationService(db)
        self.audit_service = AuditService(db)

    def _normalize_incapacidad_row(self, row: Dict[str, Any]) -> Dict[str, Any]:
        if not isinstance(row, dict):
            return row
        # Normalizar salario: la BD lo guarda como VARCHAR y puede venir ''
        salario_val = row.get("salario")
        if salario_val in ("", None):
            row["salario"] = Decimal("0")
        else:
            try:
                row["salario"] = Decimal(str(salario_val))
            except (InvalidOperation, ValueError, TypeError):
                row["salario"] = Decimal("0")

        # Normalizar fecha_registro si viene nula
        if row.get("fecha_registro") is None:
            row["fecha_registro"] = datetime.utcnow()

        return row

    def validar_google_drive_disponible(self) -> bool:
        """
        Valida que Google Drive esté configurado y disponible antes de crear incapacidades.
        Retorna True si está disponible, False si no.
        """
        try:
            print("🔍 Validando disponibilidad de Google Drive...")
            
            # Verificar configuración básica
            if not self.upload_service.gdrive_service_account_json and not self.upload_service.gdrive_oauth_json:
                print("❌ No hay credenciales de Google Drive configuradas")
                return False
            
            # Intentar configurar Google Drive
            if not self.upload_service._ensure_gdrive():
                print("❌ No se pudo configurar Google Drive")
                return False
            
            # Hacer una prueba de subida con un archivo pequeño
            test_content = b"Test de Google Drive - " + str(datetime.now()).encode()
            test_filename = f"test_gdrive_{uuid.uuid4().hex[:8]}.txt"
            
            print(f"🧪 Probando subida a Google Drive con archivo de prueba...")
            test_url = self.upload_service._gdrive_upload(
                test_content,
                original_name=test_filename,
                mime_type="text/plain"
            )
            
            if test_url:
                print(f"✅ Google Drive funcionando correctamente: {test_url}")
                return True
            else:
                print("❌ La prueba de subida a Google Drive falló")
                return False
                
        except Exception as e:
            print(f"❌ Error validando Google Drive: {str(e)}")
            return False

    def subir_documento_y_crear_registro(self, *, usuario_id: int, incapacidad_id: int, archivo_id: int, file: UploadFile) -> dict:
        """Guarda un archivo (pdf/png/jpg) SOLO en Google Drive y crea registro en incapacidad_archivo.
        url_documento almacenará la URL de Google Drive.
        """
        # Validar existencia de FK para evitar errores de integridad
        if not self.repo.get(incapacidad_id):
            raise ValueError(f"incapacidad_id {incapacidad_id} no existe")
        if not self.archivo_repo.get(archivo_id):
            raise ValueError(f"archivo_id {archivo_id} no existe")
        # Validar tipo
        allowed = {"application/pdf", "image/png", "image/jpeg"}
        content_type = (file.content_type or "").lower()
        if content_type not in allowed:
            raise ValueError("Formato no permitido. Use PDF, PNG o JPG")

        # Leer contenido del archivo
        content = file.file.read()
        
        # Nombre único conservando extensión
        ext = ".pdf" if content_type == "application/pdf" else (".png" if content_type == "image/png" else ".jpg")
        filename = f"{uuid.uuid4()}{ext}"

        # Subir SOLO a Google Drive
        gdrive_url = None
        try:
            print(f"📤 Subiendo archivo a Google Drive: {filename}")
            if self.upload_service._ensure_gdrive():
                gdrive_url = self.upload_service._gdrive_upload(
                    content, 
                    original_name=filename, 
                    mime_type=content_type
                )
                if gdrive_url:
                    print(f"✅ Archivo subido exitosamente a Google Drive: {gdrive_url}")
                else:
                    print(f"❌ Error: No se pudo subir a Google Drive")
                    raise ValueError("No se pudo subir el archivo a Google Drive")
            else:
                print(f"❌ Error: No se pudo configurar Google Drive")
                raise ValueError("No se pudo configurar Google Drive")
        except Exception as e:
            print(f"❌ Error subiendo a Google Drive: {str(e)}")
            raise ValueError(f"Error al subir archivo a Google Drive: {str(e)}")

        # Verificar si ya existe un archivo para esta incapacidad y archivo_id
        existing = self.repo.get_archivo_by_ids(incapacidad_id=incapacidad_id, archivo_id=archivo_id)
        print(f"DEBUG SERVICE: Verificando archivo existente para incapacidad_id={incapacidad_id}, archivo_id={archivo_id}")
        print(f"DEBUG SERVICE: Archivo existente: {existing}")
        
        if existing:
            print(f"DEBUG SERVICE: ⚠️ Archivo EXISTENTE encontrado, procediendo a ACTUALIZAR...")
            # Actualizar registro existente
            updated = self.repo.update_archivo_url(
                incapacidad_id=incapacidad_id,
                archivo_id=archivo_id,
                url_documento=gdrive_url
            )
            if not updated:
                print(f"DEBUG SERVICE: ❌ Error: No se pudo actualizar el registro")
                raise ValueError("No se pudo actualizar el registro de incapacidad_archivo")
            print(f"DEBUG SERVICE: ✅ Archivo actualizado exitosamente")
            created = self.repo.get_archivo_by_ids(incapacidad_id=incapacidad_id, archivo_id=archivo_id)
        else:
            print(f"DEBUG SERVICE: ✅ Archivo NO existe, procediendo a CREAR nuevo registro...")
            # Crear nuevo registro en BD con la URL de Google Drive
            created = self.repo.add_archivo_with_filename(
                incapacidad_id=incapacidad_id,
                archivo_id=archivo_id,
                filename=gdrive_url,  # Guardar la URL de Google Drive en lugar del nombre local
            )
            print(f"DEBUG SERVICE: ✅ Nuevo archivo creado: {created}")
        if not created:
            raise ValueError("No se pudo crear el registro de incapacidad_archivo")

        # Auditoría simple
        self.audit_service.log_file_upload(
            file_id=created.get("archivo_id", 0),
            user_id=usuario_id,
            filename=filename,
            file_size=len(content) if content else 0,
        )

        return {
            "id_incapacidad_archivo": created.get("id_incapacidad_archivo") or created.get("id"),
            "incapacidad_id": created.get("incapacidad_id"),
            "archivo_id": created.get("archivo_id"),
            "url_documento": gdrive_url,  # URL de Google Drive
            "gdrive_url": gdrive_url,    # URL de Google Drive (para compatibilidad)
            "fecha_subida": created.get("fecha_subida"),
        }

    def _documentos_requeridos_ids(self, tipo_incapacidad_id: int) -> List[int]:
        relaciones = self.rel_repo.list_by_tipo_incapacidad(tipo_incapacidad_id=tipo_incapacidad_id)
        return [rel.archivo_id for rel in relaciones]

    def crear_incapacidad(self, *, usuario_id: int, payload: IncapacidadCreate) -> dict:
        try:
            print(f"DEBUG: Iniciando creación de incapacidad para usuario {usuario_id}")
            print(f"DEBUG: Payload recibido: {payload}")
            
            # VALIDACIÓN CRÍTICA: Verificar que Google Drive esté disponible
            print(f"🔍 Validando disponibilidad de Google Drive antes de crear incapacidad...")
            if not self.validar_google_drive_disponible():
                error_msg = "No se puede crear la incapacidad: Google Drive no está disponible para guardar los archivos"
                print(f"❌ {error_msg}")
                raise ValueError(error_msg)
            
            print(f"✅ Google Drive validado correctamente, procediendo con la creación...")
            
            # Crear usando las columnas exactas de la BD según el esquema real
            print(f"DEBUG: Creando incapacidad en BD (columnas reales)...")
            inc = self.repo.create_by_ids(
                tipo_incapacidad_id=payload.tipo_incapacidad_id,
                usuario_id=usuario_id,
                fecha_inicio=payload.fecha_inicio,
                fecha_final=payload.fecha_final,
                dias=payload.dias,
                estado=11,  # 11 = Enviado (parametro_hijo)
                causa_incapacidad_id=payload.causa_id,  # FK a parametro_hijo (causa)
                Eps_id=payload.eps_afiliado_id,       # FK a parametro_hijo (EPS)
                servicio_id=payload.servicio_id,      # FK a parametro_hijo (servicio)
                diagnostico_id=payload.diagnostico_id, # FK a parametro_hijo (diagnóstico)
                salario_id=None,                       # No se usa por ahora
                salario=str(payload.salario),          # Guardar en columna 'salario' (varchar en BD)
            )
            print(f"DEBUG: Incapacidad creada: {inc}")

            # Normalizar claves a las esperadas por los esquemas de salida
            if isinstance(inc, dict):
                if 'causa_incapacidad_id' in inc and 'causa_id' not in inc:
                    inc['causa_id'] = inc.get('causa_incapacidad_id')
                if 'Eps_id' in inc and 'eps_afiliado_id' not in inc:
                    inc['eps_afiliado_id'] = inc.get('Eps_id')
                # limpiar claves específicas de BD que no están en el schema de salida
                for k in ('Eps_id', 'causa_incapacidad_id', 'salario_id', 'administrador_id'):
                    inc.pop(k, None)
            
            # (Eliminado) Asociación de documentos
            
            # Registrar auditoría
            print(f"DEBUG: Registrando auditoría...")
            self.audit_service.log_incapacity_action(
                action=AuditAction.CREATE,
                incapacidad_id=inc["id_incapacidad"],
                user_id=usuario_id,
                details={
                    "tipo_incapacidad_id": payload.tipo_incapacidad_id,
                    "causa_id": payload.causa_id,
                    "dias": payload.dias,
                    "archivos_count": 0
                }
            )
            print(f"DEBUG: Auditoría registrada")
            
            # Notificar al administrador
            print(f"DEBUG: Enviando notificación...")
            self.notification_service.notify_new_incapacity(inc["id_incapacidad"])
            print(f"DEBUG: Notificación enviada")
            
            # Resolver IDs y eliminar campos de texto para respuesta
            if inc.get("diagnostico"):
                found = self.param_hijo_repo.find_by_nombre_exact(inc["diagnostico"])
                inc["diagnostico_id"] = getattr(found, "id_parametrohijo", None) if found else None
            if inc.get("eps_afiliado"):
                found = self.param_hijo_repo.find_by_nombre_exact(inc["eps_afiliado"])
                inc["eps_afiliado_id"] = getattr(found, "id_parametrohijo", None) if found else None
            if inc.get("servicio"):
                found = self.param_hijo_repo.find_by_nombre_exact(inc["servicio"])
                inc["servicio_id"] = getattr(found, "id_parametrohijo", None) if found else None
            if inc.get("clase"):
                found = self.param_hijo_repo.find_by_nombre_exact(inc["clase"])
                inc["clase_id"] = getattr(found, "id_parametrohijo", None) if found else None

            # Eliminar campos de texto
            for k in ("diagnostico", "eps_afiliado", "servicio", "clase"):
                inc.pop(k, None)

            return self._normalize_incapacidad_row(inc)
            
        except Exception as e:
            print(f"DEBUG: Error en crear_incapacidad: {str(e)}")
            print(f"DEBUG: Tipo de error: {type(e)}")
            import traceback
            print(f"DEBUG: Traceback: {traceback.format_exc()}")
            raise

    def listar_mis_incapacidades(self, *, usuario_id: int, skip: int = 0, limit: int = 100) -> List[dict]:
        """Lista incapacidades del empleado sin mostrar estados ni campos administrativos"""
        data = self.repo.list_by_user(usuario_id, skip=skip, limit=limit)
        # Normalizar filas
        data = [self._normalize_incapacidad_row(dict(row)) for row in data]
        
        # Agregar información de cumplimiento de documentos
        for row in data:
            # Alinear nombre de la columna de causa a 'causa_id'
            if row.get("causa_id") is None and row.get("causa_incapacidad_id") is not None:
                row["causa_id"] = row.get("causa_incapacidad_id")
            cumplimiento = self.repo.get_documentos_cumplimiento(
                row["id_incapacidad"], 
                row["tipo_incapacidad_id"]
            )
            row["documentos_cumplimiento"] = cumplimiento

            # Resolver IDs para diagnostico, eps, servicio y clase si están por nombre
            if row.get("diagnostico") and not row.get("diagnostico_id"):
                found = self.param_hijo_repo.find_by_nombre_exact(row["diagnostico"])
                row["diagnostico_id"] = getattr(found, "id_parametrohijo", None) if found else None
            if row.get("eps_afiliado") and not row.get("eps_afiliado_id"):
                found = self.param_hijo_repo.find_by_nombre_exact(row["eps_afiliado"])
                row["eps_afiliado_id"] = getattr(found, "id_parametrohijo", None) if found else None
            if row.get("servicio") and not row.get("servicio_id"):
                found = self.param_hijo_repo.find_by_nombre_exact(row["servicio"])
                row["servicio_id"] = getattr(found, "id_parametrohijo", None) if found else None
            if row.get("clase") and not row.get("clase_id"):
                found = self.param_hijo_repo.find_by_nombre_exact(row["clase"])
                row["clase_id"] = getattr(found, "id_parametrohijo", None) if found else None
            
            # Resolver IDs y eliminar campos de texto
            if row.get("diagnostico"):
                found = self.param_hijo_repo.find_by_nombre_exact(row["diagnostico"])
                row["diagnostico_id"] = getattr(found, "id_parametrohijo", None) if found else None
            if row.get("eps_afiliado"):
                found = self.param_hijo_repo.find_by_nombre_exact(row["eps_afiliado"])
                row["eps_afiliado_id"] = getattr(found, "id_parametrohijo", None) if found else None
            if row.get("servicio"):
                found = self.param_hijo_repo.find_by_nombre_exact(row["servicio"])
                row["servicio_id"] = getattr(found, "id_parametrohijo", None) if found else None
            if row.get("clase"):
                found = self.param_hijo_repo.find_by_nombre_exact(row["clase"])
                row["causa_id"] = getattr(found, "id_parametrohijo", None) if found else None

            for k in ("diagnostico", "eps_afiliado", "servicio", "clase"):
                row.pop(k, None)

            # Eliminar campos que el empleado no debe ver (conservar 'estado' y 'mensaje_rechazo')
            campos_admin = ['clase_administrativa', 'numero_radicado', 
                          'fecha_radicado', 'paga', 'estado_administrativo', 'usuario_revisor_id']
            for campo in campos_admin:
                row.pop(campo, None)
            # Asegurar presencia explícita de 'estado' y 'mensaje_rechazo' si existen en la fila original
            if 'estado' in row:
                try:
                    row['estado'] = int(row['estado'])
                except Exception:
                    pass
            if 'mensaje_rechazo' not in row:
                # intentar mapear si llega con otro nombre común
                if 'motivo_rechazo' in row:
                    row['mensaje_rechazo'] = row.get('motivo_rechazo')
                
            # 1. NOMBRE tipo de incapacidad (catálogo ParametroHijo)
            if row.get("tipo_incapacidad_id"):
                t = self.param_hijo_repo.obtener_id(row["tipo_incapacidad_id"])
                if t:
                    row["tipo_incapacidad_nombre"] = getattr(t, "nombre", None) or ''
                else:
                    row["tipo_incapacidad_nombre"] = ''
            else:
                row["tipo_incapacidad_nombre"] = ''

            # 2. DOCUMENTOS adjuntos de la incapacidad
            from app.repositories.archivo_repository import ArchivoRepository
            from sqlalchemy import text
            archivo_repo = ArchivoRepository(self.db)
            # Obtener todos los archivos en incapacidad_archivo por incapacidad_id
            docs = self.db.execute(text(f'SELECT * FROM incapacidad_archivo WHERE incapacidad_id = :inc'), {"inc": row["id_incapacidad"]}).mappings().all()
            row["documentos"] = [dict(a) for a in docs] if docs else []

        return data

    def obtener_mi_incapacidad(self, *, usuario_id: int, id_incapacidad: int) -> Optional[dict]:
        """Obtiene detalle de incapacidad del empleado sin campos administrativos"""
        inc = self.repo.get_with_documents(id_incapacidad)
        inc = self._normalize_incapacidad_row(inc) if inc else inc
        if not inc or inc["usuario_id"] != usuario_id:
            return None
        # Alinear nombre de la columna de causa a 'causa_id'
        if inc.get("causa_id") is None and inc.get("causa_incapacidad_id") is not None:
            inc["causa_id"] = inc.get("causa_incapacidad_id")
            
        # Alinear nombre de la columna de EPS a 'Eps_id' para el esquema
        if inc.get("Eps_id") is None and inc.get("eps_afiliado_id") is not None:
            inc["Eps_id"] = inc.get("eps_afiliado_id")
            
        # Agregar cumplimiento de documentos
        cumplimiento = self.repo.get_documentos_cumplimiento(
            inc["id_incapacidad"], 
            inc["tipo_incapacidad_id"]
        )
        inc["documentos_cumplimiento"] = cumplimiento
        
        # Resolver IDs para diagnostico, eps, servicio y clase si están por nombre
        if inc.get("diagnostico"):
            found = self.param_hijo_repo.find_by_nombre_exact(inc["diagnostico"])
            inc["diagnostico_id"] = getattr(found, "id_parametrohijo", None) if found else None
        if inc.get("eps_afiliado"):
            found = self.param_hijo_repo.find_by_nombre_exact(inc["eps_afiliado"])
            inc["eps_afiliado_id"] = getattr(found, "id_parametrohijo", None) if found else None
        if inc.get("servicio"):
            found = self.param_hijo_repo.find_by_nombre_exact(inc["servicio"])
            inc["servicio_id"] = getattr(found, "id_parametrohijo", None) if found else None
        if inc.get("clase"):
            found = self.param_hijo_repo.find_by_nombre_exact(inc["clase"])
            inc["causa_id"] = getattr(found, "id_parametrohijo", None) if found else None

        for k in ("diagnostico", "eps_afiliado", "servicio", "clase"):
            inc.pop(k, None)

        # Eliminar campos administrativos (conservar 'estado' y 'mensaje_rechazo')
        campos_admin = ['clase_administrativa', 'numero_radicado', 
                      'fecha_radicado', 'paga', 'estado_administrativo', 'usuario_revisor_id']
        for campo in campos_admin:
            inc.pop(campo, None)
        # Asegurar presencia explícita de 'estado' y 'mensaje_rechazo'
        if 'estado' in inc:
            try:
                inc['estado'] = int(inc['estado'])
            except Exception:
                pass
        if 'mensaje_rechazo' not in inc and 'motivo_rechazo' in inc:
            inc['mensaje_rechazo'] = inc.get('motivo_rechazo')
            
        return inc

    def listar_admin(self, *, 
                    skip: int = 0, 
                    limit: int = 100, 
                    estado: Optional[int] = None,
                    tipo_incapacidad_id: Optional[int] = None,
                    usuario_id: Optional[int] = None,
                    fecha_inicio: Optional[datetime] = None,
                    fecha_final: Optional[datetime] = None) -> List[dict]:
        """Lista todas las incapacidades con filtros para administrador"""
        print(f"DEBUG: listar_admin llamado con estado={estado}, skip={skip}, limit={limit}")
        data = self.repo.list_all_with_details(
            skip=skip, 
            limit=limit, 
            estado=estado,
            tipo_incapacidad_id=tipo_incapacidad_id,
            usuario_id=usuario_id,
            fecha_inicio=fecha_inicio,
            fecha_final=fecha_final
        )
        print(f"DEBUG: Datos obtenidos del repositorio: {len(data)} registros")
        if data:
            print(f"DEBUG: Primer registro: {data[0]}")
            print(f"DEBUG: Campos del primer registro: {list(data[0].keys())}")
        
        normalized_data = [self._normalize_incapacidad_row(dict(row)) for row in data]
        
        # Resolver nombres de tipos de incapacidad para cada registro
        from app.repositories.tipo_incapacidad import TipoIncapacidadRepository
        tipo_repo = TipoIncapacidadRepository(self.db)
        for inc in normalized_data:
            if inc.get("tipo_incapacidad_id"):
                tipo = tipo_repo.obtener_id(inc["tipo_incapacidad_id"])
                inc["tipo_incapacidad_nombre"] = tipo.nombre if tipo else ''
                inc["tipo_incapacidad"] = {
                    "id_tipo_incapacidad": tipo.id_tipo_incapacidad,
                    "nombre": tipo.nombre,
                    "descripcion": tipo.descripcion
                }
            else:
                inc["tipo_incapacidad_nombre"] = "Tipo no especificado"
                inc["tipo_incapacidad"] = {"id_tipo_incapacidad": None, "nombre": "Tipo no especificado"}
        
        # Alinear y exponer mensaje_rechazo si existe con diferentes nombres
        for row in normalized_data:
            if 'mensaje_rechazo' not in row:
                if 'motivo_rechazo' in row:
                    row['mensaje_rechazo'] = row.get('motivo_rechazo')
                elif 'mensaje' in row:
                    row['mensaje_rechazo'] = row.get('mensaje')
        # Mantener usuario_id como entero; el frontend debe usar usuario_nombre para mostrar
        print(f"DEBUG: Datos normalizados: {len(normalized_data)} registros")
        if normalized_data:
            print(f"DEBUG: Primer registro normalizado: {normalized_data[0]}")
            print(f"DEBUG: Campos del primer registro normalizado: {list(normalized_data[0].keys())}")
        
        # Agregar estados de incapacidad disponibles para el frontend
        print(f"DEBUG: Iniciando consulta de estados con parametro_id=6")
        
        try:
            # Consulta SQL directa para asegurar que funcione
            from sqlalchemy import text
            query = text("SELECT id_parametrohijo, nombre, descripcion FROM parametro_hijo WHERE parametro_id = 6")
            result = self.db.execute(query)
            estados_disponibles = result.fetchall()
            
            print(f"DEBUG: Consulta SQL ejecutada exitosamente")
            print(f"DEBUG: Estados encontrados para parametro_id=6: {len(estados_disponibles)}")
            
            if estados_disponibles:
                for i, estado in enumerate(estados_disponibles):
                    print(f"DEBUG: Estado {i+1} - ID: {estado.id_parametrohijo}, Nombre: {estado.nombre}, Descripcion: {estado.descripcion}")
            else:
                print(f"DEBUG: No se encontraron estados para parametro_id=6")
                
        except Exception as e:
            print(f"DEBUG: Error al consultar estados: {e}")
            print(f"DEBUG: Tipo de error: {type(e)}")
            estados_disponibles = []
        
        estados_data = []
        for estado in estados_disponibles:
            estados_data.append({
                "id_parametrohijo": estado.id_parametrohijo,
                "nombre": estado.nombre,
                "descripcion": estado.descripcion
            })
        
        print(f"DEBUG: Estados_data preparados: {estados_data}")
        
        # Crear respuesta con datos y estados disponibles
        response_data = {
            "incapacidades": normalized_data,
            "estados_disponibles": estados_data
        }
        
        print(f"DEBUG: Respuesta final preparada con {len(normalized_data)} incapacidades y {len(estados_data)} estados")
        return response_data

    def obtener_incapacidad_admin(self, *, id_incapacidad: int) -> Optional[dict]:
        """Obtiene detalle completo de incapacidad para administrador"""
        print(f"DEBUG: obtener_incapacidad_admin llamado para ID {id_incapacidad}")
        inc = self.repo.get_with_documents(id_incapacidad)
        print(f"DEBUG: Datos obtenidos del repositorio: {inc}")
        print(f"DEBUG: Campos disponibles en inc: {list(inc.keys()) if inc else 'None'}")
        inc = self._normalize_incapacidad_row(inc) if inc else inc
        print(f"DEBUG: Datos después de normalización: {inc}")
        print(f"DEBUG: Campos después de normalización: {list(inc.keys()) if inc else 'None'}")
        if not inc:
            print(f"DEBUG: No se encontró incapacidad con ID {id_incapacidad}")
            return None
            
        # Alinear nombre de la columna de causa a 'causa_id'
        if inc.get("causa_id") is None and inc.get("causa_incapacidad_id") is not None:
            inc["causa_id"] = inc.get("causa_incapacidad_id")
            
        # Alinear nombre de la columna de EPS a 'Eps_id' para el esquema
        if inc.get("Eps_id") is None and inc.get("eps_afiliado_id") is not None:
            inc["Eps_id"] = inc.get("eps_afiliado_id")
            
        # Resolver IDs para diagnostico, eps, servicio y clase si están por nombre
        if inc.get("diagnostico"):
            found = self.param_hijo_repo.find_by_nombre_exact(inc["diagnostico"])
            inc["diagnostico_id"] = getattr(found, "id_parametrohijo", None) if found else None
        if inc.get("eps_afiliado"):
            found = self.param_hijo_repo.find_by_nombre_exact(inc["eps_afiliado"])
            inc["eps_afiliado_id"] = getattr(found, "id_parametrohijo", None) if found else None
        if inc.get("servicio"):
            found = self.param_hijo_repo.find_by_nombre_exact(inc["servicio"])
            inc["servicio_id"] = getattr(found, "id_parametrohijo", None) if found else None
        if inc.get("clase"):
            found = self.param_hijo_repo.find_by_nombre_exact(inc["clase"])
            inc["causa_id"] = getattr(found, "id_parametrohijo", None) if found else None
        
        # Resolver nombres desde IDs para mostrar en el frontend
        print(f"DEBUG: Iniciando resolución de nombres...")
        print(f"DEBUG: eps_afiliado_id={inc.get('eps_afiliado_id')}, eps_afiliado={inc.get('eps_afiliado')}")
        print(f"DEBUG: servicio_id={inc.get('servicio_id')}, servicio={inc.get('servicio')}")
        print(f"DEBUG: diagnostico_id={inc.get('diagnostico_id')}, diagnostico={inc.get('diagnostico')}")
        
        # Resolver EPS
        eps_id = inc.get("eps_afiliado_id") or inc.get("Eps_id")
        if eps_id:
            found = self.param_hijo_repo.obtener_id(eps_id)
            inc["eps_afiliado_nombre"] = found.nombre if found else inc.get("eps_afiliado")
            print(f"DEBUG EPS: eps_id={eps_id}, found={found}, nombre={found.nombre if found else inc.get('eps_afiliado')}")
        elif inc.get("eps_afiliado"):
            inc["eps_afiliado_nombre"] = inc.get("eps_afiliado")
            print(f"DEBUG EPS: No hay eps_id, usando eps_afiliado={inc.get('eps_afiliado')}")
        else:
            inc["eps_afiliado_nombre"] = "No especificado"
            print(f"DEBUG EPS: No hay datos de EPS disponibles")
            
        # Resolver Servicio
        if inc.get("servicio_id"):
            found = self.param_hijo_repo.obtener_id(inc["servicio_id"])
            inc["servicio_nombre"] = found.nombre if found else inc.get("servicio")
            print(f"DEBUG SERVICIO: servicio_id={inc['servicio_id']}, found={found}, nombre={found.nombre if found else inc.get('servicio')}")
        elif inc.get("servicio"):
            inc["servicio_nombre"] = inc.get("servicio")
            print(f"DEBUG SERVICIO: No hay servicio_id, usando servicio={inc.get('servicio')}")
        else:
            inc["servicio_nombre"] = "No especificado"
            print(f"DEBUG SERVICIO: No hay datos de servicio disponibles")
            
        # Resolver Diagnóstico
        if inc.get("diagnostico_id"):
            found = self.param_hijo_repo.obtener_id(inc["diagnostico_id"])
            inc["diagnostico_nombre"] = found.nombre if found else inc.get("diagnostico")
            print(f"DEBUG DIAGNOSTICO: diagnostico_id={inc['diagnostico_id']}, found={found}, nombre={found.nombre if found else inc.get('diagnostico')}")
        elif inc.get("diagnostico"):
            inc["diagnostico_nombre"] = inc.get("diagnostico")
            print(f"DEBUG DIAGNOSTICO: No hay diagnostico_id, usando diagnostico={inc.get('diagnostico')}")
        else:
            inc["diagnostico_nombre"] = "No especificado"
            print(f"DEBUG DIAGNOSTICO: No hay datos de diagnóstico disponibles")
            
        if inc.get("causa_incapacidad_id"):
            found = self.param_hijo_repo.obtener_id(inc["causa_incapacidad_id"])
            inc["clase_nombre"] = found.nombre if found else inc.get("clase")
        else:
            inc["clase_nombre"] = inc.get("clase")
        
        # Resolver nombre del usuario
        if inc.get("usuario_id"):
            from app.repositories.usuario_repository import UsuarioRepository
            usuario_repo = UsuarioRepository(self.db)
            usuario = usuario_repo.get(inc["usuario_id"])
            if usuario:
                inc["usuario_nombre"] = usuario.nombre_completo or f"Usuario {inc['usuario_id']}"
                inc["usuario"] = {
                    "id_usuario": usuario.id_usuario,
                    "nombre_completo": usuario.nombre_completo,
                    "correo_electronico": usuario.correo_electronico
                }
            else:
                inc["usuario_nombre"] = f"Usuario {inc['usuario_id']}"
                inc["usuario"] = {"id_usuario": inc["usuario_id"], "nombre_completo": f"Usuario {inc['usuario_id']}"}
        else:
            inc["usuario_nombre"] = "Usuario no especificado"
            inc["usuario"] = {"id_usuario": None, "nombre_completo": "Usuario no especificado"}
            
        # Resolver nombre del tipo de incapacidad
        if inc.get("tipo_incapacidad_id"):
            from app.repositories.tipo_incapacidad import TipoIncapacidadRepository
            tipo_repo = TipoIncapacidadRepository(self.db)
            tipo = tipo_repo.obtener_id(inc["tipo_incapacidad_id"])
            if tipo:
                inc["tipo_incapacidad_nombre"] = tipo.nombre
                inc["tipo_incapacidad"] = {
                    "id_tipo_incapacidad": tipo.id_tipo_incapacidad,
                    "nombre": tipo.nombre,
                    "descripcion": tipo.descripcion
                }
            else:
                inc["tipo_incapacidad_nombre"] = f"Tipo {inc['tipo_incapacidad_id']}"
                inc["tipo_incapacidad"] = {"id_tipo_incapacidad": inc["tipo_incapacidad_id"], "nombre": f"Tipo {inc['tipo_incapacidad_id']}"}
        else:
            inc["tipo_incapacidad_nombre"] = "Tipo no especificado"
            inc["tipo_incapacidad"] = {"id_tipo_incapacidad": None, "nombre": "Tipo no especificado"}
        
        # Mantener campos de texto como respaldo
        # for k in ("diagnostico", "eps_afiliado", "servicio", "clase"):
        #     inc.pop(k, None)
        print(f"DEBUG: Datos finales devueltos: {inc}")
        return inc

    def marcar_revisada(self, *, id_incapacidad: int) -> bool:
        """Marca incapacidad como revisada (método simple)"""
        # Obtener estado actual para auditoría
        inc_actual = self.repo.get(id_incapacidad)
        if not inc_actual:
            return False
            
        old_status = inc_actual.get("estado", 11)
        success = self.repo.update_estado(id_incapacidad, estado=12)  # 12 = Revisado (parametro_hijo)
        
        if success:
            # Registrar auditoría
            self.audit_service.log_status_change(
                incapacidad_id=id_incapacidad,
                user_id=0,  # Sistema
                old_status=old_status,
                new_status=12,
                reason="Marcada como revisada"
            )
        
        return success

    def actualizar_administrativo(self, *, 
                                id_incapacidad: int, 
                                admin_id: int,
                                payload: IncapacidadAdministrativaUpdate) -> bool:
        """Actualiza campos administrativos y marca como revisada (usa columnas reales)."""
        success = self.repo.update_administrativo(
            id_incapacidad=id_incapacidad,
            id_admin=admin_id,
            valor_pago=getattr(payload, 'valor_pago', None),
            numero_radicado=getattr(payload, 'numero_radicado', None),
            fecha_radicado=getattr(payload, 'fecha_radicado', None),
            fecha_pago=getattr(payload, 'fecha_pago', None),
            estado=getattr(payload, 'estado', 12) or 12,
        )
        
        # Registrar auditoría y notificar
        if success:
            # Auditoría de cambios administrativos
            changes = {}
            if payload.numero_radicado is not None:
                changes["numero_radicado"] = payload.numero_radicado
            if payload.fecha_radicado is not None:
                changes["fecha_radicado"] = payload.fecha_radicado.isoformat()
            if getattr(payload, 'fecha_pago', None) is not None:
                changes["fecha_pago"] = payload.fecha_pago.isoformat()
            if getattr(payload, 'valor_pago', None) is not None:
                changes["valor_pago"] = str(payload.valor_pago)
            if getattr(payload, 'estado', None) is not None:
                changes["estado"] = int(payload.estado)
            
            self.audit_service.log_administrative_change(
                incapacidad_id=id_incapacidad,
                admin_id=admin_id,
                changes=changes
            )
            
            # Auditoría de cambio de estado
            self.audit_service.log_status_change(
                incapacidad_id=id_incapacidad,
                user_id=admin_id,
                old_status=11,
                new_status=12,
                reason="Actualización administrativa"
            )
            
            # Notificar al empleado
            self.notification_service.notify_incapacidad_reviewed(id_incapacidad, admin_id)
        
        return success

    def actualizar_formulario(self, *, 
                             id_incapacidad: int, 
                             admin_id: int,
                             payload: IncapacidadFormularioUpdate) -> bool:
        """Actualiza los datos del formulario de una incapacidad"""
        
        # Verificar que la incapacidad existe
        inc_actual = self.repo.get(id_incapacidad)
        if not inc_actual:
            return False
            
        # Actualizar los datos del formulario
        success = self.repo.update_formulario(
            id_incapacidad=id_incapacidad,
            fecha_inicio=payload.fecha_inicio,
            fecha_final=payload.fecha_final,
            dias=payload.dias,
            salario=payload.salario,
            eps_afiliado_id=payload.eps_afiliado_id,
            servicio_id=payload.servicio_id,
            diagnostico_id=payload.diagnostico_id
        )
        
        # Registrar auditoría si la actualización fue exitosa
        if success:
            # Auditoría de cambios del formulario
            changes = {}
            if payload.fecha_inicio is not None:
                changes["fecha_inicio"] = payload.fecha_inicio.isoformat()
            if payload.fecha_final is not None:
                changes["fecha_final"] = payload.fecha_final.isoformat()
            if payload.dias is not None:
                changes["dias"] = payload.dias
            if payload.salario is not None:
                changes["salario"] = str(payload.salario)
            if payload.eps_afiliado_id is not None:
                changes["eps_afiliado_id"] = payload.eps_afiliado_id
            if payload.servicio_id is not None:
                changes["servicio_id"] = payload.servicio_id
            if payload.diagnostico_id is not None:
                changes["diagnostico_id"] = payload.diagnostico_id
            
            self.audit_service.log_incapacity_action(
                action=AuditAction.UPDATE,
                incapacidad_id=id_incapacidad,
                user_id=admin_id,
                details={"tipo": "formulario", "cambios": changes}
            )
        
        return success

    def actualizar_formulario_empleado(self, *, id_incapacidad: int, usuario_id: int, payload: IncapacidadFormularioUpdate) -> bool:
        """Empleado actualiza datos de su incapacidad rechazada y la reenvía a revisión (estado=11)."""
        inc_actual = self.repo.get(id_incapacidad)
        if not inc_actual or int(inc_actual.get("usuario_id", 0)) != int(usuario_id):
            return False
        
        # NO eliminar archivos anteriores - los archivos se actualizarán si se suben nuevos
        archivos_eliminados = 0
        
        # Actualiza campos permitidos
        ok = self.repo.update_formulario(
            id_incapacidad=id_incapacidad,
            fecha_inicio=payload.fecha_inicio,
            fecha_final=payload.fecha_final,
            dias=payload.dias,
            salario=payload.salario,
            eps_afiliado_id=payload.eps_afiliado_id,
            servicio_id=payload.servicio_id,
            diagnostico_id=payload.diagnostico_id,
        )
        if not ok:
            return False
        # Reinicia estado a pendiente y limpia mensaje de rechazo
        self.repo.update_estado(id_incapacidad, estado=11)
        try:
            self.repo.update_mensaje_rechazo(id_incapacidad, "")
        except Exception:
            pass
        # Auditoría
        self.audit_service.log_incapacity_action(
            action=AuditAction.UPDATE,
            incapacidad_id=id_incapacidad,
            user_id=usuario_id,
            details={"tipo": "formulario_empleado_reenvio", "archivos_eliminados": archivos_eliminados if 'archivos_eliminados' in locals() else 0}
        )
        return True

    def cambiar_estado(self, *, id_incapacidad: int, nuevo_estado: int, admin_id: int, mensaje_rechazo: str = None) -> bool:
        """Cambia el estado de una incapacidad"""
        # Obtener estado actual para auditoría
        inc_actual = self.repo.get(id_incapacidad)
        if not inc_actual:
            return False
            
        old_status = inc_actual.get("estado", 11)
        success = self.repo.update_estado(id_incapacidad, estado=nuevo_estado)
        
        # Si es rechazo, actualizar también el mensaje
        if success and nuevo_estado == 50 and mensaje_rechazo:
            success = self.repo.update_mensaje_rechazo(id_incapacidad, mensaje_rechazo)
        
        if success:
            # Registrar auditoría
            self.audit_service.log_status_change(
                incapacidad_id=id_incapacidad,
                user_id=admin_id,
                old_status=old_status,
                new_status=nuevo_estado,
                reason=f"Cambio de estado por administrador" + (f" - Rechazo: {mensaje_rechazo}" if mensaje_rechazo else "")
            )
            
            # Enviar notificación según el tipo de cambio
            if nuevo_estado == 50:  # Rechazada
                print(f"DEBUG: Enviando notificación de rechazo para incapacidad {id_incapacidad}")
                self.notification_service.notify_incapacity_rejected(
                    incapacidad_id=id_incapacidad,
                    admin_id=admin_id,
                    motivo_rechazo=mensaje_rechazo
                )
            elif nuevo_estado == 12:  # Revisada/Realizada
                print(f"DEBUG: Enviando notificación de revisión para incapacidad {id_incapacidad}")
                self.notification_service.notify_incapacity_reviewed(
                    incapacidad_id=id_incapacidad,
                    admin_id=admin_id
                )
        
        return success

    def eliminar(self, *, id_incapacidad: int, admin_id: int) -> bool:
        """Elimina una incapacidad (solo para administradores)."""
        # Verificar existencia para auditar
        inc_actual = self.repo.get(id_incapacidad)
        if not inc_actual:
            return False
        ok = self.repo.delete(id_incapacidad)
        if ok:
            self.audit_service.log_incapacity_action(
                action=AuditAction.DELETE,
                incapacidad_id=id_incapacidad,
                user_id=admin_id,
                details={}
            )
        return ok

