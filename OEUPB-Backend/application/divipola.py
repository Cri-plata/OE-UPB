"""Diccionario DIVIPOLA (DANE) para las preguntas de ubicación de las encuestas OLE.

Las preguntas de lugar (residencia actual, residencia al estudiar, al graduarse del
colegio, al primer empleo, nacimiento de la madre, ubicación de la empresa) llegan
como tres columnas: ``(DEPARTAMENTO)``, ``(MUNICIPIO)`` y ``(PAIS)``. Departamento y
municipio usan códigos DIVIPOLA; Excel suele quitarles el cero inicial (``5`` por
``05``, ``5001`` por ``05001``) o agregar ``.0``. El país usa otro estándar y no se
traduce aquí.

Fuente: ``data/divipola.json``, generado a partir de los listados del DANE
(departamentos 2012 y municipios 2007) con los complementos documentados en el
propio archivo.
"""

from __future__ import annotations

import json
import re
import unicodedata
from functools import lru_cache
from pathlib import Path
from typing import Literal, Optional

_ARCHIVO = Path(__file__).with_name("data") / "divipola.json"
_CONECTORES = {"de", "del", "la", "las", "el", "los", "y", "e", "en"}
_SUFIJO_DEPARTAMENTO = re.compile(r"\(\s*DEPARTAMENTO\s*\)\s*$", re.IGNORECASE)
_SUFIJO_MUNICIPIO = re.compile(r"\(\s*MUNICIPIO\s*\)\s*$", re.IGNORECASE)

TipoUbicacion = Literal["departamento", "municipio"]


@lru_cache(maxsize=1)
def _datos() -> dict:
    return json.loads(_ARCHIVO.read_text(encoding="utf-8"))


def _titulo(nombre: str) -> str:
    """'EL CARMEN DE VIBORAL' -> 'El Carmen de Viboral'; conserva tildes y 'D.C.'."""
    palabras = []
    for i, palabra in enumerate(nombre.lower().split()):
        if palabra.rstrip(",") in ("d.c.", "d.c"):
            palabras.append(palabra.upper())
        elif i > 0 and palabra in _CONECTORES:
            palabras.append(palabra)
        else:
            palabras.append(palabra[:1].upper() + palabra[1:])
    return " ".join(palabras)


def _clave(texto: str) -> str:
    """Forma comparable: sin tildes, signos ni mayúsculas ('Bogotá, D.C.' -> 'bogotadc')."""
    sin_tildes = "".join(c for c in unicodedata.normalize("NFD", texto) if unicodedata.category(c) != "Mn")
    return re.sub(r"[^a-z0-9]", "", sin_tildes.lower())


def _digitos(valor) -> Optional[str]:
    if valor is None:
        return None
    texto = str(valor).strip()
    if re.fullmatch(r"\d+\.0+", texto):
        texto = texto.split(".", 1)[0]
    return texto if texto.isdigit() else None


def normalizar_codigo_departamento(valor) -> Optional[str]:
    """Código de 2 dígitos, o ``None`` si el valor no es un código posible."""
    texto = _digitos(valor)
    return texto.zfill(2) if texto and len(texto) <= 2 else None


def normalizar_codigo_municipio(valor) -> Optional[str]:
    """Código de 5 dígitos (repone el cero inicial), o ``None`` si no es un código posible."""
    texto = _digitos(valor)
    return texto.zfill(5) if texto and len(texto) in (4, 5) else None


def nombre_departamento(valor) -> Optional[str]:
    codigo = normalizar_codigo_departamento(valor)
    return _datos()["departamentos"].get(codigo) if codigo else None


def nombre_municipio(valor) -> Optional[str]:
    codigo = normalizar_codigo_municipio(valor)
    nombre = _datos()["municipios"].get(codigo) if codigo else None
    return _titulo(nombre) if nombre else None


def tipo_columna_ubicacion(columna: str) -> Optional[TipoUbicacion]:
    """Indica si la columna es la parte de departamento o de municipio de una pregunta de lugar."""
    if _SUFIJO_MUNICIPIO.search(columna or ""):
        return "municipio"
    if _SUFIJO_DEPARTAMENTO.search(columna or ""):
        return "departamento"
    return None


def describir_ubicacion(columna: str, valor):
    """Traduce el código de una columna de ubicación a su nombre.

    Municipio: "Bucaramanga (Santander)". Departamento: "Santander". Si la columna no es
    de ubicación o el código no está en el diccionario, devuelve el valor sin cambios:
    nunca se inventa un lugar.
    """
    tipo = tipo_columna_ubicacion(columna)
    if tipo == "municipio":
        municipio = nombre_municipio(valor)
        if municipio:
            departamento = nombre_departamento(normalizar_codigo_municipio(valor)[:2])
            # Bogotá o San Andrés ya nombran a su departamento: no se repite entre paréntesis.
            if not departamento or _clave(municipio).startswith(_clave(departamento)):
                return municipio
            return f"{municipio} ({departamento})"
    elif tipo == "departamento":
        departamento = nombre_departamento(valor)
        if departamento:
            return departamento
    return valor


def describir_respuestas(respuestas: Optional[dict]) -> dict:
    """Copia de las respuestas con las columnas de ubicación traducidas (para mostrar)."""
    return {clave: describir_ubicacion(clave, valor) for clave, valor in (respuestas or {}).items()}
