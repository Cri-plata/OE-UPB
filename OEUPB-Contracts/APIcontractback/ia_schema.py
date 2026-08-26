# OEUPB-Contracts/APIcontractback/ia_schema.py
from pydantic import BaseModel
from typing import List, Literal

# --- DTOs de Salida (Responses) ---
class RiesgoDesempleoResponseDto(BaseModel):
    cohorte: str
    programa: str
    probabilidad_desempleo: float
    nivel_alerta: Literal['Alta', 'Media', 'Baja']

class HabilidadDto(BaseModel):
    nombre_habilidad: str
    frecuencia_porcentaje: float

class HabilidadesNLPResponseDto(BaseModel):
    habilidades: List[HabilidadDto]
