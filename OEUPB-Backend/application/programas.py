"""Comparación de nombres de programa entre sedes y cuentas (PRG-01).

No existe un catálogo institucional de programas: los nombres provienen de las
cargas. Para que "Ingeniería de Sistemas" y "ingenieria  de sistemas" se traten
como el mismo programa, toda comparación usa una clave sin mayúsculas, tildes ni
espacios repetidos. El nombre visible conserva la forma observada.
"""

import unicodedata


def limpiar_nombre_programa(nombre) -> str | None:
    """Nombre visible: sin espacios al inicio, al final ni repetidos."""
    if nombre is None:
        return None
    limpio = " ".join(str(nombre).split())
    return limpio or None


def clave_programa(nombre) -> str:
    limpio = limpiar_nombre_programa(nombre) or ""
    sin_tildes = unicodedata.normalize("NFKD", limpio).encode("ascii", "ignore").decode("ascii")
    return sin_tildes.casefold()


def claves_programas(nombres) -> set[str]:
    return {clave_programa(nombre) for nombre in nombres or [] if nombre}
