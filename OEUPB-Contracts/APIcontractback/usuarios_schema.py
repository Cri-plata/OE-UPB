# OEUPB-Contracts/APIcontractback/usuarios_schema.py
from pydantic import BaseModel, EmailStr
from typing import Optional, List, Literal
from .auth_schema import UsuarioDto

# --- DTOs de Entrada (Requests) ---
class CreateUsuarioRequestDto(BaseModel):
    nombre: str
    correo: EmailStr
    rol: Literal['Admin_CTIC', 'Coordinador_Sede', 'Directivo']
    sede_id: Optional[int] = None

# --- DTOs de Salida (Responses) ---
class GetUsuariosResponseDto(BaseModel):
    usuarios: List[UsuarioDto]
    total_registros: int
