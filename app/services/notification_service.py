from __future__ import annotations

import logging
from typing import List, Optional
from sqlalchemy.orm import Session
from datetime import datetime
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os

from app.repositories.usuario_repository import UsuarioRepository
from app.repositories.incapacidad import IncapacidadRepository


class NotificationService:
    def __init__(self, db: Session) -> None:
        self.db = db
        self.usuario_repo = UsuarioRepository(db)
        self.incapacidad_repo = IncapacidadRepository(db)
        self.logger = logging.getLogger(__name__)

    def notify_new_incapacity(self, incapacidad_id: int) -> bool:
        """
        Notifica a administradores sobre una nueva incapacidad registrada.
        """
        try:
            # Obtener información de la incapacidad
            incapacidad = self.incapacidad_repo.get(incapacidad_id)
            if not incapacidad:
                self.logger.error(f"Incapacidad {incapacidad_id} no encontrada para notificación")
                print(f"❌ Notificación: incapacidad {incapacidad_id} no encontrada")
                return False

            # Obtener información del empleado
            empleado = self.usuario_repo.get(incapacidad["usuario_id"])
            if not empleado:
                self.logger.error(f"Empleado {incapacidad['usuario_id']} no encontrado para notificación")
                return False

            # Obtener lista de administradores (rol_id = 10)
            administradores = self._get_administradores()
            
            if not administradores:
                self.logger.warning("No se encontraron administradores para notificar")
                print("⚠️ Notificación: no se encontraron administradores (rol_id=10, estado=True)")
                return False

            # LOGS DE DIAGNÓSTICO: listar destinatarios
            try:
                destinatarios = ", ".join([a.get("email", "(sin email)") for a in administradores])
            except Exception:
                destinatarios = "(error al listar destinatarios)"
            self.logger.info(f"📬 Administradores detectados para notificación ({len(administradores)}): {destinatarios}")
            print(f"📬 Admins detectados: {len(administradores)} -> {destinatarios}")

            # Verificar variables SMTP visibles en runtime (sin mostrar password)
            import os
            smtp_username = os.getenv('SMTP_USERNAME')
            smtp_password_set = bool(os.getenv('SMTP_PASSWORD'))
            smtp_server = os.getenv('SMTP_SERVER') or 'smtp.gmail.com'
            smtp_port = os.getenv('SMTP_PORT') or '587'
            print(f"🔧 SMTP en runtime -> SERVER={smtp_server} PORT={smtp_port} USER={smtp_username} PASS_SET={smtp_password_set}")

            # Preparar datos de la notificación
            notification_data = {
                "tipo": "nueva_incapacidad",
                "incapacidad_id": incapacidad_id,
                "empleado": {
                    "id": empleado.id_usuario,
                    "nombre": empleado.nombre_completo,
                    "email": empleado.correo_electronico
                },
                "incapacidad": {
                    "tipo_id": incapacidad.get("tipo_incapacidad_id"),
                    "clase": incapacidad.get("clase", "incapacidad"),
                    "fecha_inicio": incapacidad["fecha_inicio"].isoformat() if incapacidad.get("fecha_inicio") else None,
                    "fecha_final": incapacidad["fecha_final"].isoformat() if incapacidad.get("fecha_final") else None,
                    "dias": incapacidad.get("dias", 0),
                    "eps": incapacidad.get("eps_afiliado", "N/A"),
                    "servicio": incapacidad.get("servicio", "N/A"),
                    "diagnostico": incapacidad.get("diagnostico", "N/A")
                },
                "fecha_notificacion": datetime.now().isoformat()
            }

            # Enviar notificaciones
            success_count = 0
            for admin in administradores:
                self.logger.info(f"➡️  Intentando enviar notificación a admin: {admin.get('email')} ({admin.get('nombre')})")
                print(f"➡️ Enviando a: {admin.get('email')} ({admin.get('nombre')})")
                if self._send_notification_to_admin(admin, notification_data):
                    success_count += 1
                    self.logger.info(f"✅ Envío exitoso a: {admin.get('email')}")
                    print(f"✅ Enviado a: {admin.get('email')}")
                else:
                    self.logger.error(f"❌ Error al enviar a: {admin.get('email')}")
                    print(f"❌ Error al enviar a: {admin.get('email')}")

            self.logger.info(f"Notificación enviada a {success_count}/{len(administradores)} administradores")
            print(f"📊 Resultado notificación admins: {success_count}/{len(administradores)} enviados")
            return success_count > 0

        except Exception as e:
            self.logger.error(f"Error al enviar notificación de incapacidad {incapacidad_id}: {str(e)}")
            return False

    def notify_admins_new_incapacity(self, incapacidad_id: int, empleado_id: int) -> bool:
        """
        Alias para notify_new_incapacity para mantener compatibilidad con el router.
        Notifica a administradores sobre una nueva incapacidad registrada.
        """
        self.logger.info(f"🔔 Notificando a administradores sobre nueva incapacidad {incapacidad_id} del empleado {empleado_id}")
        return self.notify_new_incapacity(incapacidad_id)

    def notify_incapacity_reviewed(self, incapacidad_id: int, admin_id: int) -> bool:
        """
        Notifica al empleado cuando su incapacidad ha sido revisada.
        """
        try:
            # Obtener información de la incapacidad
            incapacidad = self.incapacidad_repo.get(incapacidad_id)
            if not incapacidad:
                return False

            # Obtener información del empleado
            empleado = self.usuario_repo.get(incapacidad["usuario_id"])
            if not empleado:
                return False

            # Obtener información del administrador
            admin = self.usuario_repo.get(admin_id)
            if not admin:
                return False

            # Preparar datos de la notificación
            notification_data = {
                "tipo": "incapacidad_revisada",
                "incapacidad_id": incapacidad_id,
                "empleado": {
                    "id": empleado.id_usuario,
                    "nombre": empleado.nombre_completo,
                    "email": empleado.correo_electronico
                },
                "administrador": {
                    "id": admin.id_usuario,
                    "nombre": admin.nombre_completo
                },
                "fecha_revision": datetime.now().isoformat()
            }

            # Enviar notificación al empleado
            return self._send_notification_to_employee(empleado, notification_data)

        except Exception as e:
            self.logger.error(f"Error al enviar notificación de revisión {incapacidad_id}: {str(e)}")
            return False

    def notify_incapacity_rejected(self, incapacidad_id: int, admin_id: int, motivo_rechazo: str = None) -> bool:
        """
        Notifica al empleado cuando su incapacidad ha sido rechazada.
        """
        try:
            # Obtener información de la incapacidad
            incapacidad = self.incapacidad_repo.get(incapacidad_id)
            if not incapacidad:
                self.logger.error(f"Incapacidad {incapacidad_id} no encontrada para notificación de rechazo")
                return False

            # Obtener información del empleado
            empleado = self.usuario_repo.get(incapacidad["usuario_id"])
            if not empleado:
                self.logger.error(f"Empleado {incapacidad['usuario_id']} no encontrado para notificación de rechazo")
                return False
            
            self.logger.info(f"📧 NOTIFICACIÓN DE RECHAZO - Datos del empleado:")
            self.logger.info(f"   👤 ID: {empleado.id_usuario}")
            self.logger.info(f"   📧 Email: {empleado.correo_electronico}")
            self.logger.info(f"   👤 Nombre: {empleado.nombre_completo}")

            # Obtener información del administrador
            admin = self.usuario_repo.get(admin_id)
            if not admin:
                self.logger.error(f"Administrador {admin_id} no encontrado para notificación de rechazo")
                return False

            # Preparar datos de la notificación
            notification_data = {
                "tipo": "incapacidad_rechazada",
                "incapacidad_id": incapacidad_id,
                "empleado": {
                    "id": empleado.id_usuario,
                    "nombre": empleado.nombre_completo,
                    "email": empleado.correo_electronico
                },
                "administrador": {
                    "id": admin.id_usuario,
                    "nombre": admin.nombre_completo
                },
                "motivo_rechazo": motivo_rechazo or "No especificado",
                "fecha_rechazo": datetime.now().isoformat(),
                "incapacidad": {
                    "tipo_id": incapacidad.get("tipo_incapacidad_id"),
                    "fecha_inicio": incapacidad["fecha_inicio"].isoformat() if incapacidad.get("fecha_inicio") else None,
                    "fecha_final": incapacidad["fecha_final"].isoformat() if incapacidad.get("fecha_final") else None,
                    "dias": incapacidad.get("dias", 0)
                }
            }

            # Enviar notificación al empleado
            success = self._send_notification_to_employee(empleado, notification_data)
            
            if success:
                self.logger.info(f"Notificación de rechazo enviada al empleado {empleado.correo_electronico} para incapacidad {incapacidad_id}")
            else:
                self.logger.error(f"Error al enviar notificación de rechazo al empleado {empleado.correo_electronico}")
            
            return success

        except Exception as e:
            self.logger.error(f"Error al enviar notificación de rechazo {incapacidad_id}: {str(e)}")
            return False

    def _get_administradores(self) -> List[dict]:
        """
        Obtiene lista de administradores activos.
        """
        try:
            # Obtener todos los usuarios con rol_id = 10 (administrador)
            usuarios = self.usuario_repo.list(skip=0, limit=1000)
            administradores = []
            
            for usuario in usuarios:
                if usuario.rol_id == 10 and usuario.estado:
                    administradores.append({
                        "id": usuario.id_usuario,
                        "nombre": usuario.nombre_completo,
                        "email": usuario.correo_electronico
                    })
            
            return administradores
            
        except Exception as e:
            self.logger.error(f"Error al obtener administradores: {str(e)}")
            return []

    def _send_notification_to_admin(self, admin: dict, notification_data: dict) -> bool:
        """
        Envía notificación a un administrador específico.
        """
        try:
            # Preparar correo para nueva incapacidad con el MISMO layout del correo de rechazo
            subject, html_content = self._create_admin_new_incapacity_email_content(notification_data)

            text_content = (
                f"Nueva incapacidad registrada por "
                f"{notification_data.get('empleado',{}).get('nombre','')} "
                f"({notification_data.get('empleado',{}).get('email','')}).\n"
                f"Fecha inicio: {self._format_date(notification_data.get('incapacidad',{}).get('fecha_inicio'))}\n"
                f"Fecha fin: {self._format_date(notification_data.get('incapacidad',{}).get('fecha_final'))}\n"
                f"Días: {notification_data.get('incapacidad',{}).get('dias','N/A')}\n"
            )

            # Enviar correo al administrador
            return self._send_email(
                to_email=admin.get('email'),
                subject=subject,
                html_content=html_content,
                text_content=text_content
            )
            
        except Exception as e:
            self.logger.error(f"Error al enviar notificación a admin {admin['email']}: {str(e)}")
            return False

    def _load_email_css(self, filename: str) -> str:
        """
        Carga estilos CSS para correos desde app/email_templates/styles/{filename}.
        Si el archivo no existe, retorna un conjunto mínimo de estilos por defecto.
        """
        try:
            base_dir = os.path.dirname(os.path.dirname(__file__))  # app/
            styles_path = os.path.join(base_dir, "email_templates", "styles", filename)
            if os.path.exists(styles_path):
                with open(styles_path, "r", encoding="utf-8") as f:
                    return f.read()
        except Exception as e:
            self.logger.warning(f"No se pudo cargar CSS de email ({filename}): {str(e)}")
        # Fallback mínimo para no romper el correo
        return (
            "body{margin:0;padding:0;background:#f4f6f8;color:#111827;"
            "font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,Arial,'Helvetica Neue',sans-serif}"
            ".wrapper{width:100%;background:#f4f6f8;padding:24px 0}"
            ".container{max-width:640px;margin:0 auto;background:#fff;border-radius:12px;overflow:hidden;"
            "box-shadow:0 1px 3px rgba(17,24,39,.08)}"
            ".header{background:linear-gradient(90deg,#1d4ed8,#2563eb);color:#fff;padding:20px 24px}"
            ".title{margin:0;font-size:20px;line-height:1.2;font-weight:700}"
            ".subtitle{margin:6px 0 0;font-size:14px;opacity:.9}"
            ".content{padding:20px 24px}"
            ".chip{display:inline-block;padding:4px 10px;border-radius:999px;background:#eff6ff;color:#1d4ed8;"
            "font-size:12px;font-weight:600;margin:6px 0 14px}"
            ".table{width:100%;border-collapse:separate;border-spacing:0;margin-top:8px}"
            ".cell-label{width:38%;background:#f9fafb;border-left:4px solid #2563eb;padding:10px 12px;font-weight:600;"
            "color:#374151;vertical-align:top}"
            ".cell-value{padding:10px 12px;color:#111827;border-bottom:1px solid #f3f4f6}"
            ".note{margin-top:16px;font-size:13px;color:#4b5563}"
            ".footer{padding:16px 24px;background:#f9fafb;color:#6b7280;font-size:12px;text-align:center}"
        )

    def _create_admin_new_incapacity_email_content(self, notification_data: dict) -> tuple[str, str]:
        """
        Genera el correo HTML para 'nueva incapacidad' usando el MISMO layout que el correo
        de rechazo (contenedor, header, info-box), con paleta azul.
        """
        empleado = notification_data.get('empleado', {})
        incapacidad = notification_data.get('incapacidad', {})
        subject = f"🆕 Nueva incapacidad - {empleado.get('nombre','Empleado')}"

        # CTA al panel (si está configurado)
        panel_url = os.getenv("ADMIN_PANEL_URL", "")
        primary = self._get_primary_color()
        cta_html = (
            f'<div style="text-align:center;margin-top:16px;"><a href="{panel_url}" '
            f'style="display:inline-block;background-color:{primary};color:#ffffff;'
            'padding:12px 18px;border-radius:8px;text-decoration:none;font-weight:600">'
            'Abrir panel administrativo</a></div>'
        ) if panel_url else ""

        # Estilos base del layout de rechazo pero con azul
        css_styles = (
            "body{font-family:Arial, sans-serif; line-height:1.6; color:#333;}"
            ".container{max-width:600px; margin:0 auto; padding:20px;}"
            f".header{{background-color:{primary}; color:white; padding:20px; text-align:center; border-radius:5px 5px 0 0;}}"
            ".content{background-color:#f8f9fa; padding:20px; border-radius:0 0 5px 5px;}"
            f".info-box{{background-color:white; padding:15px; margin:10px 0; border-left:4px solid {primary};}}"
            ".footer{text-align:center; margin-top:20px; color:#666; font-size:12px;}"
        )

        # Logo corporativo (opcional)
        logo_b64 = self._load_logo_base64()
        logo_html = (
            f'<div style="text-align:center;margin-bottom:8px;">'
            f'<img alt="UMIT" src="data:image/png;base64,{logo_b64}" '
            f'style="max-width:140px;height:auto;display:inline-block;filter:grayscale(100%);" />'
            f'</div>'
        ) if logo_b64 else ""

        # Formatear fechas sin hora
        fecha_inicio_fmt = self._format_date(incapacidad.get('fecha_inicio'))
        fecha_fin_fmt = self._format_date(incapacidad.get('fecha_final'))

        html_content = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <style>{css_styles}</style>
