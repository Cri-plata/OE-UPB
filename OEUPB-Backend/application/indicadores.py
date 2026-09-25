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
INDICADORES_REPORTE_GENERAL = ("distribucion_programas", "satisfaccion", "estado_laboral")
ETIQUETAS_ESTADO = {"empleado": "Empleado", "independiente": "Independiente", "estudiante": "Estudiante", "sin_empleo": "Sin empleo"}
MINIMO_PARES_COMPARACION = UMBRAL_MINIMO_PUBLICACION
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
    r"(^|_)usuarios?(_|$)", r"^unnamed(_|$)",
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


class Filtros:
    """Filtros analíticos del dashboard privado (HU-09). Vacío = sin filtro."""

    def __init__(self, programas=None, anios=None, momento=None):
        self.programas = set(programas or [])
        self.anios = set(anios or [])
        self.momento = momento


SIN_FILTROS = Filtros()


def _mediciones(db: Session, sede_id: int, filtros: Filtros = SIN_FILTROS, incluir_anonimas: bool = False):
    """Mediciones de la sede (último intento) como tuplas `(medicion, programa)`.

    Las anónimas no tienen programa: solo se incluyen si se piden y no hay filtro de programa.
    """
    query = (
        db.query(Medicion, Egresado.programa)
        .outerjoin(Egresado, Medicion.egresado_documento == Egresado.numero_documento)
        .filter(Medicion.sede_id == sede_id)
    )
    if not incluir_anonimas or filtros.programas:
        query = query.filter(Medicion.egresado_documento.isnot(None))
    if filtros.momento is not None:
        query = query.filter(Medicion.momento == filtros.momento)
    if filtros.programas:
        query = query.filter(Egresado.programa.in_(filtros.programas))
    if filtros.anios:
        query = query.filter(Medicion.anio.in_(filtros.anios))
    return seleccionar_intentos(query.all())


def _mediciones_identificadas(db: Session, sede_id: int, momento=None, programa=None, anio=None):
    return _mediciones(db, sede_id, Filtros([programa] if programa else None, [anio] if anio is not None else None, momento))


def distribucion_programas(db: Session, sede_id: int, filtros: Filtros = SIN_FILTROS) -> dict[str, int]:
    """Egresados identificados distintos por programa."""
    documentos_por_programa: dict[str, set[str]] = {}
    for medicion, programa in _mediciones(db, sede_id, filtros):
        documentos_por_programa.setdefault(programa, set()).add(medicion.egresado_documento)
    return {programa: len(documentos) for programa, documentos in documentos_por_programa.items()}


# --- Taxonomía laboral (RN-16) -----------------------------------------------
# Mapeo verificado el 2026-09-25 contra las opciones de respuesta de los
# cuestionarios OLE. El seguimiento (M1/M5) pregunta si realiza actividad
# remunerada y su posición; el M0 (al graduarse) pregunta si trabaja aparte de
# estudiar. La formalidad solo existe en el seguimiento (tipo de contrato).
ESTADOS_LABORALES = ("empleado", "independiente", "estudiante", "sin_empleo")
_CLAVE_REMUNERADA = "realiza_alguna_actividad_remunerada"
_CLAVE_POSICION_SEGUIMIENTO = "actividad_remunerada_que_usted_realiza_actualmente_es"
_CLAVE_CONTRATO = "que_tipo_de_contrato_tiene"
_CLAVE_TRABAJA_M0 = "aparte_de_estudiar_usted_se_dedica_a_trabajar"
_CLAVE_POSICION_M0 = "en_este_trabajo_usted_es"


def _respuesta(respuestas: dict, fragmento: str) -> str | None:
    """Valor normalizado de la pregunta cuyo nombre contiene el fragmento (ignora columnas OTRO)."""
    for clave, valor in respuestas.items():
        normalizada = normalizar_columna(clave)
        if fragmento in normalizada and not normalizada.endswith("_otro"):
            texto = normalizar_columna(valor) if valor is not None else ""
            return texto if texto not in ("", "none", "nan") else None
    return None


def _clasificar_posicion(posicion: str | None) -> str | None:
    if posicion is None:
        return None
    if "practicante" in posicion or "pasante" in posicion:
        return "estudiante"
    if any(palabra in posicion for palabra in ("independiente", "contratista", "cuenta_propia", "propietario")):
        return "independiente"
    if any(palabra in posicion for palabra in ("empleado", "dependiente", "familiar")):
        return "empleado"
    return None


def estado_laboral(respuestas: dict | None) -> str | None:
    """Clasifica una medición en RN-16; `None` si no hay información suficiente."""
    respuestas = respuestas or {}
    remunerada = _respuesta(respuestas, _CLAVE_REMUNERADA)
    if remunerada is not None:
        if remunerada == "no":
            return "sin_empleo"
        if remunerada == "si":
            return _clasificar_posicion(_respuesta(respuestas, _CLAVE_POSICION_SEGUIMIENTO))
        return None
    trabaja = _respuesta(respuestas, _CLAVE_TRABAJA_M0)
    if trabaja == "no":
        return "estudiante"
    if trabaja == "si":
        return _clasificar_posicion(_respuesta(respuestas, _CLAVE_POSICION_M0))
    return None


