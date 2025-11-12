from fastapi import APIRouter, Depends, HTTPException, Request, Response
from fastapi.responses import HTMLResponse
from typing import Optional
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.usuario import UsuarioCreate, UsuarioOut, UsuarioUpdate
from app.schemas.auth import (
    LoginRequest, 
    TokenResponse, 
    LoginResponse, 
    RefreshResponse, 
    UserInfo, 
    LogoutResponse,
    ForgotPasswordRequest,
    ForgotPasswordResponse,
    ResetPasswordRequest,
    ResetPasswordResponse
)
from app.services.usuario_service import UsuarioService
from app.services.password_reset_service import PasswordResetService
from app.core.security import decode_token
from app.core.auth_dependency import get_current_employee, get_current_admin


router = APIRouter(prefix="/auth", tags=["auth"])


def get_service(db: Session = Depends(get_db)) -> UsuarioService:
    return UsuarioService(db)


def get_password_reset_service(db: Session = Depends(get_db)) -> PasswordResetService:
    return PasswordResetService(db)


@router.post("/register", response_model=UsuarioOut)
def register(
    payload: UsuarioCreate,
    service: UsuarioService = Depends(get_service),
):
    try:
        return service.register(payload)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))


@router.post("/login", response_model=LoginResponse)
def login(
    payload: LoginRequest,
    response: Response,
    service: UsuarioService = Depends(get_service),
):
    try:
        data = service.authenticate(payload.correo_electronico, payload.password)
        
        # Configurar cookie HttpOnly para refresh token
        response.set_cookie(
            key="refresh_token",
            value=data["refresh_token"],
            httponly=True,
            secure=False,  # Solo HTTPS en producción
            samesite="lax",
            max_age=7*24*3600  # 7 días
        )
        
        # Retornar solo el access token y datos del usuario
        return LoginResponse(
            access_token=data["access_token"],
            token_type=data["token_type"],
            correo_electronico=data["correo_electronico"],
            rol=data["rol"],
            nombre=data["nombre"],
            id_usuario=data["id_usuario"]
        )
    except ValueError as exc:
        raise HTTPException(status_code=401, detail=str(exc))


@router.get("/usuarios", response_model=list[UsuarioOut])
def list_usuarios(
    skip: int = 0,
    limit: int = 100,
    service: UsuarioService = Depends(get_service),
):
    return service.list(skip=skip, limit=limit)
@router.get("/usuarios/human")
def list_usuarios_human(
    skip: int = 0,
    limit: int = 100,
    service: UsuarioService = Depends(get_service),
):
    """Lista usuarios con nombres legibles de parámetros y campos adicionales."""
    return service.list_human_readable(skip=skip, limit=limit)



@router.post("/usuarios/{id_usuario}/estado")
def cambiar_estado(
    id_usuario: int,
    payload: Optional[dict] = None,
    estado: Optional[bool] = None,
    service: UsuarioService = Depends(get_service),
):
    # Permitir ambas formas: JSON { estado } o query ?estado=true
    body_estado = payload.get("estado") if isinstance(payload, dict) else None
    final_estado = body_estado if body_estado is not None else estado
    if final_estado is None:
        raise HTTPException(status_code=400, detail="El campo 'estado' es requerido")
    ok = service.set_estado(id_usuario, bool(final_estado))
    if not ok:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    return {"ok": True}


@router.post("/usuarios/{id_usuario}/rol")
def cambiar_rol(
    id_usuario: int,
    payload: dict,
    service: UsuarioService = Depends(get_service),
    admin = Depends(get_current_admin),
):
    """Permite a un administrador asignar el rol de un usuario (por ejemplo, 10=admin, 9=empleado)."""
    try:
        nuevo_rol = int(payload.get("rol_id"))
    except Exception:
        nuevo_rol = None
    if nuevo_rol is None:
        raise HTTPException(status_code=400, detail="El campo 'rol_id' es requerido y debe ser numérico")
    ok = service.set_rol(id_usuario, nuevo_rol)
    if not ok:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    return {"ok": True, "rol_id": nuevo_rol}


