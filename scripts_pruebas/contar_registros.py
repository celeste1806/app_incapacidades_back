#!/usr/bin/env python3
"""
Script para contar exactamente los registros en el archivo SQL
"""

import re
from pathlib import Path

def contar_registros_sql():
    """Cuenta los registros en el archivo SQL"""
    
    base_dir = Path(__file__).resolve().parent.parent
    archivo_sql = base_dir / "sql_scripts" / "insert_diagnosticos_mysql.sql"
    
    print("Contando registros en el archivo SQL...")
    
    try:
        with open(archivo_sql, 'r', encoding='utf-8') as f:
            contenido = f.read()
        
        # Contar líneas totales
        lineas_totales = len(contenido.split('\n'))
        print(f"Lineas totales: {lineas_totales}")
        
        # Buscar todos los registros con el patrón específico
        patron_registro = r"\(7, '[^']+', '[^']+', 1\)"
        registros = re.findall(patron_registro, contenido)
        total_registros = len(registros)
        
        print(f"Registros encontrados: {total_registros}")
        
        # Buscar el total mencionado en los comentarios
        patron_total = r"Total de diagnosticos: (\d+)"
        match = re.search(patron_total, contenido)
        if match:
            total_esperado = int(match.group(1))
            print(f"Total esperado: {total_esperado}")
            
            if total_registros == total_esperado:
                print("✅ CORRECTO: El archivo contiene TODOS los diagnósticos")
            else:
                print(f"❌ ERROR: Faltan {total_esperado - total_registros} diagnósticos")
        
        # Mostrar primer y último registro
        if registros:
            print(f"\nPrimer registro: {registros[0]}")
            print(f"Ultimo registro: {registros[-1]}")
        
        # Contar comandos INSERT
        comandos_insert = len(re.findall(r"INSERT INTO parametro_hijo", contenido, re.IGNORECASE))
        print(f"Comandos INSERT: {comandos_insert}")
        
        return total_registros
        
    except Exception as e:
        print(f"Error al procesar el archivo: {e}")
        return 0

if __name__ == "__main__":
    print("Contador de Registros SQL")
    print("=" * 30)
    contar_registros_sql()

