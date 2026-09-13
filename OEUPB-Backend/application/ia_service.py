"""
Módulo de IA - Servicio de Análisis de Habilidades
===================================================
Módulo desacoplado para el análisis de texto libre de encuestas de egresados.
Extrae habilidades blandas y duras mencionadas usando NLP local (spaCy + scikit-learn).

Restricciones:
  - Sin APIs externas de pago (OpenAI, etc.)
  - Todo procesamiento local con librerías open source
  - El texto llega ya anonimizado; no se almacena el texto crudo
  - El diccionario es de propósito GENERAL, sin lógica condicionada a carreras específicas
"""

import unicodedata
import re
from typing import Dict, List, Set, Tuple, Optional
from collections import Counter

import numpy as np
import pandas as pd
import spacy
from sklearn.feature_extraction.text import TfidfVectorizer
from mlxtend.preprocessing import TransactionEncoder
from mlxtend.frequent_patterns import apriori, association_rules

# ─────────────────────────────────────────────────────────────────────────────
# 1. MODELO SPACY (carga lazy para no bloquear el arranque del servidor)
# ─────────────────────────────────────────────────────────────────────────────
_nlp = None

def _get_nlp():
    """Carga el modelo de spaCy en español de forma lazy (solo la primera vez)."""
    global _nlp
    if _nlp is None:
        _nlp = spacy.load("es_core_news_md")
    return _nlp


# ─────────────────────────────────────────────────────────────────────────────
# 2. PREPROCESAMIENTO DE TEXTO (Paso 1 aprobado)
# ─────────────────────────────────────────────────────────────────────────────
def _quitar_tildes(texto: str) -> str:
    """Elimina marcas diacríticas (tildes) conservando la letra base."""
    texto = unicodedata.normalize("NFD", texto)
    return "".join(c for c in texto if unicodedata.category(c) != "Mn")


def preprocesar_texto(texto: str) -> str:
    """
    Pipeline de limpieza y normalización de texto libre de encuestas.

    1. Tokenización morfosintáctica con spaCy (es_core_news_md)
    2. Filtro de stopwords, puntuación, espacios, números (like_num) y tokens <= 1 char
    3. Nombres propios (PROPN): se preserva token.text.lower() sin lematizar
       (evita sobrelematización de términos técnicos en inglés: Kubernetes → kubernetes, no kubernet)
    4. Resto de tokens: lematización estándar (lemma_.lower())
    5. Remoción de tildes para matching consistente
    """
    if not texto or not isinstance(texto, str):
        return ""

    nlp = _get_nlp()
    # Se conservan las mayúsculas originales para que spaCy etiquete correctamente los PROPN
    doc = nlp(texto.strip())
    tokens = []

    for token in doc:
        if token.is_stop or token.is_punct or token.is_space or token.like_num or len(token.text.strip()) <= 1:
            continue

        # Regla PROPN: preservar texto original en minúsculas sin lematizar
        if token.pos_ == "PROPN":
            valor = token.text.lower()
        else:
            valor = token.lemma_.lower()

        valor = _quitar_tildes(valor)
        valor = re.sub(r"[^a-zA-Z0-9]", "", valor)

        if valor and len(valor) > 1 and not valor.isdigit():
            tokens.append(valor)

    return " ".join(tokens)


def _preprocesar_crudo(texto: str) -> str:
    """
    Versión sin lematización del preprocesamiento (solo lowercase + quitar tildes).

    Genera la forma "cruda normalizada" del texto para matching doble-forma.
    Se aplica el mismo filtrado de stopwords y puntuación que preprocesar_texto(),
    pero usando token.text.lower() en vez de token.lemma_ para TODOS los tokens.

    Esto cubre los casos donde es_core_news_md asigna POS incorrecto en
    respuestas fragmentadas (palabras sueltas, listas por comas, fragmentos
    sin contexto sintáctico), produciendo lemas incorrectos.
    """
    if not texto or not isinstance(texto, str):
        return ""

    nlp = _get_nlp()
    doc = nlp(texto.strip())
    tokens = []

    for token in doc:
        if token.is_stop or token.is_punct or token.is_space or token.like_num or len(token.text.strip()) <= 1:
            continue

        # Siempre usar text.lower(), nunca lemma_
        valor = token.text.lower()
        valor = _quitar_tildes(valor)
        valor = re.sub(r"[^a-zA-Z0-9]", "", valor)

        if valor and len(valor) > 1 and not valor.isdigit():
            tokens.append(valor)

    return " ".join(tokens)


