# OEUPB-Contracts/APIcontractback/carga_schema.py
from pydantic import BaseModel
from typing import List, Literal

# --- DTOs Anidados ---
class FilaErrorDto(BaseModel):
    fila: int
    cedula: str
    motivo: str  # Ej: 'Cédula duplicada', 'Cédula vacía'

# --- DTOs de Salida (Responses) ---
class UploadExcelResponseDto(BaseModel):
    filas_cargadas: int
    filas_con_error: int
    detalles_errores: List[FilaErrorDto]
