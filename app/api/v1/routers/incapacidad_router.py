from fastapi import APIRouter, Depends, HTTPException, Query, UploadFile, File, Form, status
import os
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime

from app.db.session import get_db
from app.core.auth_dependency import get_current_employee, get_current_admin, get_current_employee_or_admin
from app.services.incapacidad_service import IncapacidadService
from app.schemas.incapacidad import (
    IncapacidadCreateV2 as IncapacidadCreate,
    IncapacidadOut,
    IncapacidadAdminOut,
    IncapacidadAdministrativaUpdate,
    IncapacidadFormularioUpdate,
)


router = APIRouter(prefix="/incapacidad", tags=["incapacidad"])


def get_service(db: Session = Depends(get_db)) -> IncapacidadService:
    return IncapacidadService(db)


@router.post("/test-simple")
def test_simple(
    empleado = Depends(get_current_employee),
):
    """Endpoint de prueba simple"""
    print(f"DEBUG: Test simple - Usuario: {empleado.id_usuario}")
    return {"message": "Test exitoso", "user_id": empleado.id_usuario}


@router.post(
    "/archivo",
    summary="Subir documento y crear registro incapacidad_archivo",
)
def subir_documento_incapacidad(
    incapacidad_id: int = Form(...),
    archivo_id: int = Form(...),
    file: UploadFile = File(...),
    service: IncapacidadService = Depends(get_service),
    usuario = Depends(get_current_employee_or_admin),
):
    """
    Acepta `incapacidad_id`, `archivo_id` y un archivo (pdf/png/jpg). Guarda el archivo en
    una carpeta del servidor y crea un registro en `incapacidad_archivo` con `url_documento`
    igual al nombre de archivo almacenado.
    """
    try:
        return service.subir_documento_y_crear_registro(
            usuario_id=usuario.id_usuario,
            incapacidad_id=incapacidad_id,
            archivo_id=archivo_id,
            file=file,
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Error al subir documento: {str(exc)}")


@router.post(
    "/",
    summary="Empleado crea una incapacidad (IDs)",
    response_model=IncapacidadOut,
)
def crear_incapacidad(
    payload: IncapacidadCreate,
    service: IncapacidadService = Depends(get_service),
    usuario = Depends(get_current_employee_or_admin),
):
    print(f"DEBUG: ===== INICIO CREAR INCAPACIDAD =====")
    print(f"DEBUG: Usuario autenticado: {usuario.id_usuario}, Rol: {usuario.rol_id}")
    print(f"DEBUG: Payload recibido: {payload}")
    print(f"DEBUG: Payload tipo: {type(payload)}")
    
    try:
        print(f"DEBUG: Llamando a service.crear_incapacidad...")
        result = service.crear_incapacidad(
            usuario_id=usuario.id_usuario,
            payload=payload
        )
        print(f"DEBUG: Incapacidad creada exitosamente: {result}")
        return result
    except ValueError as exc:
        print(f"DEBUG: ValueError en crear_incapacidad: {str(exc)}")
        raise HTTPException(status_code=400, detail=str(exc))
    except Exception as exc:
        print(f"DEBUG: Exception general en crear_incapacidad: {str(exc)}")
        print(f"DEBUG: Tipo de excepción: {type(exc)}")
        import traceback
        print(f"DEBUG: Traceback completo: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=f"Error interno: {str(exc)}")


@router.get("/mias", summary="Empleado lista sus incapacidades", response_model=List[IncapacidadOut])
def listar_mias(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    service: IncapacidadService = Depends(get_service),
    usuario = Depends(get_current_employee_or_admin),
):
    return service.listar_mis_incapacidades(
        usuario_id=usuario.id_usuario, 
        skip=skip, 
        limit=limit
    )


@router.get("/mias/{id_incapacidad}", summary="Empleado ve detalle de su incapacidad", response_model=IncapacidadOut)
def obtener_mi_incapacidad(
    id_incapacidad: int,
    service: IncapacidadService = Depends(get_service),
    empleado = Depends(get_current_employee),
):
    result = service.obtener_mi_incapacidad(
        usuario_id=empleado.id_usuario,
        id_incapacidad=id_incapacidad
    )
    if not result:
        raise HTTPException(status_code=404, detail="Incapacidad no encontrada")
    return result


@router.get("/", summary="Lista todas las incapacidades (empleado/admin)")
def listar_admin(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    estado: Optional[int] = Query(None, description="Filtrar por estado (1=Enviado, 2=Revisado)"),
    tipo_incapacidad_id: Optional[int] = Query(None, description="Filtrar por tipo de incapacidad"),
    usuario_id: Optional[int] = Query(None, description="Filtrar por empleado"),
    fecha_inicio: Optional[datetime] = Query(None, description="Fecha inicio del rango"),
    fecha_final: Optional[datetime] = Query(None, description="Fecha final del rango"),
    service: IncapacidadService = Depends(get_service),
    admin = Depends(get_current_employee_or_admin),
):
    return service.listar_admin(
        skip=skip, 
        limit=limit, 
        estado=estado,
        tipo_incapacidad_id=tipo_incapacidad_id,
        usuario_id=usuario_id,
        fecha_inicio=fecha_inicio,
        fecha_final=fecha_final
    )


@router.get("/admin/rechazadas", summary="Admin lista incapacidades rechazadas", response_model=List[IncapacidadAdminOut])
def listar_rechazadas(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    service: IncapacidadService = Depends(get_service),
    admin = Depends(get_current_admin),
):
    """Lista incapacidades rechazadas para administradores"""
    return service.listar_admin(
        skip=skip, 
        limit=limit, 
        estado=50
    )


@router.get("/{id_incapacidad}", summary="Detalle completo de incapacidad (empleado/admin)", response_model=IncapacidadAdminOut)
def obtener_incapacidad_admin(
    id_incapacidad: int,
    service: IncapacidadService = Depends(get_service),
    admin = Depends(get_current_employee_or_admin),
):
    print(f"DEBUG ROUTER: Endpoint obtener_incapacidad_admin llamado para ID {id_incapacidad}")
    result = service.obtener_incapacidad_admin(id_incapacidad=id_incapacidad)
    print(f"DEBUG ROUTER: Resultado del servicio: {result}")
    if not result:
        raise HTTPException(status_code=404, detail="Incapacidad no encontrada")
    return result


@router.put("/{id_incapacidad}/administrativo", summary="Admin actualiza campos administrativos")
def actualizar_administrativo(
    id_incapacidad: int,
    payload: IncapacidadAdministrativaUpdate,
    service: IncapacidadService = Depends(get_service),
    admin = Depends(get_current_admin),
):
    ok = service.actualizar_administrativo(
        id_incapacidad=id_incapacidad,
        admin_id=admin.id_usuario,
        payload=payload
    )
    if not ok:
        raise HTTPException(status_code=404, detail="Incapacidad no encontrada")
    return {"ok": True, "message": "Campos administrativos actualizados y marcada como revisada"}


@router.post("/{id_incapacidad}/revisar", summary="Admin marca como revisada (método simple)")
def marcar_revisada(
    id_incapacidad: int,
    service: IncapacidadService = Depends(get_service),
    admin = Depends(get_current_admin),
):
    ok = service.marcar_revisada(id_incapacidad=id_incapacidad)
    if not ok:
        raise HTTPException(status_code=404, detail="Incapacidad no encontrada")
    return {"ok": True, "message": "Incapacidad marcada como revisada"}


@router.put("/{id_incapacidad}/estado", summary="Admin cambia el estado de una incapacidad")
def cambiar_estado(
    id_incapacidad: int,
    estado_data: dict,
    service: IncapacidadService = Depends(get_service),
    admin = Depends(get_current_admin),
):
    """Cambia el estado de una incapacidad. Estados válidos: 11=Pendiente, 12=Realizada, 40=Pagas, 44=No Pagas, 50=Rechazada"""
    estado = estado_data.get("estado")
    mensaje_rechazo = estado_data.get("mensaje_rechazo")
    
    if estado is None:
        raise HTTPException(status_code=400, detail="El campo 'estado' es requerido")
    
    # Si es rechazo, validar que tenga mensaje
    if estado == 50 and not mensaje_rechazo:
        raise HTTPException(status_code=400, detail="El campo 'mensaje_rechazo' es requerido para rechazar una incapacidad")
    
    ok = service.cambiar_estado(
        id_incapacidad=id_incapacidad, 
        nuevo_estado=estado, 
        admin_id=admin.id_usuario,
        mensaje_rechazo=mensaje_rechazo
    )
    if not ok:
        raise HTTPException(status_code=404, detail="Incapacidad no encontrada")
    
    estado_text = {
        11: "Pendiente", 12: "Realizada", 40: "Pagas", 
        44: "No Pagas", 50: "Rechazada"
    }.get(estado, f"Estado {estado}")
    
    # Agregar advertencia si no hay credenciales SMTP y el estado es Rechazada
    warning = None
    if estado == 50:
        smtp_username = os.getenv('SMTP_USERNAME')
        smtp_password = os.getenv('SMTP_PASSWORD')
        if not smtp_username or not smtp_password:
            warning = (
                "Advertencia: No se envi correo de rechazo porque faltan credenciales SMTP. "
                "Configure SMTP_USERNAME y SMTP_PASSWORD en el backend."
            )
    
    response = {"ok": True, "message": f"Estado cambiado a {estado_text}"}
    if warning:
        response["warning"] = warning
    return response


@router.put("/{id_incapacidad}/formulario", summary="Admin actualiza datos del formulario de incapacidad")
def actualizar_formulario(
    id_incapacidad: int,
    payload: IncapacidadFormularioUpdate,
    service: IncapacidadService = Depends(get_service),
    admin = Depends(get_current_admin),
):
    """Actualiza los datos del formulario de una incapacidad (fechas, días, salario, EPS, servicio, diagnóstico)"""
    ok = service.actualizar_formulario(
        id_incapacidad=id_incapacidad,
        admin_id=admin.id_usuario,
        payload=payload
    )
    if not ok:
        raise HTTPException(status_code=404, detail="Incapacidad no encontrada")
    return {"ok": True, "message": "Datos del formulario actualizados correctamente"}


@router.delete("/{id_incapacidad}", status_code=status.HTTP_204_NO_CONTENT, summary="Admin elimina una incapacidad")
def eliminar_incapacidad(
    id_incapacidad: int,
    service: IncapacidadService = Depends(get_service),
    admin = Depends(get_current_admin),
):
    ok = service.eliminar(id_incapacidad=id_incapacidad, admin_id=admin.id_usuario)
    if not ok:
        raise HTTPException(status_code=404, detail="Incapacidad no encontrada")
    return None


@router.put("/mias/{id_incapacidad}", summary="Empleado corrige y reenvía su incapacidad rechazada")
def actualizar_mia_reenviar(
    id_incapacidad: int,
    payload: IncapacidadFormularioUpdate,
    service: IncapacidadService = Depends(get_service),
    empleado = Depends(get_current_employee),
):
    ok = service.actualizar_formulario_empleado(
        id_incapacidad=id_incapacidad,
        usuario_id=empleado.id_usuario,
        payload=payload,
    )
    if not ok:
        raise HTTPException(status_code=404, detail="Incapacidad no encontrada")
    return {"ok": True, "message": "Incapacidad reenviada a revisión"}


@router.post("/mias/{id_incapacidad}/reenviar", summary="Empleado reenvía su incapacidad rechazada")
def actualizar_mia_reenviar_post(
    id_incapacidad: int,
    service: IncapacidadService = Depends(get_service),
    empleado = Depends(get_current_employee),
):
    """Reenvía una incapacidad rechazada a estado pendiente (solo cambia el estado, no los datos)"""
    print(f"🔔 Recibida petición de reenvío para incapacidad {id_incapacidad}")
    print(f"🔔 Usuario: {empleado.id_usuario}")
    
    # Verificar que la incapacidad existe y pertenece al usuario
    incapacidad = service.repo.get(id_incapacidad)
    print(f"🔔 Incapacidad obtenida: {incapacidad}")
    if not incapacidad:
        raise HTTPException(status_code=404, detail="Incapacidad no encontrada")
    
    if incapacidad.get("usuario_id") != empleado.id_usuario:
        raise HTTPException(status_code=403, detail="No tienes permisos para reenviar esta incapacidad")
    
    if incapacidad.get("estado") != 50:
        raise HTTPException(status_code=400, detail="Solo se pueden reenviar incapacidades rechazadas")
    
    # Cambiar estado a 11 (Pendiente) y limpiar mensaje de rechazo
    ok = service.repo.update_estado(id_incapacidad, estado=11)
    if not ok:
        raise HTTPException(status_code=500, detail="No se pudo actualizar el estado")
    
    # Limpiar mensaje de rechazo
    try:
        service.repo.update_mensaje_rechazo(id_incapacidad, "")
    except Exception:
        pass
    
    # Registrar auditoría
    service.audit_service.log_status_change(
        incapacidad_id=id_incapacidad,
        user_id=empleado.id_usuario,
        old_status=50,
        new_status=11,
        reason="Reenvío por empleado después de modificar documentos"
    )
    
    return {"ok": True, "message": "Incapacidad reenviada a revisión"}


@router.post("/{id_incapacidad}/notify-admins", summary="Notificar a administradores sobre nueva incapacidad")
def notify_admins_nueva_incapacidad(
    id_incapacidad: int,
    service: IncapacidadService = Depends(get_service),
    empleado = Depends(get_current_employee),
):
    """
    Notifica a los administradores que se ha creado una nueva incapacidad.
    Este endpoint es llamado por el frontend después de crear una incapacidad.
    """
    try:
        print(f"🔔 Notificando a administradores sobre incapacidad {id_incapacidad}")
        
        # Verificar que la incapacidad existe y pertenece al usuario
        incapacidad = service.repo.get(id_incapacidad)
        if not incapacidad:
            raise HTTPException(status_code=404, detail="Incapacidad no encontrada")
        
        if incapacidad.get("usuario_id") != empleado.id_usuario:
            raise HTTPException(status_code=403, detail="No tienes permisos para notificar sobre esta incapacidad")
        
        # Enviar notificación a administradores
        success = service.notification_service.notify_admins_new_incapacity(
            incapacidad_id=id_incapacidad,
            empleado_id=empleado.id_usuario
        )
        
        if success:
            print(f"✅ Notificación enviada exitosamente para incapacidad {id_incapacidad}")
            return {"ok": True, "message": "Notificación enviada a administradores"}
        else:
            print(f"⚠️ No se pudo enviar notificación para incapacidad {id_incapacidad}")
            return {"ok": False, "message": "No se pudo enviar la notificación"}
            
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Error enviando notificación: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error interno: {str(e)}")
