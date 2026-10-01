"""Comparación y normalización de nombres de programa entre sedes y cuentas (PRG-01 e IA-16).

No existe un catálogo institucional único de programas: los nombres provienen de las
cargas de encuestas históricas. Para evitar fragmentación muestral en el modelo de IA
y garantizar homogeneidad ("Ing. Sistemas", "Ingeniería de Sistemas - Diurna", "INGENIERIA DE SISTEMAS"),
este módulo proporciona:
  1. Limpieza básica y claves sin tildes (PRG-01).
  2. Limpieza determinística de prefijos, sufijos de jornada/sede y abreviaturas comunes (IA-16).
  3. Resolución difusa (fuzzy matching) basada en similitud de secuencia y tokens (IA-16).
"""

import unicodedata
import re
from difflib import SequenceMatcher
from typing import Optional, List, Dict, Set


def limpiar_nombre_programa(nombre) -> Optional[str]:
    """Nombre visible: sin espacios al inicio, al final ni repetidos."""
    if nombre is None:
        return None
    limpio = " ".join(str(nombre).split())
    return limpio or None


def clave_programa(nombre) -> str:
    """Genera clave insensible a mayúsculas, tildes y espacios repetidos (PRG-01)."""
    limpio = limpiar_nombre_programa(nombre) or ""
    sin_tildes = unicodedata.normalize("NFKD", limpio).encode("ascii", "ignore").decode("ascii")
    return sin_tildes.casefold()


def claves_programas(nombres) -> Set[str]:
    return {clave_programa(nombre) for nombre in nombres or [] if nombre}


# ─────────────────────────────────────────────────────────────────────────────
# IA-16: RESOLUCIÓN DIFUSA Y CANONIZACIÓN DE PROGRAMAS ACADÉMICOS
# ─────────────────────────────────────────────────────────────────────────────

_PREFIJOS_DESCARTABLES = [
    r"^PREGRADO\s+EN\s+",
    r"^PREGRADO\s+DE\s+",
    r"^PROGRAMA\s+DE\s+",
    r"^CARRERA\s+DE\s+",
    r"^FACULTAD\s+DE\s+",
    r"^ESCUELA\s+DE\s+",
    r"^DEPARTAMENTO\s+DE\s+",
]

_SUFIJOS_DESCARTABLES = [
    r"\s*-\s*NOCTURNA$",
    r"\s*-\s*DIURNA$",
    r"\s+NOCTURNA$",
    r"\s+DIURNA$",
    r"\s+NOCTURNO$",
    r"\s+DIURNO$",
    r"\s*\((?:NOCTURNA|DIURNA|NOCTURNO|DIURNO)\)$",
    r"\s*\((?:VIRTUAL|PRESENCIAL|A\s+DISTANCIA)\)$",
    r"\s*-\s*(?:VIRTUAL|PRESENCIAL|A\s+DISTANCIA)$",
    r"\s+(?:VIRTUAL|PRESENCIAL)$",
    r"\s*\((?:MEDELLIN|BUCARAMANGA|MONTERIA|PALMIRA|BOGOTA)\)$",
    r"\s*-\s*(?:MEDELLIN|BUCARAMANGA|MONTERIA|PALMIRA|BOGOTA)$",
]

_MAPA_ABREVIATURAS = {
    r"\bING\b": "INGENIERIA",
    r"\bADM\b": "ADMINISTRACION",
    r"\bADMIN\b": "ADMINISTRACION",
    r"\bLIC\b": "LICENCIATURA",
    r"\bESP\b": "ESPECIALIZACION",
    r"\bMG\b": "MAESTRIA",
    r"\bMGR\b": "MAESTRIA",
    r"\bMTRA\b": "MAESTRIA",
    r"\bDR\b": "DOCTORADO",
    r"\bDOC\b": "DOCTORADO",
    r"\bSIST\b": "SISTEMAS",
    r"\bNEG\b": "NEGOCIOS",
    r"\bINT\b": "INTERNACIONALES",
    r"\bINTL\b": "INTERNACIONALES",
    r"\bCOM\b": "COMUNICACION",
}

