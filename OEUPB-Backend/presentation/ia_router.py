"""
Router de IA - Endpoint /api/ia/habilidades-demandadas
=======================================================
Módulo desacoplado del resto del backend.
Consulta las respuestas JSON de la tabla mediciones y ejecuta el pipeline
de análisis de habilidades sin almacenar texto crudo más allá del procesamiento.
"""

from fastapi import APIRouter, Depends, Query, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List, Optional, Set, Dict, Any

from infrastructure.database import get_db
from domain.models import Medicion, Egresado, Sede, HabilidadCurada
from application.auth_service import require_roles
from presentation.errores import RESPUESTAS_PROTEGIDAS
from application.ia_service import (
    analizar_habilidades_demandadas,
    generar_reglas_asociacion,
    extraer_habilidades_por_respuesta,
    comparar_habilidades_temporales,
    generar_excel_habilidades,
    registrar_habilidad_curada_en_memoria,
    sincronizar_curadurias_bd,
    invalidar_cache_taxonomia,
)
from application.prediccion_service import (
    predecir_empleabilidad_servicio,
    generar_excel_prediccion,
    benchmark_sedes_servicio,
)
from application.model_cache import habilidades_cache

router = APIRouter(prefix="/api/ia", tags=["Inteligencia Artificial"], responses=RESPUESTAS_PROTEGIDAS)

EXCEL_RESPONSES = {
    200: {
        "content": {
            "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet": {
                "schema": {"type": "string", "format": "binary"}
            }
        },
        "description": "Reporte Excel (.xlsx)",
    }
}


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


class CurarHabilidadRequest(BaseModel):
    termino_original: str
    etiqueta_canonica: str
    tipo: str = "dura"
    variantes: List[str] = []
    estado: str = "aprobada"


class HabilidadCuradaItem(BaseModel):
    id: int
    termino_original: str
    etiqueta_canonica: str
    tipo: str
    variantes: List[str]
    estado: str
    creado_por_id: int
    creado_por_correo: str
    fecha_creacion: str


class CurarHabilidadResponse(BaseModel):
    mensaje: str
    curada: HabilidadCuradaItem


class EliminarCuraduriaResponse(BaseModel):
    mensaje: str


class ImportanciaFactorItem(BaseModel):
    factor: str
    importancia: float


class PrediccionProgramaItem(BaseModel):
    programa: str
    total_egresados: int
    probabilidad_empleado: float
    probabilidad_independiente: float
    probabilidad_estudiante: float
    probabilidad_sin_empleo: float
    nivel_riesgo: str
    rango_salarial_estimado: str


class AlertaRiesgoItem(BaseModel):
    programa: str
    severidad: str
    mensaje: str
    riesgo_estimado: float
    tamano_muestra: int


class MatrizConfusionData(BaseModel):
    clases: List[str]
    matriz: List[List[int]]


class ComparativaAlgoritmoItem(BaseModel):
    algoritmo: str
    accuracy: float
    f1_score: float
    tiempo_ms: float
    seleccionado: bool


class BenchmarkSedeItem(BaseModel):
    sede_id: int
    sede_nombre: str
    estado: str
    total_trayectorias: int
    precision_modelo: float
    probabilidad_empleo_promedio: float
    egresados_en_riesgo: int
    factor_principal: str
    robustez: str


class ValidacionTemporalData(BaseModel):
    disponible: bool
    motivo: Optional[str] = None
    cohorte_evaluada: Optional[int] = None
    tamano_muestra_prueba: Optional[int] = None
    tamano_muestra_entrenamiento: Optional[int] = None
    accuracy_temporal: Optional[float] = None
    f1_temporal: Optional[float] = None
    diagnostico_estabilidad: Optional[str] = None
    color_estabilidad: Optional[str] = None


class PrediccionEmpleabilidadResponse(BaseModel):
    estado: str
    mensaje: str
    total_trayectorias: int
    precision_modelo: float
    f1_score: float
    programas_analizados: int
    egresados_en_riesgo: int
    importancia_factores: List[ImportanciaFactorItem]
    predicciones_programas: List[PrediccionProgramaItem]
    alertas_riesgo: List[AlertaRiesgoItem]
    matriz_confusion: MatrizConfusionData
    indicadores_robustez: Optional[Dict[str, Any]] = None
    comparativa_algoritmos: Optional[List[ComparativaAlgoritmoItem]] = []
    validacion_temporal: Optional[ValidacionTemporalData] = None


