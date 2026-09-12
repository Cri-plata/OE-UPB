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
from typing import List, Optional

from infrastructure.database import get_db
from domain.models import Medicion
from application.ia_service import analizar_habilidades_demandadas

router = APIRouter(prefix="/api/ia", tags=["Inteligencia Artificial"])


# ─────────────────────────────────────────────────────────────────────────────
# Modelos de respuesta (Pydantic)
# ─────────────────────────────────────────────────────────────────────────────
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
# Utilidad: extraer textos libres relevantes del campo JSON de respuestas
# ─────────────────────────────────────────────────────────────────────────────
# Palabras clave para identificar preguntas abiertas (texto libre) dentro
# del campo JSON dinámico de las encuestas del OLE/UPB.
_KEYWORDS_PREGUNTAS_ABIERTAS = [
    "competencia",
    "habilidad",
    "conocimiento",
    "formación",
    "preparación",
    "qué le faltó",
    "qué le hizo falta",
    "debilidad",
    "fortaleza",
    "mejorar",
    "sugerencia",
    "recomendación",
    "observación",
    "comentario",
]


def _extraer_textos_libres(respuestas_json: dict) -> List[str]:
    """
    Dado el diccionario JSON de una medición (respuestas_completas),
    extrae los valores de las preguntas que parecen ser de texto libre
    relacionadas con habilidades/competencias.

    Si ninguna pregunta coincide con los keywords, incluye TODOS los valores
    de texto con longitud >= 30 caracteres (heurística para preguntas abiertas
    vs. respuestas cerradas cortas como "SI", "NO", "3", etc.)
    """
    if not respuestas_json or not isinstance(respuestas_json, dict):
        return []

    textos = []
    textos_por_keyword = []

    for key, val in respuestas_json.items():
        if val is None or not isinstance(val, str):
            continue

        val_strip = val.strip()
        if len(val_strip) < 10:  # Descartar respuestas muy cortas
            continue

        key_lower = key.lower()

        # Buscar si la pregunta (key) contiene algún keyword de preguntas abiertas
        for kw in _KEYWORDS_PREGUNTAS_ABIERTAS:
            if kw in key_lower:
                textos_por_keyword.append(val_strip)
                break

        # Heurística: valores largos probablemente son texto libre
        if len(val_strip) >= 30:
            textos.append(val_strip)

    # Preferir textos filtrados por keyword; si no hay, usar la heurística
    return textos_por_keyword if textos_por_keyword else textos


# ─────────────────────────────────────────────────────────────────────────────
# Endpoint principal
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

    **Pipeline:**
    1. Consulta las mediciones (opcionalmente filtradas por momento y/o año)
    2. Extrae los textos libres del campo JSON de respuestas
    3. Preprocesa con spaCy (lematización, remoción de stopwords, preservación de PROPN)
    4. Hace matching contra el diccionario de habilidades (longest match first, sin doble conteo)
    5. Aplica TF-IDF (ngram_range=(1,2)) sobre el texto residual para descubrir habilidades emergentes
    6. Devuelve el resultado agregado con conteos y scores

    **Filtros opcionales:**
    - `momento`: 0 (grado), 1 (un año), 5 (cinco años)
    - `anio`: año de aplicación de la encuesta
    - `top_emergentes`: cantidad de candidatas TF-IDF a devolver (default 15)
    """
    # 1. Consultar mediciones con filtros opcionales
    query = db.query(Medicion)
    if momento is not None:
        query = query.filter(Medicion.momento == momento)
    if anio is not None:
        query = query.filter(Medicion.anio == anio)

    mediciones = query.all()

    # 2. Extraer textos libres del JSON de cada medición
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
