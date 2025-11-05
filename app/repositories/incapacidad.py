from __future__ import annotations

from typing import Any, Iterable, Optional, List
from sqlalchemy import MetaData, Table, insert, select, update, and_, delete
from sqlalchemy.orm import Session
from datetime import datetime
from decimal import Decimal


class IncapacidadRepository:
    def __init__(self, db: Session) -> None:
        self.db = db
        self._metadata = MetaData()
        # Reflejar tablas existentes sin definir modelos ORM
        self._metadata.reflect(bind=self.db.bind, only=[
            "incapacidad",
            "incapacidad_archivo",
        ])
        self.t_incapacidad: Table = self._metadata.tables["incapacidad"]
        self.t_incapacidad_archivo: Table = self._metadata.tables["incapacidad_archivo"]

    def create(self, *, 
               tipo_incapacidad_id: int, 
               usuario_id: int, 
               clase: str,
               fecha_inicio: datetime, 
               fecha_final: datetime, 
               dias: int,
               eps_afiliado: str,
               servicio: str,
               diagnostico: str,
               salario: float,
               estado: int = 11) -> dict:  # 11 = pendientes
        # Construir diccionario de valores y filtrar por columnas existentes para evitar
        # errores del tipo "Unconsumed column names" cuando el esquema de BD no coincide
        # exactamente con el modelo esperado.
        all_values = {
            "tipo_incapacidad_id": tipo_incapacidad_id,
            "usuario_id": usuario_id,
            "clase": clase,
            "fecha_inicio": fecha_inicio,
            "fecha_final": fecha_final,
            "dias": dias,
            "eps_afiliado": eps_afiliado,
            "servicio": servicio,
            "diagnostico": diagnostico,
            "salario": salario,
            "estado": estado,
            "fecha_registro": datetime.utcnow(),  # ✅ AGREGAR FECHA DE REGISTRO
        }
        existing_cols = set(self.t_incapacidad.c.keys())
        filtered_values = {k: v for k, v in all_values.items() if k in existing_cols}

        # Debug de columnas existentes y valores a insertar
        try:
            print(f"DEBUG: incapacidad columns -> {sorted(existing_cols)}")
            print(f"DEBUG: incapacidad insert keys -> {sorted(filtered_values.keys())}")
        except Exception:
            pass

        stmt = (
            insert(self.t_incapacidad)
            .values(**filtered_values)
        )
        try:
            result = self.db.execute(stmt)
        except Exception as exc:
            # Reintento con columnas mínimas si hay error de columnas no consumidas
            print(f"DEBUG: Insert falló ({type(exc)}): {exc}")
            minimal_keys = {"tipo_incapacidad_id", "usuario_id", "fecha_inicio", "fecha_final", "dias", "estado"}
            minimal_values = {k: v for k, v in all_values.items() if k in minimal_keys and k in existing_cols}
            print(f"DEBUG: reintentando insert con claves -> {sorted(minimal_values.keys())}")
            stmt_min = (
                insert(self.t_incapacidad)
                .values(**minimal_values)
            )
            result = self.db.execute(stmt_min)
        self.db.commit()

        # Recuperar fila insertada (MariaDB/MySQL no soporta RETURNING en este conector)
        try:
            last_id = getattr(result, "lastrowid", None)
        except Exception:
            last_id = None

        pk_cols = list(self.t_incapacidad.primary_key.columns)
        pk_col = pk_cols[0] if pk_cols else None

        row = None
        if last_id is not None and pk_col is not None:
            sel = select(self.t_incapacidad).where(pk_col == last_id)
            row = self.db.execute(sel).mappings().first()
        else:
            # Fallback: buscar última por orden de PK
            if pk_col is not None:
                sel = select(self.t_incapacidad).order_by(pk_col.desc())
                row = self.db.execute(sel).mappings().first()

        return dict(row) if row else {}

    def create_by_ids(self, *,
                      tipo_incapacidad_id: int,
                      usuario_id: int,
                      fecha_inicio: datetime,
                      fecha_final: datetime,
                      dias: int,
                      estado: int = 11,  # 11 = pendientes
                      causa_incapacidad_id: Optional[int] = None,
                      Eps_id: Optional[int] = None,
                      servicio_id: Optional[int] = None,
                      diagnostico_id: Optional[int] = None,
                      salario_id: Optional[int] = None,
                      salario: Optional[float] = None) -> dict:
        """Inserta usando las columnas exactas de la BD según el esquema real."""
        # Columnas exactas según tu BD (sin filtrado dinámico para evitar errores)
        values = {
            "tipo_incapacidad_id": tipo_incapacidad_id,
            "usuario_id": usuario_id,
            "fecha_inicio": fecha_inicio,
            "fecha_final": fecha_final,
            "dias": dias,
            "estado": estado,
            "fecha_registro": datetime.utcnow(),  # ✅ AGREGAR FECHA DE REGISTRO
        }
        
        # Solo agregar columnas opcionales si tienen valor
        if causa_incapacidad_id is not None:
            values["causa_incapacidad_id"] = causa_incapacidad_id
        if Eps_id is not None:
            values["Eps_id"] = Eps_id
        if servicio_id is not None:
            values["servicio_id"] = servicio_id
        if diagnostico_id is not None:
            values["diagnostico_id"] = diagnostico_id
        if salario_id is not None:
            values["salario_id"] = salario_id
        # En tu tabla existe la columna 'salario' (varchar). Guardamos el valor numérico como string
        if salario is not None:
            try:
                values["salario"] = str(salario)
            except Exception:
                values["salario"] = str(salario)

        print(f"DEBUG: incapacidad create_by_ids -> keys {sorted(values.keys())}")
        print(f"DEBUG: incapacidad create_by_ids -> values {values}")

        stmt = insert(self.t_incapacidad).values(**values)
        result = self.db.execute(stmt)
        self.db.commit()

        try:
            last_id = getattr(result, "lastrowid", None)
        except Exception:
            last_id = None

        pk_cols = list(self.t_incapacidad.primary_key.columns)
        pk_col = pk_cols[0] if pk_cols else None
        row = None
        if last_id is not None and pk_col is not None:
            sel = select(self.t_incapacidad).where(pk_col == last_id)
            row = self.db.execute(sel).mappings().first()
        elif pk_col is not None:
            sel = select(self.t_incapacidad).order_by(pk_col.desc())
            row = self.db.execute(sel).mappings().first()
        return dict(row) if row else {}

    def get(self, id_incapacidad: int) -> Optional[dict]:
        stmt = select(self.t_incapacidad).where(self.t_incapacidad.c.id_incapacidad == id_incapacidad)
        row = self.db.execute(stmt).mappings().first()
        return dict(row) if row else None

    def get_with_documents(self, id_incapacidad: int) -> Optional[dict]:
        """Obtiene incapacidad con sus documentos asociados"""
        print(f"DEBUG REPO: Columnas disponibles en t_incapacidad: {list(self.t_incapacidad.c.keys())}")
        stmt = select(self.t_incapacidad).where(self.t_incapacidad.c.id_incapacidad == id_incapacidad)
        inc = self.db.execute(stmt).mappings().first()
        if not inc:
            return None
        
        result = dict(inc)
        print(f"DEBUG REPO: Datos obtenidos de BD: {result}")
        
        # Obtener documentos asociados
        # Usar una consulta directa para debug
        from sqlalchemy import text
        raw_query = text(f"SELECT * FROM incapacidad_archivo WHERE incapacidad_id = {id_incapacidad}")
        raw_docs = self.db.execute(raw_query).mappings().all()
        print(f"DEBUG REPO: Consulta raw SQL para incapacidad {id_incapacidad}")
        print(f"DEBUG REPO: SQL: SELECT * FROM incapacidad_archivo WHERE incapacidad_id = {id_incapacidad}")
        print(f"DEBUG REPO: Documentos RAW encontrados: {len(raw_docs)}")
        print(f"DEBUG REPO: Detalles RAW: {[dict(doc) for doc in raw_docs]}")
        
        # Limpiar cache de SQLAlchemy antes de consultar
        self.db.expire_all()
        
        docs_stmt = select(self.t_incapacidad_archivo).where(
            self.t_incapacidad_archivo.c.incapacidad_id == id_incapacidad
        )
        docs = self.db.execute(docs_stmt).mappings().all()
        print(f"DEBUG REPO: Documentos SQLAlchemy encontrados para incapacidad {id_incapacidad}: {len(docs)}")
        print(f"DEBUG REPO: Detalles SQLAlchemy: {[dict(doc) for doc in docs]}")
        result['documentos'] = [dict(doc) for doc in docs]
        
        return result

    def list_by_user(self, usuario_id: int, *, skip: int = 0, limit: int = 100) -> list[dict]:
        stmt = (
            select(self.t_incapacidad)
            .where(self.t_incapacidad.c.usuario_id == usuario_id)
            .offset(skip)
            .limit(limit)
            .order_by(self.t_incapacidad.c.fecha_registro.desc())
        )
        rows = self.db.execute(stmt).mappings().all()
        return [dict(r) for r in rows]

    def list_all(self, *, 
                 skip: int = 0, 
                 limit: int = 100, 
                 estado: Optional[int] = None,
                 tipo_incapacidad_id: Optional[int] = None,
                 usuario_id: Optional[int] = None,
                 fecha_inicio: Optional[datetime] = None,
                 fecha_final: Optional[datetime] = None) -> list[dict]:
        stmt = select(self.t_incapacidad)
        
        conditions = []
        if estado is not None:
            conditions.append(self.t_incapacidad.c.estado == estado)
        if tipo_incapacidad_id is not None:
            conditions.append(self.t_incapacidad.c.tipo_incapacidad_id == tipo_incapacidad_id)
        if usuario_id is not None:
            conditions.append(self.t_incapacidad.c.usuario_id == usuario_id)
        if fecha_inicio is not None:
            conditions.append(self.t_incapacidad.c.fecha_inicio >= fecha_inicio)
        if fecha_final is not None:
            conditions.append(self.t_incapacidad.c.fecha_final <= fecha_final)
            
        if conditions:
            stmt = stmt.where(and_(*conditions))
            
        stmt = stmt.offset(skip).limit(limit).order_by(self.t_incapacidad.c.fecha_registro.desc())
        rows = self.db.execute(stmt).mappings().all()
        return [dict(r) for r in rows]

    def list_all_with_details(self, *, 
                             skip: int = 0, 
                             limit: int = 100, 
                             estado: Optional[int] = None,
                             tipo_incapacidad_id: Optional[int] = None,
                             usuario_id: Optional[int] = None,
                             fecha_inicio: Optional[datetime] = None,
                             fecha_final: Optional[datetime] = None) -> list[dict]:
        """Lista incapacidades con información de usuario y tipo de incapacidad"""
        # Reflejar tablas adicionales
        self._metadata.reflect(bind=self.db.bind, only=["usuario", "tipo_incapacidad"])
        t_usuario = self._metadata.tables["usuario"]
        t_tipo_incapacidad = self._metadata.tables["tipo_incapacidad"]
        
        # Query con JOINs
        stmt = select(
            self.t_incapacidad,
            t_usuario.c.nombre_completo.label("usuario_nombre"),
            t_tipo_incapacidad.c.nombre.label("tipo_nombre")
        ).select_from(
            self.t_incapacidad
            .join(t_usuario, self.t_incapacidad.c.usuario_id == t_usuario.c.id_usuario)
            .join(t_tipo_incapacidad, self.t_incapacidad.c.tipo_incapacidad_id == t_tipo_incapacidad.c.id_tipo_incapacidad)
        )
        
        conditions = []
        if estado is not None:
            conditions.append(self.t_incapacidad.c.estado == estado)
        if tipo_incapacidad_id is not None:
            conditions.append(self.t_incapacidad.c.tipo_incapacidad_id == tipo_incapacidad_id)
        if usuario_id is not None:
            conditions.append(self.t_incapacidad.c.usuario_id == usuario_id)
        if fecha_inicio is not None:
            conditions.append(self.t_incapacidad.c.fecha_inicio >= fecha_inicio)
        if fecha_final is not None:
            conditions.append(self.t_incapacidad.c.fecha_final <= fecha_final)
            
        if conditions:
            stmt = stmt.where(and_(*conditions))
            
        stmt = stmt.offset(skip).limit(limit).order_by(self.t_incapacidad.c.fecha_registro.desc())
        rows = self.db.execute(stmt).mappings().all()
        
        # Combinar datos
        result = []
        for row in rows:
            inc_data = dict(row)
            # Agregar información de usuario y tipo
            usuario_nombre_val = inc_data.pop("usuario_nombre", None)
            tipo_nombre_val = inc_data.pop("tipo_nombre", None)
            
            # Mantener campo anidado para compatibilidad
            inc_data["usuario"] = {"nombre_completo": usuario_nombre_val}
            # Exponer nombre directamente a nivel raíz para el frontend
            inc_data["usuario_nombre"] = usuario_nombre_val
            
            # Agregar información del tipo de incapacidad
            inc_data["tipo_incapacidad"] = {"nombre": tipo_nombre_val}
            inc_data["tipo_nombre"] = tipo_nombre_val  # También exponer directamente
            
            # Mantener usuario_id como entero (no reemplazar) para cumplir schema
            result.append(inc_data)
            
        return result

    def update_estado(self, id_incapacidad: int, *, estado: int) -> bool:
        # Preservar fecha_registro: leer valor actual y no permitir que cambie
        current = self.get(id_incapacidad)
        stmt = (
            update(self.t_incapacidad)
            .where(self.t_incapacidad.c.id_incapacidad == id_incapacidad)
            .values(estado=estado, fecha_registro=current.get('fecha_registro') if current and 'fecha_registro' in current else None)
        )
        result = self.db.execute(stmt)
        self.db.commit()
        return result.rowcount > 0

    def bulk_update_estado(self, *, from_estado: int, to_estado: int) -> int:
        """Actualiza masivamente el estado de todas las incapacidades que tengan from_estado a to_estado.
        Retorna la cantidad de filas afectadas.
        """
        # En bulk no podemos leer cada fila aquí; asumimos que la columna no tiene ON UPDATE.
        # Si existiera, la mejor práctica sería deshabilitarlo a nivel de esquema. Aquí no tocamos fecha_registro.
        stmt = (
            update(self.t_incapacidad)
            .where(self.t_incapacidad.c.estado == from_estado)
            .values(estado=to_estado)
        )
        result = self.db.execute(stmt)
        self.db.commit()
        try:
            return int(getattr(result, 'rowcount', 0) or 0)
        except Exception:
            return 0

    def update_administrativo(self, id_incapacidad: int, *,
                              id_admin: Optional[int] = None,
                              valor_pago: Optional[Decimal] = None,
                              numero_radicado: Optional[str] = None,
                              fecha_radicado: Optional[datetime] = None,
                              fecha_pago: Optional[datetime] = None,
                              estado: Optional[int] = 12) -> bool:
        """Actualiza campos administrativos conforme a columnas reales de la tabla incapacidad.
        Columnas esperadas: id_admin, valor_pago, numero_radicado, fecha_radicado, fecha_pago, estado.
        """
        update_values: dict[str, Any] = {}
        if estado is not None:
            update_values['estado'] = estado
        if id_admin is not None:
            update_values['id_admin'] = id_admin
        if valor_pago is not None:
            update_values['valor_pago'] = valor_pago
        if numero_radicado is not None:
            update_values['numero_radicado'] = numero_radicado
        if fecha_radicado is not None:
            update_values['fecha_radicado'] = fecha_radicado
        if fecha_pago is not None:
            update_values['fecha_pago'] = fecha_pago

        # Filtrar solo por columnas existentes para evitar CompileError
        existing_cols = set(self.t_incapacidad.c.keys())
        filtered_values = {k: v for k, v in update_values.items() if k in existing_cols}

        # Preservar fecha_registro si existe
        current = self.get(id_incapacidad)
        if current and 'fecha_registro' in current and 'fecha_registro' in existing_cols:
            filtered_values['fecha_registro'] = current['fecha_registro']

        if not filtered_values:
            return True

        stmt = (
            update(self.t_incapacidad)
            .where(self.t_incapacidad.c.id_incapacidad == id_incapacidad)
            .values(**filtered_values)
        )
        result = self.db.execute(stmt)
        self.db.commit()
        return result.rowcount > 0

    def add_archivos(self, *, incapacidad_id: int, archivo_ids: Iterable[int], url_builder: Optional[callable[[int], str]] = None) -> list[dict]:
        inserted: list[dict] = []
        for archivo_id in archivo_ids:
            url = url_builder(archivo_id) if url_builder else f"/uploads/{archivo_id}"
            stmt = (
                insert(self.t_incapacidad_archivo)
                .values(
                    incapacidad_id=incapacidad_id,
                    archivo_id=archivo_id,
                    url_documento=url,
                )
                .returning(self.t_incapacidad_archivo)
            )
            row = self.db.execute(stmt).mappings().first()
            if row:
                inserted.append(dict(row))
        self.db.commit()
        return inserted

    def add_archivo_with_filename(self, *, incapacidad_id: int, archivo_id: int, filename: str) -> Optional[dict]:
        """Inserta un registro en incapacidad_archivo almacenando únicamente el nombre del archivo en url_documento.
        Compatible con MySQL/MariaDB (sin RETURNING): tras insertar se consulta el registro por PK.
        """
        insert_stmt = (
            insert(self.t_incapacidad_archivo)
            .values(
                incapacidad_id=incapacidad_id,
                archivo_id=archivo_id,
                url_documento=filename,
            )
        )
        result = self.db.execute(insert_stmt)
        self.db.commit()

        # Intentar recuperar usando la PK si está disponible
        try:
            last_id = getattr(result, "lastrowid", None)
        except Exception:
            last_id = None

        pk_cols = list(self.t_incapacidad_archivo.primary_key.columns)
        pk_col = pk_cols[0] if pk_cols else None

        if last_id and pk_col is not None:
            sel = select(self.t_incapacidad_archivo).where(pk_col == last_id)
            row = self.db.execute(sel).mappings().first()
            return dict(row) if row else None

        # Fallback: buscar por campos insertados, ordenando por PK descendente
        sel = (
            select(self.t_incapacidad_archivo)
            .where(
                (self.t_incapacidad_archivo.c.incapacidad_id == incapacidad_id)
                & (self.t_incapacidad_archivo.c.archivo_id == archivo_id)
                & (self.t_incapacidad_archivo.c.url_documento == filename)
            )
        )
        if pk_col is not None:
            sel = sel.order_by(pk_col.desc())
        row = self.db.execute(sel).mappings().first()
        return dict(row) if row else None

    def get_documentos_cumplimiento(self, incapacidad_id: int, tipo_incapacidad_id: int) -> List[dict]:
        """Obtiene el estado de cumplimiento de documentos requeridos"""
        # Obtener documentos requeridos por el tipo
        from app.repositories.relacion_repository import RelacionRepository
        rel_repo = RelacionRepository(self.db)
        requeridos = rel_repo.list_by_tipo_incapacidad(tipo_incapacidad_id=tipo_incapacidad_id)
        requeridos_ids = {rel.archivo_id for rel in requeridos}
        
        # Obtener documentos subidos
        docs_stmt = select(self.t_incapacidad_archivo).where(
            self.t_incapacidad_archivo.c.incapacidad_id == incapacidad_id
        )
        docs_subidos = self.db.execute(docs_stmt).mappings().all()
        subidos_ids = {doc['archivo_id'] for doc in docs_subidos}
        
        # Calcular cumplimiento
        cumplimiento = []
        for req_id in requeridos_ids:
            cumplimiento.append({
                'archivo_id': req_id,
                'requerido': True,
                'subido': req_id in subidos_ids,
                'completo': req_id in subidos_ids
            })
            
        return cumplimiento

    def update_formulario(self, id_incapacidad: int, *, 
                          fecha_inicio: Optional[datetime] = None,
                          fecha_final: Optional[datetime] = None,
                          dias: Optional[int] = None,
                          salario: Optional[Decimal] = None,
                          eps_afiliado_id: Optional[int] = None,
                          servicio_id: Optional[int] = None,
                          diagnostico_id: Optional[int] = None) -> bool:
        """Actualiza los datos del formulario de una incapacidad"""
        
        # Construir diccionario de valores a actualizar
        update_values = {}
        
        if fecha_inicio is not None:
            update_values['fecha_inicio'] = fecha_inicio
        if fecha_final is not None:
            update_values['fecha_final'] = fecha_final
        if dias is not None:
            update_values['dias'] = dias
        if salario is not None:
            update_values['salario'] = salario
        if eps_afiliado_id is not None:
            update_values['Eps_id'] = eps_afiliado_id
        if servicio_id is not None:
            update_values['servicio_id'] = servicio_id
        if diagnostico_id is not None:
            update_values['diagnostico_id'] = diagnostico_id
        
        # Si no hay valores para actualizar, retornar True
        if not update_values:
            return True
            
        # Filtrar por columnas existentes
        existing_cols = set(self.t_incapacidad.c.keys())
        filtered_values = {k: v for k, v in update_values.items() if k in existing_cols}
        
        if not filtered_values:
            return True
            
        # Preservar fecha_registro
        current = self.get(id_incapacidad)
        if current and 'fecha_registro' in current and 'fecha_registro' in existing_cols:
            filtered_values['fecha_registro'] = current['fecha_registro']

        stmt = (
            update(self.t_incapacidad)
            .where(self.t_incapacidad.c.id_incapacidad == id_incapacidad)
            .values(**filtered_values)
        )
        
        result = self.db.execute(stmt)
        self.db.commit()
        return result.rowcount > 0

    def update_mensaje_rechazo(self, id_incapacidad: int, mensaje_rechazo: str) -> bool:
        """Actualiza el mensaje de rechazo de una incapacidad"""
        # Preservar fecha_registro
        current = self.get(id_incapacidad)
        values = {'mensaje_rechazo': mensaje_rechazo}
        if current and 'fecha_registro' in current:
            values['fecha_registro'] = current['fecha_registro']
        stmt = (
            update(self.t_incapacidad)
            .where(self.t_incapacidad.c.id_incapacidad == id_incapacidad)
            .values(**values)
        )
        
        result = self.db.execute(stmt)
        self.db.commit()
        return result.rowcount > 0

    def delete_archivos_by_incapacidad(self, id_incapacidad: int) -> int:
        """Elimina registros de incapacidad_archivo asociados a la incapacidad."""
        stmt = (
            delete(self.t_incapacidad_archivo)
            .where(self.t_incapacidad_archivo.c.incapacidad_id == id_incapacidad)
        )
        result = self.db.execute(stmt)
        self.db.commit()
        return getattr(result, 'rowcount', 0) or 0

    def delete(self, id_incapacidad: int) -> bool:
        """Elimina una incapacidad (y sus archivos asociados)."""
        # Primero eliminar archivos asociados para respetar FK
        try:
            self.delete_archivos_by_incapacidad(id_incapacidad)
        except Exception:
            # Continuar aunque no existan
            pass

        stmt = (
            delete(self.t_incapacidad)
            .where(self.t_incapacidad.c.id_incapacidad == id_incapacidad)
        )
        result = self.db.execute(stmt)
        self.db.commit()
        return result.rowcount > 0

    def get_archivo_by_ids(self, incapacidad_id: int, archivo_id: int) -> Optional[dict]:
        """Obtiene un registro de incapacidad_archivo por incapacidad_id y archivo_id"""
        stmt = select(self.t_incapacidad_archivo).where(
            (self.t_incapacidad_archivo.c.incapacidad_id == incapacidad_id) &
            (self.t_incapacidad_archivo.c.archivo_id == archivo_id)
        )
        row = self.db.execute(stmt).mappings().first()
        return dict(row) if row else None

    def update_archivo_url(self, incapacidad_id: int, archivo_id: int, url_documento: str) -> bool:
        """Actualiza la URL del documento en incapacidad_archivo"""
        print(f"DEBUG UPDATE: Actualizando archivo - incapacidad_id: {incapacidad_id}, archivo_id: {archivo_id}")
        print(f"DEBUG UPDATE: Nueva URL: {url_documento}")
        
        # Verificar si existe el registro antes de actualizar
        existing = self.get_archivo_by_ids(incapacidad_id, archivo_id)
        print(f"DEBUG UPDATE: Registro existente: {existing}")
        
        stmt = (
            update(self.t_incapacidad_archivo)
            .where(
                (self.t_incapacidad_archivo.c.incapacidad_id == incapacidad_id) &
                (self.t_incapacidad_archivo.c.archivo_id == archivo_id)
            )
            .values(url_documento=url_documento)
        )
        result = self.db.execute(stmt)
        print(f"DEBUG UPDATE: Filas afectadas: {result.rowcount}")
        self.db.commit()
        
        # Verificar después de actualizar
        updated = self.get_archivo_by_ids(incapacidad_id, archivo_id)
        print(f"DEBUG UPDATE: Registro después de actualizar: {updated}")
        
        return result.rowcount > 0