class HabilidadComparativaItem(BaseModel):
    habilidad: str
    tipo: str
    m0_menciones: int
    m0_pct: float
    m1_menciones: int
    m1_pct: float
    m5_menciones: int
    m5_pct: float
    delta_m1_m0: float
    tendencia: str
    total_menciones: int


class HabilidadesComparativaResponse(BaseModel):
    comparativa: List[HabilidadComparativaItem]
    totales_respuestas: Dict[str, int]
    totales_con_habilidad: Dict[str, int]


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
    programa: Optional[str] = Query(None, description="Filtrar por programa académico del egresado"),
    top_emergentes: int = Query(15, ge=1, le=50, description="Cantidad de candidatas emergentes a devolver"),
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_roles("Coordinador_Sede")),
):
    """
    Analiza las respuestas abiertas de las encuestas de egresados y extrae
    las habilidades blandas y duras más demandadas por el mercado laboral.
    """
    # Normalizar parámetros si se invoca directamente fuera de FastAPI
    if hasattr(momento, "default"): momento = momento.default
    if hasattr(anio, "default"): anio = anio.default
    if hasattr(programa, "default"): programa = programa.default
    if hasattr(top_emergentes, "default"): top_emergentes = top_emergentes.default or 15

    # IA-15: Sincronizar curadurías aprobadas/descartadas desde la BD
    sincronizar_curadurias_bd(db)

    # 1. Consultar mediciones con filtros opcionales
    query = db.query(Medicion)
    if current_user.get("sede_id"):
        query = query.filter(Medicion.sede_id == current_user["sede_id"])
    if momento is not None:
        query = query.filter(Medicion.momento == momento)
    if anio is not None:
        query = query.filter(Medicion.anio == anio)
    if programa:
        query = query.join(Medicion.egresado).filter(Egresado.programa == programa)

    mediciones = query.all()

    # Cache en memoria (TTL 5m) para respuestas inmediatas
    cache_key = f"habs_{current_user.get('sede_id')}_{momento}_{anio}_{programa}_{top_emergentes}_{len(mediciones)}"
    cached = habilidades_cache.get_by_key(cache_key)
    if cached is not None:
        return cached

    # 2. Extraer textos libres de las preguntas abiertas de cada medición
    todos_los_textos: List[str] = []
    for m in mediciones:
        textos_extraidos = _extraer_textos_libres(m.respuestas)
        todos_los_textos.extend(textos_extraidos)

    # 3. Si no hay textos que analizar, devolver resultado vacío
    if not todos_los_textos:
        empty_res = HabilidadesDemandadasResponse(
            habilidades_reconocidas=[],
            candidatas_emergentes=[],
            estadisticas=EstadisticasAnalisis(
                total_respuestas_analizadas=0,
                respuestas_con_habilidad=0,
                respuestas_sin_habilidad=0,
            ),
        )
        return empty_res

    # 4. Ejecutar el pipeline completo de análisis (ia_service)
    resultado = analizar_habilidades_demandadas(
        textos_respuestas=todos_los_textos,
        top_emergentes=top_emergentes,
    )

    habilidades_cache.set_by_key(cache_key, resultado)
    return resultado


