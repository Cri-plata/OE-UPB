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

import copy
import hashlib
import unicodedata
import re
from functools import lru_cache
from typing import Any, Dict, List, Set, Tuple, Optional
from collections import Counter

import numpy as np
import pandas as pd

try:
    import spacy
except Exception:
    spacy = None

try:
    from sklearn.feature_extraction.text import TfidfVectorizer
except Exception:
    TfidfVectorizer = None

try:
    from mlxtend.preprocessing import TransactionEncoder
    from mlxtend.frequent_patterns import apriori, association_rules
except Exception:
    TransactionEncoder = None
    apriori = None
    association_rules = None

# ─────────────────────────────────────────────────────────────────────────────
# 1. MODELO SPACY (carga lazy y fallback resiliente)
# ─────────────────────────────────────────────────────────────────────────────
_STOPWORDS_ES = {
    "de", "la", "que", "el", "en", "y", "a", "los", "del", "se", "las", "por", "un", "para", "con", "no",
    "una", "su", "al", "lo", "como", "mas", "pero", "sus", "le", "ya", "o", "este", "si", "porque", "esta",
    "entre", "cuando", "muy", "sin", "sobre", "tambien", "me", "hasta", "hay", "donde", "quien", "desde",
    "todo", "nos", "durante", "todos", "uno", "les", "ni", "contra", "otros", "ese", "eso", "ante", "ellos",
    "e", "esto", "mi", "antes", "algunos", "que", "unos", "yo", "otro", "otras", "otra", "el", "tanto",
    "esa", "estos", "mucho", "quienes", "nada", "muchos", "cual", "sea", "poco", "ella", "estar", "haber"
}

_nlp = None

def _get_nlp():
    """Carga el modelo de spaCy en español de forma lazy (solo la primera vez).
    Desactiva 'parser' y 'ner' para acelerar drásticamente la tokenización y lematización.
    """
    global _nlp
    if _nlp is None:
        if spacy is not None:
            try:
                _nlp = spacy.load("es_core_news_md", disable=["parser", "ner"])
            except Exception:
                _nlp = False
        else:
            _nlp = False
    return _nlp if _nlp is not False else None


# ─────────────────────────────────────────────────────────────────────────────
# 2. PREPROCESAMIENTO DE TEXTO (Paso 1 aprobado)
# ─────────────────────────────────────────────────────────────────────────────
def _quitar_tildes(texto: str) -> str:
    """Elimina marcas diacríticas (tildes) conservando la letra base."""
    texto = unicodedata.normalize("NFD", texto)
    return "".join(c for c in texto if unicodedata.category(c) != "Mn")


@lru_cache(maxsize=16384)
def _preprocesar_dual(texto: str) -> Tuple[str, str]:
    """
    Pipeline unificado de preprocesamiento en UNA SOLA PASADA.
    Genera simultáneamente la forma lematizada y la forma cruda normalizada.
    Memoizado con @lru_cache para responder en 0 ms ante respuestas repetidas.
    """
    if not texto or not isinstance(texto, str):
        return "", ""

    texto_strip = re.sub(r"[_\-]+", " ", texto.strip())
    if not texto_strip:
        return "", ""

    nlp = _get_nlp()
    if nlp is not None:
        doc = nlp(texto_strip)
        tokens_lema = []
        tokens_crudo = []

        for token in doc:
            if token.is_stop or token.is_punct or token.is_space or token.like_num or len(token.text.strip()) <= 1:
                continue

            # Forma cruda: text.lower() sin tildes ni caracteres extraños
            val_crudo = _quitar_tildes(token.text.lower())
            val_crudo = re.sub(r"[^a-zA-Z0-9]", "", val_crudo)

            # Forma lematizada: PROPN preserva original; otros usan lemma_.lower()
            if token.pos_ == "PROPN":
                val_lema = val_crudo
            else:
                val_lema = _quitar_tildes(token.lemma_.lower())
                val_lema = re.sub(r"[^a-zA-Z0-9]", "", val_lema)

            if val_crudo and len(val_crudo) > 1 and not val_crudo.isdigit():
                tokens_crudo.append(val_crudo)

            if val_lema and len(val_lema) > 1 and not val_lema.isdigit():
                tokens_lema.append(val_lema)

        return " ".join(tokens_lema), " ".join(tokens_crudo)
    else:
        palabras = re.findall(r"\b[a-zA-ZáéíóúüñÁÉÍÓÚÜÑ0-9]+\b", texto_strip)
        tokens = []
        for p in palabras:
            p_limpia = _quitar_tildes(p.lower())
            p_limpia = re.sub(r"[^a-zA-Z0-9]", "", p_limpia)
            if p_limpia in _STOPWORDS_ES or p_limpia.isdigit() or len(p_limpia) <= 1:
                continue
            tokens.append(p_limpia)
        res = " ".join(tokens)
        return res, res


