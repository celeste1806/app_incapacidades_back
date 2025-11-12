#!/usr/bin/env python3
"""
Script para diagnosticar problemas con el envío de correos de reset de contraseña
"""

import sys
import os
from dotenv import load_dotenv

# Agregar el directorio del proyecto al path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.db.session import get_db
from app.services.password_reset_service import PasswordResetService
from app.repositories.usuario_repository import UsuarioRepository

def test_password_reset_email():
    """Prueba el envío de correo de reset de contraseña"""
    print("🔍 Diagnóstico de Reset de Contraseña")
    print("=" * 50)
    
    # Cargar configuración
    load_dotenv()
    
    # Verificar configuración SMTP
    smtp_server = os.getenv('SMTP_SERVER', '')
    smtp_username = os.getenv('SMTP_USERNAME', '')
    smtp_password = os.getenv('SMTP_PASSWORD', '')
    
    print(f"📧 Configuración SMTP:")
    print(f"   Servidor: {smtp_server}")
    print(f"   Usuario: {smtp_username}")
    print(f"   Contraseña: {'✅ Configurada' if smtp_password else '❌ No configurada'}")
    
    if not smtp_username or not smtp_password:
        print("\n❌ PROBLEMA: Configuración SMTP incompleta")
        print("💡 Solución: Configura las variables SMTP_USERNAME y SMTP_PASSWORD en tu .env")
        return False
    
    # Verificar usuario
    test_email = "celestetijaro@gmail.com"
    print(f"\n👤 Verificando usuario: {test_email}")
    
    try:
        db = next(get_db())
        usuario_repo = UsuarioRepository(db)
        usuario = usuario_repo.get_by_email(test_email)
        
        if not usuario:
            print(f"❌ PROBLEMA: Usuario no encontrado")
            print("💡 Solución: Verifica que el email existe en la base de datos")
            return False
        
        print(f"✅ Usuario encontrado: {usuario.nombre_completo}")
        print(f"   ID: {usuario.id_usuario}")
        print(f"   Estado: {'Activo' if usuario.estado else 'Inactivo'}")
        
        if not usuario.estado:
            print(f"❌ PROBLEMA: Usuario inactivo")
            print("💡 Solución: Activa el usuario en la base de datos")
            return False
        
        # Probar servicio de reset
        print(f"\n🔧 Probando servicio de reset...")
        password_reset_service = PasswordResetService(db)
        
        # Intentar enviar correo
        print(f"📤 Enviando correo de reset...")
        success = password_reset_service.request_password_reset(test_email)
        
        if success:
            print(f"✅ Servicio de reset ejecutado correctamente")
            print(f"📧 Revisa el correo en {test_email}")
            print(f"📧 También revisa la carpeta de spam")
            print(f"🔗 El enlace debería apuntar a: http://localhost:8000/api/auth/reset-password-page?token=TU_TOKEN")
        else:
            print(f"❌ Error en el servicio de reset")
        
        return success
        
    except Exception as e:
        print(f"❌ Error durante la prueba: {str(e)}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        if 'db' in locals():
            db.close()

def check_recent_logs():
    """Verifica los logs recientes del servidor"""
    print(f"\n📋 Verificando logs del servidor...")
    print(f"💡 Revisa la terminal donde está corriendo el servidor backend")
    print(f"💡 Busca mensajes que contengan:")
    print(f"   - '📧 ENVIANDO NOTIFICACIÓN'")
    print(f"   - '✅ Correo enviado exitosamente'")
    print(f"   - '❌ Error al enviar correo'")
    print(f"   - '⚠️ CONFIGURACIÓN SMTP NO ENCONTRADA'")

if __name__ == "__main__":
    print("🔍 Diagnóstico de Problemas con Correos de Reset")
    print("=" * 60)
    
    success = test_password_reset_email()
    
    check_recent_logs()
    
    print("\n" + "=" * 60)
    if success:
        print("🎉 ¡Diagnóstico completado!")
        print("📧 Si el correo no llega, revisa:")
        print("   1. Carpeta de spam")
        print("   2. Logs del servidor")
        print("   3. Configuración SMTP")
    else:
        print("❌ Se encontraron problemas")
        print("📝 Revisa los errores anteriores")
    
    print("\n💡 Soluciones comunes:")
    print("1. 🔄 Reinicia el servidor backend")
    print("2. 📧 Verifica la configuración SMTP")
    print("3. 📁 Revisa la carpeta de spam")
    print("4. 🔍 Revisa los logs del servidor")





