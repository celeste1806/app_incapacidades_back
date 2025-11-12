#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para generar INSERT de servicios en la tabla parametro_hijo
parametro_id = 9 (Servicios)
"""

import os
import re

def procesar_servicios():
    """Procesa el archivo servicios.txt y genera INSERT statements"""
    
    # Ruta del archivo servicios.txt
    archivo_servicios = "../incapacidades froend/incapacidades/public/servicios.txt"
    
    if not os.path.exists(archivo_servicios):
        print(f"Error: No se encontro el archivo {archivo_servicios}")
        return 0, 0
    
    try:
        with open(archivo_servicios, 'r', encoding='utf-8') as f:
            lineas = f.readlines()
        
        # Filtrar líneas vacías y procesar
        servicios = []
        for linea in lineas:
            linea = linea.strip()
            if linea and linea != '':
                # Dividir por tabulaciones múltiples
                partes = re.split(r'\t+', linea)
                if len(partes) >= 2:
                    nombre = partes[0].strip()
                    descripcion = partes[1].strip()
                    
                    # Limpiar nombres y descripciones
                    nombre = nombre.replace('"', '\\"').replace("'", "\\'")
                    descripcion = descripcion.replace('"', '\\"').replace("'", "\\'")
                    
                    if nombre and descripcion:
                        servicios.append((nombre, descripcion))
        
        print(f"Servicios encontrados: {len(servicios)}")
        
        # Generar SQL
        sql_content = generar_sql_servicios(servicios)
        
        # Guardar archivo SQL
        archivo_sql = "insert_servicios_mysql.sql"
        with open(archivo_sql, 'w', encoding='utf-8') as f:
            f.write(sql_content)
        
        print(f"Archivo SQL generado: {archivo_sql}")
        print(f"Total de servicios procesados: {len(servicios)}")
        
        return len(servicios), len(servicios)
        
    except Exception as e:
        print(f"Error al procesar el archivo: {e}")
        return 0, 0

def generar_sql_servicios(servicios):
    """Genera el contenido SQL para los servicios"""
    
    sql_lines = [
        "-- =====================================================",
        "-- INSERT para tabla parametro_hijo con parametro_id = 9 (Servicios)",
        "-- Generado automaticamente desde servicios.txt",
        "-- Base de datos: MySQL",
        f"-- Total de servicios: {len(servicios)}",
        "-- =====================================================",
        "",
        "-- Configuracion inicial para MySQL",
        "SET NAMES utf8mb4;",
        "SET FOREIGN_KEY_CHECKS = 0;",
        "",
        "-- Limpiar datos existentes (opcional)",
        "-- DELETE FROM parametro_hijo WHERE parametro_id = 9;",
        "",
    ]
    
    # Procesar en lotes de 50
    lote_size = 50
    total_lotes = (len(servicios) + lote_size - 1) // lote_size
    
    for i in range(0, len(servicios), lote_size):
        lote_num = (i // lote_size) + 1
        lote_servicios = servicios[i:i + lote_size]
        
        sql_lines.append(f"-- Lote {lote_num} de {total_lotes} (registros {i+1}-{min(i+lote_size, len(servicios))})")
        sql_lines.append("INSERT INTO parametro_hijo (parametro_id, nombre, descripcion, estado) VALUES")
        
        valores = []
        for nombre, descripcion in lote_servicios:
            valor = f"(9, '{nombre}', '{descripcion}', 1)"
            valores.append(valor)
        
        sql_lines.append(",\n".join(valores) + ";")
        sql_lines.append("")
    
    sql_lines.extend([
        "-- Restaurar configuracion",
        "SET FOREIGN_KEY_CHECKS = 1;",
        "",
        "-- Verificar insercion",
        f"SELECT COUNT(*) as total_servicios FROM parametro_hijo WHERE parametro_id = 9;",
        "",
        "-- Mostrar algunos ejemplos",
        "SELECT id_parametrohijo, nombre, descripcion FROM parametro_hijo WHERE parametro_id = 9 LIMIT 10;"
    ])
    
    return "\n".join(sql_lines)

if __name__ == "__main__":
    print("Generando INSERT para servicios (parametro_id = 9)")
    print("=" * 50)
    
    total_procesados, total_generados = procesar_servicios()
    
    if total_procesados > 0:
        print(f"\nProceso completado exitosamente!")
        print(f"Servicios procesados: {total_procesados}")
        print(f"Archivo SQL generado: insert_servicios_mysql.sql")
        print(f"\nPara ejecutar en MySQL:")
        print(f"   mysql -u usuario -p base_datos < insert_servicios_mysql.sql")
    else:
        print(f"\nNo se pudieron procesar los servicios")

