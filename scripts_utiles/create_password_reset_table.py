#!/usr/bin/env python3
"""
Script para crear la tabla de tokens de reset de contraseña
"""

import sys
import os

# Agregar el directorio del proyecto al path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.db.session import engine
from app.models.base import Base
from app.models.usuario import Usuario  # Importar para resolver foreign key
from app.models.password_reset_token import PasswordResetToken

def create_password_reset_table():
    """Crea la tabla de tokens de reset de contraseña"""
    print("🔧 Creando tabla de tokens de reset de contraseña...")
    
    try:
        # Crear la tabla
        PasswordResetToken.__table__.create(bind=engine, checkfirst=True)
        print("✅ Tabla 'password_reset_tokens' creada exitosamente")
        
        # Verificar que se creó
        from sqlalchemy import inspect
        inspector = inspect(engine)
        tables = inspector.get_table_names()
        
        if 'password_reset_tokens' in tables:
            print("✅ Verificación: La tabla existe en la base de datos")
            
            # Mostrar estructura de la tabla
            columns = inspector.get_columns('password_reset_tokens')
            print("\n📋 Estructura de la tabla:")
            for column in columns:
                print(f"  - {column['name']}: {column['type']}")
        else:
            print("❌ Error: La tabla no se encontró después de crearla")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ Error creando tabla: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("🚀 Configuración de Tabla de Reset de Contraseña")
    print("=" * 50)
    
    success = create_password_reset_table()
    
    print("=" * 50)
    if success:
        print("🎉 ¡Configuración exitosa!")
        print("💡 Ahora puedes reiniciar el servidor para usar la funcionalidad de reset")
    else:
        print("❌ La configuración falló")
        print("📝 Revisa los errores anteriores")
    
    print("\n🔧 Próximos pasos:")
    print("1. Reinicia el servidor backend")
    print("2. Ejecuta: python test_password_reset.py")
    print("3. Prueba la funcionalidad completa")