@router.get("/reglas-asociacion", response_model=ReglasAsociacionResponse)
def get_reglas_asociacion(
    momento: Optional[int] = Query(None, description="Filtrar por momento de encuesta (0, 1 o 5)"),
    anio: Optional[int] = Query(None, description="Filtrar por año de carga"),
    programa: Optional[str] = Query(None, description="Filtrar por programa académico del egresado"),
    min_soporte: float = Query(0.01, ge=0.001, le=1.0, description="Soporte mínimo para apriori (default 0.01)"),
    min_confianza: float = Query(0.4, ge=0.01, le=1.0, description="Confianza mínima para las reglas (default 0.4)"),
    min_ocurrencias: int = Query(2, ge=1, description="Ocurrencias mínimas absolutas de egresados para respaldar la regla (default 2)"),
    top_reglas: int = Query(20, ge=1, le=100, description="Cantidad máxima de reglas a devolver (default 20)"),
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_roles("Coordinador_Sede")),
):
    """
    Calcula reglas de asociación (Market Basket Analysis) sobre las habilidades demandadas.
    Construye la 'canasta' consolidada por cada egresado (unificando todas las preguntas
    abiertas que respondió) y aplica Apriori con max_len=2 para pares 1 a 1.
    """
    # Normalizar parámetros si se invoca directamente fuera de FastAPI
    if hasattr(momento, "default"): momento = momento.default
    if hasattr(anio, "default"): anio = anio.default
    if hasattr(programa, "default"): programa = programa.default
    if hasattr(min_soporte, "default"): min_soporte = min_soporte.default or 0.01
    if hasattr(min_confianza, "default"): min_confianza = min_confianza.default or 0.4
    if hasattr(min_ocurrencias, "default"): min_ocurrencias = min_ocurrencias.default or 2
    if hasattr(top_reglas, "default"): top_reglas = top_reglas.default or 20

    # 1. Consultar mediciones con filtros opcionales
    query = db.query(Medicion)
    if current_user.get("sede_id"):
        query = query.filter(Medicion.sede_id == current_user["sede_id"])
    if momento is not None:
        query = query.filter(Medicion.momento == momento)
    if anio is not None:
        query = query.filter(Medicion.anio == anio)
    if programa:
        query = query.join(Medicion.egresado).filter(Egresado.programa == programa)

    mediciones = query.all()

    # Cache en memoria (TTL 5m) para respuestas inmediatas
    cache_key = f"reglas_{current_user.get('sede_id')}_{momento}_{anio}_{programa}_{min_soporte}_{min_confianza}_{min_ocurrencias}_{top_reglas}_{len(mediciones)}"
    cached = habilidades_cache.get_by_key(cache_key)
    if cached is not None:
        return cached

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

    habilidades_cache.set_by_key(cache_key, resultado)
    return resultado


@router.get("/habilidades-comparativa", response_model=HabilidadesComparativaResponse)
def get_habilidades_comparativa(
    anio: Optional[int] = Query(None, description="Filtrar por año de cohorte"),
    programa: Optional[str] = Query(None, description="Filtrar por programa académico"),
    top_n: int = Query(25, ge=5, le=50, description="Top N habilidades a comparar"),
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_roles("Coordinador_Sede")),
):
    """
    Comparativa Temporal Longitudinal de Habilidades Demandadas (IA-06).
    Compara las menciones relativas entre M0 (grado), M1 (1 año) y M5 (5 años)
    para clasificar tendencias emergentes, crecientes o decrecientes.
    """
    # Normalizar parámetros si se invoca directamente fuera de FastAPI
    if hasattr(anio, "default"): anio = anio.default
    if hasattr(programa, "default"): programa = programa.default
    if hasattr(top_n, "default"): top_n = top_n.default or 25

    query = db.query(Medicion)
    if current_user.get("sede_id"):
        query = query.filter(Medicion.sede_id == current_user["sede_id"])
    if anio is not None:
        query = query.filter(Medicion.anio == anio)
    if programa:
        query = query.join(Medicion.egresado).filter(Egresado.programa == programa)

    mediciones = query.all()

    # Cache en memoria (TTL 5m) para comparativas temporales
    cache_key = f"comp_{current_user.get('sede_id')}_{anio}_{programa}_{top_n}_{len(mediciones)}"
    cached = habilidades_cache.get_by_key(cache_key)
    if cached is not None:
        return cached

    textos_por_momento: Dict[int, List[str]] = {0: [], 1: [], 5: []}
    for m in mediciones:
        if m.momento in textos_por_momento:
            textos_por_momento[m.momento].extend(_extraer_textos_libres(m.respuestas))

    resultado = comparar_habilidades_temporales(textos_por_momento, top_n=top_n)

    resp = HabilidadesComparativaResponse(
        comparativa=[HabilidadComparativaItem(**row) for row in resultado["comparativa"]],
        totales_respuestas={str(k): v for k, v in resultado["totales_respuestas"].items()},
        totales_con_habilidad={str(k): v for k, v in resultado["totales_con_habilidad"].items()},
    )
    habilidades_cache.set_by_key(cache_key, resp)
    return resp


