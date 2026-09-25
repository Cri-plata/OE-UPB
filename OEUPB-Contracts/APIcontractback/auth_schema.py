# OEUPB-Contracts/APIcontractback/auth_schema.py
from pydantic import BaseModel, EmailStr
from typing import Optional, Literal

# --- DTOs de Entrada (Requests) ---
class LoginRequestDto(BaseModel):
    correo_institucional: EmailStr
    contrasena: str

# --- Entidades Core transferidas ---
class UsuarioDto(BaseModel):
    id: int
    nombre: str
    correo: EmailStr
    rol: Literal['Admin_CTIC', 'Coordinador_Sede', 'Usuario_Consulta']
    sede_id: Optional[int] = None

# --- DTOs de Salida (Responses) ---
class LoginResponseDto(BaseModel):
    token: str
    usuario: UsuarioDto
