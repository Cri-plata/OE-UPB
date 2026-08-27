from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from infrastructure.database import get_db
from application.auth_service import authenticate_user, create_access_token
from pydantic import BaseModel

router = APIRouter(prefix="/api/auth", tags=["Autenticación"])

class LoginRequest(BaseModel):
    correoInstitucional: str
    contrasena: str

class LoginResponse(BaseModel):
    token: str
    usuario: dict

@router.post("/login", response_model=LoginResponse)
def login(request: LoginRequest, db: Session = Depends(get_db)):
    user = authenticate_user(db, request.correoInstitucional, request.contrasena)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Correo o contraseña incorrectos",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Generar Token
    access_token = create_access_token(
        data={"sub": user.correo, "rol": user.rol, "sede_id": user.sede_id}
    )
    
    return {
        "token": access_token,
        "usuario": {
            "id": user.id,
            "nombre": user.nombre,
            "correo": user.correo,
            "rol": user.rol,
            "sedeId": user.sede_id
        }
    }
