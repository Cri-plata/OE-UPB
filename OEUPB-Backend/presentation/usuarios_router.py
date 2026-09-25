from typing import List, Literal, Optional
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, Field, field_validator
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from application.auth_service import (
    INITIAL_CREDENTIAL_MODE,
    expiracion_credencial_inicial,
    expiracion_credencial_recuperacion,
    generar_contrasena_temporal,
    generar_credencial_inicial,
    get_current_user,
    get_password_hash,
)
from application.documentos import normalizar_documento_obligatorio
from presentation.errores import RESPUESTAS_PROTEGIDAS, errores
from application.programas import clave_programa, claves_programas
from domain.models import AuditoriaCuenta, Egresado, Medicion, Sede, Usuario
from infrastructure.database import get_db

router = APIRouter(prefix="/api/usuarios", tags=["Usuarios"], responses=RESPUESTAS_PROTEGIDAS)

PERMISOS_CONSULTA = {"ver_reporte_general", "ver_tendencias", "ver_explorador", "ver_publicaciones"}
ETIQUETAS = {"Rector", "Profesor", "Administrativo"}


PATRON_CORREO_INSTITUCIONAL = r"^[^@\s]+@[Uu][Pp][Bb]\.[Ee][Dd][Uu]\.[Cc][Oo]$"


class UsuarioCreateRequest(BaseModel):
    nombre: str
    # El patrón documenta RN-19 en el contrato; el backend lo vuelve a validar (400) sin distinguir mayúsculas.
    correo: str = Field(json_schema_extra={"pattern": PATRON_CORREO_INSTITUCIONAL, "format": "email"})
    numero_documento: str = Field(min_length=5, max_length=40, description="Se normaliza: sin espacios, puntos ni guiones, en mayúsculas")
    rol: Literal["Coordinador_Sede", "Usuario_Consulta"]
    sede_id: Optional[int] = None
    etiqueta: Optional[Literal["Rector", "Profesor", "Administrativo"]] = None
    permisos: List[Literal["ver_reporte_general", "ver_tendencias", "ver_explorador", "ver_publicaciones"]] = Field(default_factory=list)
    programas: List[str] = Field(default_factory=list)

    @field_validator("numero_documento")
    @classmethod
    def normalizar_documento(cls, valor: str) -> str:
        return normalizar_documento_obligatorio(valor)


class UsuarioUpdateRequest(BaseModel):
    nombre: Optional[str] = None
    sede_id: Optional[int] = None
    etiqueta: Optional[Literal["Rector", "Profesor", "Administrativo"]] = None
    permisos: Optional[List[Literal["ver_reporte_general", "ver_tendencias", "ver_explorador", "ver_publicaciones"]]] = None
    programas: Optional[List[str]] = None


class UsuarioResponse(BaseModel):
    id: int
    nombre: str
    correo: str
    rol: Literal["Admin_CTIC", "Coordinador_Sede", "Usuario_Consulta"]
    sede_id: Optional[int] = None
    debe_cambiar_contrasena: bool
    credencial_temporal_expira_en: Optional[datetime] = None
    activo: bool
    version_autorizacion: int
    etiqueta: Optional[Literal["Rector", "Profesor", "Administrativo"]] = None
    permisos: List[Literal["ver_reporte_general", "ver_tendencias", "ver_explorador", "ver_publicaciones"]]
    programas: List[str]
    programas_sin_datos: List[str] = Field(default_factory=list, description="Programas asignados que ya no se observan en cargas de la sede")


class UsuarioCreateResponse(UsuarioResponse):
    contrasena_temporal: str
    modo_credencial: Literal["documento", "random"]


class ReemisionCredencialRequest(BaseModel):
    motivo: str = Field(min_length=10, max_length=500)


class ReemisionCredencialResponse(BaseModel):
    usuario: UsuarioResponse
    contrasena_temporal: str
    credencial_temporal_expira_en: datetime


class MotivoRequest(BaseModel):
    motivo: str = Field(min_length=10, max_length=500)


class MensajeResponse(BaseModel):
    mensaje: str