_DICCIONARIO_TILDE_PROGRAMAS = {
    "ingenieria": "Ingeniería",
    "administracion": "Administración",
    "comunicacion": "Comunicación",
    "pedagogia": "Pedagogía",
    "economia": "Economía",
    "psicologia": "Psicología",
    "teologia": "Teología",
    "filosofia": "Filosofía",
    "musica": "Música",
    "educacion": "Educación",
    "gestion": "Gestión",
    "diseno": "Diseño",
    "quimica": "Química",
    "fisica": "Física",
    "matematicas": "Matemáticas",
    "biologia": "Biología",
    "odontologia": "Odontología",
    "enfermeria": "Enfermería",
}


def _quitar_tildes_str(texto: str) -> str:
    """Elimina acentos y caracteres diacríticos."""
    nfkd = unicodedata.normalize("NFKD", texto)
    return "".join(c for c in nfkd if not unicodedata.combining(c))


def normalizar_forma_base(nombre: Optional[str]) -> str:
    """
    Limpia determinísticamente un nombre de programa:
      1. Mayúsculas y sin acentos.
      2. Remueve prefijos institucionales vacíos (Pregrado en, Programa de...).
      3. Remueve sufijos de jornada, modalidad y sede (- Diurna, Virtual...).
      4. Normaliza puntos de abreviaturas y expande términos (Ing. -> INGENIERIA).
    """
    if not nombre or not isinstance(nombre, str):
        return ""

    limpio = " ".join(nombre.strip().split())
    if not limpio:
        return ""

    texto_mayusc = _quitar_tildes_str(limpio.upper())

    # 1. Quitar prefijos
    for pref in _PREFIJOS_DESCARTABLES:
        texto_mayusc = re.sub(pref, "", texto_mayusc, flags=re.IGNORECASE)

    # 2. Quitar sufijos
    for suf in _SUFIJOS_DESCARTABLES:
        texto_mayusc = re.sub(suf, "", texto_mayusc, flags=re.IGNORECASE)

    # 3. Remover puntos de abreviatura pegados a letras (ej: ING. -> ING, INT. -> INT)
    texto_mayusc = re.sub(r"\b([A-Z]+)\.", r"\1", texto_mayusc)

    # 4. Expandir abreviaturas
    for abrev_regex, expansion in _MAPA_ABREVIATURAS.items():
        texto_mayusc = re.sub(abrev_regex, expansion, texto_mayusc, flags=re.IGNORECASE)

    # Re-limpiar espacios dobles generados
    return " ".join(texto_mayusc.split())


def _similitud_combinada(str1: str, str2: str) -> float:
    """
    Calcula similitud combinada entre dos cadenas:
    promedio ponderado de SequenceMatcher, tokens ordenados y contención de tokens.
    """
    if not str1 or not str2:
        return 0.0
    if str1 == str2:
        return 1.0

    # 1. Similitud de secuencia directa
    ratio_seq = SequenceMatcher(None, str1, str2).ratio()

    # 2. Similitud de tokens ordenados
    tokens1 = sorted(str1.split())
    tokens2 = sorted(str2.split())
    ratio_tokens_seq = SequenceMatcher(None, " ".join(tokens1), " ".join(tokens2)).ratio()

    # 3. Similitud Jaccard y Contención (para prefijos de programas como 'Ing. Sistemas' en 'Ing. de Sistemas e Informática')
    set1, set2 = set(tokens1), set(tokens2)
    jaccard = len(set1 & set2) / len(set1 | set2) if (set1 | set2) else 0.0
    min_len = min(len(set1), len(set2))
    contencion = len(set1 & set2) / min_len if min_len > 0 else 0.0

    score = 0.35 * ratio_seq + 0.25 * ratio_tokens_seq + 0.20 * jaccard + 0.20 * contencion
    return round(float(score), 4)


