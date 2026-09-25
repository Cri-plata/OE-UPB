from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from infrastructure.database import get_db
from application.auth_service import require_roles
from presentation.errores import RESPUESTAS_PROTEGIDAS, ErrorResponse
from application.indicadores import (
    ETIQUETAS_MOMENTOS,
    Filtros,
    _mediciones,
    comparacion_momentos,
    conteo_respuestas,
    distribucion_programas,
    es_variable_analitica,
    preguntas_analiticas,
    recortar_etiqueta,
    resumen_laboral,
    satisfaccion_general,
    tendencias_por_programa,
)
from pydantic import BaseModel
from typing import Dict, List, Literal, Optional

router = APIRouter(prefix="/api/reportes", tags=["Reportes"], responses=RESPUESTAS_PROTEGIDAS)

class RangoSalarialResponse(BaseModel):
    minimo: float
    mediana: float
    maximo: float
    observaciones: int


class KpisResponse(BaseModel):
    total_egresados: int
    total_encuestados: int
    tasa_empleabilidad: float
    tasa_formalidad: Optional[float] = None
    tasa_informalidad: Optional[float] = None
    observaciones_formalidad: int
    promedio_salarial: float
    rango_salarial: Optional[RangoSalarialResponse] = None
    distribucion_estado_laboral: Dict[str, int]
    distribucion_programas: dict
    nivel_satisfaccion: dict


class FiltrosDisponiblesResponse(BaseModel):
    programas: List[str]
    anios: List[int]
    momentos: List[int]


class ComparacionProgramaResponse(BaseModel):
    programa: str
    pares: int
    suficiente: bool
    valor_inicial: Optional[float] = None
    valor_final: Optional[float] = None


class ComparacionResponse(BaseModel):
    momento_inicial: int
    momento_final: int
    indicador: str
    minimo_pares: int
    programas: List[ComparacionProgramaResponse]


class ChartDatasetResponse(BaseModel):
    label: str
    data: List[Optional[float]]
    borderColor: Optional[str] = None
    backgroundColor: Optional[str] = None
    borderWidth: Optional[int] = None
    pointBackgroundColor: Optional[str] = None
    pointBorderColor: Optional[str] = None
    pointBorderWidth: Optional[int] = None
    pointRadius: Optional[int] = None
    pointHoverRadius: Optional[int] = None
    fill: Optional[bool] = None
    tension: Optional[float] = None
    spanGaps: Optional[bool] = None


class TendenciasResponse(BaseModel):
    labels: List[str]
    datasets: List[ChartDatasetResponse]


class ExploradorInitResponse(BaseModel):
    preguntas: List[str]
    programas: List[str]
    anios: List[int]


class ExploradorResponse(BaseModel):
    labels: List[str]
    valores: List[int]


COLORES_TENDENCIAS = [
    {"border": "#E63946", "bg": "rgba(230, 57, 70, 0.2)"},
    {"border": "#1D3557", "bg": "rgba(29, 53, 87, 0.2)"},
    {"border": "#2A9D8F", "bg": "rgba(42, 157, 143, 0.2)"},
    {"border": "#F4A261", "bg": "rgba(244, 162, 97, 0.2)"},
    {"border": "#9B5DE5", "bg": "rgba(155, 93, 229, 0.2)"}
]

def validar_momento_opcional(momento: Optional[int]) -> None:
    if momento is not None and momento not in (0, 1, 5):
        raise HTTPException(status_code=422, detail="El momento debe ser 0, 1 o 5")


@router.get("/filtros", response_model=FiltrosDisponiblesResponse)
def filtros_disponibles(db: Session = Depends(get_db), current_user: dict = Depends(require_roles("Coordinador_Sede"))):
    mediciones = _mediciones(db, current_user.get("sede_id"))
    return {
        "programas": sorted({programa for _, programa in mediciones if programa}),
        "anios": sorted({medicion.anio for medicion, _ in mediciones if medicion.anio}),
        "momentos": sorted({medicion.momento for medicion, _ in mediciones}),
    }


