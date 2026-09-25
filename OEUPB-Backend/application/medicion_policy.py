"""Reglas explícitas de selección de intentos para indicadores agregados."""

POLITICAS_INDICADORES = {
    "reporte_general": "ultimo_intento_identificado_y_todos_los_anonimos",
    "tendencias": "ultimo_intento_identificado_y_todos_los_anonimos",
    "explorador": "ultimo_intento_identificado_y_todos_los_anonimos",
}


def seleccionar_intentos(items):
    """Conserva el intento más reciente por persona/alcance y todos los anónimos.

    Acepta mediciones o tuplas cuyo primer elemento sea una medición, para poder
    aplicarse sin alterar la forma de las consultas existentes.
    """
    seleccionados = {}
    anonimos = []
    for item in items:
        medicion = item if hasattr(item, "egresado_documento") else item[0]
        if medicion.egresado_documento is None:
            anonimos.append(item)
            continue
        clave = (
            medicion.egresado_documento,
            medicion.sede_id,
            medicion.momento,
            medicion.anio,
        )
        anterior = seleccionados.get(clave)
        if anterior is None:
            seleccionados[clave] = item
            continue
        med_anterior = anterior if hasattr(anterior, "egresado_documento") else anterior[0]
        if (medicion.intento, medicion.id) > (med_anterior.intento, med_anterior.id):
            seleccionados[clave] = item
    return list(seleccionados.values()) + anonimos
