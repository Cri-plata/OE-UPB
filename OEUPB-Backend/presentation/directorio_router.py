from datetime import datetime
from io import BytesIO
from typing import Any, Dict, List, Optional

import pandas as pd
from fastapi import APIRouter, Depends, HTTPException, Query, Response
from pydantic import BaseModel, Field, field_validator
from sqlalchemy import or_
from sqlalchemy.orm import Session

from application.auth_service import require_roles
from presentation.errores import RESPUESTAS_PROTEGIDAS, errores
from application.documentos import normalizar_documento, normalizar_documento_obligatorio
from application.programas import limpiar_nombre_programa
from application.indicadores import ETIQUETAS_ESTADO, clave_salario, estado_laboral
from domain.models import AuditoriaEgresado, Egresado, EgresadoSede, Medicion
from infrastructure.database import get_db

router = APIRouter(prefix="/api/directorio", tags=["Directorio"], responses=RESPUESTAS_PROTEGIDAS)


class DirectorioItem(BaseModel):
    documento: str
    nombre_completo: str
    programa: Optional[str]
    fecha_grado: str
    encuestas: str


class DirectorioResponse(BaseModel):
    total: int
    page: int
    limit: int
    data: List[DirectorioItem]


class EncuestaPerfilResponse(BaseModel):
    momento: int
    anio: int
    empleabilidad: Any
    salario: Any
    respuestas_completas: Dict[str, Any]


class PerfilEgresadoResponse(BaseModel):
    documento: str
    nombre_completo: str
    programa: Optional[str]
    fecha_grado: str
    encuestas: List[EncuestaPerfilResponse]


class EgresadoManualRequest(BaseModel):
    numero_documento: str = Field(min_length=5, max_length=40, description="Se normaliza: sin espacios, puntos ni guiones, en mayúsculas")
    primer_nombre: str = Field(min_length=1, max_length=100)
    primer_apellido: Optional[str] = Field(default=None, max_length=100)
    programa: str = Field(min_length=1, max_length=150)
    fecha_grado: Optional[str] = None
    motivo: str = Field(min_length=5, max_length=500)

    @field_validator("numero_documento")
    @classmethod
    def normalizar_documento(cls, valor: str) -> str:
        return normalizar_documento_obligatorio(valor)


class EgresadoManualUpdate(BaseModel):
    primer_nombre: Optional[str] = Field(default=None, min_length=1, max_length=100)
    primer_apellido: Optional[str] = Field(default=None, max_length=100)
    programa: Optional[str] = Field(default=None, min_length=1, max_length=150)
    fecha_grado: Optional[str] = None
    motivo: str = Field(min_length=5, max_length=500)


class EliminarEgresadoRequest(BaseModel):
    motivo: str = Field(min_length=5, max_length=500)


class OperacionEgresadoResponse(BaseModel):
    documento: str
    estado: str


def _documentos_visibles(db: Session, sede_id: int):
    medidos = db.query(Medicion.egresado_documento).filter(Medicion.sede_id == sede_id)
    manuales = db.query(EgresadoSede.egresado_documento).filter(EgresadoSede.sede_id == sede_id)
    return medidos.union(manuales)


def _query_directorio(db: Session, sede_id: int, q: Optional[str], programa: Optional[str]):
    query = db.query(Egresado).filter(Egresado.numero_documento.in_(_documentos_visibles(db, sede_id)))
    if q:
        termino = f"%{q}%"
        query = query.filter(or_(Egresado.numero_documento.like(termino), Egresado.primer_nombre.like(termino), Egresado.primer_apellido.like(termino)))
    if programa:
        query = query.filter(Egresado.programa == programa)
    return query.order_by(Egresado.primer_apellido, Egresado.primer_nombre)


def _parse_fecha(value: Optional[str]):
    if not value:
        return None
    try:
        return datetime.strptime(value, "%Y-%m-%d")
    except ValueError as exc:
        raise HTTPException(status_code=422, detail="fecha_grado debe usar YYYY-MM-DD") from exc


def _auditar(db: Session, user: dict, documento: str, accion: str, cambios: dict, motivo: str):
    db.add(AuditoriaEgresado(accion=accion, actor_id=user["usuario_id"], actor_correo=user["correo"], sede_id=user["sede_id"], egresado_documento=documento, cambios=cambios, motivo=motivo))