def preprocesar_texto(texto: str) -> str:
    """
    Pipeline de limpieza y normalización de texto libre de encuestas.
    (Versión lematizada estándar).
    """
    return _preprocesar_dual(texto)[0]


def _preprocesar_crudo(texto: str) -> str:
    """
    Versión sin lematización del preprocesamiento (solo lowercase + quitar tildes).
    Genera la forma 'cruda normalizada' para matching doble-forma.
    """
    return _preprocesar_dual(texto)[1]


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
    "Programación y desarrollo": {
        "tipo": "dura",
        "variantes": ["programación", "desarrollo de software", "python", "java", "javascript", "código", "desarrollo web", "backend", "frontend"]
    },
    "Bases de datos y SQL": {
        "tipo": "dura",
        "variantes": ["bases de datos", "sql", "postgresql", "mysql", "modelado de datos", "consultas sql", "oracle"]
    },
    "Contabilidad y normas NIIF": {
        "tipo": "dura",
        "variantes": ["contabilidad", "normas niif", "tributaria", "declaración de renta", "auditoría contable", "revisoría fiscal"]
    },
    "Diseño gráfico y multimedia": {
        "tipo": "dura",
        "variantes": ["diseño gráfico", "illustrator", "photoshop", "edición de video", "diseño ui", "diseño ux", "multimedia"]
    },
    "Machine Learning e IA": {
        "tipo": "dura",
        "variantes": ["machine learning", "aprendizaje automático", "inteligencia artificial", "modelos predictivos", "deep learning", "nlp"]
    },
    "Redes y telecomunicaciones": {
        "tipo": "dura",
        "variantes": ["redes de computadores", "telecomunicaciones", "infraestructura de redes", "protocolos de comunicación", "enrutamiento"]
    },
    "Ciberseguridad y seguridad de la información": {
        "tipo": "dura",
        "variantes": ["ciberseguridad", "seguridad informática", "seguridad de la información", "hacking ético", "gestión de vulnerabilidades"]
    },
    "Arquitectura de software y cloud": {
        "tipo": "dura",
        "variantes": ["computación en la nube", "cloud computing", "aws", "azure", "docker", "microservicios", "arquitectura de software"]
    },
    "Primeros auxilios y seguridad en el trabajo": {
        "tipo": "dura",
        "variantes": ["primeros auxilios", "seguridad y salud en el trabajo", "sst", "salud ocupacional", "prevención de riesgos"]
    },
    "Investigación y metodología científica": {
        "tipo": "dura",
        "variantes": ["investigación científica", "metodología de la investigación", "redacción de artículos científicos", "revisión bibliográfica"]
    },
    "Automatización y optimización de procesos": {
        "tipo": "dura",
        "variantes": ["automatización de procesos", "optimización de procesos", "mejora continua", "lean", "diagramación de procesos"]
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
            variante_norm = re.sub(r"[_\-]+", " ", variante)
            # Forma lematizada (pipeline completo con spaCy)
            v_prep = preprocesar_texto(variante_norm)
            if v_prep:
                vars_limpias.add(v_prep)
            # Forma cruda normalizada (sin lematizar, solo minúsculas + quitar tildes)
            # Esto cubre los casos en que spaCy asigna POS distinto en aislamiento vs. contexto
            v_cruda = _quitar_tildes(variante_norm.lower().strip())
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


# Variables globales para cachear la compilación de la taxonomía (carga lazy)
_TAXONOMIA_PREP = None
_TIPOS_HABILIDAD = None
_PATRONES_COMPILADOS = None


def _asegurar_taxonomia():
    """Compila la taxonomía de forma lazy la primera vez que se requiere."""
    global _TAXONOMIA_PREP, _TIPOS_HABILIDAD, _PATRONES_COMPILADOS
    if _PATRONES_COMPILADOS is None:
        _TAXONOMIA_PREP, _TIPOS_HABILIDAD, _PATRONES_COMPILADOS = _compilar_taxonomia()
    return _TAXONOMIA_PREP, _TIPOS_HABILIDAD, _PATRONES_COMPILADOS


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
    _, _, patrones_compilados = _asegurar_taxonomia()
    ocupados = [False] * len(texto_preprocesado)
    matches = []

    for _, regex, etiqueta, variante in patrones_compilados:
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

_STOPWORDS_DINAMICAS: Set[str] = set()


_TAXONOMIA_BASE: Dict[str, Dict] = copy.deepcopy(TAXONOMIA_HABILIDADES_BRUTA)
_FIRMA_CURADURIAS: Optional[str] = None


def invalidar_cache_taxonomia():
    """Invalida la taxonomía compilada; la próxima sincronización la reconstruye desde la base."""
    global _TAXONOMIA_PREP, _TIPOS_HABILIDAD, _PATRONES_COMPILADOS, _FIRMA_CURADURIAS
    _TAXONOMIA_PREP = None
    _TIPOS_HABILIDAD = None
    _PATRONES_COMPILADOS = None
    _FIRMA_CURADURIAS = None
    _extraer_habilidades_cached.cache_clear()


def _aplicar_curaduria(termino_original: str, etiqueta_canonica: str, tipo: str, variantes: List[str], estado: str):
    """Integra una curaduría en la taxonomía en memoria (IA-15), sin recompilar.

    'aprobada' agrega o amplía la categoría canónica; 'descartada' la añade a las
    stopwords dinámicas para que TF-IDF no la vuelva a sugerir.
    """
    term_limpio = termino_original.lower().strip()
    if estado == "aprobada":
        vars_unificadas = list(set([termino_original, etiqueta_canonica] + (variantes or [])))
        if etiqueta_canonica in TAXONOMIA_HABILIDADES_BRUTA:
            existentes = TAXONOMIA_HABILIDADES_BRUTA[etiqueta_canonica].get("variantes", [])
            TAXONOMIA_HABILIDADES_BRUTA[etiqueta_canonica]["variantes"] = list(set(existentes + vars_unificadas))
        else:
            TAXONOMIA_HABILIDADES_BRUTA[etiqueta_canonica] = {
                "tipo": tipo if tipo in ("blanda", "dura") else "dura",
                "variantes": vars_unificadas,
            }
        _STOPWORDS_DINAMICAS.discard(term_limpio)
        for v in vars_unificadas:
            _STOPWORDS_DINAMICAS.discard(v.lower().strip())
    elif estado == "descartada":
        _STOPWORDS_DINAMICAS.add(term_limpio)
        for v in (variantes or []):
            _STOPWORDS_DINAMICAS.add(v.lower().strip())


def sincronizar_curadurias_bd(db) -> str:
    """Alinea la taxonomía en memoria con `habilidades_curadas` y devuelve su firma.

    Cada worker de Uvicorn tiene su propia memoria: la firma detecta altas, cambios y
    reversiones hechas en otro proceso. Si cambió, la taxonomía se reconstruye desde la
    base fija más las curadurías vigentes, de modo que una reversión deja de aplicarse.
    Las cachés de resultados incluyen la firma en su clave.
    """
    global _FIRMA_CURADURIAS
    from domain.models import HabilidadCurada
    curadas = db.query(HabilidadCurada).order_by(HabilidadCurada.id).all()
    firma = hashlib.sha256(repr([
        (c.id, c.termino_original, c.etiqueta_canonica, c.tipo, c.estado, sorted(c.variantes or []))
        for c in curadas
    ]).encode("utf-8")).hexdigest()[:16]
    if firma == _FIRMA_CURADURIAS:
        return firma
    TAXONOMIA_HABILIDADES_BRUTA.clear()
    TAXONOMIA_HABILIDADES_BRUTA.update(copy.deepcopy(_TAXONOMIA_BASE))
    _STOPWORDS_DINAMICAS.clear()
    for c in curadas:
        _aplicar_curaduria(c.termino_original, c.etiqueta_canonica, c.tipo, c.variantes or [], c.estado)
    invalidar_cache_taxonomia()
    _FIRMA_CURADURIAS = firma
    return firma


def _extraer_emergentes_tfidf(textos_residuales: List[str], top_n: int = 15) -> List[dict]:
    """
    Aplica TF-IDF con ngram_range=(1,2) sobre los textos residuales (ya libres de
    habilidades reconocidas) para descubrir términos emergentes no catalogados.

    Filtra ruido sintáctico con stopwords de relleno de encuestas y términos descartados por curaduría.
    Retorna lista de dicts: [{"termino": str, "score_tfidf": float, "frecuencia_documentos": int}]
    """
    # Filtrar textos vacíos
    textos_validos = [t for t in textos_residuales if t.strip()]
    if not textos_validos:
        return []

    todas_stopwords = list(set(_STOPWORDS_ENCUESTA) | _STOPWORDS_DINAMICAS)

    if TfidfVectorizer is not None:
        try:
            vectorizer = TfidfVectorizer(
                ngram_range=(1, 2),
                token_pattern=r"(?u)\b\w+\b",
                stop_words=todas_stopwords,
                min_df=1,
            )
            X = vectorizer.fit_transform(textos_validos)
            feature_names = vectorizer.get_feature_names_out()
            matriz = X.toarray()

            # Score máximo que alcanza cada término en los documentos
            scores_max = matriz.max(axis=0)
            # Frecuencia documental (en cuántas respuestas aparece)
            doc_freq = (matriz > 0).sum(axis=0)

            # Ordenar por score descendente
            ranking = np.argsort(scores_max)[::-1]

            emergentes = []
            for idx in ranking:
                term = str(feature_names[idx])
                # Excluir explícitamente términos descartados (unigramas o componentes)
                if term in _STOPWORDS_DINAMICAS or any(w in _STOPWORDS_DINAMICAS for w in term.split()):
                    continue
                emergentes.append({
                    "termino": term,
                    "score_tfidf": round(float(scores_max[idx]), 4),
                    "frecuencia_documentos": int(doc_freq[idx]),
                })
                if len(emergentes) >= top_n:
                    break

            return emergentes
        except Exception:
            pass

    # Fallback puro Python para TF-IDF si TfidfVectorizer no está disponible
    import math
    stopwords_set = set(_STOPWORDS_ENCUESTA)
    doc_words = []
    df_counter = Counter()
    for t in textos_validos:
        words = [w for w in re.findall(r"\b\w+\b", t.lower()) if w not in stopwords_set and len(w) > 2]
        ngrams = words + [f"{words[i]} {words[i+1]}" for i in range(len(words)-1)]
        doc_words.append(ngrams)
        df_counter.update(set(ngrams))

    n_docs = len(textos_validos)
    scores = {}
    for ngrams in doc_words:
        tf = Counter(ngrams)
        total_terms = len(ngrams) or 1
        for term, count in tf.items():
            idf = math.log((1 + n_docs) / (1 + df_counter[term])) + 1
            score = (count / total_terms) * idf
            if term not in scores or score > scores[term]:
                scores[term] = score

    sorted_terms = sorted(scores.items(), key=lambda x: x[1], reverse=True)[:top_n]
    return [
        {
            "termino": term,
            "score_tfidf": round(float(score), 4),
            "frecuencia_documentos": int(df_counter[term]),
        }
        for term, score in sorted_terms
    ]


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
        # 1. Preprocesar con AMBAS formas (single-pass memoizado)
        texto_lema, texto_crudo_norm = _preprocesar_dual(texto_crudo)

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
    _, tipos_habilidad, _ = _asegurar_taxonomia()
    habilidades_resultado = []
    for etiqueta, menciones in conteo_global.most_common():
        habilidades_resultado.append({
            "habilidad": etiqueta,
            "tipo": tipos_habilidad.get(etiqueta, "desconocido"),
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
@lru_cache(maxsize=16384)
def _extraer_habilidades_cached(texto_crudo: str) -> Tuple[str, ...]:
    """Extracción memoizada de habilidades por respuesta individual."""
    if not texto_crudo or not isinstance(texto_crudo, str):
        return ()

    texto_lema, texto_crudo_norm = _preprocesar_dual(texto_crudo)

    habs_lema = _extraer_habilidades_y_residual(texto_lema)[0] if texto_lema else set()
    habs_crudo = _extraer_habilidades_y_residual(texto_crudo_norm)[0] if texto_crudo_norm else set()

    return tuple(sorted(habs_lema | habs_crudo))


def extraer_habilidades_por_respuesta(texto_crudo: str) -> Set[str]:
    """
    Extrae el conjunto de habilidades únicas detectadas en una respuesta abierta
    utilizando el pipeline de doble-forma (lematizada + cruda) con memoización LRU.
    """
    return set(_extraer_habilidades_cached(texto_crudo))


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

    reglas_formateadas = []

    # 3. Intentar con mlxtend si está disponible
    if TransactionEncoder is not None and apriori is not None and association_rules is not None:
        try:
            te = TransactionEncoder()
            te_ary = te.fit(transacciones_validas).transform(transacciones_validas)
            df = pd.DataFrame(te_ary, columns=te.columns_)

            frequent_itemsets = apriori(
                df,
                min_support=min_soporte,
                use_colnames=True,
                max_len=2,
            )

            if not frequent_itemsets.empty:
                rules = association_rules(
                    frequent_itemsets,
                    metric="confidence",
                    min_threshold=min_confianza,
                )
                if not rules.empty:
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
        except Exception:
            reglas_formateadas = []

    # Fallback puro Python para pares 1 a 1 si mlxtend no está disponible o falló
    if not reglas_formateadas:
        pair_counts = Counter()
        item_counts = Counter()
        for trans in transacciones_validas:
            habs = sorted(set(trans))
            for h in habs:
                item_counts[h] += 1
            for i in range(len(habs)):
                for j in range(i + 1, len(habs)):
                    pair_counts[(habs[i], habs[j])] += 1
                    pair_counts[(habs[j], habs[i])] += 1

        for (ant, con), count in pair_counts.items():
            if count < min_ocurrencias:
                continue
            sup = count / total_validas
            if sup < min_soporte:
                continue
            conf = count / item_counts[ant]
            if conf < min_confianza:
                continue
            p_con = item_counts[con] / total_validas
            lift = conf / p_con if p_con > 0 else 0
            if lift >= 1.0:
                reglas_formateadas.append({
                    "si_menciona": ant,
                    "tambien_menciona": con,
                    "ocurrencias": count,
                    "soporte": round(float(sup), 4),
                    "confianza": round(float(conf), 4),
                    "lift": round(float(lift), 4),
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


def comparar_habilidades_temporales(
    textos_por_momento: Dict[int, List[str]],
    top_n: int = 25,
) -> Dict[str, Any]:
    """
    Compara longitudinalmente la frecuencia de habilidades demandadas entre
    los momentos de medición (M0: grado, M1: 1 año, M5: 5 años). (IA-06)

    Calcula menciones absolutas, porcentajes relativos por momento y deltas
    para clasificar la tendencia: 'crece', 'decrece', 'estable', 'emergente_en_m1', 'emergente_en_m5'.
    """
    momentos = [0, 1, 5]
    conteos_por_momento: Dict[int, Counter] = {}
    totales_respuestas: Dict[int, int] = {}
    totales_con_habilidad: Dict[int, int] = {}

    for m in momentos:
        textos = textos_por_momento.get(m, [])
        totales_respuestas[m] = len(textos)
        counter = Counter()
        con_hab = 0

        for t in textos:
            habs = extraer_habilidades_por_respuesta(t)
            if habs:
                con_hab += 1
                for h in set(habs):  # conteo binario por respuesta
                    counter[h] += 1

        conteos_por_momento[m] = counter
        totales_con_habilidad[m] = con_hab

    # Unir todas las habilidades detectadas en al menos un momento
    todas_habs: Set[str] = set()
    for m in momentos:
        todas_habs.update(conteos_por_momento[m].keys())

    _, tipos_hab, _ = _asegurar_taxonomia()

    filas = []
    for h in todas_habs:
        m0_count = conteos_por_momento[0].get(h, 0)
        m1_count = conteos_por_momento[1].get(h, 0)
        m5_count = conteos_por_momento[5].get(h, 0)

        tot_m0 = totales_con_habilidad[0] if totales_con_habilidad[0] > 0 else 1
        tot_m1 = totales_con_habilidad[1] if totales_con_habilidad[1] > 0 else 1
        tot_m5 = totales_con_habilidad[5] if totales_con_habilidad[5] > 0 else 1

        pct_m0 = round((m0_count / tot_m0) * 100.0, 1) if totales_con_habilidad[0] > 0 else 0.0
        pct_m1 = round((m1_count / tot_m1) * 100.0, 1) if totales_con_habilidad[1] > 0 else 0.0
        pct_m5 = round((m5_count / tot_m5) * 100.0, 1) if totales_con_habilidad[5] > 0 else 0.0

        delta_m1_m0 = round(pct_m1 - pct_m0, 1)

        # Determinar tendencia
        if m0_count == 0 and m1_count > 0:
            tendencia = "emergente_en_m1"
        elif m0_count == 0 and m1_count == 0 and m5_count > 0:
            tendencia = "emergente_en_m5"
        elif delta_m1_m0 >= 4.0:
            tendencia = "crece"
        elif delta_m1_m0 <= -4.0:
            tendencia = "decrece"
        else:
            tendencia = "estable"

        filas.append({
            "habilidad": h,
            "tipo": tipos_hab.get(h, "blanda"),
            "m0_menciones": m0_count,
            "m0_pct": pct_m0,
            "m0_porcentaje": pct_m0,
            "m1_menciones": m1_count,
            "m1_pct": pct_m1,
            "m1_porcentaje": pct_m1,
            "m5_menciones": m5_count,
            "m5_pct": pct_m5,
            "m5_porcentaje": pct_m5,
            "delta_m1_m0": delta_m1_m0,
            "tendencia": tendencia,
            "total_menciones": m0_count + m1_count + m5_count,
        })

    # Ordenar por total de menciones y limitar al top_n
    filas.sort(key=lambda x: (x["total_menciones"], x["m1_menciones"]), reverse=True)
    comparativa = filas[:top_n]

    return {
        "comparativa": comparativa,
        "totales_respuestas": totales_respuestas,
        "totales_con_habilidad": totales_con_habilidad,
    }


def generar_excel_habilidades(
    habilidades_data: Dict[str, Any],
    reglas_data: Dict[str, Any],
    comparativa_data: Optional[Dict[str, Any]] = None,
) -> "io.BytesIO":
    """
    Genera un archivo Excel (.xlsx) estructurado (IA-07):
      1. Habilidades Reconocidas
      2. Reglas de Asociación
      3. Candidatas Emergentes (TF-IDF)
      4. Comparativa Temporal M0-M1-M5 (si se suministra)
    Aplica cabecera institucional y anchos de columna automáticos.
    """
    import io
    import openpyxl
    from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
    from openpyxl.utils import get_column_letter

    wb = openpyxl.Workbook()

    header_fill = PatternFill(start_color="1A1818", end_color="1A1818", fill_type="solid")
    header_font = Font(name="Calibri", size=11, bold=True, color="FFFFFF")
    border_thin = Border(
        left=Side(style="thin", color="E2E3E1"),
        right=Side(style="thin", color="E2E3E1"),
        top=Side(style="thin", color="E2E3E1"),
        bottom=Side(style="thin", color="E2E3E1"),
    )

    # ── HOJA 1: Habilidades Reconocidas ──
    ws1 = wb.active
    ws1.title = "Habilidades Reconocidas"
    headers1 = ["Habilidad Canónica", "Tipo", "Menciones"]
    ws1.append(headers1)

    for h in habilidades_data.get("habilidades_reconocidas", []):
        ws1.append([h["habilidad"], h["tipo"].capitalize(), h["menciones"]])

    # ── HOJA 2: Reglas de Asociación ──
    ws2 = wb.create_sheet(title="Reglas de Asociación")
    headers2 = [
        "Si Menciona (Antecedente)",
        "También Menciona (Consecuente)",
        "Ocurrencias",
        "Soporte",
        "Confianza",
        "Lift",
    ]
    ws2.append(headers2)

    for r in reglas_data.get("reglas", []):
        ws2.append([
            r["si_menciona"],
            r["tambien_menciona"],
            r["ocurrencias"],
            f"{round(r['soporte'] * 100, 1)}%",
            f"{round(r['confianza'] * 100, 1)}%",
            round(r["lift"], 2),
        ])

    # ── HOJA 3: Candidatas Emergentes ──
    ws3 = wb.create_sheet(title="Candidatas Emergentes")
    headers3 = ["Término / Bigrama Emergente", "Score TF-IDF", "Frecuencia en Documentos"]
    ws3.append(headers3)

    for c in habilidades_data.get("candidatas_emergentes", []):
        ws3.append([
            c["termino"],
            round(c["score_tfidf"], 4),
            c["frecuencia_documentos"],
        ])

    sheets_to_style = [ws1, ws2, ws3]

    # ── HOJA 4: Comparativa Temporal (Opcional) ──
    if comparativa_data and comparativa_data.get("comparativa"):
        ws4 = wb.create_sheet(title="Comparativa Temporal M0-M1-M5")
        headers4 = [
            "Habilidad Canónica",
            "Tipo",
            "Total Menciones",
            "M0 Menciones",
            "% M0",
            "M1 Menciones",
            "% M1",
            "M5 Menciones",
            "% M5",
            "Delta M1-M0 (pp)",
            "Tendencia",
        ]
        ws4.append(headers4)

        for row in comparativa_data.get("comparativa", []):
            ws4.append([
                row.get("habilidad", ""),
                str(row.get("tipo", "")).capitalize(),
                row.get("total_menciones", 0),
                row.get("m0_menciones", 0),
                f"{row.get('m0_porcentaje', 0.0)}%",
                row.get("m1_menciones", 0),
                f"{row.get('m1_porcentaje', 0.0)}%",
                row.get("m5_menciones", 0),
                f"{row.get('m5_porcentaje', 0.0)}%",
                f"{row.get('delta_m1_m0', 0.0)} pp",
                row.get("tendencia", "").replace("_", " ").title(),
            ])
        sheets_to_style.append(ws4)

    # Estilizar hojas y autoajustar anchos
    for ws in sheets_to_style:
        for cell in ws[1]:
            cell.fill = header_fill
            cell.font = header_font
            cell.alignment = Alignment(horizontal="center", vertical="center")

        for row in ws.iter_rows(min_row=2):
            for cell in row:
                cell.border = border_thin
                cell.alignment = Alignment(vertical="center")

        for col in ws.columns:
            max_len = max(len(str(cell.value or "")) for cell in col)
            col_letter = get_column_letter(col[0].column)
            ws.column_dimensions[col_letter].width = max(max_len + 4, 12)

    output = io.BytesIO()
    wb.save(output)
    output.seek(0)
    return output
