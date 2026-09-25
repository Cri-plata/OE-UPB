from datetime import datetime, timezone
from typing import Literal

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field, model_validator
from sqlalchemy.orm import Session

from application.auth_service import get_current_user, require_roles
from domain.models import Egresado, Medicion, PublicacionGrafica, Sede
from infrastructure.database import get_db


router = APIRouter(prefix="/api/publicaciones", tags=["Publicaciones"])

PERMISOS_POR_ORIGEN = {
    "reporte_general": "ver_reporte_general",
    "tendencias": "ver_tendencias",
    "explorador": "ver_explorador",
}


class DefinicionGrafica(BaseModel):
    origen: Literal["reporte_general", "tendencias", "explorador"]
    tipo_visualizacion: Literal["bar", "line", "pie", "doughnut"]
    indicador: str | None = Field(default=None, max_length=100)
    pregunta: str | None = Field(default=None, max_length=300)
    momento: Literal[0, 1, 5] | None = None
    programa: str | None = Field(default=None, max_length=150)
    anio: int | None = Field(default=None, ge=1900, le=2200)


class DatasetGrafica(BaseModel):
    label: str = Field(max_length=150)
    data: list[float | None] = Field(min_length=1, max_length=100)
    backgroundColor: str | list[str] | None = None
    borderColor: str | None = None


class MetricasGrafica(BaseModel):
    labels: list[str] = Field(min_length=1, max_length=100)
    datasets: list[DatasetGrafica] = Field(min_length=1, max_length=20)

    @model_validator(mode="after")
    def validar_dimensiones(self):
        if any(len(etiqueta) > 200 for etiqueta in self.labels):
            raise ValueError("Las etiquetas de la gráfica no pueden superar 200 caracteres")
        if any(len(dataset.data) != len(self.labels) for dataset in self.datasets):
            raise ValueError("Cada serie debe contener un valor por etiqueta")
        return self


class PublicacionCreate(BaseModel):
    grafica_key: str = Field(pattern=r"^[a-z0-9_\-]+$", min_length=3, max_length=100)
    titulo: str = Field(min_length=3, max_length=180)
    programas: list[str] = Field(min_length=1, max_length=100)
    definicion: DefinicionGrafica
    metricas: MetricasGrafica
    aprobada_privacidad: Literal[True]


class PublicacionResponse(BaseModel):
    id: int
    grafica_key: str
    titulo: str
    sede_id: int
    sede_nombre: str
    programas: list[str]
    permiso_requerido: str
    definicion: DefinicionGrafica
    metricas: MetricasGrafica
    version: int
    estado: str
    aprobada_privacidad: bool
    fecha_publicacion: datetime
    fecha_retiro: datetime | None


def _ahora() -> datetime:
    return datetime.now(timezone.utc).replace(tzinfo=None)


def _serializar(publicacion: PublicacionGrafica, sede_nombre: str) -> dict:
    return {
        "id": publicacion.id,
        "grafica_key": publicacion.grafica_key,
        "titulo": publicacion.titulo,
        "sede_id": publicacion.sede_id,
        "sede_nombre": sede_nombre,
        "programas": list(publicacion.programas or []),
        "permiso_requerido": publicacion.permiso_requerido,
        "definicion": publicacion.definicion,
        "metricas": publicacion.metricas,
        "version": publicacion.version,
        "estado": publicacion.estado,
        "aprobada_privacidad": publicacion.aprobada_privacidad,
        "fecha_publicacion": publicacion.fecha_publicacion,
        "fecha_retiro": publicacion.fecha_retiro,
    }


def _programas_de_sede(db: Session, sede_id: int) -> set[str]:
    filas = (
        db.query(Egresado.programa)
        .join(Medicion, Medicion.egresado_documento == Egresado.numero_documento)
        .filter(Medicion.sede_id == sede_id, Egresado.programa.isnot(None))
        .distinct()
        .all()
    )
    return {programa for (programa,) in filas if programa}