def _serializar(usuario: Usuario, observados: Optional[set[str]] = None) -> dict:
    programas = list(usuario.programas or [])
    return {
        "id": usuario.id, "nombre": usuario.nombre, "correo": usuario.correo,
        "rol": usuario.rol, "sede_id": usuario.sede_id,
        "debe_cambiar_contrasena": usuario.debe_cambiar_contrasena,
        "credencial_temporal_expira_en": usuario.credencial_temporal_expira_en,
        "activo": usuario.activo, "version_autorizacion": usuario.version_autorizacion,
        "etiqueta": usuario.etiqueta, "permisos": list(usuario.permisos or []),
        "programas": programas,
        "programas_sin_datos": [p for p in programas if observados is not None and clave_programa(p) not in observados],
    }


def _validar_administracion(actor: dict, objetivo: Usuario) -> None:
    permitido = (
        actor.get("rol") == "Admin_CTIC" and objetivo.rol == "Coordinador_Sede"
    ) or (
        actor.get("rol") == "Coordinador_Sede"
        and objetivo.rol == "Usuario_Consulta"
        and objetivo.sede_id == actor.get("sede_id")
    )
    if not permitido:
        raise HTTPException(status_code=403, detail="No puedes administrar esta cuenta")


def _programas_sede(db: Session, sede_id: int) -> set[str]:
    filas = (
        db.query(Egresado.programa)
        .join(Medicion, Medicion.egresado_documento == Egresado.numero_documento)
        .filter(Medicion.sede_id == sede_id, Egresado.programa.isnot(None))
        .distinct().all()
    )
    return {fila[0] for fila in filas if fila[0]}


def _validar_alcance_consulta(db: Session, sede_id: int, etiqueta: Optional[str], permisos: List[str], programas: List[str], actuales: Optional[List[str]] = None) -> List[str]:
    """Valida el alcance y devuelve los programas con el nombre observado en la sede.

    La comparación usa la clave normalizada (PRG-01). Un programa ya asignado que
    dejó de observarse se conserva para no bloquear la edición de la cuenta.
    """
    if etiqueta not in ETIQUETAS:
        raise HTTPException(status_code=422, detail="Etiqueta de perfil inválida")
    invalidos = set(permisos) - PERMISOS_CONSULTA
    if invalidos:
        raise HTTPException(status_code=422, detail=f"Permisos inválidos: {sorted(invalidos)}")
    observados = {clave_programa(p): p for p in _programas_sede(db, sede_id)}
    asignados = {clave_programa(p): p for p in actuales or []}
    resultado, no_disponibles = [], []
    for programa in programas:
        clave = clave_programa(programa)
        if clave in observados:
            resultado.append(observados[clave])
        elif clave in asignados:
            resultado.append(asignados[clave])
        else:
            no_disponibles.append(programa)
    if no_disponibles:
        raise HTTPException(status_code=422, detail=f"Programas fuera del alcance de la sede: {sorted(no_disponibles)}")
    return sorted(set(resultado))


def _validar_sede(db: Session, sede_id: Optional[int]) -> int:
    if sede_id is None:
        raise HTTPException(status_code=422, detail="La sede es obligatoria")
    existe = db.query(Sede).filter(Sede.id == sede_id, Sede.activa.is_(True)).first()
    if existe is None:
        raise HTTPException(status_code=422, detail="La sede no existe o está inactiva")
    return sede_id


@router.get("/programas-asignables", response_model=List[str])
def programas_asignables(db: Session = Depends(get_db), current_user: dict = Depends(get_current_user)):
    if current_user.get("rol") != "Coordinador_Sede" or current_user.get("sede_id") is None:
        raise HTTPException(status_code=403, detail="Solo un coordinador puede consultar programas asignables")
    return sorted(_programas_sede(db, current_user["sede_id"]))


@router.get("/", response_model=List[UsuarioResponse])
def get_usuarios(incluir_inactivos: bool = Query(True), db: Session = Depends(get_db), current_user: dict = Depends(get_current_user)):
    if current_user.get("rol") == "Admin_CTIC":
        query = db.query(Usuario).filter(Usuario.rol == "Coordinador_Sede")
    elif current_user.get("rol") == "Coordinador_Sede":
        query = db.query(Usuario).filter(Usuario.rol == "Usuario_Consulta", Usuario.sede_id == current_user.get("sede_id"))
    else:
        raise HTTPException(status_code=403, detail="No puedes administrar usuarios")
    if not incluir_inactivos:
        query = query.filter(Usuario.activo.is_(True))
    observados = claves_programas(_programas_sede(db, current_user["sede_id"])) if current_user.get("rol") == "Coordinador_Sede" else None
    return [_serializar(usuario, observados) for usuario in query.order_by(Usuario.nombre).all()]


