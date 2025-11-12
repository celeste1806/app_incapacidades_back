#!/usr/bin/env python3
"""
Script para verificar los parámetros en la base de datos
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.db.session import get_db
from app.repositories.parametro_hijo_repository import ParametroHijoRepository
from app.repositories.parametro_repository import ParametroRepository

def verificar_parametros():
    """Verifica qué parámetros hay en la base de datos"""
    print("Iniciando verificación de parámetros...")
    
    try:
        db = next(get_db())
        print("Conexión a la base de datos establecida")
        
        # Verificar parámetros padre
        print("Consultando parámetros padre...")
        param_repo = ParametroRepository(db)
        parametros_padre = param_repo.list()
        
        print("=== PARÁMETROS PADRE ===")
        print(f"Total de parámetros padre: {len(parametros_padre)}")
        for param in parametros_padre:
            print(f"ID: {param.id_parametro}, Nombre: {param.nombre}, Descripcion: {param.descripcion}")
        
        print("\n=== PARÁMETROS HIJO ===")
        param_hijo_repo = ParametroHijoRepository(db)
        parametros_hijo = param_hijo_repo.list()
        
        print(f"Total de parámetros hijo: {len(parametros_hijo)}")
        for param in parametros_hijo:
            print(f"ID: {param.id_parametrohijo}, Parametro_ID: {param.parametro_id}, Nombre: {param.nombre}, Descripcion: {param.descripcion}")
        
        print("\n=== PARÁMETROS HIJO CON PARAMETRO_ID = 6 ===")
        estados_parametro_6 = param_hijo_repo.papa(6)
        
        if estados_parametro_6:
            print(f"Se encontraron {len(estados_parametro_6)} estados para parametro_id=6:")
            for estado in estados_parametro_6:
                print(f"  - ID: {estado.id_parametrohijo}, Nombre: {estado.nombre}, Descripcion: {estado.descripcion}")
        else:
            print("No se encontraron estados para parametro_id=6")
            
    except Exception as e:
        print(f"Error al verificar parámetros: {e}")
        import traceback
        traceback.print_exc()
    finally:
        try:
            db.close()
            print("Conexión cerrada")
        except:
            pass

if __name__ == "__main__":
    verificar_parametros()
