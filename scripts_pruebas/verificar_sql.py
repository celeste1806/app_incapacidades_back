#!/usr/bin/env python3
"""
Script para verificar que el archivo SQL contiene todos los diagnósticos
"""

import re
from pathlib import Path

def verificar_archivo_sql():
    """Verifica que el archivo SQL contenga todos los diagnósticos"""
    
    archivo_sql = Path(__file__).resolve().parent.parent / "sql_scripts" / "insert_diagnosticos_mysql.sql"
    
    if not archivo_sql.exists():
        print(f"Error: No se encontro el archivo {archivo_sql}")
        return
    
    print(f"Verificando archivo: {archivo_sql}")
    
    # Leer el archivo
    with open(archivo_sql, 'r', encoding='utf-8') as f:
        contenido = f.read()
    
    # Contar líneas totales
    lineas_totales = len(contenido.split('\n'))
    print(f"Lineas totales en el archivo: {lineas_totales}")
    
    # Buscar comandos INSERT
    insert_pattern = r"INSERT INTO parametro_hijo"
    inserts_encontrados = len(re.findall(insert_pattern, contenido, re.IGNORECASE))
    print(f"Comandos INSERT encontrados: {inserts_encontrados}")
    
    # Contar registros individuales (patrón de valores)
    valores_pattern = r"\(7, '[^']+', '[^']+', 1\)"
    registros_encontrados = len(re.findall(valores_pattern, contenido))
    print(f"Registros individuales encontrados: {registros_encontrados}")
    
    # Buscar el total mencionado en los comentarios
    total_pattern = r"Total de diagnosticos: (\d+)"
    match = re.search(total_pattern, contenido)
    if match:
        total_esperado = int(match.group(1))
        print(f"Total esperado segun comentarios: {total_esperado}")
        
        if registros_encontrados == total_esperado:
            print("✅ El archivo contiene TODOS los diagnósticos esperados")
        else:
            print(f"❌ FALTAN {total_esperado - registros_encontrados} diagnósticos")
            print(f"   Esperados: {total_esperado}")
            print(f"   Encontrados: {registros_encontrados}")
    
    # Mostrar algunos ejemplos de registros
    print(f"\nEjemplos de registros encontrados:")
    ejemplos = re.findall(valores_pattern, contenido)[:5]
    for i, ejemplo in enumerate(ejemplos, 1):
        print(f"  {i}. {ejemplo}")
    
    # Verificar el final del archivo
    print(f"\nUltimas 5 lineas del archivo:")
    lineas = contenido.split('\n')
    for linea in lineas[-5:]:
        if linea.strip():
            print(f"  {linea}")

if __name__ == "__main__":
    print("Verificador de Archivo SQL")
    print("=" * 40)
    verificar_archivo_sql()