@router.post("/", response_model=UsuarioCreateResponse, responses=errores(400, d400="Correo fuera de @upb.edu.co o ya registrado"))
def create_usuario(user_data: UsuarioCreateRequest, db: Session = Depends(get_db), current_user: dict = Depends(get_current_user)):
    correo = user_data.correo.strip().lower()
    if not correo.endswith("@upb.edu.co"):
        raise HTTPException(status_code=400, detail="El correo debe ser @upb.edu.co")
    if db.query(Usuario).filter(Usuario.correo == correo).first():
        raise HTTPException(status_code=400, detail="El correo ya está registrado en el sistema")

    if current_user.get("rol") == "Admin_CTIC":
        if user_data.rol != "Coordinador_Sede":
            raise HTTPException(status_code=403, detail="CTIC solo puede crear coordinadores")
        sede_id = _validar_sede(db, user_data.sede_id)
        etiqueta, permisos, programas = None, [], []
    elif current_user.get("rol") == "Coordinador_Sede":
        if user_data.rol != "Usuario_Consulta":
            raise HTTPException(status_code=403, detail="El coordinador solo puede crear usuarios de consulta")
        sede_id = current_user.get("sede_id")
        if sede_id is None:
            raise HTTPException(status_code=403, detail="El coordinador no tiene sede asignada")
        if user_data.sede_id is not None and user_data.sede_id != sede_id:
            raise HTTPException(status_code=403, detail="Solo puedes crear usuarios de tu propia sede")
        programas = _validar_alcance_consulta(db, sede_id, user_data.etiqueta, user_data.permisos, user_data.programas)
        etiqueta, permisos = user_data.etiqueta, sorted(set(user_data.permisos))
    else:
        raise HTTPException(status_code=403, detail="No puedes crear usuarios")

    temporal = generar_credencial_inicial(user_data.numero_documento)
    expira_en = expiracion_credencial_inicial()
    usuario = Usuario(
        nombre=user_data.nombre.strip(), correo=correo,
        contrasena_hash=get_password_hash(temporal), rol=user_data.rol,
        sede_id=sede_id, debe_cambiar_contrasena=True, activo=True,
        credencial_temporal_expira_en=expira_en,
        version_autorizacion=1, etiqueta=etiqueta, permisos=permisos, programas=programas,
    )
    db.add(usuario); db.commit(); db.refresh(usuario)
    return {**_serializar(usuario), "contrasena_temporal": temporal, "modo_credencial": INITIAL_CREDENTIAL_MODE}