# ─────────────────────────────────────────────────────────────────────────────
# 3. TAXONOMÍA DE HABILIDADES (Paso 2 aprobado con los 3 ajustes)
# ─────────────────────────────────────────────────────────────────────────────
# Etiqueta canónica → lista de variantes en texto CRUDO (se preprocesan al compilar)
# NUNCA se condiciona la lógica a un valor de "programa" específico.
TAXONOMIA_HABILIDADES_BRUTA: Dict[str, Dict] = {
    # ── Habilidades Blandas ──
    "Trabajo en equipo": {
        "tipo": "blanda",
        "variantes": ["trabajo en equipo", "trabajo colaborativo", "colaboración"]
    },
    "Trabajo bajo presión": {
        "tipo": "blanda",
        "variantes": ["trabajo bajo presión", "manejo de la presión", "tolerancia a la presión", "manejo del estrés"]
    },
    "Liderazgo": {
        "tipo": "blanda",
        "variantes": ["liderazgo", "manejo de personal", "dirección de equipos"]
    },
    "Comunicación": {
        "tipo": "blanda",
        "variantes": ["comunicación", "comunicación asertiva", "comunicación efectiva", "habilidades de comunicación", "expresión oral"]
    },
    "Resolución de problemas": {
        "tipo": "blanda",
        "variantes": ["resolución de problemas", "solución de problemas", "resolución de conflictos"]
    },
    "Pensamiento crítico": {
        "tipo": "blanda",
        "variantes": ["pensamiento crítico", "pensamiento analítico", "capacidad analítica"]
    },
    "Adaptabilidad al cambio": {
        "tipo": "blanda",
        "variantes": ["adaptabilidad", "adaptabilidad al cambio", "flexibilidad laboral", "tolerancia a la frustración"]
    },
    "Gestión del tiempo": {
        "tipo": "blanda",
        "variantes": ["gestión del tiempo", "manejo del tiempo", "organización del trabajo", "capacidad de organización", "puntualidad"]
    },
    "Negociación": {
        "tipo": "blanda",
        "variantes": ["negociación", "capacidad de negociación", "persuasión"]
    },
    "Toma de decisiones": {
        "tipo": "blanda",
        "variantes": ["toma de decisiones", "criterio propio"]
    },
    "Inteligencia emocional": {
        "tipo": "blanda",
        "variantes": ["inteligencia emocional", "empatía", "relaciones interpersonales"]
    },
    "Creatividad e innovación": {
        "tipo": "blanda",
        "variantes": ["creatividad", "innovación", "pensamiento lateral"]
    },

    # ── Habilidades Duras / Técnicas Transversales ──
    "Manejo de Excel / Office": {
        "tipo": "dura",
        "variantes": ["excel avanzado", "manejo de excel", "excel", "herramientas ofimáticas"]
    },
    "Análisis de datos": {
        "tipo": "dura",
        "variantes": ["análisis de datos", "ciencia de datos", "business intelligence", "power bi", "estadística"]
    },
    "Inglés / Segundo idioma": {
        "tipo": "dura",
        "variantes": ["inglés conversacional", "inglés", "segundo idioma", "bilingüismo"]
    },
    "Gestión de proyectos": {
        "tipo": "dura",
        "variantes": ["gestión de proyectos", "metodologías ágiles", "scrum", "dirección de proyectos"]
    },
    "Atención al cliente": {
        "tipo": "dura",
        "variantes": ["atención al cliente", "servicio al cliente", "manejo de usuarios"]
    },
    "Planeación estratégica": {
        "tipo": "dura",
        "variantes": ["planeación estratégica", "planificación estratégica", "gestión estratégica"]
    },
    "Normativa y regulación": {
        "tipo": "dura",
        "variantes": ["normativa legal", "cumplimiento normativo", "marco regulatorio", "legislación vigente"]
    },
    "Redacción de informes": {
        "tipo": "dura",
        "variantes": ["redacción de informes", "redacción técnica", "elaboración de documentos"]
    },
    "Finanzas y presupuestos": {
        "tipo": "dura",
        "variantes": ["elaboración de presupuestos", "análisis financiero", "costos y presupuestos"]
    },
    "Marketing y ventas": {
        "tipo": "dura",
        "variantes": ["marketing digital", "estrategias de venta", "ventas"]
    },
}


