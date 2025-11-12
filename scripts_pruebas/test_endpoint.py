#!/usr/bin/env python3
"""
Script para probar el endpoint directamente
"""

import requests
import json

def test_endpoint():
    base_url = "http://localhost:8000"
    
    # Primero hacer login como admin
    login_data = {
        "email": "talentohumano@umit.com.co",
        "password": "123456"
    }
    
    print("=== HACIENDO LOGIN ===")
    login_response = requests.post(f"{base_url}/api/auth/login", json=login_data)
    print(f"Login status: {login_response.status_code}")
    
    if login_response.status_code == 200:
        login_result = login_response.json()
        token = login_result.get("access_token")
        print(f"Token obtenido: {token[:50]}...")
        
        # Probar el endpoint de incapacidad
        headers = {
            "Authorization": f"Bearer {token}",
            "Accept": "application/json"
        }
        
        print("\n=== PROBANDO ENDPOINT /api/incapacidad/25 ===")
        response = requests.get(f"{base_url}/api/incapacidad/25", headers=headers)
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"Datos recibidos:")
            print(f"  Eps_id: {data.get('Eps_id')}")
            print(f"  eps_afiliado_nombre: {data.get('eps_afiliado_nombre')}")
            print(f"  eps_afiliado: {data.get('eps_afiliado')}")
            print(f"  eps_afiliado_id: {data.get('eps_afiliado_id')}")
            print(f"\nDatos completos:")
            print(json.dumps(data, indent=2, default=str))
        else:
            print(f"Error: {response.text}")
    else:
        print(f"Error en login: {login_response.text}")

if __name__ == "__main__":
    test_endpoint()
