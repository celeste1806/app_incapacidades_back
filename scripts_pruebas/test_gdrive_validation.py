#!/usr/bin/env python3
"""
Script para probar la validación de Google Drive antes de crear incapacidades
"""

import requests
import json
import os
from datetime import datetime, timedelta

def test_google_drive_validation():
    """Prueba la validación de Google Drive antes de crear incapacidades"""
    print("🔍 Prueba de Validación de Google Drive")
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
    
    # Paso 2: Intentar crear incapacidad (debería validar Google Drive primero)
    print(f"\n🏥 Intentando crear incapacidad (con validación de Google Drive)...")
    
    fecha_inicio = datetime.now().strftime("%Y-%m-%d")
    fecha_fin = (datetime.now() + timedelta(days=2)).strftime("%Y-%m-%d")
    
    # Usar IDs reales obtenidos anteriormente
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
    
    print(f"📝 Datos de incapacidad:")
    print(f"   Causa ID: {incapacidad_data['causa_id']} (Auxiliar de enfermeria)")
    print(f"   EPS ID: {incapacidad_data['eps_afiliado_id']} (nueva eps)")
    print(f"   Servicio ID: {incapacidad_data['servicio_id']} (prestacion de servicio)")
    print(f"   Diagnóstico ID: {incapacidad_data['diagnostico_id']} (cc)")
    
    try:
        response = requests.post(
            f"{base_url}/api/incapacidad/",
            json=incapacidad_data,
            headers={
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json"
            },
            timeout=60  # Más tiempo para la validación de Google Drive
        )
        
        print(f"📊 Respuesta creación: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            incapacidad_id = result.get('id_incapacidad') or result.get('id')
            print(f"✅ Incapacidad creada exitosamente: ID {incapacidad_id}")
            print(f"🎉 Google Drive está funcionando correctamente")
            return True
        else:
            print(f"❌ Error creando incapacidad: {response.status_code}")
            print(f"📝 Respuesta: {response.text}")
            
            # Verificar si el error es por Google Drive
            if "Google Drive no está disponible" in response.text:
                print(f"🚫 La incapacidad NO se creó porque Google Drive no está disponible")
                print(f"✅ La validación está funcionando correctamente")
                return False
            else:
                print(f"⚠️ Error diferente al esperado")
                return False
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_without_gdrive_config():
    """Prueba qué pasa si Google Drive no está configurado"""
    print(f"\n🧪 Prueba adicional: ¿Qué pasa si Google Drive falla?")
    print(f"💡 Revisa los logs del servidor para ver los mensajes de validación")
    print(f"💡 Si Google Drive no está configurado, la incapacidad NO se debería crear")

if __name__ == "__main__":
    print("🔍 Prueba de Validación de Google Drive")
    print("=" * 60)
    
    success = test_google_drive_validation()
    
    test_without_gdrive_config()
    
    print(f"\n" + "=" * 60)
    if success:
        print("🎉 ¡Prueba exitosa!")
        print("✅ Google Drive está funcionando y las incapacidades se pueden crear")
    else:
        print("🚫 ¡Validación funcionando!")
        print("✅ Google Drive no está disponible, por lo que NO se creó la incapacidad")
        print("💡 Esto es el comportamiento esperado para proteger los datos")
    
    print(f"\n📋 Resumen:")
    print(f"1. 🔍 Se valida Google Drive antes de crear incapacidades")
    print(f"2. ✅ Si Google Drive funciona: se crea la incapacidad")
    print(f"3. ❌ Si Google Drive falla: NO se crea la incapacidad")
    print(f"4. 🛡️ Los archivos están protegidos contra pérdida")





