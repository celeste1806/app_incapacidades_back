#!/usr/bin/env python3
"""
Script de configuración para el sistema de notificaciones por correo
"""

import os
import sys
from pathlib import Path

def crear_archivo_env():
    """Crea el archivo .env con la configuración SMTP"""
    
    print("🔧 CONFIGURACIÓN DEL SISTEMA DE NOTIFICACIONES POR CORREO")
    print("=" * 60)
    
    # Verificar si ya existe .env
    env_path = Path(".env")
    if env_path.exists():
        respuesta = input("⚠️  El archivo .env ya existe. ¿Desea sobrescribirlo? (s/n): ")
        if respuesta.lower() != 's':
            print("❌ Configuración cancelada.")
            return
    
    print("\n📧 CONFIGURACIÓN SMTP")
    print("Seleccione su proveedor de correo:")
    print("1. Gmail (Recomendado)")
    print("2. Outlook/Hotmail")
    print("3. Yahoo")
    print("4. Servidor SMTP personalizado")
    
    opcion = input("\nIngrese su opción (1-4): ").strip()
    
    configuraciones = {
        "1": {
            "server": "smtp.gmail.com",
            "port": "587",
            "descripcion": "Gmail"
        },
        "2": {
            "server": "smtp-mail.outlook.com", 
            "port": "587",
            "descripcion": "Outlook/Hotmail"
        },
        "3": {
            "server": "smtp.mail.yahoo.com",
            "port": "587", 
            "descripcion": "Yahoo"
        },
        "4": {
            "server": "",
            "port": "587",
            "descripcion": "Personalizado"
        }
    }
    
    if opcion not in configuraciones:
        print("❌ Opción inválida.")
        return
    
    config = configuraciones[opcion]
    
    if opcion == "4":
        config["server"] = input("Ingrese el servidor SMTP: ").strip()
        config["port"] = input("Ingrese el puerto SMTP (por defecto 587): ").strip() or "587"
    
    # Solicitar credenciales
    print(f"\n📝 CONFIGURACIÓN PARA {config['descripcion'].upper()}")
    email = input("Ingrese su dirección de correo: ").strip()
    
    if opcion == "1":  # Gmail
        print("\n🔐 IMPORTANTE PARA GMAIL:")
        print("1. Debe tener autenticación de 2 factores habilitada")
        print("2. Debe generar una 'Contraseña de aplicación'")
        print("3. Vaya a: Configuración de Google → Seguridad → Contraseñas de aplicaciones")
        print("4. Genere una nueva contraseña para 'Correo'")
        print("5. Use esa contraseña aquí (NO su contraseña normal)")
        
    password = input("Ingrese su contraseña o contraseña de aplicación: ").strip()
    
    # Crear contenido del archivo .env
    env_content = f"""# Configuración de Base de Datos
DATABASE_URL=sqlite:///./incapacidades.db

# Configuración SMTP para envío de correos automáticos
SMTP_SERVER={config['server']}
SMTP_PORT={config['port']}
SMTP_USERNAME={email}
SMTP_PASSWORD={password}
FROM_EMAIL={email}

# Configuración de seguridad
SECRET_KEY=tu_clave_secreta_muy_larga_y_segura_aqui_cambiar_en_produccion
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Configuración de logging
LOG_LEVEL=INFO
"""
    
    # Escribir archivo .env
    try:
        with open(".env", "w", encoding="utf-8") as f:
            f.write(env_content)
        
        print(f"\n✅ Archivo .env creado exitosamente!")
        print(f"📧 Servidor SMTP: {config['server']}:{config['port']}")
        print(f"📧 Email: {email}")
        
        print("\n🚀 PRÓXIMOS PASOS:")
        print("1. Reinicie el servidor backend")
        print("2. Pruebe rechazar una incapacidad desde el panel de administración")
        print("3. Verifique que el correo llegue al empleado")
        
        print("\n📋 LOGS:")
        print("Revise los logs del servidor para ver el estado del envío de correos")
        
    except Exception as e:
        print(f"❌ Error al crear archivo .env: {e}")

def verificar_configuracion():
    """Verifica la configuración actual"""
    print("\n🔍 VERIFICANDO CONFIGURACIÓN ACTUAL")
    print("=" * 40)
    
    env_path = Path(".env")
    if not env_path.exists():
        print("❌ No se encontró archivo .env")
        return
    
    try:
        with open(".env", "r", encoding="utf-8") as f:
            content = f.read()
        
        # Extraer configuración SMTP
        smtp_server = None
        smtp_port = None
        smtp_username = None
        smtp_password = None
        from_email = None
        
        for line in content.split('\n'):
            if line.startswith('SMTP_SERVER='):
                smtp_server = line.split('=', 1)[1]
            elif line.startswith('SMTP_PORT='):
                smtp_port = line.split('=', 1)[1]
            elif line.startswith('SMTP_USERNAME='):
                smtp_username = line.split('=', 1)[1]
            elif line.startswith('SMTP_PASSWORD='):
                smtp_password = line.split('=', 1)[1]
            elif line.startswith('FROM_EMAIL='):
                from_email = line.split('=', 1)[1]
        
        print(f"📧 Servidor SMTP: {smtp_server or 'No configurado'}")
        print(f"📧 Puerto: {smtp_port or 'No configurado'}")
        print(f"📧 Usuario: {smtp_username or 'No configurado'}")
        print(f"📧 Contraseña: {'***' if smtp_password else 'No configurada'}")
        print(f"📧 Email origen: {from_email or 'No configurado'}")
        
        if all([smtp_server, smtp_port, smtp_username, smtp_password, from_email]):
            print("\n✅ Configuración SMTP completa")
        else:
            print("\n⚠️  Configuración SMTP incompleta")
            
    except Exception as e:
        print(f"❌ Error al leer configuración: {e}")

def main():
    """Función principal"""
    print("🔧 CONFIGURADOR DE NOTIFICACIONES POR CORREO")
    print("=" * 50)
    
    while True:
        print("\nOpciones disponibles:")
        print("1. Crear/Actualizar configuración SMTP")
        print("2. Verificar configuración actual")
        print("3. Salir")
        
        opcion = input("\nSeleccione una opción (1-3): ").strip()
        
        if opcion == "1":
            crear_archivo_env()
        elif opcion == "2":
            verificar_configuracion()
        elif opcion == "3":
            print("👋 ¡Hasta luego!")
            break
        else:
            print("❌ Opción inválida. Intente nuevamente.")

if __name__ == "__main__":
    main()