</head>
<body>
    <div class="container">
        <div class="header">
            {logo_html}
            <h1>🆕 Nueva Incapacidad</h1>
        </div>
        <div class="content">
            <p>Se ha creado una nueva incapacidad por el empleado <strong>{empleado.get('nombre','')}</strong> ({empleado.get('email','')}).</p>
            <div class="info-box">
                <h3>📅 Fechas</h3>
                <p><strong>Fecha de Inicio:</strong> {fecha_inicio_fmt}</p>
                <p><strong>Fecha de Fin:</strong> {fecha_fin_fmt}</p>
                <p><strong>Días:</strong> {incapacidad.get('dias','N/A')}</p>
            </div>
            {cta_html}
            <p>Por favor ingresa al panel administrativo para revisar y gestionar esta solicitud.</p>
        </div>
        <div class="footer">
            Este es un mensaje automático. Por favor no respondas a este correo.
        </div>
    </div>
</body>
</html>
"""
        return subject, html_content
    
    def _format_date(self, value) -> str:
        """
        Devuelve la fecha en formato AAAA-MM-DD, removiendo hora si viene en ISO o con 'T'.
        Acepta datetime/date o string. Si no hay valor, retorna 'N/A'.
        """
        try:
            if not value:
                return "N/A"
            # Si es datetime o date
            if hasattr(value, "isoformat"):
                # Para datetime con hora, tomar solo la parte de fecha
                iso = value.isoformat()
                return iso.split("T")[0].split(" ")[0]
            # Si es string
            if isinstance(value, str):
                # Separar por 'T' o por espacio
                return value.split("T")[0].split(" ")[0]
        except Exception:
            pass
        return str(value)

    def _get_primary_color(self) -> str:
        """
        Color fijo para los correos de 'nueva incapacidad'.
        Solicitado por el usuario: usar azul cielo/celeste.
        """
        
        return "#dc2626"

    def _load_logo_base64(self) -> Optional[str]:
        """
        Carga un logo PNG desde app/email_templates/assets o la ruta en EMAIL_LOGO_FILE.
        Devuelve el contenido en base64 para incrustarlo en el HTML del correo.
        """
        try:
            import base64
            base_dir = os.path.dirname(os.path.dirname(__file__))  # app/
            assets_dir = os.path.join(base_dir, "email_templates", "assets")
            candidates: List[str] = []
            env_path = os.getenv("EMAIL_LOGO_FILE")
            if env_path:
                candidates.append(env_path)
            candidates += ["@Logo negro UMIT.png", "logo_umit.png", "logo.png"]
            for name in candidates:
                path = name if os.path.isabs(name) else os.path.join(assets_dir, name)
                if os.path.exists(path):
                    with open(path, "rb") as f:
                        return base64.b64encode(f.read()).decode("ascii")
        except Exception as e:
            self.logger.warning(f"No se pudo cargar el logo: {str(e)}")
        return None

    def _send_notification_to_employee(self, empleado, notification_data: dict) -> bool:
        """
        Envía notificación a un empleado específico.
        """
        try:
            tipo_notificacion = notification_data.get("tipo", "general")
            
            if tipo_notificacion == "incapacidad_rechazada":
                # Notificación específica para rechazo
                motivo = notification_data.get("motivo_rechazo", "No especificado")
                incapacidad_id = notification_data.get("incapacidad_id")
                admin_nombre = notification_data.get("administrador", {}).get("nombre", "Administrador")
                
                self.logger.info(f"📧 ENVIANDO NOTIFICACIÓN DE RECHAZO:")
                self.logger.info(f"   📧 Para: {empleado.correo_electronico}")
                self.logger.info(f"   👤 Empleado: {empleado.nombre_completo}")
                self.logger.info(f"   🆔 Incapacidad ID: {incapacidad_id}")
                self.logger.info(f"   ❌ Motivo del rechazo: {motivo}")
                self.logger.info(f"   👨‍💼 Rechazado por: {admin_nombre}")
                self.logger.info(f"   📅 Fecha: {notification_data.get('fecha_rechazo', 'N/A')}")
                
                # Crear y enviar correo de rechazo
                asunto, html_content = self._create_rejection_email_content(notification_data)
                text_content = f"Incapacidad rechazada. Motivo: {motivo}"
                
                email_success = self._send_email(
                    to_email=empleado.correo_electronico,
                    subject=asunto,
                    html_content=html_content,
                    text_content=text_content
                )
                
                if email_success:
                    self.logger.info(f"✅ Correo de rechazo enviado exitosamente a {empleado.correo_electronico}")
                else:
                    self.logger.error(f"❌ Error al enviar correo de rechazo a {empleado.correo_electronico}")
                
                return email_success
                
            elif tipo_notificacion == "incapacidad_revisada":
                # Notificación específica para revisión
                incapacidad_id = notification_data.get("incapacidad_id")
                admin_nombre = notification_data.get("administrador", {}).get("nombre", "Administrador")
                
                self.logger.info(f"📧 NOTIFICACIÓN DE REVISIÓN ENVIADA:")
                self.logger.info(f"   📧 Para: {empleado.correo_electronico}")
                self.logger.info(f"   👤 Empleado: {empleado.nombre_completo}")
                self.logger.info(f"   🆔 Incapacidad ID: {incapacidad_id}")
                self.logger.info(f"   ✅ Revisado por: {admin_nombre}")
                self.logger.info(f"   📅 Fecha: {notification_data.get('fecha_revision', 'N/A')}")
                
            else:
                # Notificación general
                self.logger.info(f"📧 NOTIFICACIÓN GENERAL ENVIADA:")
                self.logger.info(f"   📧 Para: {empleado.correo_electronico}")
                self.logger.info(f"   👤 Empleado: {empleado.nombre_completo}")
                self.logger.info(f"   📋 Tipo: {tipo_notificacion}")
            
            self.logger.info(f"📊 Datos completos: {notification_data}")
            
            # Simular envío exitoso
            return True
            
        except Exception as e:
            self.logger.error(f"Error al enviar notificación a empleado {empleado.correo_electronico}: {str(e)}")
            return False

    def get_notification_history(self, user_id: int, *, skip: int = 0, limit: int = 100) -> List[dict]:
        """
        Obtiene historial de notificaciones para un usuario.
        En un entorno real, esto consultaría una tabla de notificaciones.
        """
        # Por ahora, retornamos una lista vacía
        # En el futuro, implementarías una tabla de notificaciones
        return []

    def mark_notification_as_read(self, notification_id: int, user_id: int) -> bool:
        """
        Marca una notificación como leída.
        """
        # Por ahora, siempre retorna True
        # En el futuro, actualizarías el estado en la BD
        return True

    def _send_email(self, to_email: str, subject: str, html_content: str, text_content: str = None) -> bool:
        """
        Envía un correo electrónico usando SMTP.
        Configura las variables de entorno para el servidor SMTP.
        """
        try:
            # Configuración SMTP desde variables de entorno
            smtp_server = os.getenv('SMTP_SERVER', 'smtp.gmail.com')
            smtp_port = int(os.getenv('SMTP_PORT', '587'))
            smtp_username = os.getenv('SMTP_USERNAME')
            smtp_password = os.getenv('SMTP_PASSWORD')
            from_email = os.getenv('FROM_EMAIL', smtp_username)
            
            # Si no hay configuración SMTP, solo loggear
            if not smtp_username or not smtp_password:
                self.logger.warning(f"⚠️ CONFIGURACIÓN SMTP NO ENCONTRADA")
                self.logger.warning(f"📧 Simulando envío a {to_email}")
                self.logger.info(f"📋 Asunto: {subject}")
                self.logger.info(f"📄 Contenido: {text_content or html_content}")
                self.logger.warning(f"🔧 Para habilitar envío real, configure las variables SMTP en .env")
                return True
            
            # Crear mensaje
            msg = MIMEMultipart('alternative')
            msg['Subject'] = subject
            msg['From'] = from_email
            msg['To'] = to_email
            
            # Agregar contenido de texto plano
            if text_content:
                text_part = MIMEText(text_content, 'plain', 'utf-8')
                msg.attach(text_part)
            
            # Agregar contenido HTML
            html_part = MIMEText(html_content, 'html', 'utf-8')
            msg.attach(html_part)
            
            # Enviar correo
            with smtplib.SMTP(smtp_server, smtp_port) as server:
                server.starttls()
                server.login(smtp_username, smtp_password)
                server.send_message(msg)
            
            self.logger.info(f"Correo enviado exitosamente a {to_email}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error al enviar correo a {to_email}: {str(e)}")
            return False

    def _create_rejection_email_content(self, notification_data: dict) -> tuple[str, str]:
        """
        Crea el contenido del correo para notificación de rechazo.
        Retorna (asunto, contenido_html)
        """
        empleado = notification_data.get('empleado', {})
        administrador = notification_data.get('administrador', {})
        incapacidad = notification_data.get('incapacidad', {})
        motivo_rechazo = notification_data.get('motivo_rechazo', 'No especificado')
        
        nombre_empleado = empleado.get('nombre', 'Estimado empleado')
        nombre_admin = administrador.get('nombre', 'Administrador')
        
        asunto = f"❌ Incapacidad Rechazada - {nombre_empleado}"
        
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .header {{ background-color: #dc3545; color: white; padding: 20px; text-align: center; border-radius: 5px 5px 0 0; }}
                .content {{ background-color: #f8f9fa; padding: 20px; border-radius: 0 0 5px 5px; }}
                .info-box {{ background-color: white; padding: 15px; margin: 10px 0; border-left: 4px solid #dc3545; }}
                .footer {{ text-align: center; margin-top: 20px; color: #666; font-size: 12px; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>❌ Incapacidad Rechazada</h1>
                </div>
                <div class="content">
                    <p>Estimado/a <strong>{nombre_empleado}</strong>,</p>
                    
                    <p>Lamentamos informarle que su incapacidad ha sido <strong>rechazada</strong> por el administrador.</p>
                    
                    <div class="info-box">
                        <h3>📋 Detalles de la Incapacidad</h3>
                        <p><strong>ID de Incapacidad:</strong> {notification_data.get('incapacidad_id', 'N/A')}</p>
                        <p><strong>Fecha de Inicio:</strong> {incapacidad.get('fecha_inicio', 'N/A')}</p>
                        <p><strong>Fecha de Fin:</strong> {incapacidad.get('fecha_final', 'N/A')}</p>
                        <p><strong>Días Solicitados:</strong> {incapacidad.get('dias', 'N/A')}</p>
                    </div>
                    
                    <div class="info-box">
                        <h3>❌ Motivo del Rechazo</h3>
                        <p><strong>{motivo_rechazo}</strong></p>
                    </div>
                    
                    <div class="info-box">
                        <h3>👨‍💼 Información del Administrador</h3>
                        <p><strong>Revisado por:</strong> {nombre_admin}</p>
                        <p><strong>Fecha de Rechazo:</strong> {notification_data.get('fecha_rechazo', 'N/A')}</p>
                    </div>
                    
                    <p>Si tiene alguna pregunta o desea más información sobre este rechazo, por favor contacte al departamento de recursos humanos.</p>
                    
                    <p>Atentamente,<br>
                    <strong>Equipo de Recursos Humanos</strong></p>
                </div>
                <div class="footer">
                    <p>Este es un mensaje automático. Por favor no responda a este correo.</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        text_content = f"""
        INCAPACIDAD RECHAZADA
        
        Estimado/a {nombre_empleado},
        
        Lamentamos informarle que su incapacidad ha sido RECHAZADA por el administrador.
        
        Detalles de la Incapacidad:
        - ID: {notification_data.get('incapacidad_id', 'N/A')}
        - Fecha de Inicio: {incapacidad.get('fecha_inicio', 'N/A')}
        - Fecha de Fin: {incapacidad.get('fecha_final', 'N/A')}
        - Días Solicitados: {incapacidad.get('dias', 'N/A')}
        
        Motivo del Rechazo:
        {motivo_rechazo}
        
        Información del Administrador:
        - Revisado por: {nombre_admin}
        - Fecha de Rechazo: {notification_data.get('fecha_rechazo', 'N/A')}
        
        Si tiene alguna pregunta, contacte al departamento de recursos humanos.
        
        Atentamente,
        Equipo de Recursos Humanos
        """
        
        return asunto, html_content
