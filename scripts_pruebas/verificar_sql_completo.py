#!/usr/bin/env python3
"""
Script simple para verificar y regenerar el archivo SQL MySQL
"""

import os
import re
from pathlib import Path

def verificar_y_regenerar():
    """Verifica el archivo actual y lo regenera si es necesario"""
    
    print("Verificando archivo SQL MySQL...")
    
    # Ruta al archivo de diagnósticos
    archivo_diagnosticos = Path("incapacidades froend/incapacidades/public/diagnosticos.txt")
    archivo_sql = Path(__file__).resolve().parent.parent / "sql_scripts" / "insert_diagnosticos_mysql.sql"
    
    if not archivo_diagnosticos.exists():
        print(f"Error: No se encontro el archivo {archivo_diagnosticos}")
        return
    
    # Leer diagnósticos
    print("Leyendo archivo de diagnosticos...")
    with open(archivo_diagnosticos, 'r', encoding='utf-8') as f:
        lineas = f.readlines()
    
    diagnosticos = []
    for linea in lineas:
        linea = linea.strip()
        if not linea or linea.startswith("COD_4") or linea.startswith("DESCRIPCION"):
            continue
        
        partes = linea.split('\t', 1)
        if len(partes) >= 2:
            codigo = partes[0].strip()
            descripcion = partes[1].strip()
            
            if len(codigo) >= 4 and codigo[0].isalpha() and codigo[1:].isdigit():
                diagnosticos.append({
                    'codigo': codigo,
                    'descripcion': descripcion
                })
    
    print(f"Diagnosticos encontrados: {len(diagnosticos)}")
    
    # Generar archivo SQL
    print("Generando archivo SQL...")
    archivo_sql.parent.mkdir(parents=True, exist_ok=True)

    with open(archivo_sql, 'w', encoding='utf-8') as f:
        f.write("-- INSERT para tabla parametro_hijo con parametro_id = 7 (Diagnosticos)\n")
        f.write("-- Generado automaticamente desde diagnosticos.txt\n")
        f.write("-- Base de datos: MySQL\n")
        f.write("-- Total de diagnosticos: {}\n\n".format(len(diagnosticos)))
        
        f.write("SET NAMES utf8mb4;\n")
        f.write("SET FOREIGN_KEY_CHECKS = 0;\n\n")
        
        # Escribir en lotes de 100
        batch_size = 100
        total_batches = (len(diagnosticos) + batch_size - 1) // batch_size
        
        for batch_num in range(total_batches):
            start_idx = batch_num * batch_size
            end_idx = min(start_idx + batch_size, len(diagnosticos))
            batch_diagnosticos = diagnosticos[start_idx:end_idx]
            
            f.write(f"-- Lote {batch_num + 1} de {total_batches}\n")
            f.write("INSERT INTO parametro_hijo (parametro_id, nombre, descripcion, estado) VALUES\n")
            
            valores = []
            for diag in batch_diagnosticos:
                descripcion_escaped = diag['descripcion'].replace("'", "\\'").replace('"', '\\"')
                nombre_escaped = diag['codigo'].replace("'", "\\'").replace('"', '\\"')
                valor = f"(7, '{nombre_escaped}', '{descripcion_escaped}', 1)"
                valores.append(valor)
            
            f.write(",\n".join(valores))
            f.write(";\n\n")
        
        f.write("SET FOREIGN_KEY_CHECKS = 1;\n\n")
        f.write("-- Verificacion\n")
        f.write("SELECT COUNT(*) as total FROM parametro_hijo WHERE parametro_id = 7;\n")
    
    print(f"Archivo SQL generado: {archivo_sql}")
    
    # Verificar el archivo generado
    print("Verificando archivo generado...")
    with open(archivo_sql, 'r', encoding='utf-8') as f:
        contenido = f.read()
    
    # Contar registros
    patron = r"\(7, '[^']+', '[^']+', 1\)"
    registros_encontrados = len(re.findall(patron, contenido))
    
    print(f"Registros en el archivo SQL: {registros_encontrados}")
    print(f"Diagnosticos procesados: {len(diagnosticos)}")
    
    if registros_encontrados == len(diagnosticos):
        print("✅ CORRECTO: El archivo contiene todos los diagnosticos")
    else:
        print(f"❌ ERROR: Faltan {len(diagnosticos) - registros_encontrados} registros")
    
    # Mostrar ejemplos
    print(f"\nEjemplos:")
    for i, diag in enumerate(diagnosticos[:3]):
        print(f"  {i+1}. {diag['codigo']} - {diag['descripcion'][:50]}...")
    
    print(f"\nUltimo diagnostico:")
    print(f"  {diagnosticos[-1]['codigo']} - {diagnosticos[-1]['descripcion'][:50]}...")

if __name__ == "__main__":
    print("Verificador y Regenerador de SQL MySQL")
    print("=" * 50)
    verificar_y_regenerar()