def _item(db: Session, egresado: Egresado, sede_id: int) -> dict:
    momentos = db.query(Medicion.momento, Medicion.anio).filter(Medicion.egresado_documento == egresado.numero_documento, Medicion.sede_id == sede_id).all()
    historial = [f"M{m.momento} ({m.anio if m.anio else 'N/A'})" for m in momentos]
    return {"documento": egresado.numero_documento, "nombre_completo": f"{egresado.primer_nombre} {egresado.primer_apellido or ''}".strip(), "programa": egresado.programa, "fecha_grado": egresado.fecha_grado.strftime("%Y-%m-%d") if egresado.fecha_grado else "N/A", "encuestas": ", ".join(historial) if historial else "Ninguna"}


@router.get("/tabla", response_model=DirectorioResponse)
def obtener_directorio(q: Optional[str] = None, programa: Optional[str] = None, page: int = Query(1, ge=1), limit: int = Query(50, ge=1, le=100), db: Session = Depends(get_db), current_user: dict = Depends(require_roles("Coordinador_Sede"))):
    query = _query_directorio(db, current_user["sede_id"], q, programa)
    total = query.count()
    return {"total": total, "page": page, "limit": limit, "data": [_item(db, e, current_user["sede_id"]) for e in query.offset((page - 1) * limit).limit(limit).all()]}


@router.get("/programas", response_model=List[str])
def obtener_programas_unicos(db: Session = Depends(get_db), current_user: dict = Depends(require_roles("Coordinador_Sede"))):
    filas = db.query(Egresado.programa).filter(Egresado.programa.is_not(None), Egresado.numero_documento.in_(_documentos_visibles(db, current_user["sede_id"]))).distinct().all()
    return sorted(p[0] for p in filas if p[0])


@router.get("/perfil/{documento}", response_model=PerfilEgresadoResponse, responses=errores(404, d404="Egresado no encontrado en su sede"))
def obtener_perfil_egresado(documento: str, db: Session = Depends(get_db), current_user: dict = Depends(require_roles("Coordinador_Sede"))):
    documento = normalizar_documento(documento) or ""
    egresado = db.query(Egresado).filter(Egresado.numero_documento == documento, Egresado.numero_documento.in_(_documentos_visibles(db, current_user["sede_id"]))).first()
    if not egresado:
        raise HTTPException(status_code=404, detail="Egresado no encontrado en su sede")
    mediciones = db.query(Medicion).filter(Medicion.egresado_documento == documento, Medicion.sede_id == current_user["sede_id"]).order_by(Medicion.momento).all()
    encuestas = []
    for medicion in mediciones:
        respuestas = medicion.respuestas or {}
        encuestas.append({"momento": medicion.momento, "anio": medicion.anio, "empleabilidad": ETIQUETAS_ESTADO.get(estado_laboral(respuestas), "No informa"), "salario": str(respuestas.get(clave_salario(respuestas) or "") or "No informa"), "respuestas_completas": respuestas})
    return {"documento": documento, "nombre_completo": f"{egresado.primer_nombre} {egresado.primer_apellido or ''}".strip(), "programa": egresado.programa, "fecha_grado": egresado.fecha_grado.strftime("%Y-%m-%d") if egresado.fecha_grado else "N/A", "encuestas": encuestas}


@router.post("/egresados", response_model=OperacionEgresadoResponse, status_code=201, responses=errores(409, d409="El documento ya está registrado"))
def crear_egresado(payload: EgresadoManualRequest, db: Session = Depends(get_db), current_user: dict = Depends(require_roles("Coordinador_Sede"))):
    documento = payload.numero_documento
    if db.get(Egresado, documento):
        raise HTTPException(status_code=409, detail="El documento ya está registrado; si pertenece a su sede, use la edición del directorio")
    egresado = Egresado(numero_documento=documento, primer_nombre=payload.primer_nombre.strip(), primer_apellido=(payload.primer_apellido or "").strip() or None, programa=limpiar_nombre_programa(payload.programa), fecha_grado=_parse_fecha(payload.fecha_grado))
    db.add(egresado)
    db.flush()
    db.add(EgresadoSede(egresado_documento=documento, sede_id=current_user["sede_id"], creado_por_id=current_user["usuario_id"]))
    _auditar(db, current_user, documento, "crear", {"despues": payload.model_dump(exclude={"motivo"})}, payload.motivo)
    db.commit()
    return {"documento": documento, "estado": "creado"}


