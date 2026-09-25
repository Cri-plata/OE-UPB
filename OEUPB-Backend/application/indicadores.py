"""Cálculo de indicadores agregados y reglas de privacidad para publicarlos.

Los endpoints privados de reportes y la publicación de gráficas comparten estas
funciones para que una instantánea publicada provenga siempre de datos fuente de
la sede autenticada y nunca de métricas enviadas por el cliente (RN-11, RN-14).
"""

import re
import unicodedata

from sqlalchemy.orm import Session

from application.medicion_policy import seleccionar_intentos
from domain.models import Egresado, Medicion

UMBRAL_MINIMO_PUBLICACION = 5
ETIQUETA_OTROS = "Otros (agrupados por privacidad)"
MOMENTOS = (0, 1, 5)
ETIQUETAS_MOMENTOS = ["Momento 0 (Grado)", "Momento 1 (1 año)", "Momento 5 (5 años)"]
INDICADORES_TENDENCIAS = ("empleabilidad", "salario", "satisfaccion")
INDICADORES_REPORTE_GENERAL = ("distribucion_programas", "satisfaccion")
CATEGORIAS_SATISFACCION = (
    "Aplicación Conocimientos",
    "Retos Intelectuales",
    "Estabilidad",
    "Ascenso",
)
PALETA = ["#c8102e", "#1d3557", "#2a9d8f", "#f4a261", "#9b5de5", "#0077b6", "#00b4d8", "#90e0ef", "#e9c46a", "#457b9d"]

# RN-31: familias de columnas que nunca son variables analíticas. Se comparan
# contra el nombre normalizado (minúsculas, sin tildes, separado por "_").
_PATRONES_EXCLUIDOS = [re.compile(patron) for patron in (
    r"(^|_)(numero_)?documento(_|$)", r"(^|_)(cedula|identificacion|pasaporte)(_|$)", r"(^|_)(nro|num|no)_doc",
    r"(^|_)(primer|segundo)?_?nombres?(_|$)", r"(^|_)(primer|segundo)?_?apellidos?(_|$)",
    r"(^|_)e?_?mail(_|$)", r"(^|_)correo", r"(^|_)(celular|telefono|movil|whatsapp)(_|$)",
    r"(^|_)direccion(_|$)", r"(^|_)fecha(_|$)", r"(^|_)nacimiento(_|$)",
    r"(^|_)id(_|$)", r"(^|_)cod(igo)?(_|$)", r"(^|_)estado_(de_)?(la_)?encuesta(_|$)",
    r"(^|_)ies(_|$)", r"(^|_)nivel_(academico|de_formacion|formacion)(_|$)",
    r"(^|_)pais(_|$)", r"(^|_)token(_|$)", r"(^|_)ip(_|$)",
)]


class DatosInsuficientesError(ValueError):
    """La gráfica no conserva ninguna celda publicable tras aplicar el umbral."""


def normalizar_columna(nombre: str) -> str:
    sin_tildes = unicodedata.normalize("NFKD", str(nombre)).encode("ascii", "ignore").decode("ascii")
    return re.sub(r"[^a-z0-9]+", "_", sin_tildes.lower()).strip("_")


def es_variable_analitica(nombre: str) -> bool:
    normalizado = normalizar_columna(nombre)
    if not normalizado:
        return False
    return not any(patron.search(normalizado) for patron in _PATRONES_EXCLUIDOS)


def _mediciones_identificadas(db: Session, sede_id: int, momento=None, programa=None, anio=None):
    query = (
        db.query(Medicion, Egresado.programa)
        .join(Egresado, Medicion.egresado_documento == Egresado.numero_documento)
        .filter(Medicion.sede_id == sede_id)
    )
    if momento is not None:
        query = query.filter(Medicion.momento == momento)
    if programa:
        query = query.filter(Egresado.programa == programa)
    if anio is not None:
        query = query.filter(Medicion.anio == anio)
    return seleccionar_intentos(query.all())


def distribucion_programas(db: Session, sede_id: int) -> dict[str, int]:
    documentos = db.query(Medicion.egresado_documento).filter(Medicion.sede_id == sede_id)
    filas = db.query(Egresado.programa).filter(Egresado.numero_documento.in_(documentos)).all()
    distribucion: dict[str, int] = {}
    for (programa,) in filas:
        distribucion[programa] = distribucion.get(programa, 0) + 1
    return distribucion


