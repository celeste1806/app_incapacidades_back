from sqlalchemy import Integer, String, ForeignKey, DateTime, func, Numeric, Boolean
from sqlalchemy.orm import Mapped, mapped_column
from datetime import datetime

from app.models.base import Base


class Incapacidad(Base):
    __tablename__ = "incapacidad"

    id_incapacidad: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    tipo_incapacidad_id: Mapped[int] = mapped_column(Integer, ForeignKey("Tipo_incapacidad.id_tipo_incapacidad"))
    usuario_id: Mapped[int] = mapped_column(Integer, ForeignKey("usuario.id_usuario"))
    
    # Campos obligatorios del empleado
    clase: Mapped[str] = mapped_column(String(50), nullable=False)  # incapacidad | prórroga
    fecha_inicio: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    fecha_final: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    dias: Mapped[int] = mapped_column(Integer, nullable=False)
    eps_afiliado: Mapped[str] = mapped_column(String(200), nullable=False)
    servicio: Mapped[str] = mapped_column(String(200), nullable=False)
    diagnostico: Mapped[str] = mapped_column(String(500), nullable=False)
    salario: Mapped[Numeric] = mapped_column(Numeric(15, 2), nullable=False)
    
    # Estados internos (no visibles al empleado)
    estado: Mapped[int] = mapped_column(Integer, nullable=False, default=11)  # 11=pendientes, 12=realizada, 40=pagas, 44=no pagas, 50=rechazada
    fecha_registro: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=func.now())
    
    # Campos administrativos (solo para administradores)
    clase_administrativa: Mapped[str] = mapped_column(String(50), nullable=True)
    numero_radicado: Mapped[str] = mapped_column(String(100), nullable=True)
    fecha_radicado: Mapped[datetime] = mapped_column(DateTime, nullable=True)
    paga: Mapped[bool] = mapped_column(Boolean, nullable=True)
    estado_administrativo: Mapped[str] = mapped_column(String(100), nullable=True)
    usuario_revisor_id: Mapped[int] = mapped_column(Integer, ForeignKey("usuario.id_usuario"), nullable=True)
    
    # Campo para mensaje de rechazo
    mensaje_rechazo: Mapped[str] = mapped_column(String(500), nullable=True)
    
    # Campo para motivo cuando no están pagas
    motivo_no_pagas: Mapped[str] = mapped_column(String(500), nullable=True)
   