# ─────────────────────────────────────────────────────────────────────────────
# 4. COMPILACIÓN DE PATRONES (se ejecuta al importar el módulo)
# ─────────────────────────────────────────────────────────────────────────────
def _compilar_taxonomia() -> Tuple[Dict[str, List[str]], Dict[str, str], list]:
    """
    Preprocesa cada variante de la taxonomía con la MISMA función preprocesar_texto()
    y compila los patrones regex ordenados por longitud descendente (longest match first).
    
    Retorna:
      - taxonomia_prep: {etiqueta: [variantes preprocesadas]}
      - tipos_habilidad: {etiqueta: "blanda" | "dura"}
      - patrones: lista ordenada de (num_palabras, regex_compilada, etiqueta, variante)
    """
    taxonomia_prep = {}
    tipos_habilidad = {}

    for etiqueta, config in TAXONOMIA_HABILIDADES_BRUTA.items():
        tipos_habilidad[etiqueta] = config["tipo"]
        vars_limpias = set()
        for variante in config["variantes"]:
            # Forma lematizada (pipeline completo con spaCy)
            v_prep = preprocesar_texto(variante)
            if v_prep:
                vars_limpias.add(v_prep)
            # Forma cruda normalizada (sin lematizar, solo minúsculas + quitar tildes)
            # Esto cubre los casos en que spaCy asigna POS distinto en aislamiento vs. contexto
            v_cruda = _quitar_tildes(variante.lower().strip())
            v_cruda = re.sub(r"[^a-zA-Z0-9\s]", "", v_cruda)
            v_cruda = " ".join(p for p in v_cruda.split() if len(p) > 1)
            if v_cruda and v_cruda not in vars_limpias:
                vars_limpias.add(v_cruda)
        # Ordenar por número de palabras descendente dentro de cada etiqueta
        taxonomia_prep[etiqueta] = sorted(list(vars_limpias), key=lambda x: len(x.split()), reverse=True)


    # Compilar patrones globales con \b (límites de palabra)
    patrones = []
    for etiqueta, variantes in taxonomia_prep.items():
        for var in variantes:
            num_palabras = len(var.split())
            regex = re.compile(rf"\b{re.escape(var)}\b")
            patrones.append((num_palabras, regex, etiqueta, var))

    # Ordenar globalmente: frases más largas primero (longest match first)
    patrones.sort(key=lambda x: x[0], reverse=True)

    return taxonomia_prep, tipos_habilidad, patrones


# Compilación al importar el módulo (una sola vez)
_TAXONOMIA_PREP, _TIPOS_HABILIDAD, _PATRONES_COMPILADOS = _compilar_taxonomia()


# ─────────────────────────────────────────────────────────────────────────────
# 5. EXTRACCIÓN DE HABILIDADES Y TEXTO RESIDUAL (Paso 3 aprobado)
# ─────────────────────────────────────────────────────────────────────────────
def _extraer_habilidades_y_residual(texto_preprocesado: str) -> Tuple[Set[str], List[dict], str]:
    """
    Extrae las habilidades presentes en un texto ya preprocesado.

    Protección contra doble conteo:
      1. Nivel tokens/n-gramas: Longest Match First con máscara de caracteres ocupados.
         Si un match más largo ya consumió un tramo, un match más corto no puede reutilizarlo.
      2. Nivel respuesta/egresado: Se devuelve un Set de etiquetas canónicas.
         Cada habilidad se cuenta exactamente 1 vez por respuesta, sin importar
         cuántas veces o con cuántos sinónimos la mencione el egresado.

    Retorna:
      - habilidades_unicas: Set[str] con las etiquetas canónicas detectadas
      - detalles_matches: Lista de dicts con evidencia, ordenada por posición en el texto (span[0])
      - texto_residual: Texto con los tramos ocupados enmascarados, listo para TF-IDF
    """
    ocupados = [False] * len(texto_preprocesado)
    matches = []

    for _, regex, etiqueta, variante in _PATRONES_COMPILADOS:
        for m in regex.finditer(texto_preprocesado):
            s, e = m.start(), m.end()
            # Si algún carácter del match ya fue tomado por un patrón más largo, ignorar
            if any(ocupados[i] for i in range(s, e)):
                continue
            # Reclamar el tramo de texto
            for i in range(s, e):
                ocupados[i] = True
            matches.append({"habilidad": etiqueta, "variante": variante, "span": (s, e)})

    # Ordenar evidencia por posición cronológica de aparición en el texto
    matches.sort(key=lambda x: x["span"][0])

    # Habilidades únicas (1 por respuesta, sin importar repeticiones)
    habilidades_unicas = {m["habilidad"] for m in matches}

    # Reconstruir texto residual: enmascarar caracteres ocupados con espacio
    chars_residuales = [" " if ocupados[i] else ch for i, ch in enumerate(texto_preprocesado)]
    texto_residual = re.sub(r"\s+", " ", "".join(chars_residuales)).strip()

    return habilidades_unicas, matches, texto_residual


