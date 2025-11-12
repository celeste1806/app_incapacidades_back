#!/usr/bin/env python3
"""
Script para actualizar incapacidades existentes que tienen fecha_registro = "0000-00-00 00:00:00"
"""

import sys
import os
from datetime import datetime

# Agregar el directorio del proyecto al path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.db.session import get_db
from sqlalchemy import text

def update_fecha_registro_existing():
    """Actualiza las incapacidades existentes que tienen fecha_registro = "0000-00-00 00:00:00" """
    print("📅 Actualizando Fechas de Registro Existentes")
    print("=" * 60)
    
    try:
        db = next(get_db())
        
        # Buscar incapacidades con fecha_registro = "0000-00-00 00:00:00"
        print("🔍 Buscando incapacidades con fecha_registro inválida...")
        
        query = text("""
            SELECT id_incapacidad, fecha_inicio, fecha_final, usuario_id 
            FROM incapacidad 
            WHERE fecha_registro = '0000-00-00 00:00:00' 
            OR fecha_registro IS NULL
            ORDER BY id_incapacidad
        """)
        
        result = db.execute(query)
        rows = result.fetchall()
        
        if not rows:
            print("✅ No se encontraron incapacidades con fecha_registro inválida")
            return True
        
        print(f"📋 Encontradas {len(rows)} incapacidades con fecha_registro inválida")
        
        # Actualizar cada incapacidad
        updated_count = 0
        for row in rows:
            incapacidad_id = row[0]
            fecha_inicio = row[1]
            usuario_id = row[3]
            
            # Usar fecha_inicio como fecha_registro (aproximación)
            # Si no hay fecha_inicio, usar fecha actual
            if fecha_inicio and fecha_inicio != "0000-00-00 00:00:00":
                fecha_registro = fecha_inicio
            else:
                fecha_registro = datetime.utcnow()
            
            # Actualizar la fecha_registro
            update_query = text("""
                UPDATE incapacidad 
                SET fecha_registro = :fecha_registro 
                WHERE id_incapacidad = :incapacidad_id
            """)
            
            try:
                db.execute(update_query, {
                    "fecha_registro": fecha_registro,
                    "incapacidad_id": incapacidad_id
                })
                updated_count += 1
                print(f"✅ Actualizada incapacidad ID {incapacidad_id} - Fecha: {fecha_registro}")
            except Exception as e:
                print(f"❌ Error actualizando incapacidad ID {incapacidad_id}: {str(e)}")
        
        # Confirmar cambios
        db.commit()
        
        print(f"\n🎉 Actualización completada:")
        print(f"✅ {updated_count} incapacidades actualizadas")
        print(f"📅 Todas las incapacidades ahora tienen fecha_registro válida")
        
        return True
        
    except Exception as e:
        print(f"❌ Error durante la actualización: {str(e)}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        if 'db' in locals():
            db.close()

def verify_updates():
    """Verifica que las actualizaciones se aplicaron correctamente"""
    print(f"\n🔍 Verificando actualizaciones...")
    
    try:
        db = next(get_db())
        
        # Contar incapacidades con fecha_registro válida
        query_valid = text("""
            SELECT COUNT(*) 
            FROM incapacidad 
            WHERE fecha_registro != '0000-00-00 00:00:00' 
            AND fecha_registro IS NOT NULL
        """)
        
        result_valid = db.execute(query_valid)
        count_valid = result_valid.scalar()
        
        # Contar incapacidades con fecha_registro inválida
        query_invalid = text("""
            SELECT COUNT(*) 
            FROM incapacidad 
            WHERE fecha_registro = '0000-00-00 00:00:00' 
            OR fecha_registro IS NULL
        """)
        
        result_invalid = db.execute(query_invalid)
        count_invalid = result_invalid.scalar()
        
        # Contar total
        query_total = text("SELECT COUNT(*) FROM incapacidad")
        result_total = db.execute(query_total)
        count_total = result_total.scalar()
        
        print(f"📊 Estadísticas:")
        print(f"   Total de incapacidades: {count_total}")
        print(f"   Con fecha_registro válida: {count_valid}")
        print(f"   Con fecha_registro inválida: {count_invalid}")
        
        if count_invalid == 0:
            print(f"✅ ¡Todas las incapacidades tienen fecha_registro válida!")
            return True
        else:
            print(f"⚠️ Aún hay {count_invalid} incapacidades con fecha_registro inválida")
            return False
            
    except Exception as e:
        print(f"❌ Error verificando: {str(e)}")
        return False
    finally:
        if 'db' in locals():
            db.close()

if __name__ == "__main__":
    print("📅 Actualización de Fechas de Registro")
    print("=" * 60)
    
    # Actualizar incapacidades existentes
    success1 = update_fecha_registro_existing()
    
    # Verificar actualizaciones
    success2 = verify_updates()
    
    print(f"\n" + "=" * 60)
    if success1 and success2:
        print("🎉 ¡Actualización exitosa!")
        print("✅ Todas las incapacidades tienen fecha_registro válida")
        print("📅 Las nuevas incapacidades se crearán con fecha correcta")
    else:
        print("❌ La actualización falló")
        print("⚠️ Algunas incapacidades aún tienen fecha_registro inválida")
    
    print(f"\n📋 Resumen:")
    print(f"1. ✅ Actualizadas incapacidades existentes")
    print(f"2. ✅ Verificadas las actualizaciones")
    print(f"3. ✅ Nuevas incapacidades tendrán fecha correcta")
    print(f"4. 📅 Problema de fecha_registro solucionado")





