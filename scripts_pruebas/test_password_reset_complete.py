#!/usr/bin/env python3
"""
Script para probar la funcionalidad completa de reset de contraseña
"""

import requests
import json
import time
from datetime import datetime

def test_complete_password_reset():
    """Prueba el flujo completo de reset de contraseña"""
    print("🔐 Prueba Completa de Reset de Contraseña")
    print("=" * 60)
    
    base_url = "http://localhost:8000"
    
    # Paso 1: Solicitar reset de contraseña
    print("📧 Paso 1: Solicitar reset de contraseña...")
    
    test_email = "celestetijaro@gmail.com"  # Cambiar por un email válido en tu sistema
    
    forgot_password_data = {
        "email": test_email
    }
    
    try:
        response = requests.post(
            f"{base_url}/api/auth/forgot-password",
            json=forgot_password_data,
            timeout=30
        )
        
        print(f"📊 Respuesta: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Solicitud exitosa: {result.get('message', 'Sin mensaje')}")
            print("📧 Revisa el correo para obtener el enlace de reset")
            print("🔗 El enlace ahora apunta a: http://localhost:8000/api/auth/reset-password-page?token=TU_TOKEN")
        else:
            print(f"❌ Error: {response.status_code}")
            print(f"📝 Respuesta: {response.text}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Error de conexión: {e}")
        return False
    
    print("\n" + "=" * 60)
    print("🎉 ¡Solicitud de reset enviada!")
    print("\n💡 Próximos pasos:")
    print("1. 📧 Revisa tu correo (incluyendo spam)")
    print("2. 🔗 Haz clic en el enlace del correo")
    print("3. 📝 Ingresa tu nueva contraseña")
    print("4. ✅ Confirma el cambio")
    
    print(f"\n🔧 Si el enlace no funciona, puedes:")
    print(f"1. Copiar el token del enlace")
    print(f"2. Ir directamente a: http://localhost:8000/api/auth/reset-password-page?token=TU_TOKEN")
    
    return True

def test_reset_with_token(token: str):
    """Prueba el reset de contraseña con un token específico"""
    print("🔑 Probando reset de contraseña con token...")
    
    base_url = "http://localhost:8000"
    new_password = "nueva_contraseña_123"
    
    reset_data = {
        "token": token,
        "new_password": new_password
    }
    
    try:
        response = requests.post(
            f"{base_url}/api/auth/reset-password",
            json=reset_data,
            timeout=30
        )
        
        print(f"📊 Respuesta: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Reset exitoso: {result.get('message', 'Sin mensaje')}")
            print(f"🔑 Nueva contraseña: {new_password}")
            print("📧 Revisa el correo para confirmación")
            return True
        else:
            print(f"❌ Error: {response.status_code}")
            print(f"📝 Respuesta: {response.text}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Error de conexión: {e}")
        return False

def test_login_with_new_password():
    """Prueba el login con la nueva contraseña"""
    print("🔐 Probando login con nueva contraseña...")
    
    base_url = "http://localhost:8000"
    
    login_data = {
        "email": "celestetijaro@gmail.com",  # Cambiar por el email usado
        "password": "nueva_contraseña_123"
    }
    
    try:
        response = requests.post(
            f"{base_url}/api/auth/login",
            json=login_data,
            timeout=30
        )
        
        print(f"📊 Respuesta: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Login exitoso con nueva contraseña")
            print(f"👤 Usuario: {result.get('nombre', 'N/A')}")
            print(f"📧 Email: {result.get('correo_electronico', 'N/A')}")
            return True
        else:
            print(f"❌ Error en login: {response.status_code}")
            print(f"📝 Respuesta: {response.text}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Error de conexión: {e}")
        return False

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "--token":
        if len(sys.argv) < 3:
            print("❌ Uso: python test_password_reset_complete.py --token TU_TOKEN_AQUI")
            sys.exit(1)
        
        token = sys.argv[2]
        print("🔐 Prueba de Reset de Contraseña con Token")
        print("=" * 60)
        
        success = test_reset_with_token(token)
        
        if success:
            print("\n🎉 ¡Reset exitoso!")
            print("💡 Ahora puedes probar el login con la nueva contraseña")
            
            # Preguntar si quiere probar el login
            try:
                test_login = input("\n¿Quieres probar el login con la nueva contraseña? (s/n): ")
                if test_login.lower() in ['s', 'si', 'sí', 'y', 'yes']:
                    test_login_with_new_password()
            except KeyboardInterrupt:
                print("\n👋 Prueba cancelada")
        else:
            print("\n❌ Reset falló")
            print("💡 Verifica que el token sea válido y no haya expirado")
    
    else:
        # Prueba normal (solo solicitar reset)
        success = test_complete_password_reset()
        
        print("\n" + "=" * 60)
        if success:
            print("🎉 ¡Prueba de solicitud exitosa!")
            print("📧 Revisa el correo para continuar con el proceso")
        else:
            print("❌ La prueba falló")
            print("📝 Revisa los errores anteriores")
        
        print("\n💡 Instrucciones:")
        print("1. 📧 Revisa el correo en tu bandeja de entrada (y spam)")
        print("2. 🔗 Haz clic en el enlace del correo")
        print("3. 📝 Ingresa tu nueva contraseña en la página que se abre")
        print("4. ✅ Confirma el cambio")
        print("5. 🔐 Prueba hacer login con la nueva contraseña")