def _egresado_editable(db: Session, documento: str, sede_id: int) -> Egresado:
    egresado = db.query(Egresado).filter(Egresado.numero_documento == documento, Egresado.numero_documento.in_(_documentos_visibles(db, sede_id))).first()
    if not egresado:
        raise HTTPException(status_code=404, detail="Egresado no encontrado en su sede")
    if db.query(Medicion.id).filter(Medicion.egresado_documento == documento, Medicion.sede_id != sede_id).first() or db.query(EgresadoSede.id).filter(EgresadoSede.egresado_documento == documento, EgresadoSede.sede_id != sede_id).first():
        raise HTTPException(status_code=409, detail="El registro está vinculado a más de una sede; solo puede modificarse mediante cargas de cada sede")
    return egresado


@router.patch("/egresados/{documento}", response_model=OperacionEgresadoResponse, responses=errores(404, 409, d409="El egresado está vinculado a más de una sede"))
def editar_egresado(documento: str, payload: EgresadoManualUpdate, db: Session = Depends(get_db), current_user: dict = Depends(require_roles("Coordinador_Sede"))):
    documento = normalizar_documento(documento) or ""
    egresado = _egresado_editable(db, documento, current_user["sede_id"])
    antes = {"primer_nombre": egresado.primer_nombre, "primer_apellido": egresado.primer_apellido, "programa": egresado.programa, "fecha_grado": egresado.fecha_grado.isoformat() if egresado.fecha_grado else None}
    cambios = payload.model_dump(exclude_none=True, exclude={"motivo"})
    if "fecha_grado" in cambios:
        cambios["fecha_grado"] = _parse_fecha(cambios["fecha_grado"])
    for campo, valor in cambios.items():
        if campo == "programa":
            valor = limpiar_nombre_programa(valor)
        setattr(egresado, campo, valor.strip() if isinstance(valor, str) else valor)
    _auditar(db, current_user, documento, "editar", {"antes": antes, "despues": {k: v.isoformat() if isinstance(v, datetime) else v for k, v in cambios.items()}}, payload.motivo)
    db.commit()
    return {"documento": documento, "estado": "actualizado"}


@router.delete("/egresados/{documento}", response_model=OperacionEgresadoResponse, responses=errores(404, 409, d409="El egresado tiene mediciones o está vinculado a otra sede"))
def eliminar_egresado(documento: str, payload: EliminarEgresadoRequest, db: Session = Depends(get_db), current_user: dict = Depends(require_roles("Coordinador_Sede"))):
    documento = normalizar_documento(documento) or ""
    egresado = _egresado_editable(db, documento, current_user["sede_id"])
    if db.query(Medicion.id).filter(Medicion.egresado_documento == documento).first():
        raise HTTPException(status_code=409, detail="No se elimina un egresado con mediciones; retire primero la carga fuente")
    snapshot = {"primer_nombre": egresado.primer_nombre, "primer_apellido": egresado.primer_apellido, "programa": egresado.programa, "fecha_grado": egresado.fecha_grado.isoformat() if egresado.fecha_grado else None}
    db.query(EgresadoSede).filter(EgresadoSede.egresado_documento == documento, EgresadoSede.sede_id == current_user["sede_id"]).delete()
    db.delete(egresado)
    _auditar(db, current_user, documento, "eliminar", {"antes": snapshot}, payload.motivo)
    db.commit()
    return {"documento": documento, "estado": "eliminado"}


@router.get("/exportar.xlsx", response_class=Response, responses={200: {"content": {"application/vnd.openxmlformats-officedocument.spreadsheetml.sheet": {"schema": {"type": "string", "format": "binary"}}}, "description": "Directorio Excel"}})
def exportar_directorio(q: Optional[str] = None, programa: Optional[str] = None, db: Session = Depends(get_db), current_user: dict = Depends(require_roles("Coordinador_Sede"))):
    filas = _query_directorio(db, current_user["sede_id"], q, programa).all()
    datos = [{"Documento": e.numero_documento, "Nombre": f"{e.primer_nombre} {e.primer_apellido or ''}".strip(), "Programa": e.programa, "Fecha de grado": e.fecha_grado.date() if e.fecha_grado else None} for e in filas]
    buffer = BytesIO()
    pd.DataFrame(datos, columns=["Documento", "Nombre", "Programa", "Fecha de grado"]).to_excel(buffer, index=False, sheet_name="Directorio")
    return Response(content=buffer.getvalue(), media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", headers={"Content-Disposition": 'attachment; filename="directorio-egresados.xlsx"'})