@router.get("/general", response_model=KpisResponse)
def get_reporte_general(
    programas: List[str] = Query(default_factory=list, description="Programas (multiselección)"),
    anios: List[int] = Query(default_factory=list, description="Cohortes (multiselección)"),
    momento: Optional[int] = Query(None, description="Momento 0, 1 o 5"),
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_roles("Coordinador_Sede")),
):
    validar_momento_opcional(momento)
    sede_id = current_user.get("sede_id")
    filtros = Filtros(programas, anios, momento)
    distribucion = distribucion_programas(db, sede_id, filtros)
    mediciones = _mediciones(db, sede_id, filtros, incluir_anonimas=True)
    laboral = resumen_laboral(mediciones)
    satisfaccion = {
        categoria: round(celda["suma"] / celda["count"], 1) if celda["count"] > 0 else 0
        for categoria, celda in satisfaccion_general(db, sede_id, filtros).items()
    }
    return {
        "total_egresados": sum(distribucion.values()),
        "total_encuestados": len(mediciones),
        "tasa_empleabilidad": laboral["tasa_empleabilidad"],
        "tasa_formalidad": laboral["tasa_formalidad"],
        "tasa_informalidad": laboral["tasa_informalidad"],
        "observaciones_formalidad": laboral["observaciones_formalidad"],
        "promedio_salarial": laboral["promedio_salarial"],
        "rango_salarial": laboral["rango_salarial"],
        "distribucion_estado_laboral": laboral["distribucion_estado_laboral"],
        "distribucion_programas": distribucion,
        "nivel_satisfaccion": satisfaccion,
    }


@router.get("/tendencias", response_model=TendenciasResponse)
def get_tendencias(
    indicador: Literal["empleabilidad", "salario", "satisfaccion"] = "empleabilidad",
    programas: List[str] = Query(default_factory=list, description="Programas (multiselección)"),
    anios: List[int] = Query(default_factory=list, description="Cohortes (multiselección)"),
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_roles("Coordinador_Sede")),
):
    datasets = []
    for idx, (programa, celdas) in enumerate(tendencias_por_programa(db, current_user.get("sede_id"), indicador, Filtros(programas, anios))):
        color = COLORES_TENDENCIAS[idx % len(COLORES_TENDENCIAS)]
        datasets.append({
            "label": programa,
            "data": [valor for valor, _ in celdas],
            "borderColor": color["border"],
            "backgroundColor": color["bg"],
            "borderWidth": 3,
            "pointBackgroundColor": "#ffffff",
            "pointBorderColor": color["border"],
            "pointBorderWidth": 2,
            "pointRadius": 5,
            "pointHoverRadius": 7,
            "fill": True,
            "tension": 0.4,
            "spanGaps": True
        })
    return {"labels": list(ETIQUETAS_MOMENTOS), "datasets": datasets}


@router.get(
    "/comparacion",
    response_model=ComparacionResponse,
    responses={422: {"model": ErrorResponse, "description": "Momentos o indicador inválidos"}},
)
def get_comparacion(
    momento_inicial: int = Query(..., description="Momento 0, 1 o 5"),
    momento_final: int = Query(..., description="Momento 0, 1 o 5, distinto del inicial"),
    indicador: Literal["empleabilidad", "salario"] = "empleabilidad",
    programas: List[str] = Query(default_factory=list, description="Programas (multiselección)"),
    anios: List[int] = Query(default_factory=list, description="Cohortes (multiselección)"),
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_roles("Coordinador_Sede")),
):
    validar_momento_opcional(momento_inicial)
    validar_momento_opcional(momento_final)
    if momento_inicial == momento_final:
        raise HTTPException(status_code=422, detail="Seleccione dos momentos distintos")
    return comparacion_momentos(
        db, current_user.get("sede_id"), momento_inicial, momento_final, indicador, Filtros(programas, anios)
    )


@router.get("/explorador/init", response_model=ExploradorInitResponse)
def explorador_init(db: Session = Depends(get_db), current_user: dict = Depends(require_roles("Coordinador_Sede"))):
    preguntas, programas, anios = preguntas_analiticas(db, current_user.get("sede_id"))
    return {"preguntas": preguntas, "programas": programas, "anios": anios}


@router.get(
    "/explorador",
    response_model=ExploradorResponse,
    responses={422: {"model": ErrorResponse, "description": "La variable no pertenece al catálogo analítico autorizado o los filtros son inválidos"}},
)
def explorador_data(
    pregunta: str = Query(..., max_length=300),
    momento: Optional[int] = Query(None, description="Momento 0, 1 o 5"),
    programa: Optional[str] = Query(None, max_length=150),
    anio: Optional[int] = Query(None, ge=1900, le=2200),
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_roles("Coordinador_Sede"))
):
    validar_momento_opcional(momento)
    if not es_variable_analitica(pregunta):
        raise HTTPException(status_code=422, detail="La variable solicitada no pertenece al catálogo analítico autorizado")
    conteo, _ = conteo_respuestas(db, current_user.get("sede_id"), pregunta, momento, programa or None, anio)
    ordenados = sorted(conteo.items(), key=lambda item: item[1], reverse=True)
    return {
        "labels": [recortar_etiqueta(valor) for valor, _ in ordenados],
        "valores": [cantidad for _, cantidad in ordenados],
    }