@router.post("/", response_model=PublicacionResponse, status_code=status.HTTP_201_CREATED)
def publicar_grafica(
    payload: PublicacionCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_roles("Coordinador_Sede")),
):
    sede_id = current_user.get("sede_id")
    if not sede_id:
        raise HTTPException(status_code=403, detail="El coordinador no tiene una sede asignada")
    programas = list(dict.fromkeys(programa.strip() for programa in payload.programas if programa.strip()))
    invalidos = set(programas) - _programas_de_sede(db, sede_id)
    if not programas or invalidos:
        raise HTTPException(
            status_code=422,
            detail=f"Programas fuera del alcance de la sede: {', '.join(sorted(invalidos))}",
        )

    anteriores = (
        db.query(PublicacionGrafica)
        .filter(
            PublicacionGrafica.sede_id == sede_id,
            PublicacionGrafica.grafica_key == payload.grafica_key,
        )
        .order_by(PublicacionGrafica.version.desc())
        .all()
    )
    ahora = _ahora()
    for anterior in anteriores:
        if anterior.estado == "publicada":
            anterior.estado = "reemplazada"
            anterior.fecha_retiro = ahora
            anterior.retirado_por_id = current_user["usuario_id"]

    publicacion = PublicacionGrafica(
        grafica_key=payload.grafica_key,
        titulo=payload.titulo.strip(),
        sede_id=sede_id,
        coordinador_id=current_user["usuario_id"],
        coordinador_correo=current_user["correo"],
        programas=programas,
        permiso_requerido=PERMISOS_POR_ORIGEN[payload.definicion.origen],
        definicion=payload.definicion.model_dump(exclude_none=True),
        metricas=payload.metricas.model_dump(exclude_none=True),
        version=(anteriores[0].version + 1) if anteriores else 1,
        aprobada_privacidad=True,
        estado="publicada",
        fecha_creacion=ahora,
        fecha_publicacion=ahora,
    )
    db.add(publicacion)
    db.commit()
    db.refresh(publicacion)
    sede = db.query(Sede).filter(Sede.id == sede_id).one()
    return _serializar(publicacion, sede.nombre)


@router.delete("/{publicacion_id}", response_model=PublicacionResponse)
def retirar_publicacion(
    publicacion_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_roles("Coordinador_Sede")),
):
    publicacion = db.query(PublicacionGrafica).filter(PublicacionGrafica.id == publicacion_id).first()
    if publicacion is None:
        raise HTTPException(status_code=404, detail="Publicación no encontrada")
    if publicacion.sede_id != current_user.get("sede_id") or publicacion.coordinador_id != current_user.get("usuario_id"):
        raise HTTPException(status_code=403, detail="Solo el coordinador propietario puede retirar esta publicación")
    if publicacion.estado != "publicada":
        raise HTTPException(status_code=409, detail="La publicación ya no está activa")
    publicacion.estado = "retirada"
    publicacion.fecha_retiro = _ahora()
    publicacion.retirado_por_id = current_user["usuario_id"]
    db.commit()
    db.refresh(publicacion)
    sede = db.query(Sede).filter(Sede.id == publicacion.sede_id).one()
    return _serializar(publicacion, sede.nombre)


@router.get("/mias", response_model=list[PublicacionResponse])
def listar_publicaciones_propias(
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_roles("Coordinador_Sede")),
):
    filas = (
        db.query(PublicacionGrafica, Sede.nombre)
        .join(Sede, Sede.id == PublicacionGrafica.sede_id)
        .filter(
            PublicacionGrafica.sede_id == current_user.get("sede_id"),
            PublicacionGrafica.coordinador_id == current_user.get("usuario_id"),
            PublicacionGrafica.estado == "publicada",
        )
        .order_by(PublicacionGrafica.fecha_publicacion.desc())
        .all()
    )
    return [_serializar(publicacion, sede_nombre) for publicacion, sede_nombre in filas]


@router.get("/", response_model=list[PublicacionResponse])
def listar_publicaciones_autorizadas(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    rol = current_user.get("rol")
    if rol not in {"Coordinador_Sede", "Usuario_Consulta"}:
        raise HTTPException(status_code=403, detail="No tienes permisos para consultar publicaciones")

    query = (
        db.query(PublicacionGrafica, Sede.nombre)
        .join(Sede, Sede.id == PublicacionGrafica.sede_id)
        .filter(PublicacionGrafica.estado == "publicada")
    )
    if rol == "Coordinador_Sede":
        query = query.filter(PublicacionGrafica.sede_id != current_user.get("sede_id"))
    else:
        permisos = set(current_user.get("permisos") or [])
        programas = set(current_user.get("programas") or [])
        if "ver_publicaciones" not in permisos or not programas:
            return []
        query = query.filter(PublicacionGrafica.permiso_requerido.in_(permisos))

    filas = query.order_by(PublicacionGrafica.fecha_publicacion.desc()).all()
    if rol == "Usuario_Consulta":
        filas = [
            fila for fila in filas
            if programas.intersection(set(fila[0].programas or []))
        ]
    return [_serializar(publicacion, sede_nombre) for publicacion, sede_nombre in filas]
