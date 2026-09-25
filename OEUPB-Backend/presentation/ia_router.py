"""
Router de IA - Endpoint /api/ia/habilidades-demandadas
=======================================================
Módulo desacoplado del resto del backend.
Consulta las respuestas JSON de la tabla mediciones y ejecuta el pipeline
de análisis de habilidades sin almacenar texto crudo más allá del procesamiento.
"""

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List, Optional, Set

from infrastructure.database import get_db
from domain.models import Medicion
from application.ia_service import (
    analizar_habilidades_demandadas,
    generar_reglas_asociacion,
    extraer_habilidades_por_respuesta,
)

router = APIRouter(prefix="/api/ia", tags=["Inteligencia Artificial"])


# ─────────────────────────────────────────────────────────────────────────────
# Modelos de respuesta (Pydantic)
# ─────────────────────────────────────────────────────────────────────────────
class ReglaAsociacionItem(BaseModel):
    si_menciona: str
    tambien_menciona: str
    ocurrencias: int
    soporte: float
    confianza: float
    lift: float


class ReglasAsociacionResponse(BaseModel):
    total_respuestas: int
    transacciones_validas: int
    transacciones_insuficientes: int
    total_reglas: int
    reglas: List[ReglaAsociacionItem]


class HabilidadReconocida(BaseModel):
    habilidad: str
    tipo: str
    menciones: int


class CandidataEmergente(BaseModel):
    termino: str
    score_tfidf: float
    frecuencia_documentos: int


class EstadisticasAnalisis(BaseModel):
    total_respuestas_analizadas: int
    respuestas_con_habilidad: int
    respuestas_sin_habilidad: int


class HabilidadesDemandadasResponse(BaseModel):
    habilidades_reconocidas: List[HabilidadReconocida]
    candidatas_emergentes: List[CandidataEmergente]
    estadisticas: EstadisticasAnalisis


# ─────────────────────────────────────────────────────────────────────────────
# Utilidad: extraer textos libres relevantes de preguntas abiertas auténticas
# ─────────────────────────────────────────────────────────────────────────────
# Patrones para identificar preguntas abiertas en el instrumento de egresados UPB / SNIES
_OPEN_PATTERNS = [
    "describa brevemente la principal tarea",
    "tarea que usted realiza",
    "aspecto a mejorar",
    "aspectos a mejorar",
    "qué le faltó",
    "qué le hizo falta",
    "sugerencia",
    "recomendación",
    "recomendacion",
    "observación",
    "observacion",
    "comentario",
    "curso",
    "seminario",
    "(otro)",
]

# Patrones para excluir preguntas de opción múltiple fija o metadatos
_EXCLUDE_PATTERNS = [
    "canal de b",
    "dificultad a la hora",
    "razón para recomendar",
    "razon para recomendar",
    "razón para no recomendar",
    "razon para no recomendar",
    "opciones de formación",
    "opciones de formacion",
    "lugar de residencia",
    "tipo de contrato",
    "sector está",
    "sector esta",
    "sector se",
    "factor",
    "smlv",
    "ingreso mensual",
    "cine ",
    "formas de trabajo",
]


def _extraer_textos_libres(respuestas_json: dict) -> List[str]:
    """
    Dado el diccionario JSON de una medición (respuestas_completas),
    extrae los textos libres de preguntas abiertas (tareas laborales, aspectos
    a mejorar, campos de especificación 'Otro', cursos o sugerencias).

    Filtra explícitamente opciones cerradas de selección única para evitar
    ruido estadístico en el análisis de PLN.
    """
    if not respuestas_json or not isinstance(respuestas_json, dict):
        return []

    textos = []
    for key, val in respuestas_json.items():
        if val is None or not isinstance(val, str):
            continue

        val_strip = val.strip()
        if len(val_strip) < 5:
            continue

        key_lower = key.lower()

        # Descartar preguntas que son de opción múltiple cerrada conocida
        if any(exc in key_lower for exc in _EXCLUDE_PATTERNS):
            continue

        # Extraer si coincide con preguntas abiertas reconocidas
        if any(pat in key_lower for pat in _OPEN_PATTERNS):
            textos.append(val_strip)

    return textos


