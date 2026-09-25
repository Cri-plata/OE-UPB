import re
import unicodedata
from collections import Counter

PII = [
    (re.compile(r"\b[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}\b", re.I), "[CORREO]"),
    (re.compile(r"\b\+?\d[\d\s().-]{6,}\d\b"), "[DATO_NUMERICO]"),
]
COMPETENCIAS = {
    "Comunicación": ("comunicacion", "comunicar", "presentacion"),
    "Liderazgo": ("liderazgo", "liderar", "lider"),
    "Trabajo en equipo": ("trabajo en equipo", "colaboracion", "equipo"),
    "Tecnología y datos": ("python", "programacion", "datos", "analitica", "tecnologia"),
    "Idiomas": ("ingles", "idioma", "bilingue"),
    "Gestión de proyectos": ("proyecto", "gestion", "planificacion"),
    "Adaptabilidad": ("adaptacion", "adaptabilidad", "cambio"),
}
NEGATIVOS = ("desemple", "sin empleo", "no encuentro", "dificil conseguir", "pocas oportunidades", "salario bajo", "inestabilidad")
CLAVES_ABIERTAS = ("coment", "observ", "competenc", "habilidad", "suger", "porque", "por que", "abierta")


def normalizar(texto: str) -> str:
    return "".join(c for c in unicodedata.normalize("NFD", texto.lower()) if unicodedata.category(c) != "Mn")


def anonimizar(texto: str, datos_personales: list[str] | None = None) -> str:
    resultado = texto
    for patron, reemplazo in PII:
        resultado = patron.sub(reemplazo, resultado)
    for dato in datos_personales or []:
        if dato and len(dato.strip()) >= 3:
            resultado = re.sub(re.escape(dato.strip()), "[PERSONA]", resultado, flags=re.I)
    return resultado


def extraer_textos(respuestas: dict, datos_personales: list[str] | None = None) -> list[str]:
    textos = []
    for clave, valor in (respuestas or {}).items():
        if isinstance(valor, str) and any(fragmento in normalizar(str(clave)) for fragmento in CLAVES_ABIERTAS):
            limpio = anonimizar(valor.strip(), datos_personales)
            if limpio:
                textos.append(limpio)
    return textos


def clasificar(textos: list[str]) -> tuple[Counter, int]:
    conteo = Counter()
    negativos = 0
    for texto in textos:
        normal = normalizar(texto)
        for categoria, palabras in COMPETENCIAS.items():
            if any(palabra in normal for palabra in palabras):
                conteo[categoria] += 1
        if any(patron in normal for patron in NEGATIVOS):
            negativos += 1
    return conteo, negativos
