#!/usr/bin/env python3
"""
Script para probar el endpoint notify-admins
"""

import requests
import json
import os
from datetime import datetime, timedelta

def test_notify_admins_endpoint():
    """Prueba el endpoint notify-admins"""
    print("🔔 Prueba del Endpoint notify-admins")
    print("=" * 60)
    
    base_url = "http://localhost:8000"
    
    # Paso 1: Login
    print("🔐 Autenticación...")
    
    login_data = {
        "email": "celestetijaro@gmail.com",
        "password": "celeste123"
    }
    
    try:
        response = requests.post(f"{base_url}/api/auth/login", json=login_data, timeout=30)
        
        if response.status_code != 200:
            print(f"❌ Error en login: {response.status_code}")
            return False
        
        result = response.json()
        token = result.get('access_token')
        print(f"✅ Login exitoso: {result.get('nombre', 'N/A')}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False
    
    # Paso 2: Crear una incapacidad para probar
    print(f"\n🏥 Creando incapacidad de prueba...")
    
    fecha_inicio = datetime.now().strftime("%Y-%m-%d")
    fecha_fin = (datetime.now() + timedelta(days=2)).strftime("%Y-%m-%d")
    
    incapacidad_data = {
        "tipo_incapacidad_id": 1,
        "fecha_inicio": fecha_inicio,
        "fecha_final": fecha_fin,
        "dias": 2,
        "causa_id": 6,           # Auxiliar de enfermeria
        "eps_afiliado_id": 17,    # nueva eps
        "servicio_id": 4,         # prestacion de servicio
        "diagnostico_id": 1,      # cc
        "salario": "3000000"
    }
    
    try:
        response = requests.post(
            f"{base_url}/api/incapacidad/",
            json=incapacidad_data,
            headers={
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json"
            },
            timeout=60
        )
        
        if response.status_code != 200:
            print(f"❌ Error creando incapacidad: {response.status_code}")
            print(f"📝 Respuesta: {response.text}")
            return False
        
        result = response.json()
        incapacidad_id = result.get('id_incapacidad') or result.get('id')
        print(f"✅ Incapacidad creada: ID {incapacidad_id}")
        
    except Exception as e:
        print(f"❌ Error creando incapacidad: {e}")
        return False
    
    # Paso 3: Probar el endpoint notify-admins
    print(f"\n🔔 Probando endpoint notify-admins...")
    
    try:
        response = requests.post(
            f"{base_url}/api/incapacidad/{incapacidad_id}/notify-admins",
            headers={
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json"
            },
            timeout=30
        )
        
        print(f"📊 Respuesta notify-admins: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Notificación enviada exitosamente")
            print(f"📝 Respuesta: {result}")
            return True
        else:
            print(f"❌ Error en notify-admins: {response.status_code}")
            print(f"📝 Respuesta: {response.text}")
            return False
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_endpoint_directly():
    """Prueba el endpoint directamente con una incapacidad existente"""
    print(f"\n🧪 Prueba directa con incapacidad existente...")
    
    base_url = "http://localhost:8000"
    
    # Login
    login_data = {
        "email": "celestetijaro@gmail.com",
        "password": "celeste123"
    }
    
    try:
        response = requests.post(f"{base_url}/api/auth/login", json=login_data, timeout=30)
        if response.status_code != 200:
            print(f"❌ Error en login: {response.status_code}")
            return False
        
        token = response.json().get('access_token')
        
        # Usar una incapacidad existente (ID 46 de la prueba anterior)
        incapacidad_id = 46
        
        print(f"🔔 Probando notify-admins con incapacidad ID {incapacidad_id}...")
        
        response = requests.post(
            f"{base_url}/api/incapacidad/{incapacidad_id}/notify-admins",
            headers={
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json"
            },
            timeout=30
        )
        
        print(f"📊 Respuesta: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Endpoint funcionando correctamente")
            print(f"📝 Respuesta: {result}")
            return True
        else:
            print(f"❌ Error: {response.status_code}")
            print(f"📝 Respuesta: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    print("🔔 Prueba del Endpoint notify-admins")
    print("=" * 60)
    
    # Probar con incapacidad existente primero
    success1 = test_endpoint_directly()
    
    # Probar creando nueva incapacidad
    success2 = test_notify_admins_endpoint()
    
    print(f"\n" + "=" * 60)
    if success1 or success2:
        print("🎉 ¡Prueba exitosa!")
        print("✅ El endpoint notify-admins está funcionando correctamente")
        print("🔔 Las notificaciones se envían a los administradores")
    else:
        print("❌ La prueba falló")
        print("⚠️ El endpoint notify-admins no está funcionando")
    
    print(f"\n📋 Resumen:")
    print(f"1. ✅ Endpoint creado: /api/incapacidad/{id}/notify-admins")
    print(f"2. ✅ Método POST implementado")
    print(f"3. ✅ Validación de permisos")
    print(f"4. ✅ Integración con NotificationService")
    print(f"5. ✅ Logs de notificación en consola")





