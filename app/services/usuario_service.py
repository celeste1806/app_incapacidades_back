from typing import List, Optional
from sqlalchemy.orm import Session

from app.repositories.usuario_repository import UsuarioRepository
from app.repositories.parametro_hijo_repository import ParametroHijoRepository
from app.schemas.usuario import UsuarioCreate, UsuarioOut
from app.core.security import (
    hash_password, 
    verify_password, 
    create_access_token, 
    create_refresh_token,
    validate_refresh_token,
    create_tokens_from_refresh_token
)


class UsuarioService:
    def __init__(self, db: Session) -> None:
        self.repo = UsuarioRepository(db)
        self.parametro_repo = ParametroHijoRepository(db)

    def register(self, payload: UsuarioCreate) -> UsuarioOut:
        existing = self.repo.get_by_email(payload.correo_electronico)
        if existing:
            raise ValueError("El correo ya está registrado")
        entity = self.repo.create(
            nombre_completo=payload.nombre_completo,
            numero_identificacion=payload.numero_identificacion,
            tipo_identificacion_id=payload.tipo_identificacion_id,
            tipo_empleador_id=payload.tipo_empleador_id,
            cargo_interno_id=payload.cargo_interno,
            correo_electronico=payload.correo_electronico,
            telefono=getattr(payload, 'telefono', None),
            password_hashed=hash_password(payload.password),
            rol_id=payload.rol_id,
            estado=payload.estado,
        )
        return UsuarioOut.model_validate(entity)

    def authenticate(self, correo_electronico: str, password: str) -> dict:
        # Normalizar correo para evitar discrepancias por espacios/mayúsculas
        correo_norm = (correo_electronico or "").strip().lower()
        user = self.repo.get_by_email(correo_norm)
        if user is None:
            print(f"[AUTH] No existe usuario con email: {correo_norm}")
            raise ValueError("Credenciales inválidas")
        # Cualquier excepción/verificación fallida se trata como credenciales inválidas
        try:
            is_valid = verify_password(password, user.password)
        except Exception as e:
            print(f"[AUTH] Error verificando password: {e}")
            is_valid = False
        if not is_valid:
            print(f"[AUTH] Password inválido para: {user.correo_electronico}")
            raise ValueError("Credenciales inválidas")
        
        # Validar que el usuario esté activo
        if not bool(user.estado):
            print(f"[AUTH] Usuario inactivo: {user.correo_electronico}")
            raise ValueError("Usuario inactivo")

        # Validar roles permitidos (solo 9 y 10)
        allowed_roles = {9, 10}
        try:
            user_role_id = int(user.rol_id) if user.rol_id is not None else None
        except Exception:
            user_role_id = None
        if user_role_id not in allowed_roles:
            print(f"[AUTH] Rol no autorizado: {user.rol_id} para {user.correo_electronico}")
            raise ValueError("Rol no autorizado")
        
        # Crear access token y refresh token
        access_token = create_access_token(
            subject=str(user.id_usuario),
            claims={
                "correo_electronico": user.correo_electronico,
                "rol": user.rol_id,
                "nombre": user.nombre_completo,
            },
        )
        refresh_token = create_refresh_token(subject=str(user.id_usuario))
        
        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
            "correo_electronico": user.correo_electronico,
            "rol": user.rol_id,
            "nombre": user.nombre_completo,
            "id_usuario": user.id_usuario,
        }
    
    def refresh_access_token(self, refresh_token: str) -> dict:
        """Genera un nuevo access token a partir del refresh token"""
        try:
            new_access_token = create_tokens_from_refresh_token(refresh_token)
            return {
                "access_token": new_access_token,
                "token_type": "bearer"
            }
        except ValueError as e:
            raise ValueError(f"Refresh token inválido: {str(e)}")
    
    def get_user_by_id(self, user_id: int) -> Optional[UsuarioOut]:
        """Obtiene un usuario por su ID"""
        user = self.repo.get(user_id)
        if user:
            return UsuarioOut.model_validate(user)
        return None

    def get_user_info_human_readable(self, user_id: int) -> Optional[dict]:
        """Retorna información del usuario con nombres de parámetros en lugar de IDs"""
        user = self.repo.get(user_id)
        if not user:
            return None

        def nombre_parametro(id_param: Optional[int]) -> Optional[str]:
            if id_param is None:
                return None
            hijo = self.parametro_repo.obtener_id(id_param)
            return hijo.nombre if hijo else None

        return {
            "id_usuario": user.id_usuario,
            "nombre": user.nombre_completo,
            "numero_identificacion": user.numero_identificacion,
            "correo_electronico": user.correo_electronico,
            "telefono": getattr(user, "telefono", None),
            "tipo_identificacion": nombre_parametro(user.tipo_identificacion_id),
            "tipo_empleador": nombre_parametro(user.tipo_empleador_id),
            "cargo_interno": nombre_parametro(user.cargo_interno_id),
            "rol": nombre_parametro(user.rol_id),
        }

    def list(self, skip: int = 0, limit: int = 100) -> List[UsuarioOut]:
        items = self.repo.list(skip=skip, limit=limit)
        return [UsuarioOut.model_validate(x) for x in items]

    def set_estado(self, id_usuario: int, estado: bool) -> bool:
        return self.repo.set_estado(id_usuario, estado)

    def set_rol(self, id_usuario: int, rol_id: int) -> bool:
        """Actualiza el rol de un usuario. Permite, por ejemplo, asignar rol 10 (admin)."""
        return self.repo.set_rol(id_usuario, int(rol_id))

    def update_me(self, user_id: int, payload: dict) -> bool:
        return self.repo.update_me(
            user_id,
            nombre=payload.get("nombre"),
            numero_identificacion=payload.get("numero_identificacion"),
            tipo_empleador_id=payload.get("tipo_empleador_id"),
            cargo_interno=payload.get("cargo_interno"),
            correo_electronico=payload.get("correo_electronico"),
            telefono=payload.get("telefono"),
        )

    def list_human_readable(self, skip: int = 0, limit: int = 100) -> List[dict]:
        users = self.repo.list(skip=skip, limit=limit)
        result: List[dict] = []
        for user in users:
            info = self.get_user_info_human_readable(user.id_usuario)
            if not info:
                continue
            # Agregar campos crudos adicionales
            info["correo_electronico"] = getattr(user, "correo_electronico", None)
            info["estado"] = bool(getattr(user, "estado", False))
            # Intentar exponer fecha_registro si existe en la tabla (puede no estar mapeada)
            info["fecha_registro"] = getattr(user, "fecha_registro", None)
            result.append(info)
        return result