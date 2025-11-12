#!/usr/bin/env python3
"""
Script de prueba para verificar el envío de correos automáticos
"""

import os
import sys
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime

def cargar_configuracion():
    """Carga la configuración desde el archivo .env"""
    config = {}
    
    if not os.path.exists('.env'):
        print("❌ No se encontró archivo .env")
        print("Ejecute primero: python configurar_correos.py")
        return None
    
    try:
        with open('.env', 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    config[key] = value
        
        return config
    except Exception as e:
        print(f"❌ Error al leer configuración: {e}")
        return None

def probar_conexion_smtp(config):
    """Prueba la conexión SMTP"""
    print("🔌 Probando conexión SMTP...")
    
    try:
        server = smtplib.SMTP(config['SMTP_SERVER'], int(config['SMTP_PORT']))
        server.starttls()
        server.login(config['SMTP_USERNAME'], config['SMTP_PASSWORD'])
        server.quit()
        
        print("✅ Conexión SMTP exitosa!")
        return True
        
    except Exception as e:
        print(f"❌ Error de conexión SMTP: {e}")
        return False

def enviar_correo_prueba(config, email_destino):
    """Envía un correo de prueba"""
    print(f"📧 Enviando correo de prueba a {email_destino}...")
    
    try:
        # Crear mensaje
        msg = MIMEMultipart('alternative')
        msg['Subject'] = f"🧪 Prueba de Notificaciones - {datetime.now().strftime('%Y-%m-%d %H:%M')}"
        msg['From'] = config['FROM_EMAIL']
        msg['To'] = email_destino
        
        # Contenido de texto plano
        text_content = f"""
PRUEBA DE NOTIFICACIONES AUTOMÁTICAS

Estimado/a usuario,

Este es un correo de prueba para verificar que el sistema de notificaciones por correo está funcionando correctamente.

Detalles de la prueba:
- Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
- Servidor SMTP: {config['SMTP_SERVER']}:{config['SMTP_PORT']}
- Email origen: {config['FROM_EMAIL']}

Si recibió este correo, el sistema está configurado correctamente.

Atentamente,
Sistema de Incapacidades
"""
        
        # Contenido HTML
        html_content = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <style>
        body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
        .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
        .header {{ background-color: #28a745; color: white; padding: 20px; text-align: center; border-radius: 5px 5px 0 0; }}
        .content {{ background-color: #f8f9fa; padding: 20px; border-radius: 0 0 5px 5px; }}
        .info-box {{ background-color: white; padding: 15px; margin: 10px 0; border-left: 4px solid #28a745; }}
        .footer {{ text-align: center; margin-top: 20px; color: #666; font-size: 12px; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🧪 Prueba de Notificaciones</h1>
        </div>
        <div class="content">
            <p>Estimado/a usuario,</p>
            
            <p>Este es un <strong>correo de prueba</strong> para verificar que el sistema de notificaciones por correo está funcionando correctamente.</p>
            
            <div class="info-box">
                <h3>📋 Detalles de la Prueba</h3>
                <p><strong>Fecha:</strong> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
                <p><strong>Servidor SMTP:</strong> {config['SMTP_SERVER']}:{config['SMTP_PORT']}</p>
                <p><strong>Email origen:</strong> {config['FROM_EMAIL']}</p>
            </div>
            
            <p>Si recibió este correo, el sistema está <strong>configurado correctamente</strong> y podrá enviar notificaciones automáticas cuando se rechacen incapacidades.</p>
            
            <p>Atentamente,<br>
            <strong>Sistema de Incapacidades</strong></p>
        </div>
        <div class="footer">
            <p>Este es un mensaje de prueba automático.</p>
        </div>
    </div>
</body>
</html>
"""
        
        # Agregar contenido al mensaje
        text_part = MIMEText(text_content, 'plain', 'utf-8')
        html_part = MIMEText(html_content, 'html', 'utf-8')
        
        msg.attach(text_part)
        msg.attach(html_part)
        
        # Enviar correo
        server = smtplib.SMTP(config['SMTP_SERVER'], int(config['SMTP_PORT']))
        server.starttls()
        server.login(config['SMTP_USERNAME'], config['SMTP_PASSWORD'])
        server.send_message(msg)
        server.quit()
        
        print("✅ Correo de prueba enviado exitosamente!")
        return True
        
    except Exception as e:
        print(f"❌ Error al enviar correo: {e}")
        return False

def main():
    """Función principal"""
    print("🧪 PRUEBA DEL SISTEMA DE NOTIFICACIONES POR CORREO")
    print("=" * 60)
    
    # Cargar configuración
    config = cargar_configuracion()
    if not config:
        return
    
    # Verificar configuración requerida
    required_keys = ['SMTP_SERVER', 'SMTP_PORT', 'SMTP_USERNAME', 'SMTP_PASSWORD', 'FROM_EMAIL']
    missing_keys = [key for key in required_keys if not config.get(key)]
    
    if missing_keys:
        print(f"❌ Configuración incompleta. Faltan: {', '.join(missing_keys)}")
        print("Ejecute: python configurar_correos.py")
        return
    
    print("✅ Configuración encontrada")
    print(f"📧 Servidor: {config['SMTP_SERVER']}:{config['SMTP_PORT']}")
    print(f"📧 Email origen: {config['FROM_EMAIL']}")
    
    # Probar conexión SMTP
    if not probar_conexion_smtp(config):
        return
    
    # Solicitar email de destino
    print("\n📧 CORREO DE PRUEBA")
    email_destino = input("Ingrese el email donde enviar la prueba: ").strip()
    
    if not email_destino:
        print("❌ Email de destino requerido")
        return
    
    # Enviar correo de prueba
    if enviar_correo_prueba(config, email_destino):
        print("\n🎉 PRUEBA COMPLETADA EXITOSAMENTE!")
        print("El sistema está listo para enviar notificaciones automáticas.")
        print("\n📋 PRÓXIMOS PASOS:")
        print("1. Reinicie el servidor backend")
        print("2. Rechace una incapacidad desde el panel de administración")
        print("3. Verifique que el empleado reciba el correo de notificación")
    else:
        print("\n❌ La prueba falló. Revise la configuración SMTP.")

if __name__ == "__main__":
    main()
