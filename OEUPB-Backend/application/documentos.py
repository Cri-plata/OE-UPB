"""Normalización única del documento de identidad (ETL-01).

Se eliminan espacios, puntos y guiones y se pasa a mayúsculas. Se conservan las
letras (pasaporte, cédula de extranjería) y los ceros a la izquierda. La misma
regla aplica a cargas, directorio manual y cuentas de usuario.
"""

import math
import re

LONGITUD_MINIMA = 5
LONGITUD_MAXIMA = 20
MENSAJE_INVALIDO = (
    f"El documento debe tener entre {LONGITUD_MINIMA} y {LONGITUD_MAXIMA} letras o números "
    "(se ignoran espacios, puntos y guiones)"
)
_SEPARADORES = re.compile(r"[\s.\-]")
_FLOTANTE_ENTERO = re.compile(r"^\d+\.0+$")
_VALIDO = re.compile(rf"^[A-Z0-9]{{{LONGITUD_MINIMA},{LONGITUD_MAXIMA}}}$")


def normalizar_documento(valor) -> str | None:
    """Devuelve el documento normalizado o `None` si está vacío."""
    if valor is None or (isinstance(valor, float) and math.isnan(valor)):
        return None
    texto = str(valor).strip()
    # Excel/Pandas pueden entregar un número entero como "1098765432.0".
    if _FLOTANTE_ENTERO.match(texto):
        texto = texto.split(".", 1)[0]
    texto = _SEPARADORES.sub("", texto).upper()
    if texto in ("", "NAN", "NONE"):
        return None
    return texto


def es_documento_valido(documento: str | None) -> bool:
    return documento is not None and bool(_VALIDO.match(documento))


def normalizar_documento_obligatorio(valor) -> str:
    """Normaliza y valida; lanza `ValueError` con un mensaje apto para el usuario."""
    documento = normalizar_documento(valor)
    if not es_documento_valido(documento):
        raise ValueError(MENSAJE_INVALIDO)
    return documento