def _formato_titulo_respetuoso(texto_norm: str) -> str:
    """
    Convierte un texto normalizado a Capitalización Institucional (Title Case),
    respetando tildes de catálogo institucional y conectores en minúsculas (de, en, y, e, para).
    """
    conectores = {"de", "en", "y", "e", "para", "la", "el", "los", "las", "del", "al"}
    palabras = texto_norm.lower().split()
    if not palabras:
        return ""

    resultado = []
    for i, p in enumerate(palabras):
        if p in _DICCIONARIO_TILDE_PROGRAMAS:
            resultado.append(_DICCIONARIO_TILDE_PROGRAMAS[p])
        elif i == 0 or p not in conectores:
            resultado.append(p.capitalize())
        else:
            resultado.append(p)

    return " ".join(resultado)


def canonizar_programa(
    nombre: Optional[str],
    catalogo_canonica: Optional[List[str]] = None,
    umbral_similitud: float = 0.85,
) -> str:
    """
    Devuelve la forma canónica estandarizada de un programa académico.

    Args:
        nombre: Nombre de programa observado (con posibles abreviaturas o sufijos).
        catalogo_canonica: Lista de nombres oficiales conocidos para resolución difusa.
        umbral_similitud: Mínimo puntaje de concordancia difusa para adoptar la forma
                          del catálogo (default 0.85 = 85%).

    Returns:
        Nombre canónico homogéneo.
    """
    if not nombre or not isinstance(nombre, str):
        return "Otros"

    forma_base = normalizar_forma_base(nombre)
    if not forma_base:
        return "Otros"

    if catalogo_canonica:
        mejor_match = None
        mejor_score = 0.0

        for canon in catalogo_canonica:
            canon_base = normalizar_forma_base(canon)
            score = _similitud_combinada(forma_base, canon_base)
            if score > mejor_score:
                mejor_score = score
                mejor_match = canon

        if mejor_match and mejor_score >= umbral_similitud:
            return mejor_match.strip()

    # Si no hay match difuso en el catálogo, devolver la forma base formateada como título
    return _formato_titulo_respetuoso(forma_base)


def construir_mapa_canonico(
    programas_observados: List[str],
    umbral_similitud: float = 0.85,
) -> Dict[str, str]:
    """
    Dado un conjunto de nombres observados en la base de datos (con repeticiones y variantes),
    construye un diccionario {nombre_observado: nombre_canonico_unificado}.
    Las formas más completas y con acentuación correcta actúan como anclas canónicas.
    """
    limpios = [p.strip() for p in programas_observados if p and p.strip()]
    if not limpios:
        return {}

    # Agrupar formas observadas por su forma base determinística
    grupos_base: Dict[str, List[str]] = {}
    for p in limpios:
        base = normalizar_forma_base(p)
        grupos_base.setdefault(base, []).append(p)

    # Identificar nombres canónicos para cada grupo base
    canones_identificados: List[str] = []
    mapa_base_a_canon: Dict[str, str] = {}

    for base, variantes in grupos_base.items():
        # La forma canónica deriva de la base limpia para excluir sufijos y abreviaturas
        canon_tit = _formato_titulo_respetuoso(base)
        mapa_base_a_canon[base] = canon_tit
        canones_identificados.append(canon_tit)

    # Segunda pasada: unificar entre grupos base que tengan alta similitud difusa (ej. contención / fuzzy)
    mapa_final: Dict[str, str] = {}
    for p in limpios:
        base = normalizar_forma_base(p)
        canon = canonizar_programa(
            nombre=p,
            catalogo_canonica=canones_identificados,
            umbral_similitud=umbral_similitud,
        )
        mapa_final[p] = canon

    return mapa_final