@router.put("/usuarios/{id_usuario}")
def actualizar_usuario_admin(
    id_usuario: int,
    payload: UsuarioUpdate,
    service: UsuarioService = Depends(get_service),
    admin = Depends(get_current_admin),
):
    updated = service.update_admin(id_usuario, payload.model_dump(exclude_unset=True))
    if not updated:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    return {"ok": True}


@router.post("/refresh", response_model=RefreshResponse)
def refresh(
    request: Request,
    response: Response,
    service: UsuarioService = Depends(get_service),
):
    """Renueva el access token usando el refresh token de la cookie"""
    refresh_token = request.cookies.get("refresh_token")
    if not refresh_token:
        raise HTTPException(status_code=401, detail="No refresh token found")
    
    try:
        data = service.refresh_access_token(refresh_token)
        return RefreshResponse(**data)
    except ValueError as exc:
        raise HTTPException(status_code=401, detail=str(exc))


@router.post("/logout", response_model=LogoutResponse)
def logout(response: Response):
    """Elimina la cookie de refresh token"""
    response.delete_cookie("refresh_token")
    return LogoutResponse(message="Logged out successfully")


@router.get("/test-auth")
def test_auth(empleado = Depends(get_current_employee)):
    """Endpoint de prueba para verificar autenticación"""
    return {"message": "Autenticación exitosa", "user_id": empleado.id_usuario}

@router.post("/test-post")
def test_post_auth(
    empleado = Depends(get_current_employee),
    request: Request = None
):
    """Endpoint POST de prueba para verificar autenticación"""
    print(f"DEBUG: POST test - Usuario autenticado: {empleado.id_usuario}")
    return {"message": "POST autenticación exitosa", "user_id": empleado.id_usuario}

@router.get("/me", response_model=UserInfo)
def get_current_user(
    request: Request,
    service: UsuarioService = Depends(get_service),
):
    """Obtiene información del usuario actual desde el token"""
    # Intentar obtener el token del header Authorization
    authorization = request.headers.get("Authorization")
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Token no proporcionado")
    
    token = authorization.split(" ")[1]
    try:
        payload = decode_token(token)
        user_id = int(payload.get("sub"))
        
        user_info = service.get_user_info_human_readable(user_id)
        if not user_info:
            raise HTTPException(status_code=404, detail="Usuario no encontrado")
        
        return UserInfo(**user_info)
    except (ValueError, KeyError, TypeError):
        raise HTTPException(status_code=401, detail="Token inválido")


@router.put("/me")
def update_me(
    request: Request,
    payload: dict,
    service: UsuarioService = Depends(get_service),
):
    authorization = request.headers.get("Authorization")
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Token no proporcionado")
    token = authorization.split(" ")[1]
    try:
        decoded = decode_token(token)
        user_id = int(decoded.get("sub"))
    except Exception:
        raise HTTPException(status_code=401, detail="Token inválido")
    ok = service.update_me(user_id, payload or {})
    if not ok:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    return {"ok": True}


@router.post("/forgot-password", response_model=ForgotPasswordResponse)
def forgot_password(
    payload: ForgotPasswordRequest,
    password_reset_service: PasswordResetService = Depends(get_password_reset_service),
):
    """
    Solicita un reset de contraseña enviando un correo con enlace.
    Por seguridad, siempre retorna el mismo mensaje independientemente de si el correo existe.
    """
    try:
        success = password_reset_service.request_password_reset(payload.correo_electronico)
        return ForgotPasswordResponse(
            message="Si el correo existe en nuestro sistema, se enviará un enlace para restablecer la contraseña"
        )
    except Exception as e:
        # Por seguridad, siempre retornar el mismo mensaje
        return ForgotPasswordResponse(
            message="Si el correo existe en nuestro sistema, se enviará un enlace para restablecer la contraseña"
        )


@router.post("/reset-password", response_model=ResetPasswordResponse)
def reset_password(
    payload: ResetPasswordRequest,
    password_reset_service: PasswordResetService = Depends(get_password_reset_service),
):
    """
    Restablece la contraseña usando el token enviado por correo.
    """
    try:
        success = password_reset_service.reset_password(payload.token, payload.new_password)
        if not success:
            raise HTTPException(
                status_code=400, 
                detail="Token inválido, expirado o ya utilizado"
            )
        
        return ResetPasswordResponse(
            message="Contraseña restablecida exitosamente"
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500, 
            detail="Error interno del servidor"
        )


