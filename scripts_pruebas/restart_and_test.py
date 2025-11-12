#!/usr/bin/env python3
"""
Script para reiniciar el servidor y probar la funcionalidad de reset
"""

import subprocess
import time
import requests
import sys
import os

def restart_server():
    """Reinicia el servidor"""
    print("🔄 Reiniciando servidor...")
    
    try:
        # Detener procesos en puerto 8000
        subprocess.run(["taskkill", "/F", "/IM", "python.exe"], capture_output=True)
        time.sleep(2)
        
        # Iniciar servidor en background
        print("🚀 Iniciando servidor...")
        process = subprocess.Popen([
            sys.executable, "run_server.py"
        ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        
        # Esperar a que el servidor esté listo
        print("⏳ Esperando a que el servidor esté listo...")
        for i in range(30):  # Esperar máximo 30 segundos
            try:
                response = requests.get("http://localhost:8000/health", timeout=1)
                if response.status_code == 200:
                    print("✅ Servidor iniciado correctamente")
                    return True
            except:
                pass
            time.sleep(1)
            print(f"   Esperando... ({i+1}/30)")
        
        print("❌ El servidor no respondió en 30 segundos")
        return False
        
    except Exception as e:
        print(f"❌ Error reiniciando servidor: {e}")
        return False

def test_password_reset():
    """Prueba la funcionalidad de reset de contraseña"""
    print("\n🔐 Probando funcionalidad de reset de contraseña...")
    
    base_url = "http://localhost:8000"
    test_email = "celestetijaro@gmail.com"
    
    try:
        response = requests.post(
            f"{base_url}/api/auth/forgot-password",
            json={"email": test_email},
            timeout=30
        )
        
        print(f"📊 Respuesta: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Solicitud exitosa: {result.get('message', 'Sin mensaje')}")
            print("📧 Revisa el correo para obtener el nuevo enlace")
            print("🔗 El enlace ahora debería apuntar a: http://localhost:8000/api/auth/reset-password-page?token=TU_TOKEN")
            return True
        else:
            print(f"❌ Error: {response.status_code}")
            print(f"📝 Respuesta: {response.text}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Error de conexión: {e}")
        return False

if __name__ == "__main__":
    print("🔄 Reinicio y Prueba del Servidor")
    print("=" * 50)
    
    # Reiniciar servidor
    if restart_server():
        # Probar funcionalidad
        test_password_reset()
        
        print("\n" + "=" * 50)
        print("🎉 ¡Proceso completado!")
        print("📧 Revisa el correo para el nuevo enlace")
        print("🔗 El enlace debería funcionar ahora")
    else:
        print("\n❌ Error en el proceso")
        print("💡 Intenta reiniciar el servidor manualmente")
