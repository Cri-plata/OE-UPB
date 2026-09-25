from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from infrastructure.database import get_db
from application.auth_service import (
    authenticate_user,
    credencial_temporal_vencida,
    create_access_token,
    get_password_hash,
    get_token_user,
    verify_password,
)
from domain.models import Usuario
from pydantic import BaseModel
from typing import Literal

router = APIRouter(prefix="/api/auth", tags=["Autenticación"])

class LoginRequest(BaseModel):
    correoInstitucional: str
    contrasena: str


class UsuarioLoginResponse(BaseModel):
    id: int
    nombre: str
    correo: str
    rol: Literal["Admin_CTIC", "Coordinador_Sede", "Usuario_Consulta"]
    sedeId: int | None
    debeCambiarContrasena: bool


class LoginResponse(BaseModel):
    token: str
    usuario: UsuarioLoginResponse


class CambioContrasenaTemporalRequest(BaseModel):
    nuevaContrasena: str
    confirmarContrasena: str


def construir_respuesta_login(user: Usuario) -> dict:
    access_token = create_access_token(
        data={
            "sub": user.correo,
            "rol": user.rol,
            "sede_id": user.sede_id,
            "debe_cambiar_contrasena": user.debe_cambiar_contrasena,
            "usuario_id": user.id,
            "version_autorizacion": user.version_autorizacion,
        }
    )
    return {
        "token": access_token,
        "usuario": {
            "id": user.id,
            "nombre": user.nombre,
            "correo": user.correo,
            "rol": user.rol,
            "sedeId": user.sede_id,
            "debeCambiarContrasena": user.debe_cambiar_contrasena,
        },
    }

@router.post(
    "/login",
    response_model=LoginResponse,
    responses={
        401: {"description": "Correo o contraseña incorrectos"},
    },
)
def login(request: LoginRequest, db: Session = Depends(get_db)):
    user = authenticate_user(db, request.correoInstitucional, request.contrasena)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Correo o contraseña incorrectos",
            headers={"WWW-Authenticate": "Bearer"},
        )
    if credencial_temporal_vencida(user):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={
                "codigo": "CREDENCIAL_TEMPORAL_VENCIDA",
                "mensaje": "La credencial temporal venció; solicita una nueva al administrador",
            },
        )

    return construir_respuesta_login(user)


@router.post(
    "/cambiar-contrasena-temporal",
    response_model=LoginResponse,
    responses={
        400: {"description": "La contraseña no cumple la política"},
        401: {"description": "Token inválido o vencido"},
        409: {"description": "La cuenta no requiere cambio inicial"},
    },
)
def cambiar_contrasena_temporal(
    request: CambioContrasenaTemporalRequest,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_token_user),
):
    user = db.query(Usuario).filter(
        Usuario.correo == current_user.get("correo")
    ).first()
    if user is None:
        raise HTTPException(status_code=401, detail="Usuario no encontrado")
    if not user.activo or current_user.get("version_autorizacion") != user.version_autorizacion:
        raise HTTPException(status_code=401, detail="La sesión fue revocada")
    if not user.debe_cambiar_contrasena:
        raise HTTPException(
            status_code=409,
            detail="La cuenta no requiere cambio de contraseña temporal",
        )
    if credencial_temporal_vencida(user):
        raise HTTPException(status_code=401, detail="La credencial temporal venció")
    if request.nuevaContrasena != request.confirmarContrasena:
        raise HTTPException(status_code=400, detail="Las contraseñas no coinciden")

    nueva = request.nuevaContrasena
    if verify_password(nueva, user.contrasena_hash):
        raise HTTPException(status_code=400, detail="La contraseña personal debe ser diferente de la temporal")
    if (
        len(nueva) < 10
        or not any(c.isupper() for c in nueva)
        or not any(c.islower() for c in nueva)
        or not any(c.isdigit() for c in nueva)
    ):
        raise HTTPException(
            status_code=400,
            detail=(
                "La contraseña debe tener al menos 10 caracteres, una mayúscula, "
                "una minúscula y un número"
            ),
        )

    user.contrasena_hash = get_password_hash(nueva)
    user.debe_cambiar_contrasena = False
    user.credencial_temporal_expira_en = None
    user.version_autorizacion += 1
    db.commit()
    db.refresh(user)
    return construir_respuesta_login(user)