@router.get("/reset-password-page", response_class=HTMLResponse)
def reset_password_page(token: str):
    """
    Página temporal para reset de contraseña.
    Esta es una página HTML simple para probar la funcionalidad.
    """
    html_content = f"""
    <!DOCTYPE html>
    <html lang="es">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Restablecer Contraseña</title>
        <style>
            body {{
                font-family: Arial, sans-serif;
                max-width: 500px;
                margin: 50px auto;
                padding: 20px;
                background-color: #f5f5f5;
            }}
            .container {{
                background: white;
                padding: 30px;
                border-radius: 10px;
                box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            }}
            h1 {{
                color: #333;
                text-align: center;
                margin-bottom: 30px;
            }}
            .form-group {{
                margin-bottom: 20px;
            }}
            label {{
                display: block;
                margin-bottom: 5px;
                font-weight: bold;
                color: #555;
            }}
            input[type="password"] {{
                width: 100%;
                padding: 12px;
                border: 1px solid #ddd;
                border-radius: 5px;
                font-size: 16px;
                box-sizing: border-box;
            }}
            button {{
                width: 100%;
                padding: 12px;
                background-color: #007bff;
                color: white;
                border: none;
                border-radius: 5px;
                font-size: 16px;
                cursor: pointer;
                margin-top: 10px;
            }}
            button:hover {{
                background-color: #0056b3;
            }}
            .message {{
                padding: 10px;
                margin: 10px 0;
                border-radius: 5px;
                text-align: center;
            }}
            .success {{
                background-color: #d4edda;
                color: #155724;
                border: 1px solid #c3e6cb;
            }}
            .error {{
                background-color: #f8d7da;
                color: #721c24;
                border: 1px solid #f5c6cb;
            }}
            .info {{
                background-color: #d1ecf1;
                color: #0c5460;
                border: 1px solid #bee5eb;
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🔐 Restablecer Contraseña</h1>
            
            <div class="info">
                <strong>Token detectado:</strong> {token[:20]}...
            </div>
            
            <form id="resetForm">
                <div class="form-group">
                    <label for="newPassword">Nueva Contraseña:</label>
                    <input type="password" id="newPassword" name="newPassword" required minlength="6">
                </div>
                
                <div class="form-group">
                    <label for="confirmPassword">Confirmar Contraseña:</label>
                    <input type="password" id="confirmPassword" name="confirmPassword" required minlength="6">
                </div>
                
                <button type="submit">Restablecer Contraseña</button>
            </form>
            
            <div id="message"></div>
        </div>

        <script>
            document.getElementById('resetForm').addEventListener('submit', async function(e) {{
                e.preventDefault();
                
                const newPassword = document.getElementById('newPassword').value;
                const confirmPassword = document.getElementById('confirmPassword').value;
                const messageDiv = document.getElementById('message');
                
                // Validar que las contraseñas coincidan
                if (newPassword !== confirmPassword) {{
                    messageDiv.innerHTML = '<div class="error">Las contraseñas no coinciden</div>';
                    return;
                }}
                
                // Validar longitud mínima
                if (newPassword.length < 6) {{
                    messageDiv.innerHTML = '<div class="error">La contraseña debe tener al menos 6 caracteres</div>';
                    return;
                }}
                
                try {{
                    const response = await fetch('/api/auth/reset-password', {{
                        method: 'POST',
                        headers: {{
                            'Content-Type': 'application/json',
                        }},
                        body: JSON.stringify({{
                            token: '{token}',
                            new_password: newPassword
                        }})
                    }});
                    
                    const result = await response.json();
                    
                    if (response.ok) {{
                        messageDiv.innerHTML = '<div class="success">✅ ' + result.message + '</div>';
                        document.getElementById('resetForm').style.display = 'none';
                    }} else {{
                        messageDiv.innerHTML = '<div class="error">❌ ' + result.detail + '</div>';
                    }}
                }} catch (error) {{
                    messageDiv.innerHTML = '<div class="error">❌ Error de conexión: ' + error.message + '</div>';
                }}
            }});
        </script>
    </body>
    </html>
    """
    return HTMLResponse(content=html_content)