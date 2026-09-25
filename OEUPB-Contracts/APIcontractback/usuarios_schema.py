# OEUPB-Contracts/APIcontractback/usuarios_schema.py
from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List, Literal
from .auth_schema import UsuarioDto

# --- DTOs de Entrada (Requests) ---
class CreateUsuarioRequestDto(BaseModel):
    nombre: str
    correo: EmailStr
    numero_documento: str = Field(min_length=6, max_length=20, pattern=r"^[0-9]+$")
    rol: Literal['Coordinador_Sede', 'Usuario_Consulta']
    sede_id: Optional[int] = None
    etiqueta: Optional[Literal['Rector', 'Profesor', 'Administrativo']] = None
    permisos: List[Literal['ver_reporte_general', 'ver_tendencias', 'ver_explorador', 'ver_publicaciones']] = Field(default_factory=list)
    programas: List[str] = Field(default_factory=list)

# --- DTOs de Salida (Responses) ---
class GetUsuariosResponseDto(BaseModel):
    usuarios: List[UsuarioDto]
    total_registros: int