@router.get("/habilidades-export", responses=EXCEL_RESPONSES)
def exportar_habilidades_excel(
    momento: Optional[int] = Query(None, description="Filtrar por momento (0, 1 o 5)"),
    anio: Optional[int] = Query(None, description="Filtrar por año"),
    programa: Optional[str] = Query(None, description="Filtrar por programa académico"),
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_roles("Coordinador_Sede")),
):
    """
    Exportación de Resultados NLP a Hoja de Cálculo Excel .xlsx (IA-07).
    Genera un archivo con 3 hojas: Habilidades Reconocidas, Reglas de Asociación y Candidatas Emergentes.
    """
    # Normalizar parámetros si se invoca directamente fuera de FastAPI
    if hasattr(momento, "default"): momento = momento.default
    if hasattr(anio, "default"): anio = anio.default
    if hasattr(programa, "default"): programa = programa.default

    query = db.query(Medicion)
    if current_user.get("sede_id"):
        query = query.filter(Medicion.sede_id == current_user["sede_id"])
    if momento is not None:
        query = query.filter(Medicion.momento == momento)
    if anio is not None:
        query = query.filter(Medicion.anio == anio)
    if programa:
        query = query.join(Medicion.egresado).filter(Egresado.programa == programa)

    mediciones = query.all()

    # Extraer textos para NLP y transacciones para reglas
    todos_los_textos: List[str] = []
    textos_por_momento: Dict[int, List[str]] = {0: [], 1: [], 5: []}
    por_egresado: Dict[str, Set[str]] = {}

    for m in mediciones:
        textos = _extraer_textos_libres(m.respuestas)
        todos_los_textos.extend(textos)
        if m.momento in textos_por_momento:
            textos_por_momento[m.momento].extend(textos)
        for t in textos:
            habs = extraer_habilidades_por_respuesta(t)
            if habs:
                if m.egresado_documento not in por_egresado:
                    por_egresado[m.egresado_documento] = set()
                por_egresado[m.egresado_documento].update(habs)

    habilidades_data = analizar_habilidades_demandadas(todos_los_textos, top_emergentes=25)
    transacciones = [sorted(h) for h in por_egresado.values() if len(h) >= 2]
    reglas_data = generar_reglas_asociacion(transacciones, min_ocurrencias=2, min_confianza=0.4, top_reglas=50)

    comparativa_data = None
    if momento is None and any(len(txts) > 0 for txts in textos_por_momento.values()):
        comparativa_data = comparar_habilidades_temporales(textos_por_momento, top_n=30)

    excel_stream = generar_excel_habilidades(habilidades_data, reglas_data, comparativa_data)

    return StreamingResponse(
        excel_stream,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": "attachment; filename=habilidades_demandadas_oeupb.xlsx"},
    )


@router.get("/prediccion-empleabilidad", response_model=PrediccionEmpleabilidadResponse)
def get_prediccion_empleabilidad(
    momento_origen: int = Query(0, description="Momento inicial de trayectoria (default 0 - graduación)"),
    momento_destino: int = Query(1, description="Momento longitudinal a proyectar (1 o 5, default 1)"),
    programa: Optional[str] = Query(None, description="Filtrar por programa académico"),
    anio: Optional[int] = Query(None, description="Filtrar por cohorte / año"),
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_roles("Coordinador_Sede")),
):
    """
    Modelo Predictivo de Empleabilidad (RF-71 / IA-01).
    Entrena modelos supervisados (GradientBoostingClassifier) usando trayectorias longitudinales
    de egresados (M0 -> M1 o M0/M1 -> M5) para proyectar probabilidades de inserción laboral,
    riesgo de desempleo y nivel salarial agregado por programa.
    """
    query = db.query(Medicion)
    if current_user.get("sede_id"):
        query = query.filter(Medicion.sede_id == current_user["sede_id"])

    mediciones = query.all()
    egresados = db.query(Egresado).all()

    resultado = predecir_empleabilidad_servicio(
        mediciones=mediciones,
        egresados=egresados,
        momento_origen=momento_origen,
        momento_destino=momento_destino,
        filtro_programa=programa,
        filtro_anio=anio,
    )

    return resultado


