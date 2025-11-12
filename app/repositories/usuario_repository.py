from typing import Optional, List
from sqlalchemy.orm import Session
from sqlalchemy import func


from app.models.usuario import Usuario


class UsuarioRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def get(self, id_usuario: int) -> Usuario | None:
        return self.db.get(Usuario, id_usuario)

    def get_by_email(self, correo_electronico: str) -> Usuario | None:
        # Comparación normalizada: TRIM + LOWER en DB vs valor normalizado en app
        correo_norm = (correo_electronico or "").strip().lower()
        return (
            self.db.query(Usuario)  # type: ignore[attr-defined]
            .filter(func.lower(func.trim(Usuario.correo_electronico)) == correo_norm)
            .first()
        )

    def create(
        self,
        *,
        nombre_completo: str,
        numero_identificacion: str,
        tipo_identificacion_id: Optional[int],
        tipo_empleador_id: Optional[int],
        cargo_interno_id: int,
        correo_electronico: str,
        telefono: Optional[str],
        password_hashed: str,
        rol_id: Optional[int],
        estado: bool = True,
    ) -> Usuario:
        entity = Usuario(
            nombre_completo=nombre_completo,
            numero_identificacion=numero_identificacion,
            tipo_identificacion_id=tipo_identificacion_id,
            tipo_empleador_id=tipo_empleador_id,
            cargo_interno_id=cargo_interno_id,
            correo_electronico=correo_electronico,
            telefono=telefono,
            password=password_hashed,
            rol_id=rol_id,
            estado=estado,
        )
        self.db.add(entity)
        self.db.commit()
        self.db.refresh(entity)
        return entity

    def list(self, *, skip: int = 0, limit: int = 1000) -> List[Usuario]:
        return (
            self.db.query(Usuario)  # type: ignore[attr-defined]
            .offset(skip)
            .limit(limit)
            .all()
        )

    def set_estado(self, id_usuario: int, estado: bool) -> bool:
        entity = self.get(id_usuario)
        if entity is None:
            return False
        entity.estado = estado
        self.db.commit()
        return True

    def set_rol(self, id_usuario: int, rol_id: int) -> bool:
        entity = self.get(id_usuario)
        if entity is None:
            return False
        entity.rol_id = int(rol_id)
        self.db.commit()
        return True

    def update_me(self, id_usuario: int, *, nombre: Optional[str] = None, numero_identificacion: Optional[str] = None, tipo_empleador_id: Optional[int] = None, cargo_interno: Optional[int] = None, correo_electronico: Optional[str] = None, telefono: Optional[str] = None) -> bool:
        entity = self.get(id_usuario)
        if entity is None:
            return False
        if nombre is not None:
            entity.nombre_completo = nombre
        if numero_identificacion is not None:
            entity.numero_identificacion = numero_identificacion
        if tipo_empleador_id is not None:
            entity.tipo_empleador_id = tipo_empleador_id
        if cargo_interno is not None:
            entity.cargo_interno_id = cargo_interno
        if correo_electronico is not None:
            entity.correo_electronico = correo_electronico
        if telefono is not None:
            entity.telefono = telefono
        self.db.commit()
        return True

    def update_admin(
        self,
        id_usuario: int,
        *,
        nombre_completo: Optional[str] = None,
        numero_identificacion: Optional[str] = None,
        tipo_identificacion_id: Optional[int] = None,
        tipo_empleador_id: Optional[int] = None,
        cargo_interno_id: Optional[int] = None,
        correo_electronico: Optional[str] = None,
        telefono: Optional[str] = None,
        rol_id: Optional[int] = None,
        estado: Optional[bool] = None,
    ) -> bool:
        entity = self.get(id_usuario)
        if entity is None:
            return False

        if nombre_completo is not None:
            entity.nombre_completo = nombre_completo
        if numero_identificacion is not None:
            entity.numero_identificacion = numero_identificacion
        if tipo_identificacion_id is not None:
            entity.tipo_identificacion_id = tipo_identificacion_id
        if tipo_empleador_id is not None:
            entity.tipo_empleador_id = tipo_empleador_id
        if cargo_interno_id is not None:
            entity.cargo_interno_id = cargo_interno_id
        if correo_electronico is not None:
            entity.correo_electronico = correo_electronico
        if telefono is not None:
            entity.telefono = telefono
        if rol_id is not None:
            entity.rol_id = int(rol_id)
        if estado is not None:
            entity.estado = bool(estado)

        self.db.commit()
        return True