# ─────────────────────────────────────────────────────────────────────────────
# 6. EXTRACCIÓN TF-IDF DE HABILIDADES EMERGENTES (Paso 4 aprobado)
# ─────────────────────────────────────────────────────────────────────────────

# Stopwords de discurso/contexto propias de encuestas de egresados
_STOPWORDS_ENCUESTA = [
    "considerar", "faltar", "exigir", "requerir", "necesitar", "aprender",
    "deber", "tener", "dar", "hacer", "solicitar", "necesario", "solido",
    "mayor", "bueno", "ano", "actual", "especialmente", "ejercicio",
    "profesional", "preparacion", "conocimiento", "ambito", "trabajo",
]


def _extraer_emergentes_tfidf(textos_residuales: List[str], top_n: int = 15) -> List[dict]:
    """
    Aplica TF-IDF con ngram_range=(1,2) sobre los textos residuales (ya libres de
    habilidades reconocidas) para descubrir términos emergentes no catalogados.

    Filtra ruido sintáctico con stopwords de relleno de encuestas y ordena por
    score TF-IDF real descendente.

    Retorna lista de dicts: [{"termino": str, "score_tfidf": float, "frecuencia_documentos": int}]
    """
    # Filtrar textos vacíos
    textos_validos = [t for t in textos_residuales if t.strip()]
    if not textos_validos:
        return []

    vectorizer = TfidfVectorizer(
        ngram_range=(1, 2),
        token_pattern=r"(?u)\b\w+\b",
        stop_words=_STOPWORDS_ENCUESTA,
        min_df=1,
    )

    try:
        X = vectorizer.fit_transform(textos_validos)
    except ValueError:
        # Si tras filtrar stopwords no queda vocabulario
        return []

    feature_names = vectorizer.get_feature_names_out()
    matriz = X.toarray()

    # Score máximo que alcanza cada término en los documentos
    scores_max = matriz.max(axis=0)
    # Frecuencia documental (en cuántas respuestas aparece)
    doc_freq = (matriz > 0).sum(axis=0)

    # Ordenar por score descendente
    ranking = np.argsort(scores_max)[::-1]

    emergentes = []
    for idx in ranking[:top_n]:
        emergentes.append({
            "termino": str(feature_names[idx]),
            "score_tfidf": round(float(scores_max[idx]), 4),
            "frecuencia_documentos": int(doc_freq[idx]),
        })

    return emergentes


