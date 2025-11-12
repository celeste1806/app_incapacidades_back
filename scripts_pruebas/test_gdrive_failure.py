#!/usr/bin/env python3
"""
Script para simular fallo de Google Drive y verificar que NO se creen incapacidades
"""

import sys
import os
from dotenv import load_dotenv

# Agregar el directorio del proyecto al path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.db.session import get_db
from app.services.incapacidad_service import IncapacidadService
from app.schemas.incapacidad import IncapacidadCreate
from datetime import datetime, timedelta

def test_gdrive_failure_simulation():
    """Simula un fallo de Google Drive para verificar que NO se creen incapacidades"""
    print("🚫 Simulación de Fallo de Google Drive")
    print("=" * 60)
    
    # Cargar configuración
    load_dotenv()
    
    try:
        db = next(get_db())
        service = IncapacidadService(db)
        
        # Simular fallo de Google Drive modificando temporalmente la configuración
        print("🔧 Simulando fallo de Google Drive...")
        original_config = service.upload_service.gdrive_service_account_json
        service.upload_service.gdrive_service_account_json = "archivo_inexistente.json"
        
        print("🧪 Probando validación con Google Drive fallido...")
        is_available = service.validar_google_drive_disponible()
        
        if not is_available:
            print("✅ Validación detectó correctamente que Google Drive no está disponible")
            
            # Intentar crear incapacidad (debería fallar)
            print("\n🏥 Intentando crear incapacidad con Google Drive fallido...")
            
            fecha_inicio = datetime.now()
            fecha_fin = fecha_inicio + timedelta(days=2)
            
            payload = IncapacidadCreate(
                tipo_incapacidad_id=1,
                causa_id=6,
                fecha_inicio=fecha_inicio,
                fecha_final=fecha_fin,
                dias=2,
                eps_afiliado_id=17,
                servicio_id=4,
                diagnostico_id=1,
                salario=3000000
            )
            
            try:
                result = service.crear_incapacidad(usuario_id=1, payload=payload)
                print(f"❌ ERROR: Se creó la incapacidad cuando NO debería haberse creado")
                print(f"📝 Resultado: {result}")
                return False
            except ValueError as e:
                if "Google Drive no está disponible" in str(e):
                    print(f"✅ CORRECTO: La incapacidad NO se creó porque Google Drive no está disponible")
                    print(f"📝 Error esperado: {str(e)}")
                    return True
                else:
                    print(f"❌ ERROR: Error inesperado: {str(e)}")
                    return False
            except Exception as e:
                print(f"❌ ERROR: Excepción inesperada: {str(e)}")
                return False
        else:
            print("❌ ERROR: La validación no detectó el fallo de Google Drive")
            return False
            
    except Exception as e:
        print(f"❌ Error durante la prueba: {str(e)}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        if 'db' in locals():
            db.close()

if __name__ == "__main__":
    print("🚫 Prueba de Fallo de Google Drive")
    print("=" * 60)
    
    success = test_gdrive_failure_simulation()
    
    print(f"\n" + "=" * 60)
    if success:
        print("🎉 ¡Prueba exitosa!")
        print("✅ El sistema protege correctamente contra fallos de Google Drive")
        print("🛡️ Las incapacidades NO se crean si no se pueden guardar los archivos")
    else:
        print("❌ La prueba falló")
        print("⚠️ El sistema no está protegiendo correctamente contra fallos de Google Drive")
    
    print(f"\n📋 Comportamiento esperado:")
    print(f"1. 🔍 Se valida Google Drive antes de crear incapacidades")
    print(f"2. ✅ Si Google Drive funciona: se crea la incapacidad")
    print(f"3. ❌ Si Google Drive falla: NO se crea la incapacidad")
    print(f"4. 🛡️ Los archivos están protegidos contra pérdida")





