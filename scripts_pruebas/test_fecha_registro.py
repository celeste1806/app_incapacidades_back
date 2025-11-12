#!/usr/bin/env python3
"""
Script para probar que la fecha_registro se guarda correctamente
"""

import requests
import json
import os
from datetime import datetime, timedelta

def test_fecha_registro():
    """Prueba que la fecha_registro se guarda correctamente"""
    print("📅 Prueba de Fecha de Registro")
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
    
    # Paso 2: Crear una incapacidad y verificar fecha_registro
    print(f"\n🏥 Creando incapacidad para probar fecha_registro...")
    
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
        print(f"📝 Creando incapacidad con datos:")
        print(f"   Fecha inicio: {fecha_inicio}")
        print(f"   Fecha fin: {fecha_fin}")
        print(f"   Días: {incapacidad_data['dias']}")
        
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
        fecha_registro = result.get('fecha_registro')
        
        print(f"✅ Incapacidad creada: ID {incapacidad_id}")
        print(f"📅 Fecha de registro: {fecha_registro}")
        
        # Verificar que la fecha_registro no sea 0000-00-00
        if fecha_registro and fecha_registro != "0000-00-00 00:00:00":
            print(f"✅ ¡Fecha de registro guardada correctamente!")
            print(f"📅 Fecha: {fecha_registro}")
            return True
        else:
            print(f"❌ Error: Fecha de registro no se guardó correctamente")
            print(f"📅 Valor recibido: {fecha_registro}")
            return False
        
    except Exception as e:
        print(f"❌ Error creando incapacidad: {e}")
        return False

def test_existing_incapacidad():
    """Prueba una incapacidad existente para ver su fecha_registro"""
    print(f"\n🔍 Verificando incapacidad existente...")
    
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
        
        # Obtener incapacidad existente (ID 46)
        incapacidad_id = 46
        
        print(f"🔍 Obteniendo incapacidad ID {incapacidad_id}...")
        
        response = requests.get(
            f"{base_url}/api/incapacidad/{incapacidad_id}",
            headers={
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json"
            },
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            fecha_registro = result.get('fecha_registro')
            
            print(f"📅 Fecha de registro actual: {fecha_registro}")
            
            if fecha_registro and fecha_registro != "0000-00-00 00:00:00":
                print(f"✅ Fecha de registro válida")
                return True
            else:
                print(f"❌ Fecha de registro inválida (0000-00-00)")
                return False
        else:
            print(f"❌ Error obteniendo incapacidad: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    print("📅 Prueba de Fecha de Registro")
    print("=" * 60)
    
    # Probar incapacidad existente
    success1 = test_existing_incapacidad()
    
    # Probar nueva incapacidad
    success2 = test_fecha_registro()
    
    print(f"\n" + "=" * 60)
    if success2:
        print("🎉 ¡Prueba exitosa!")
        print("✅ La fecha_registro se está guardando correctamente")
        print("📅 Las nuevas incapacidades tendrán fecha de registro válida")
    else:
        print("❌ La prueba falló")
        print("⚠️ La fecha_registro no se está guardando correctamente")
    
    print(f"\n📋 Resumen:")
    print(f"1. ✅ Agregada fecha_registro a create_by_ids()")
    print(f"2. ✅ Agregada fecha_registro a create()")
    print(f"3. ✅ Usando datetime.utcnow() para fecha actual")
    print(f"4. ✅ Las nuevas incapacidades tendrán fecha válida")
    print(f"5. 🔄 Reinicia el servidor para aplicar cambios")





