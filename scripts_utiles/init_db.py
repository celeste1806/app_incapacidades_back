#!/usr/bin/env python3

"""
Inicializa la base de datos apuntada por DATABASE_URL (crea tablas)
y, si no hay usuarios, crea un admin por defecto opcionalmente.
"""

import os
from typing import Optional

from app.db.session import engine, SessionLocal
from app.models.base import Base
from app.models.usuario import Usuario
# Asegurar que el metadata conoce todas las tablas referenciadas
from app.models import parametro as _parametro  # noqa: F401
from app.models import tipo_incapacidad as _tipo_incapacidad  # noqa: F401
from app.models import archivo as _archivo  # noqa: F401
from app.models import relacion as _relacion  # noqa: F401
from app.models import parametro_hijo as _parametro_hijo  # noqa: F401
from app.core.security import hash_password


def init_db(create_admin: bool = True, admin_email: str = "admin@umit.com.co", admin_password: str = "123456") -> None:
    # Crear tablas
    Base.metadata.create_all(bind=engine)

    # Crear admin si no hay usuarios
    if not create_admin:
        return

    with SessionLocal() as db:
        has_users = db.query(Usuario).first() is not None  # type: ignore[attr-defined]
        if not has_users:
            admin = Usuario(
                nombre_completo="Administrador",
                numero_identificacion="000000",
                tipo_identificacion_id=None,
                tipo_empleador_id=None,
                cargo_interno_id=0,
                correo_electronico=admin_email,
                password=hash_password(admin_password),
                rol_id=9,
                estado=True,
            )
            db.add(admin)
            db.commit()
            print(f"[OK] Usuario admin creado: {admin_email} / {admin_password}")
        else:
            print("[OK] Tablas listas. Ya existen usuarios; no se creó admin.")


if __name__ == "__main__":
    email = os.environ.get("INIT_ADMIN_EMAIL", "admin@umit.com.co")
    pwd = os.environ.get("INIT_ADMIN_PASSWORD", "123456")
    init_db(create_admin=True, admin_email=email, admin_password=pwd)


