import jwt
from datetime import datetime, timedelta, timezone
import bcrypt
import os
import secrets
import string
from sqlalchemy.orm import Session
from domain.models import Usuario
from infrastructure.database import get_db
from dotenv import load_dotenv

load_dotenv()
APP_ENV = os.getenv("APP_ENV", "development").strip().lower()
ALGORITHM = os.getenv("ALGORITHM", "HS256")
INITIAL_CREDENTIAL_MODE = os.getenv("INITIAL_CREDENTIAL_MODE", "documento").strip().lower()
TEMPORARY_CREDENTIAL_EXPIRE_HOURS = int(os.getenv("TEMPORARY_CREDENTIAL_EXPIRE_HOURS", "24"))
RECOVERY_CREDENTIAL_EXPIRE_MINUTES = int(os.getenv("RECOVERY_CREDENTIAL_EXPIRE_MINUTES", "60"))


def validate_security_settings(app_env: str, secret_key: str | None, credential_mode: str) -> str:
    no_productivo = app_env in {"development", "test"}
    if credential_mode not in {"documento", "random"}:
        raise RuntimeError("INITIAL_CREDENTIAL_MODE debe ser 'documento' o 'random'")
    if not no_productivo:
        if not secret_key or len(secret_key) < 32 or secret_key in {"clave_por_defecto", "replace_with_a_long_random_value"}:
            raise RuntimeError("SECRET_KEY debe configurarse con al menos 32 caracteres fuera de desarrollo")
        if credential_mode != "random":
            raise RuntimeError("INITIAL_CREDENTIAL_MODE=random es obligatorio fuera de desarrollo")
    return secret_key or "oeupb-development-only-secret"


SECRET_KEY = validate_security_settings(APP_ENV, os.getenv("SECRET_KEY"), INITIAL_CREDENTIAL_MODE)
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "120"))


def generar_contrasena_temporal() -> str:
    caracteres = string.ascii_letters + string.digits + "!@#$%"
    partes = [
        secrets.choice(string.ascii_uppercase),
        secrets.choice(string.ascii_lowercase),
        secrets.choice(string.digits),
        secrets.choice("!@#$%"),
    ]
    partes.extend(secrets.choice(caracteres) for _ in range(10))
    secrets.SystemRandom().shuffle(partes)
    return "".join(partes)


def generar_credencial_inicial(numero_documento: str) -> str:
    return numero_documento if INITIAL_CREDENTIAL_MODE == "documento" else generar_contrasena_temporal()


def expiracion_credencial_inicial() -> datetime:
    return datetime.now(timezone.utc).replace(tzinfo=None) + timedelta(hours=TEMPORARY_CREDENTIAL_EXPIRE_HOURS)


def expiracion_credencial_recuperacion() -> datetime:
    return datetime.now(timezone.utc).replace(tzinfo=None) + timedelta(minutes=RECOVERY_CREDENTIAL_EXPIRE_MINUTES)


def credencial_temporal_vencida(user: Usuario) -> bool:
    return bool(
        user.debe_cambiar_contrasena
        and user.credencial_temporal_expira_en
        and user.credencial_temporal_expira_en <= datetime.now(timezone.utc).replace(tzinfo=None)
    )

def verify_password(plain_password: str, hashed_password: str) -> bool:
    password_bytes = plain_password.encode('utf-8')
    hash_bytes = hashed_password.encode('utf-8')
    return bcrypt.checkpw(password_bytes, hash_bytes)

def get_password_hash(password: str) -> str:
    pwd_bytes = password.encode('utf-8')
    salt = bcrypt.gensalt()
    hashed_password = bcrypt.hashpw(pwd_bytes, salt)
    return hashed_password.decode('utf-8')

def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def authenticate_user(db: Session, correo: str, contrasena: str):
    user = db.query(Usuario).filter(Usuario.correo == correo).first()
    if not user or not user.activo:
        return False
    if not verify_password(contrasena, user.contrasena_hash):
        return False
    return user


from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from fastapi import Depends, HTTPException, status
from pydantic import BaseModel

bearer_scheme = HTTPBearer(auto_error=False)

def get_token_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="No se pudo validar las credenciales",
        headers={"WWW-Authenticate": "Bearer"},
    )
    if credentials is None or credentials.scheme.lower() != "bearer":
        raise credentials_exception

    token = credentials.credentials
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        correo: str = payload.get("sub")
        rol: str = payload.get("rol")
        sede_id: int = payload.get("sede_id")
        usuario_id: int = payload.get("usuario_id")
        version_autorizacion: int = payload.get("version_autorizacion")
        debe_cambiar_contrasena: bool = payload.get("debe_cambiar_contrasena", False)
        if correo is None:
            raise credentials_exception
        return {
            "correo": correo,
            "rol": rol,
            "sede_id": sede_id,
            "usuario_id": usuario_id,
            "version_autorizacion": version_autorizacion,
            "debe_cambiar_contrasena": debe_cambiar_contrasena,
        }
    except jwt.PyJWTError:
        raise credentials_exception


def get_current_user(
    current_user: dict = Depends(get_token_user),
    db: Session = Depends(get_db),
):
    user = db.query(Usuario).filter(Usuario.correo == current_user.get("correo")).first()
    if user is None or not user.activo:
        raise HTTPException(status_code=401, detail="La cuenta está inactiva o ya no existe")
    if current_user.get("version_autorizacion") != user.version_autorizacion:
        raise HTTPException(status_code=401, detail="La autorización de la sesión fue revocada")
    if current_user.get("debe_cambiar_contrasena"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={
                "codigo": "CAMBIO_CONTRASENA_REQUERIDO",
                "mensaje": "Debes cambiar la contraseña temporal antes de continuar",
            },
        )
    return {
        "usuario_id": user.id,
        "correo": user.correo,
        "rol": user.rol,
        "sede_id": user.sede_id,
        "permisos": list(user.permisos or []),
        "programas": list(user.programas or []),
        "version_autorizacion": user.version_autorizacion,
        "debe_cambiar_contrasena": user.debe_cambiar_contrasena,
    }


def require_roles(*roles: str):
    def dependency(current_user: dict = Depends(get_current_user)):
        if current_user.get("rol") not in roles:
            raise HTTPException(status_code=403, detail="No tienes permisos para esta operación")
        return current_user

    return dependency