# ─────────────────────────────────────────────────────────────────────────────
# 7. FUNCIÓN PÚBLICA PRINCIPAL (orquesta todo el pipeline)
# ─────────────────────────────────────────────────────────────────────────────
def analizar_habilidades_demandadas(
    textos_respuestas: List[str],
    top_emergentes: int = 15,
) -> dict:
    """
    Pipeline completo de análisis de habilidades demandadas por el mercado laboral.

    Recibe una lista de textos libres de respuestas de encuestas de egresados
    (ya anonimizados) y devuelve:

    1. habilidades_reconocidas: lista de habilidades del diccionario con su conteo
       de menciones (cuántos egresados la mencionaron) y tipo (blanda/dura).
    2. candidatas_emergentes: lista de n-gramas no catalogados con su score TF-IDF
       y frecuencia documental, para revisión del coordinador.
    3. estadisticas: metadatos del procesamiento (total respuestas, total con
       al menos 1 habilidad, total sin habilidades).

    Args:
        textos_respuestas: Lista de strings con las respuestas abiertas crudas.
        top_emergentes: Cantidad de candidatas emergentes a devolver (default 15).

    Returns:
        dict con las 3 secciones descritas.
    """
    conteo_global = Counter()
    textos_residuales = []
    respuestas_con_habilidad = 0

    for texto_crudo in textos_respuestas:
        # 1. Preprocesar con AMBAS formas (doble-forma en texto entrante)
        texto_lema = preprocesar_texto(texto_crudo)      # Con lematización
        texto_crudo_norm = _preprocesar_crudo(texto_crudo)  # Sin lematización

        if not texto_lema and not texto_crudo_norm:
            textos_residuales.append("")
            continue

        # 2. Extraer habilidades de AMBAS versiones del texto
        habs_lema, _, residual_lema = _extraer_habilidades_y_residual(texto_lema) if texto_lema else (set(), [], "")
        habs_crudo, _, residual_crudo = _extraer_habilidades_y_residual(texto_crudo_norm) if texto_crudo_norm else (set(), [], "")

        # 3. Unificar habilidades de ambas pasadas (sin doble conteo)
        habilidades = habs_lema | habs_crudo

        # 4. Conteo global: 1 por habilidad por egresado
        conteo_global.update(habilidades)

        if habilidades:
            respuestas_con_habilidad += 1

        # 5. Texto residual para TF-IDF: excluir tokens ocupados por CUALQUIERA de las 2 pasadas
        #    Si la pasada cruda detectó una habilidad que la lematizada no (ej. "estadistica" detectada
        #    en cruda pero "estadisticar" no matcheó en lema), el token lematizado incorrecto debe
        #    quedar fuera del TF-IDF. Usamos el residual crudo como base y filtramos sus tokens.
        if habs_crudo - habs_lema:
            # Hay habilidades que solo la pasada cruda detectó → usar residual crudo
            # (más limpio que el lematizado para estos casos)
            textos_residuales.append(residual_crudo)
        else:
            # Ambas pasadas coinciden → usar lematizado (más normalizado para TF-IDF)
            textos_residuales.append(residual_lema if texto_lema else residual_crudo)

    # 4. TF-IDF sobre textos residuales para descubrir emergentes
    emergentes = _extraer_emergentes_tfidf(textos_residuales, top_n=top_emergentes)

    # 5. Formatear resultado de habilidades reconocidas ordenado por menciones
    habilidades_resultado = []
    for etiqueta, menciones in conteo_global.most_common():
        habilidades_resultado.append({
            "habilidad": etiqueta,
            "tipo": _TIPOS_HABILIDAD.get(etiqueta, "desconocido"),
            "menciones": menciones,
        })

    total = len(textos_respuestas)
    return {
        "habilidades_reconocidas": habilidades_resultado,
        "candidatas_emergentes": emergentes,
        "estadisticas": {
            "total_respuestas_analizadas": total,
            "respuestas_con_habilidad": respuestas_con_habilidad,
            "respuestas_sin_habilidad": total - respuestas_con_habilidad,
        },
    }


# ─────────────────────────────────────────────────────────────────────────────
# 6. ANÁLISIS DE REGLAS DE ASOCIACIÓN (Market Basket Analysis)
# ─────────────────────────────────────────────────────────────────────────────
def extraer_habilidades_por_respuesta(texto_crudo: str) -> Set[str]:
    """
    Extrae el conjunto de habilidades únicas detectadas en una respuesta abierta
    utilizando el pipeline de doble-forma (lematizada + cruda).
    """
    if not texto_crudo or not isinstance(texto_crudo, str):
        return set()

    texto_lema = preprocesar_texto(texto_crudo)
    texto_crudo_norm = _preprocesar_crudo(texto_crudo)

    habs_lema = _extraer_habilidades_y_residual(texto_lema)[0] if texto_lema else set()
    habs_crudo = _extraer_habilidades_y_residual(texto_crudo_norm)[0] if texto_crudo_norm else set()

    return habs_lema | habs_crudo


# Alias de compatibilidad
extraer_habilidades_de_texto = extraer_habilidades_por_respuesta


