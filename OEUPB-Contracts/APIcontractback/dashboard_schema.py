# OEUPB-Contracts/APIcontractback/dashboard_schema.py
from pydantic import BaseModel
from typing import List

# --- DTOs de Salida (Responses) ---
class ResumenKpiResponseDto(BaseModel):
    total_egresados: int
    demora_promedio_meses: float
    satisfaccion_laboral_sobre_5: float
    tasa_empleabilidad: float

class SerieTiempoDto(BaseModel):
    cohorte: str
    tasa_momento_1: float
    tasa_momento_5: float

class TendenciasResponseDto(BaseModel):
    series: List[SerieTiempoDto]