def satisfaccion_general(db: Session, sede_id: int) -> dict[str, dict[str, float]]:
    """Devuelve suma y conteo por categoría de satisfacción (pregunta 54)."""
    acumulado = {categoria: {"suma": 0.0, "count": 0} for categoria in CATEGORIAS_SATISFACCION}
    mediciones = seleccionar_intentos(db.query(Medicion).filter(Medicion.sede_id == sede_id).all())
    for medicion in mediciones:
        for clave, valor in (medicion.respuestas or {}).items():
            clave_min = clave.lower()
            if "califique su nivel de satisfacci" not in clave_min or valor is None:
                continue
            try:
                numero = float(valor)
            except (TypeError, ValueError):
                continue
            if "aplicaci" in clave_min and "conocimientos" in clave_min:
                categoria = "Aplicación Conocimientos"
            elif "retos y desaf" in clave_min:
                categoria = "Retos Intelectuales"
            elif "estabilidad" in clave_min:
                categoria = "Estabilidad"
            elif "ascenso" in clave_min:
                categoria = "Ascenso"
            else:
                continue
            acumulado[categoria]["suma"] += numero
            acumulado[categoria]["count"] += 1
    return acumulado


def extraer_salario(texto):
    if not texto or not isinstance(texto, str):
        return None
    texto = texto.lower()
    if "entre" in texto and "smlv" in texto:
        match = re.search(r"entre ([\d,]+) y ([\d,]+)", texto)
        if match:
            v1 = float(match.group(1).replace(",", "."))
            v2 = float(match.group(2).replace(",", "."))
            return (v1 + v2) / 2.0
    if "menos de 1" in texto:
        return 0.8
    if "más de 10" in texto or "mas de 10" in texto:
        return 12.0
    if "1 smlv" in texto:
        return 1.0
    numeros = re.findall(r"([\d,]+)", texto.split("(")[0])
    if numeros:
        return float(numeros[0].replace(",", "."))
    return None


def tendencias_por_programa(db: Session, sede_id: int, indicador: str) -> list[tuple[str, list[tuple[float | None, int]]]]:
    """Top 5 de programas con (valor, observaciones) para cada momento 0, 1 y 5."""
    store: dict[str, dict[int, dict[str, float]]] = {}
    for medicion, programa in _mediciones_identificadas(db, sede_id):
        if programa not in store:
            store[programa] = {m: {"emp": 0, "total": 0, "suma_salario": 0.0, "count_salario": 0, "suma_sat": 0.0, "count_sat": 0} for m in MOMENTOS}
        momento = medicion.momento if medicion.momento in MOMENTOS else 1
        celda = store[programa][momento]
        respuestas = medicion.respuestas or {}

        clave_empleo = next((k for k in respuestas if "realiza alguna actividad remunerada?" in k.lower()), None)
        if clave_empleo:
            valor = str(respuestas[clave_empleo]).strip().upper()
            if valor in ("SI", "SÍ", "NO"):
                celda["total"] += 1
                if valor in ("SI", "SÍ"):
                    celda["emp"] += 1

        clave_salario = next((k for k in respuestas if "ingreso mensual" in k.lower() and "smlv" in k.lower()), None)
        if clave_salario and respuestas[clave_salario]:
            salario = extraer_salario(str(respuestas[clave_salario]))
            if salario is not None:
                celda["suma_salario"] += salario
                celda["count_salario"] += 1

        suma_sat, conteo_sat = 0.0, 0
        for clave, valor in respuestas.items():
            if "nivel de satisfacci" in clave.lower() and valor is not None:
                try:
                    suma_sat += float(valor)
                    conteo_sat += 1
                except (TypeError, ValueError):
                    pass
        if conteo_sat:
            celda["suma_sat"] += suma_sat / conteo_sat
            celda["count_sat"] += 1

    def observaciones(celda: dict) -> int:
        if indicador == "salario":
            return celda["count_salario"]
        if indicador == "satisfaccion":
            return celda["count_sat"]
        return celda["total"]

    def valor(celda: dict) -> float | None:
        n = observaciones(celda)
        if n == 0:
            return None
        if indicador == "salario":
            return round(celda["suma_salario"] / n, 2)
        if indicador == "satisfaccion":
            return round(celda["suma_sat"] / n, 2)
        return round(celda["emp"] / n * 100, 1)

    ordenados = sorted(store, key=lambda p: sum(observaciones(store[p][m]) for m in MOMENTOS), reverse=True)[:5]
    return [(programa, [(valor(store[programa][m]), observaciones(store[programa][m])) for m in MOMENTOS]) for programa in ordenados]


def conteo_respuestas(db: Session, sede_id: int, pregunta: str, momento=None, programa=None, anio=None) -> tuple[dict[str, int], set[str]]:
    """Cuenta respuestas de una variable analítica y devuelve los programas observados."""
    conteo: dict[str, int] = {}
    programas: set[str] = set()
    for medicion, programa_egresado in _mediciones_identificadas(db, sede_id, momento, programa, anio):
        respuestas = medicion.respuestas or {}
        if pregunta not in respuestas:
            continue
        valor = str(respuestas[pregunta]).strip()
        if valor.lower() in ("nan", "none", ""):
            valor = "Sin respuesta"
        conteo[valor] = conteo.get(valor, 0) + 1
        if programa_egresado:
            programas.add(programa_egresado)
    return conteo, programas