def generar_reglas_asociacion(
    textos_respuestas: List[str] = None,
    transacciones: List[Set[str]] = None,
    min_soporte: float = 0.05,
    min_confianza: float = 0.5,
    min_ocurrencias: int = 3,
    top_reglas: int = 20,
) -> dict:
    """
    Calcula reglas de asociación (Market Basket Analysis) sobre las habilidades demandadas.
    Aplica Apriori con max_len=2 (reglas 1 a 1: 'si menciona X, también menciona Y') y
    filtra por ocurrencias mínimas absolutas para evitar reglas basadas en datos insuficientes.

    Args:
        textos_respuestas: Lista de respuestas abiertas crudas (opcional si se pasan transacciones).
        transacciones: Lista de sets de habilidades ya extraídas por respuesta (opcional).
        min_soporte: Proporción mínima de transacciones que deben contener el par (default 0.05).
        min_confianza: Probabilidad condicional mínima P(Y|X) (default 0.5).
        min_ocurrencias: Conteo absoluto mínimo de transacciones reales que respaldan la regla (default 3).
        top_reglas: Límite de reglas a devolver, ordenadas por lift descendente (default 20).

    Returns:
        dict con metadatos de filtrado y lista de reglas formateadas:
        {
            "total_respuestas": int,
            "transacciones_validas": int,
            "transacciones_insuficientes": int,
            "total_reglas": int,
            "reglas": [
                {
                    "si_menciona": str,
                    "tambien_menciona": str,
                    "ocurrencias": int,
                    "soporte": float,
                    "confianza": float,
                    "lift": float,
                }
            ]
        }
    """
    # 1. Obtener transacciones (sets de habilidades por respuesta)
    if transacciones is None:
        transacciones = [extraer_habilidades_por_respuesta(t) for t in (textos_respuestas or [])]

    total_respuestas = len(transacciones)

    # 2. Filtrar transacciones con al menos 2 habilidades (las de < 2 no pueden formar pares)
    transacciones_validas = [list(habs) for habs in transacciones if len(habs) >= 2]
    total_validas = len(transacciones_validas)
    insuficientes = total_respuestas - total_validas

    if total_validas < 2:
        return {
            "total_respuestas": total_respuestas,
            "transacciones_validas": total_validas,
            "transacciones_insuficientes": insuficientes,
            "total_reglas": 0,
            "reglas": [],
        }

    # 3. Construir matriz binaria con TransactionEncoder
    te = TransactionEncoder()
    te_ary = te.fit(transacciones_validas).transform(transacciones_validas)
    df = pd.DataFrame(te_ary, columns=te.columns_)

    # 4. Apriori con max_len=2 (estrictamente pares: un antecedente y un consecuente)
    try:
        frequent_itemsets = apriori(
            df,
            min_support=min_soporte,
            use_colnames=True,
            max_len=2,
        )
    except Exception:
        frequent_itemsets = pd.DataFrame()

    if frequent_itemsets.empty:
        return {
            "total_respuestas": total_respuestas,
            "transacciones_validas": total_validas,
            "transacciones_insuficientes": insuficientes,
            "total_reglas": 0,
            "reglas": [],
        }

    # 5. Generar reglas de asociación filtrando por confianza mínima
    try:
        rules = association_rules(
            frequent_itemsets,
            metric="confidence",
            min_threshold=min_confianza,
        )
    except Exception:
        rules = pd.DataFrame()

    if rules.empty:
        return {
            "total_respuestas": total_respuestas,
            "transacciones_validas": total_validas,
            "transacciones_insuficientes": insuficientes,
            "total_reglas": 0,
            "reglas": [],
        }

    # 6. Filtrar por ocurrencias mínimas absolutas (soporte * total_transacciones >= min_ocurrencias)
    reglas_formateadas = []
    for _, row in rules.iterrows():
        ocurrencias = int(round(row["support"] * total_validas))
        if ocurrencias < min_ocurrencias:
            continue

        antecedente = list(row["antecedents"])[0]
        consecuente = list(row["consequents"])[0]

        reglas_formateadas.append({
            "si_menciona": antecedente,
            "tambien_menciona": consecuente,
            "ocurrencias": ocurrencias,
            "soporte": round(float(row["support"]), 4),
            "confianza": round(float(row["confidence"]), 4),
            "lift": round(float(row["lift"]), 4),
        })

    # 7. Ordenar por lift descendente (desempate por confianza y soporte)
    reglas_formateadas.sort(
        key=lambda r: (r["lift"], r["confianza"], r["soporte"]),
        reverse=True,
    )

    if top_reglas and top_reglas > 0:
        reglas_formateadas = reglas_formateadas[:top_reglas]

    return {
        "total_respuestas": total_respuestas,
        "transacciones_validas": total_validas,
        "transacciones_insuficientes": insuficientes,
        "total_reglas": len(reglas_formateadas),
        "reglas": reglas_formateadas,
    }


# Alias de compatibilidad
calcular_reglas_asociacion = generar_reglas_asociacion