@router.get("/prediccion-export", responses=EXCEL_RESPONSES)
def exportar_prediccion_excel(
    momento_origen: int = Query(0, description="Momento inicial de trayectoria"),
    momento_destino: int = Query(1, description="Momento longitudinal a proyectar"),
    programa: Optional[str] = Query(None, description="Filtrar por programa académico"),
    anio: Optional[int] = Query(None, description="Filtrar por año"),
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_roles("Coordinador_Sede")),
):
    """
    Descarga del Informe Ejecutivo Predictivo en Hoja de Cálculo Excel (.xlsx) (IA-14).
    """
    query = db.query(Medicion)
    if current_user.get("sede_id"):
        query = query.filter(Medicion.sede_id == current_user["sede_id"])

    mediciones = query.all()
    egresados = db.query(Egresado).all()

    resultado = predecir_empleabilidad_servicio(
        mediciones=mediciones,
        egresados=egresados,
        momento_origen=momento_origen,
        momento_destino=momento_destino,
        filtro_programa=programa,
        filtro_anio=anio,
    )

    excel_stream = generar_excel_prediccion(resultado)
    return StreamingResponse(
        excel_stream,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": "attachment; filename=informe_predictivo_empleabilidad_oeupb.xlsx"},
    )


@router.get("/prediccion-benchmark-sedes", response_model=List[BenchmarkSedeItem])
def get_benchmark_sedes(
    momento_origen: int = Query(0, description="Momento inicial"),
    momento_destino: int = Query(1, description="Momento proyectado"),
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_roles("Admin_CTIC", "Coordinador_Sede")),
):
    """
    Benchmark Inter-Sedes de Trayectorias y Empleabilidad (IA-08).
    Permite contrastar la capacidad predictiva y métricas entre sedes institucionales.
    """
    sedes = db.query(Sede).filter(Sede.activa == True).all()
    sedes_info = [{"id": s.id, "nombre": s.nombre} for s in sedes]

    query = db.query(Medicion)
    if current_user.get("rol") == "Coordinador_Sede" and current_user.get("sede_id"):
        sedes_info = [s for s in sedes_info if s["id"] == current_user["sede_id"]]
        query = query.filter(Medicion.sede_id == current_user["sede_id"])

    all_mediciones = query.all()
    egresados = db.query(Egresado).all()

    mediciones_por_sede: Dict[int, List[Medicion]] = {}
    for m in all_mediciones:
        if m.sede_id not in mediciones_por_sede:
            mediciones_por_sede[m.sede_id] = []
        mediciones_por_sede[m.sede_id].append(m)

    benchmark = benchmark_sedes_servicio(
        mediciones_por_sede=mediciones_por_sede,
        sedes_info=sedes_info,
        egresados=egresados,
        momento_origen=momento_origen,
        momento_destino=momento_destino,
    )

    return benchmark


# ─────────────────────────────────────────────────────────────────────────────
# IA-15: CURADURÍA DE HABILIDADES EMERGENTES (HUMAN-IN-THE-LOOP)
# ─────────────────────────────────────────────────────────────────────────────
@router.get("/habilidades/curadas", response_model=List[HabilidadCuradaItem])
def get_habilidades_curadas(
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_roles("Coordinador_Sede", "Admin_CTIC")),
):
    """
    Lista de habilidades curadas por el equipo (IA-15 / Human-in-the-Loop).
    Permite auditar los términos aprobados y descartados.
    """
    curadas = db.query(HabilidadCurada).order_by(HabilidadCurada.fecha_creacion.desc()).all()
    return [
        HabilidadCuradaItem(
            id=c.id,
            termino_original=c.termino_original,
            etiqueta_canonica=c.etiqueta_canonica,
            tipo=c.tipo,
            variantes=c.variantes or [],
            estado=c.estado,
            creado_por_id=c.creado_por_id,
            creado_por_correo=c.creado_por_correo,
            fecha_creacion=c.fecha_creacion.isoformat() if c.fecha_creacion else "",
        )
        for c in curadas
    ]


