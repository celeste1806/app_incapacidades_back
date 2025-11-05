from pydantic import BaseModel, Field, validator
from datetime import datetime
from typing import List, Optional
from decimal import Decimal


class IncapacidadCreate(BaseModel):
    """Schema para crear incapacidad (empleado)"""
    tipo_incapacidad_id: int = Field(..., description="ID del tipo de incapacidad")
    causa_id: int = Field(..., description="ID de la causa (parametro_hijo)")
    fecha_inicio: datetime = Field(..., description="Fecha de inicio")
    fecha_final: datetime = Field(..., description="Fecha final")
    dias: int = Field(..., description="Número de días")
    eps_afiliado_id: int = Field(..., description="ID de la EPS afiliado (parametro_hijo)")
    servicio_id: int = Field(..., description="ID del servicio (parametro_hijo)")
    diagnostico_id: int = Field(..., description="ID del diagnóstico (parametro_hijo)")
    salario: Decimal = Field(..., gt=0, description="Salario")

    @validator('fecha_final')
    def validate_fechas(cls, v, values):
        if 'fecha_inicio' in values and v <= values['fecha_inicio']:
            raise ValueError('fecha_final debe ser posterior a fecha_inicio')
        return v
class IncapacidadCreateV2(IncapacidadCreate):
    """
    Alias explícito para asegurar que FastAPI/Swagger tome la versión con IDs
    y evite caché de clases previas.
    """
    class Config:
        title = "IncapacidadCreateIDs"


class IncapacidadCreateLegacy(BaseModel):
    """Schema legacy que acepta strings. Mantener solo para transición."""
    tipo_incapacidad_id: int = Field(..., description="ID del tipo de incapacidad")
    clase: str = Field(..., description="Clase (texto)")
    fecha_inicio: datetime = Field(..., description="Fecha de inicio")
    fecha_final: datetime = Field(..., description="Fecha final")
    dias: int = Field(..., description="Número de días")
    eps_afiliado: str = Field(..., description="EPS afiliado (texto)")
    servicio: str = Field(..., description="Servicio (texto)")
    diagnostico: str = Field(..., description="Diagnóstico (texto)")
    salario: Decimal = Field(..., gt=0, description="Salario")

    @validator('fecha_final')
    def validate_fechas(cls, v, values):
        if 'fecha_inicio' in values and v <= values['fecha_inicio']:
            raise ValueError('fecha_final debe ser posterior a fecha_inicio')
        return v

    @validator('dias')
    def validate_dias(cls, v, values):
        if 'fecha_inicio' in values and 'fecha_final' in values:
            fecha_inicio = values['fecha_inicio']
            fecha_final = values['fecha_final']
            dias_calculados = (fecha_final - fecha_inicio).days + 1
            if v != dias_calculados:
                raise ValueError(f'Los días ({v}) no coinciden con el rango de fechas ({dias_calculados} días)')
        return v


    @validator('dias')
    def validate_dias(cls, v, values):
        if 'fecha_inicio' in values and 'fecha_final' in values:
            fecha_inicio = values['fecha_inicio']
            fecha_final = values['fecha_final']
            dias_calculados = (fecha_final - fecha_inicio).days + 1
            if v != dias_calculados:
                raise ValueError(f'Los días ({v}) no coinciden con el rango de fechas ({dias_calculados} días)')
        return v


class IncapacidadAdministrativaUpdate(BaseModel):
    """Schema para actualizar campos administrativos (admin) según columnas reales."""
    valor_pago: Optional[Decimal] = None
    numero_radicado: Optional[str] = Field(None, max_length=50)
    fecha_radicado: Optional[datetime] = None
    fecha_pago: Optional[datetime] = None
    estado: Optional[int] = None


class IncapacidadFormularioUpdate(BaseModel):
    """Schema para actualizar datos del formulario de incapacidad (admin/empleado). Ningún campo es obligatorio."""
    fecha_inicio: Optional[datetime] = None
    fecha_final: Optional[datetime] = None
    dias: Optional[int] = None
    salario: Optional[Decimal] = None
    eps_afiliado_id: Optional[int] = None
    servicio_id: Optional[int] = None
    diagnostico_id: Optional[int] = None


class IncapacidadOut(BaseModel):
    """Schema de salida para empleado (sin campos administrativos pero con estado)"""
    id_incapacidad: int
    tipo_incapacidad_id: int
    causa_id: int | None = None
    fecha_inicio: datetime
    fecha_final: datetime
    dias: int
    Eps_id: int | None = None
    servicio_id: int | None = None
    diagnostico_id: int | None = None
    salario: Decimal
    estado: int  # Agregado para que el empleado pueda ver el estado de sus incapacidades
    fecha_registro: datetime
    mensaje_rechazo: Optional[str] = None  # Agregado para mostrar motivo de rechazo
    documentos_cumplimiento: List[dict] = Field(default_factory=list)
    documentos: List[dict] = Field(default_factory=list)

    class Config:
        from_attributes = True


class IncapacidadAdminOut(BaseModel):
    """Schema de salida para administrador (con todos los campos)"""
    id_incapacidad: int
    tipo_incapacidad_id: int
    usuario_id: int
    # Nombre completo del usuario (expuesto por el backend al hacer JOIN)
    usuario_nombre: Optional[str] = None
    causa_id: int | None = None
    fecha_inicio: datetime
    fecha_final: datetime
    dias: int
    Eps_id: int | None = None
    servicio_id: int | None = None
    diagnostico_id: int | None = None
    salario: Decimal
    estado: int
    fecha_registro: datetime
    mensaje_rechazo: Optional[str] = None
    # Campos administrativos reales
    id_admin: Optional[int] = None
    valor_pago: Optional[Decimal] = None
    numero_radicado: Optional[str] = None
    fecha_radicado: Optional[datetime] = None
    fecha_pago: Optional[datetime] = None
    documentos: List[dict] = Field(default_factory=list)
    
    # Campos de nombres resueltos para mostrar en el frontend
    eps_afiliado_nombre: Optional[str] = None
    servicio_nombre: Optional[str] = None
    diagnostico_nombre: Optional[str] = None
    clase_nombre: Optional[str] = None
    tipo_incapacidad_nombre: Optional[str] = None

    class Config:
        from_attributes = True