def formalidad(respuestas: dict | None) -> str | None:
    """`formal` = empleado con contrato laboral; `no_formal` = independiente. `None` si no aplica.

    Solo el cuestionario de seguimiento (M1/M5) pregunta el tipo de contrato; en M0 no se clasifica.
    """
    if _respuesta(respuestas or {}, _CLAVE_REMUNERADA) is None:
        return None
    estado = estado_laboral(respuestas)
    if estado == "independiente":
        return "no_formal"
    if estado == "empleado":
        contrato = _respuesta(respuestas or {}, _CLAVE_CONTRATO)
        if contrato and "contrato" in contrato:
            return "formal"
    return None


def clave_salario(respuestas: dict) -> str | None:
    for clave in respuestas:
        normalizada = normalizar_columna(clave)
        if "ingreso_mensual" in normalizada and any(t in normalizada for t in ("smlv", "smmlv", "salarios_minimos")):
            return clave
    return None


def salario(respuestas: dict | None) -> float | None:
    respuestas = respuestas or {}
    clave = clave_salario(respuestas)
    return extraer_salario(str(respuestas[clave])) if clave and respuestas[clave] else None


def _mediana(valores: list[float]) -> float:
    ordenados = sorted(valores)
    mitad = len(ordenados) // 2
    return ordenados[mitad] if len(ordenados) % 2 else (ordenados[mitad - 1] + ordenados[mitad]) / 2


def resumen_laboral(mediciones) -> dict:
    """KPI laborales sobre mediciones (o tuplas medición, programa)."""
    conteo = {estado: 0 for estado in ESTADOS_LABORALES}
    formales = no_formales = 0
    salarios: list[float] = []
    for item in mediciones:
        medicion = item if hasattr(item, "respuestas") else item[0]
        estado = estado_laboral(medicion.respuestas)
        if estado:
            conteo[estado] += 1
        tipo = formalidad(medicion.respuestas)
        formales += tipo == "formal"
        no_formales += tipo == "no_formal"
        valor = salario(medicion.respuestas)
        if valor is not None:
            salarios.append(valor)
    clasificados = sum(conteo.values())
    ocupados = conteo["empleado"] + conteo["independiente"]
    con_formalidad = formales + no_formales
    return {
        "distribucion_estado_laboral": conteo,
        "clasificados": clasificados,
        "tasa_empleabilidad": round(ocupados / clasificados * 100, 1) if clasificados else 0,
        "tasa_formalidad": round(formales / con_formalidad * 100, 1) if con_formalidad else None,
        "tasa_informalidad": round(no_formales / con_formalidad * 100, 1) if con_formalidad else None,
        "observaciones_formalidad": con_formalidad,
        "promedio_salarial": round(sum(salarios) / len(salarios), 1) if salarios else 0,
        "rango_salarial": {
            "minimo": min(salarios), "mediana": round(_mediana(salarios), 2), "maximo": max(salarios),
            "observaciones": len(salarios),
        } if salarios else None,
    }


def satisfaccion_general(db: Session, sede_id: int, filtros: Filtros = SIN_FILTROS) -> dict[str, dict[str, float]]:
    """Devuelve suma y conteo por categoría de satisfacción (pregunta 54)."""
    acumulado = {categoria: {"suma": 0.0, "count": 0} for categoria in CATEGORIAS_SATISFACCION}
    for medicion, _ in _mediciones(db, sede_id, filtros, incluir_anonimas=True):
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
    # Las opciones usan "SMLV" o "SMMLV"; un rango se resume en su punto medio.
    if "entre" in texto:
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


def tendencias_por_programa(db: Session, sede_id: int, indicador: str, filtros: Filtros = SIN_FILTROS) -> list[tuple[str, list[tuple[float | None, int]]]]:
    """Top 5 de programas con (valor, observaciones) para cada momento 0, 1 y 5.

    Empleabilidad = ocupados (empleado + independiente) / clasificados en RN-16.
    """
    store: dict[str, dict[int, dict[str, float]]] = {}
    for medicion, programa in _mediciones(db, sede_id, Filtros(filtros.programas, filtros.anios)):
        if programa not in store:
            store[programa] = {m: {"emp": 0, "total": 0, "suma_salario": 0.0, "count_salario": 0, "suma_sat": 0.0, "count_sat": 0} for m in MOMENTOS}
        momento = medicion.momento if medicion.momento in MOMENTOS else 1
        celda = store[programa][momento]
        respuestas = medicion.respuestas or {}

        estado = estado_laboral(respuestas)
        if estado:
            celda["total"] += 1
            if estado in ("empleado", "independiente"):
                celda["emp"] += 1

        valor_salario = salario(respuestas)
        if valor_salario is not None:
            celda["suma_salario"] += valor_salario
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