@router.post("/habilidades/curar", response_model=CurarHabilidadResponse)
def post_curar_habilidad(
    req: CurarHabilidadRequest,
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_roles("Coordinador_Sede", "Admin_CTIC")),
):
    """
    Registra la aprobación o descarte de un término emergente (IA-15).
    Disponible para Coordinador_Sede y Admin_CTIC con trazabilidad de autoría (Opción 1).
    """
    termino_norm = req.termino_original.strip()
    if not termino_norm:
        raise HTTPException(status_code=400, detail="El término original es obligatorio.")

    estado_norm = req.estado.lower().strip()
    if estado_norm not in ("aprobada", "descartada"):
        raise HTTPException(status_code=400, detail="El estado debe ser 'aprobada' o 'descartada'.")

    tipo_norm = req.tipo.lower().strip()
    if tipo_norm not in ("blanda", "dura"):
        tipo_norm = "dura"

    etiqueta = req.etiqueta_canonica.strip() or termino_norm.title()

    # Verificar si ya existe curaduría para este término
    existente = db.query(HabilidadCurada).filter(HabilidadCurada.termino_original == termino_norm).first()
    if existente:
        existente.etiqueta_canonica = etiqueta
        existente.tipo = tipo_norm
        existente.variantes = req.variantes or [termino_norm]
        existente.estado = estado_norm
        existente.creado_por_id = current_user.get("usuario_id", 1)
        existente.creado_por_correo = current_user.get("sub", "desconocido")
        db.commit()
        db.refresh(existente)
        curada_obj = existente
    else:
        curada_obj = HabilidadCurada(
            termino_original=termino_norm,
            etiqueta_canonica=etiqueta,
            tipo=tipo_norm,
            variantes=req.variantes or [termino_norm],
            estado=estado_norm,
            creado_por_id=current_user.get("usuario_id", 1),
            creado_por_correo=current_user.get("sub", "desconocido"),
        )
        db.add(curada_obj)
        db.commit()
        db.refresh(curada_obj)

    # Actualizar la taxonomía en memoria e invalidar caché
    registrar_habilidad_curada_en_memoria(
        termino_original=curada_obj.termino_original,
        etiqueta_canonica=curada_obj.etiqueta_canonica,
        tipo=curada_obj.tipo,
        variantes=curada_obj.variantes or [],
        estado=curada_obj.estado,
    )
    habilidades_cache.clear()

    return CurarHabilidadResponse(
        mensaje=f"Habilidad '{curada_obj.termino_original}' registrada como '{curada_obj.estado}' exitosamente.",
        curada=HabilidadCuradaItem(
            id=curada_obj.id,
            termino_original=curada_obj.termino_original,
            etiqueta_canonica=curada_obj.etiqueta_canonica,
            tipo=curada_obj.tipo,
            variantes=curada_obj.variantes or [],
            estado=curada_obj.estado,
            creado_por_id=curada_obj.creado_por_id,
            creado_por_correo=curada_obj.creado_por_correo,
            fecha_creacion=curada_obj.fecha_creacion.isoformat() if curada_obj.fecha_creacion else "",
        ),
    )


@router.delete("/habilidades/curar/{curada_id}", response_model=EliminarCuraduriaResponse)
def delete_curar_habilidad(
    curada_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_roles("Coordinador_Sede", "Admin_CTIC")),
):
    """
    Revierte o elimina una curaduría previa (IA-15).
    Admin_CTIC puede revertir cualquiera; Coordinador_Sede puede revertir las que haya creado.
    """
    curada = db.query(HabilidadCurada).filter(HabilidadCurada.id == curada_id).first()
    if not curada:
        raise HTTPException(status_code=404, detail="Curaduría no encontrada.")

    if current_user.get("rol") != "Admin_CTIC" and curada.creado_por_id != current_user.get("usuario_id"):
        raise HTTPException(status_code=403, detail="No tiene permisos para revertir esta curaduría.")

    db.delete(curada)
    db.commit()

    # Re-sincronizar taxonomía completa
    invalidar_cache_taxonomia()
    sincronizar_curadurias_bd(db)
    habilidades_cache.clear()

    return {"mensaje": f"Curaduría de '{curada.termino_original}' eliminada exitosamente."}