@router.post("/{usuario_id}/regenerar-credencial-temporal", response_model=ReemisionCredencialResponse, responses=errores(404, 409))
def regenerar_credencial_temporal(
    usuario_id: int,
    solicitud: ReemisionCredencialRequest,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    usuario = db.query(Usuario).filter(Usuario.id == usuario_id).first()
    if usuario is None:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    _validar_administracion(current_user, usuario)
    if not usuario.activo:
        raise HTTPException(status_code=409, detail="Reactiva la cuenta antes de recuperar su acceso")
    actor = db.query(Usuario).filter(Usuario.correo == current_user.get("correo")).first()
    if actor is None:
        raise HTTPException(status_code=401, detail="Usuario autenticado no encontrado")

    temporal = generar_contrasena_temporal()
    expira_en = expiracion_credencial_recuperacion()
    usuario.contrasena_hash = get_password_hash(temporal)
    usuario.debe_cambiar_contrasena = True
    usuario.credencial_temporal_expira_en = expira_en
    usuario.version_autorizacion += 1
    db.add(AuditoriaCuenta(
        accion="REEMISION_CREDENCIAL",
        actor_id=actor.id,
        actor_correo=actor.correo,
        objetivo_id=usuario.id,
        objetivo_correo=usuario.correo,
        objetivo_rol=usuario.rol,
        sede_id=usuario.sede_id,
        motivo=solicitud.motivo.strip(),
    ))
    db.commit()
    db.refresh(usuario)
    return {
        "usuario": _serializar(usuario),
        "contrasena_temporal": temporal,
        "credencial_temporal_expira_en": expira_en,
    }


@router.patch("/{usuario_id}", response_model=UsuarioResponse, responses=errores(404))
def actualizar_usuario(usuario_id: int, cambios: UsuarioUpdateRequest, db: Session = Depends(get_db), current_user: dict = Depends(get_current_user)):
    usuario = db.query(Usuario).filter(Usuario.id == usuario_id).first()
    if usuario is None:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    _validar_administracion(current_user, usuario)
    if cambios.nombre is not None:
        usuario.nombre = cambios.nombre.strip()
    if usuario.rol == "Coordinador_Sede" and cambios.sede_id is not None:
        usuario.sede_id = _validar_sede(db, cambios.sede_id)
    if usuario.rol == "Usuario_Consulta":
        etiqueta = cambios.etiqueta if cambios.etiqueta is not None else usuario.etiqueta
        permisos = cambios.permisos if cambios.permisos is not None else list(usuario.permisos or [])
        programas = cambios.programas if cambios.programas is not None else list(usuario.programas or [])
        programas = _validar_alcance_consulta(db, usuario.sede_id, etiqueta, permisos, programas, actuales=list(usuario.programas or []))
        usuario.etiqueta, usuario.permisos, usuario.programas = etiqueta, sorted(set(permisos)), programas
    elif any(value is not None for value in (cambios.etiqueta, cambios.permisos, cambios.programas)):
        raise HTTPException(status_code=422, detail="Los coordinadores no usan permisos de consulta")
    usuario.version_autorizacion += 1
    db.commit(); db.refresh(usuario)
    return _serializar(usuario)


def _cambiar_estado(usuario_id: int, activo: bool, db: Session, current_user: dict) -> dict:
    usuario = db.query(Usuario).filter(Usuario.id == usuario_id).first()
    if usuario is None:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    _validar_administracion(current_user, usuario)
    usuario.activo = activo
    usuario.version_autorizacion += 1
    db.commit(); db.refresh(usuario)
    return _serializar(usuario)


@router.post("/{usuario_id}/desactivar", response_model=UsuarioResponse, responses=errores(404))
def desactivar_usuario(usuario_id: int, db: Session = Depends(get_db), current_user: dict = Depends(get_current_user)):
    return _cambiar_estado(usuario_id, False, db, current_user)


@router.post("/{usuario_id}/reactivar", response_model=UsuarioResponse, responses=errores(404))
def reactivar_usuario(usuario_id: int, db: Session = Depends(get_db), current_user: dict = Depends(get_current_user)):
    return _cambiar_estado(usuario_id, True, db, current_user)


@router.delete("/{usuario_id}", response_model=UsuarioResponse, responses=errores(404), deprecated=True)
def delete_usuario(usuario_id: int, db: Session = Depends(get_db), current_user: dict = Depends(get_current_user)):
    """Alias obsoleto de `POST /{usuario_id}/desactivar`; se conserva por compatibilidad (API-02)."""
    return _cambiar_estado(usuario_id, False, db, current_user)


@router.delete("/{usuario_id}/permanente", response_model=MensajeResponse, responses=errores(404, 409, d409="La cuenta sigue activa o conserva relaciones"))
def borrar_usuario_permanentemente(usuario_id: int, solicitud: MotivoRequest, db: Session = Depends(get_db), current_user: dict = Depends(get_current_user)):
    usuario = db.query(Usuario).filter(Usuario.id == usuario_id).first()
    if usuario is None:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    _validar_administracion(current_user, usuario)
    if usuario.activo:
        raise HTTPException(status_code=409, detail="Desactiva la cuenta antes del borrado físico")
    actor = db.query(Usuario).filter(Usuario.correo == current_user.get("correo")).first()
    if actor is None:
        raise HTTPException(status_code=401, detail="Usuario autenticado no encontrado")
    db.add(AuditoriaCuenta(
        accion="BORRADO_FISICO", actor_id=actor.id, actor_correo=actor.correo,
        objetivo_id=usuario.id, objetivo_correo=usuario.correo, objetivo_rol=usuario.rol,
        sede_id=usuario.sede_id, motivo=solicitud.motivo.strip(),
    ))
    db.delete(usuario)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=409,
            detail="La cuenta conserva relaciones y no puede borrarse físicamente",
        )
    return {"mensaje": "Usuario eliminado físicamente y evento auditado"}
