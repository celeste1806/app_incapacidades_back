#!/usr/bin/env python3
"""
Script de prueba para la funcionalidad de reset de contraseña
"""

import requests
import json
import time
from datetime import datetime

def test_password_reset_flow():
    """Prueba el flujo completo de reset de contraseña"""
    print("🔐 Prueba de Reset de Contraseña")
    print("=" * 50)
    
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
            print("📧 Revisa los logs del servidor para ver si se envió el correo")
            print("📧 También revisa tu carpeta de spam si no ves el correo")
        else:
            print(f"❌ Error: {response.status_code}")
            print(f"📝 Respuesta: {response.text}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Error de conexión: {e}")
        return False
    
    # Paso 2: Simular uso del token (necesitarías el token real del correo)
    print("\n🔑 Paso 2: Reset de contraseña con token...")
    print("⚠️  Para probar este paso, necesitas:")
    print("   1. Revisar el correo enviado")
    print("   2. Copiar el token del enlace")
    print("   3. Usar ese token en el siguiente paso")
    
    # Token de ejemplo (no funcionará, es solo para mostrar el formato)
    example_token = "ejemplo_token_aqui"
    new_password = "nueva_contraseña_123"
    
    reset_data = {
        "token": example_token,
        "new_password": new_password
    }
    
    print(f"\n📋 Ejemplo de datos para reset:")
    print(f"   Token: {example_token}")
    print(f"   Nueva contraseña: {new_password}")
    
    print(f"\n💡 Para probar el reset completo:")
    print(f"   1. Ejecuta este script")
    print(f"   2. Revisa el correo en {test_email}")
    print(f"   3. Copia el token del enlace")
    print(f"   4. Ejecuta: python test_password_reset.py --token TU_TOKEN_AQUI")
    
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
            print("❌ Uso: python test_password_reset.py --token TU_TOKEN_AQUI")
            sys.exit(1)
        
        token = sys.argv[2]
        print("🔐 Prueba de Reset de Contraseña con Token")
        print("=" * 50)
        
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
        success = test_password_reset_flow()
        
        print("\n" + "=" * 50)
        if success:
            print("🎉 ¡Prueba de solicitud exitosa!")
            print("📧 Revisa el correo para continuar con el proceso")
        else:
            print("❌ La prueba falló")
            print("📝 Revisa los errores anteriores")
        
        print("\n💡 Próximos pasos:")
        print("1. Revisa el correo en tu bandeja de entrada (y spam)")
        print("2. Copia el token del enlace")
        print("3. Ejecuta: python test_password_reset.py --token TU_TOKEN_AQUI")