def preguntas_analiticas(db: Session, sede_id: int) -> tuple[list[str], list[str], list[int]]:
    preguntas, programas, anios = set(), set(), set()
    for medicion, programa in _mediciones_identificadas(db, sede_id):
        programas.add(programa)
        if medicion.anio:
            anios.add(medicion.anio)
        preguntas.update(clave for clave in (medicion.respuestas or {}) if es_variable_analitica(clave))
    return sorted(preguntas), sorted(p for p in programas if p), sorted(anios)


def recortar_etiqueta(texto: str) -> str:
    return texto[:50] + ("..." if len(texto) > 50 else "")


def _agrupar_categorias(conteo: dict[str, int]) -> tuple[list[str], list[float]]:
    """Suprime categorías con menos observaciones que el umbral.

    Las categorías pequeñas se agrupan en una sola celda si en conjunto alcanzan el
    umbral; en caso contrario se omiten para no revelar casos individuales.
    """
    visibles = sorted(((k, v) for k, v in conteo.items() if v >= UMBRAL_MINIMO_PUBLICACION), key=lambda item: item[1], reverse=True)
    pequenas = sum(v for v in conteo.values() if v < UMBRAL_MINIMO_PUBLICACION)
    if pequenas >= UMBRAL_MINIMO_PUBLICACION:
        visibles.append((ETIQUETA_OTROS, pequenas))
    return [recortar_etiqueta(k) for k, _ in visibles], [float(v) for _, v in visibles]


def construir_publicacion(db: Session, sede_id: int, definicion: dict) -> tuple[dict, list[str]]:
    """Recalcula en backend las métricas publicables y la audiencia por programa.

    Devuelve `(metricas, programas)`. Lanza `ValueError` si la definición no es
    publicable y `DatosInsuficientesError` si ninguna celda supera el umbral.
    """
    origen = definicion["origen"]
    indicador = definicion.get("indicador")

    if origen == "reporte_general":
        if indicador == "distribucion_programas":
            distribucion = distribucion_programas(db, sede_id)
            labels, data = _agrupar_categorias(distribucion)
            metricas = {"labels": labels, "datasets": [{"label": "Egresados", "data": data, "backgroundColor": [PALETA[i % len(PALETA)] for i in range(len(labels))]}]}
            agrupados = ETIQUETA_OTROS in labels
            programas = sorted(
                p for p, n in distribucion.items()
                if p and (n >= UMBRAL_MINIMO_PUBLICACION or agrupados)
            )
        elif indicador == "satisfaccion":
            acumulado = satisfaccion_general(db, sede_id)
            data = [
                round(celda["suma"] / celda["count"], 1) if celda["count"] >= UMBRAL_MINIMO_PUBLICACION else None
                for celda in acumulado.values()
            ]
            metricas = {"labels": list(acumulado), "datasets": [{"label": "Satisfacción Promedio", "data": data, "backgroundColor": PALETA[:len(data)]}]}
            programas = sorted(p for p in distribucion_programas(db, sede_id) if p)
        else:
            raise ValueError("El reporte general exige indicador 'distribucion_programas' o 'satisfaccion'")

    elif origen == "tendencias":
        if indicador not in INDICADORES_TENDENCIAS:
            raise ValueError("Indicador de tendencias no soportado")
        datasets = []
        for idx, (programa, celdas) in enumerate(tendencias_por_programa(db, sede_id, indicador)):
            data = [valor if n >= UMBRAL_MINIMO_PUBLICACION else None for valor, n in celdas]
            if any(valor is not None for valor in data):
                color = PALETA[idx % len(PALETA)]
                datasets.append({"label": programa, "data": data, "backgroundColor": color, "borderColor": color})
        metricas = {"labels": list(ETIQUETAS_MOMENTOS), "datasets": datasets}
        programas = [dataset["label"] for dataset in datasets]

    elif origen == "explorador":
        pregunta = definicion.get("pregunta")
        if not pregunta or not es_variable_analitica(pregunta):
            raise ValueError("La variable solicitada no pertenece al catálogo analítico autorizado")
        conteo, observados = conteo_respuestas(
            db, sede_id, pregunta, definicion.get("momento"), definicion.get("programa"), definicion.get("anio")
        )
        labels, data = _agrupar_categorias(conteo)
        metricas = {"labels": labels, "datasets": [{"label": "Respuestas", "data": data, "backgroundColor": [PALETA[i % len(PALETA)] for i in range(len(labels))]}]}
        programas = sorted(observados)
    else:
        raise ValueError("Origen de gráfica no soportado")

    tiene_datos = metricas["labels"] and any(
        valor is not None for dataset in metricas["datasets"] for valor in dataset["data"]
    )
    if not tiene_datos or not programas:
        raise DatosInsuficientesError(
            f"No hay celdas con al menos {UMBRAL_MINIMO_PUBLICACION} observaciones para publicar esta gráfica"
        )
    return metricas, programas
