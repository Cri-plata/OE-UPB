from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from infrastructure.database import get_db
from application.auth_service import require_roles
from application.indicadores import (
    ETIQUETAS_MOMENTOS,
    conteo_respuestas,
    distribucion_programas,
    es_variable_analitica,
    extraer_salario,
    preguntas_analiticas,
    recortar_etiqueta,
    satisfaccion_general,
    tendencias_por_programa,
)
from domain.models import Medicion
from pydantic import BaseModel
from typing import List, Literal, Optional
from application.medicion_policy import seleccionar_intentos

router = APIRouter(prefix="/api/reportes", tags=["Reportes"])

class KpisResponse(BaseModel):
    total_egresados: int
    tasa_empleabilidad: float
    promedio_salarial: float
    distribucion_programas: dict
    nivel_satisfaccion: dict


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

@router.get("/general", response_model=KpisResponse)
def get_reporte_general(db: Session = Depends(get_db), current_user: dict = Depends(require_roles("Coordinador_Sede"))):
    
    sede_id = current_user.get("sede_id")
    distribucion = distribucion_programas(db, sede_id)
    mediciones = seleccionar_intentos(db.query(Medicion).filter(Medicion.sede_id == sede_id).all())

    empleados_count = 0
    respuestas_validas = 0
    suma_salarios = 0
    salarios_validos = 0

    for m in mediciones:
        resp = m.respuestas if m.respuestas else {}

        # 1. Empleabilidad (Pregunta 22)
        key_empleo = next((k for k in resp.keys() if "realiza alguna actividad remunerada?" in k.lower()), None)
        if key_empleo:
            val = str(resp[key_empleo]).strip().upper()
            if val in ["SI", "SÍ", "NO"]:
                respuestas_validas += 1
                if val in ["SI", "SÍ"]:
                    empleados_count += 1

        # 2. Salario (Pregunta 55)
        key_salario = next((k for k in resp.keys() if "ingreso mensual" in k.lower() and "smlv" in k.lower() and "realiza" in k.lower()), None)
        if key_salario and resp[key_salario]:
            val_sal = extraer_salario(str(resp[key_salario]))
            if val_sal is not None:
                suma_salarios += val_sal
                salarios_validos += 1

    tasa_empleabilidad = round((empleados_count / respuestas_validas) * 100, 1) if respuestas_validas > 0 else 0
    promedio_salarial = round(suma_salarios / salarios_validos, 1) if salarios_validos > 0 else 0
    satisfaccion = {
        categoria: round(celda["suma"] / celda["count"], 1) if celda["count"] > 0 else 0
        for categoria, celda in satisfaccion_general(db, sede_id).items()
    }

    return {
        "total_egresados": sum(distribucion.values()),
        "tasa_empleabilidad": tasa_empleabilidad,
        "promedio_salarial": promedio_salarial,
        "distribucion_programas": distribucion,
        "nivel_satisfaccion": satisfaccion
    }

@router.get("/tendencias", response_model=TendenciasResponse)
def get_tendencias(indicador: Literal["empleabilidad", "salario", "satisfaccion"] = "empleabilidad", db: Session = Depends(get_db), current_user: dict = Depends(require_roles("Coordinador_Sede"))):
    datasets = []
    for idx, (programa, celdas) in enumerate(tendencias_por_programa(db, current_user.get("sede_id"), indicador)):
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


@router.get("/explorador/init", response_model=ExploradorInitResponse)
def explorador_init(db: Session = Depends(get_db), current_user: dict = Depends(require_roles("Coordinador_Sede"))):
    preguntas, programas, anios = preguntas_analiticas(db, current_user.get("sede_id"))
    return {"preguntas": preguntas, "programas": programas, "anios": anios}


@router.get(
    "/explorador",
    response_model=ExploradorResponse,
    responses={422: {"description": "La variable no pertenece al catálogo analítico autorizado o los filtros son inválidos"}},
)
def explorador_data(
    pregunta: str = Query(..., max_length=300),
    momento: Optional[int] = Query(None, description="Momento 0, 1 o 5"),
    programa: Optional[str] = Query(None, max_length=150),
    anio: Optional[int] = Query(None, ge=1900, le=2200),
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_roles("Coordinador_Sede"))
):
    if momento is not None and momento not in (0, 1, 5):
        raise HTTPException(status_code=422, detail="El momento debe ser 0, 1 o 5")
    if not es_variable_analitica(pregunta):
        raise HTTPException(status_code=422, detail="La variable solicitada no pertenece al catálogo analítico autorizado")
    conteo, _ = conteo_respuestas(db, current_user.get("sede_id"), pregunta, momento, programa or None, anio)
    ordenados = sorted(conteo.items(), key=lambda item: item[1], reverse=True)
    return {
        "labels": [recortar_etiqueta(valor) for valor, _ in ordenados],
        "valores": [cantidad for _, cantidad in ordenados],
    }