# ─────────────────────────────────────────────────────────────────────────────
# Endpoints de IA
# ─────────────────────────────────────────────────────────────────────────────
@router.get("/habilidades-demandadas", response_model=HabilidadesDemandadasResponse)
def get_habilidades_demandadas(
    momento: Optional[int] = Query(None, description="Filtrar por momento de encuesta (0, 1 o 5)"),
    anio: Optional[int] = Query(None, description="Filtrar por año de carga"),
    top_emergentes: int = Query(15, ge=1, le=50, description="Cantidad de candidatas emergentes a devolver"),
    db: Session = Depends(get_db),
):
    """
    Analiza las respuestas abiertas de las encuestas de egresados y extrae
    las habilidades blandas y duras más demandadas por el mercado laboral.
    """
    # 1. Consultar mediciones con filtros opcionales
    query = db.query(Medicion)
    if momento is not None:
        query = query.filter(Medicion.momento == momento)
    if anio is not None:
        query = query.filter(Medicion.anio == anio)

    mediciones = query.all()

    # 2. Extraer textos libres de las preguntas abiertas de cada medición
    todos_los_textos: List[str] = []
    for m in mediciones:
        textos_extraidos = _extraer_textos_libres(m.respuestas)
        todos_los_textos.extend(textos_extraidos)

    # 3. Si no hay textos que analizar, devolver resultado vacío
    if not todos_los_textos:
        return HabilidadesDemandadasResponse(
            habilidades_reconocidas=[],
            candidatas_emergentes=[],
            estadisticas=EstadisticasAnalisis(
                total_respuestas_analizadas=0,
                respuestas_con_habilidad=0,
                respuestas_sin_habilidad=0,
            ),
        )

    # 4. Ejecutar el pipeline completo de análisis (ia_service)
    resultado = analizar_habilidades_demandadas(
        textos_respuestas=todos_los_textos,
        top_emergentes=top_emergentes,
    )

    return resultado


@router.get("/reglas-asociacion", response_model=ReglasAsociacionResponse)
def get_reglas_asociacion(
    momento: Optional[int] = Query(None, description="Filtrar por momento de encuesta (0, 1 o 5)"),
    anio: Optional[int] = Query(None, description="Filtrar por año de carga"),
    min_soporte: float = Query(0.01, ge=0.001, le=1.0, description="Soporte mínimo para apriori (default 0.01)"),
    min_confianza: float = Query(0.4, ge=0.01, le=1.0, description="Confianza mínima para las reglas (default 0.4)"),
    min_ocurrencias: int = Query(2, ge=1, description="Ocurrencias mínimas absolutas de egresados para respaldar la regla (default 2)"),
    top_reglas: int = Query(20, ge=1, le=100, description="Cantidad máxima de reglas a devolver (default 20)"),
    db: Session = Depends(get_db),
):
    """
    Calcula reglas de asociación (Market Basket Analysis) sobre las habilidades demandadas.
    Construye la 'canasta' consolidada por cada egresado (unificando todas las preguntas
    abiertas que respondió) y aplica Apriori con max_len=2 para pares 1 a 1.
    """
    # 1. Consultar mediciones con filtros opcionales
    query = db.query(Medicion)
    if momento is not None:
        query = query.filter(Medicion.momento == momento)
    if anio is not None:
        query = query.filter(Medicion.anio == anio)

    mediciones = query.all()

    # 2. Construir transacciones por egresado / medición (Canasta unificada de MBA)
    transacciones: List[Set[str]] = []
    for m in mediciones:
        textos_m = _extraer_textos_libres(m.respuestas)
        habs_egresado: Set[str] = set()
        for t in textos_m:
            habs_egresado.update(extraer_habilidades_por_respuesta(t))
        transacciones.append(habs_egresado)

    if not transacciones:
        return ReglasAsociacionResponse(
            total_respuestas=0,
            transacciones_validas=0,
            transacciones_insuficientes=0,
            total_reglas=0,
            reglas=[],
        )

    # 3. Calcular reglas de asociación con mlxtend a nivel de egresado
    resultado = generar_reglas_asociacion(
        transacciones=transacciones,
        min_soporte=min_soporte,
        min_confianza=min_confianza,
        min_ocurrencias=min_ocurrencias,
        top_reglas=top_reglas,
    )

    return resultado