def comparacion_momentos(db: Session, sede_id: int, momento_inicial: int, momento_final: int, indicador: str, filtros: Filtros = SIN_FILTROS) -> dict:
    """Compara dos momentos sobre los mismos egresados (HU-08).

    Un par es un egresado identificado con medición en ambos momentos, en la
    misma sede y la misma cohorte. Solo se informa un valor cuando el programa
    reúne al menos MINIMO_PARES_COMPARACION pares con dato en ambos momentos (RN-26).
    """
    if indicador not in ("empleabilidad", "salario"):
        raise ValueError("Indicador de comparación no soportado")
    base = Filtros(filtros.programas, filtros.anios)
    por_momento: dict[int, dict[tuple[str, int], tuple]] = {momento_inicial: {}, momento_final: {}}
    for medicion, programa in _mediciones(db, sede_id, base):
        if medicion.momento in por_momento:
            por_momento[medicion.momento][(medicion.egresado_documento, medicion.anio)] = (medicion, programa)

    def valor(medicion):
        if indicador == "salario":
            return salario(medicion.respuestas)
        estado = estado_laboral(medicion.respuestas)
        return None if estado is None else float(estado in ("empleado", "independiente"))

    acumulado: dict[str, list[tuple[float, float]]] = {}
    for clave, (inicial, programa) in por_momento[momento_inicial].items():
        final = por_momento[momento_final].get(clave)
        if final is None:
            continue
        v_inicial, v_final = valor(inicial), valor(final[0])
        if v_inicial is not None and v_final is not None:
            acumulado.setdefault(programa, []).append((v_inicial, v_final))

    escala = 1 if indicador == "salario" else 100
    programas = []
    for programa, pares in sorted(acumulado.items(), key=lambda item: -len(item[1])):
        suficiente = len(pares) >= MINIMO_PARES_COMPARACION
        programas.append({
            "programa": programa,
            "pares": len(pares),
            "suficiente": suficiente,
            "valor_inicial": round(sum(p[0] for p in pares) / len(pares) * escala, 1) if suficiente else None,
            "valor_final": round(sum(p[1] for p in pares) / len(pares) * escala, 1) if suficiente else None,
        })
    return {
        "momento_inicial": momento_inicial,
        "momento_final": momento_final,
        "indicador": indicador,
        "minimo_pares": MINIMO_PARES_COMPARACION,
        "programas": programas,
    }


def construir_publicacion(db: Session, sede_id: int, definicion: dict) -> tuple[dict, list[str]]:
    """Recalcula en backend las métricas publicables y la audiencia por programa.

    Devuelve `(metricas, programas)`. Lanza `ValueError` si la definición no es
    publicable y `DatosInsuficientesError` si ninguna celda supera el umbral.
    """
    origen = definicion["origen"]
    indicador = definicion.get("indicador")
    # Tendencias ignora el momento (su eje X son los momentos); el Explorador usa sus propios filtros.
    filtros = Filtros(definicion.get("programas"), definicion.get("anios"), definicion.get("momento"))

    if origen == "reporte_general":
        if indicador == "distribucion_programas":
            distribucion = distribucion_programas(db, sede_id, filtros)
            labels, data = _agrupar_categorias(distribucion)
            metricas = {"labels": labels, "datasets": [{"label": "Egresados", "data": data, "backgroundColor": [PALETA[i % len(PALETA)] for i in range(len(labels))]}]}
            agrupados = ETIQUETA_OTROS in labels
            programas = sorted(
                p for p, n in distribucion.items()
                if p and (n >= UMBRAL_MINIMO_PUBLICACION or agrupados)
            )
        elif indicador == "satisfaccion":
            acumulado = satisfaccion_general(db, sede_id, filtros)
            data = [
                round(celda["suma"] / celda["count"], 1) if celda["count"] >= UMBRAL_MINIMO_PUBLICACION else None
                for celda in acumulado.values()
            ]
            metricas = {"labels": list(acumulado), "datasets": [{"label": "Satisfacción Promedio", "data": data, "backgroundColor": PALETA[:len(data)]}]}
            programas = sorted(p for p in distribucion_programas(db, sede_id, filtros) if p)
        elif indicador == "estado_laboral":
            mediciones = _mediciones(db, sede_id, filtros)
            conteo = resumen_laboral(mediciones)["distribucion_estado_laboral"]
            labels, data = _agrupar_categorias({ETIQUETAS_ESTADO[k]: v for k, v in conteo.items() if v})
            metricas = {"labels": labels, "datasets": [{"label": "Egresados", "data": data, "backgroundColor": [PALETA[i % len(PALETA)] for i in range(len(labels))]}]}
            programas = sorted({p for _, p in mediciones if p})
        else:
            raise ValueError("El reporte general exige indicador 'distribucion_programas', 'satisfaccion' o 'estado_laboral'")

    elif origen == "tendencias":
        if indicador not in INDICADORES_TENDENCIAS:
            raise ValueError("Indicador de tendencias no soportado")
        datasets = []
        for idx, (programa, celdas) in enumerate(tendencias_por_programa(db, sede_id, indicador, filtros)):
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
