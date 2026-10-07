# ADR-020 — Alcance de la IA, propiedad y privacidad de publicaciones y cargas por cohorte

**Estado:** Aceptado

**Fecha:** 2026-10-03

## Contexto

La [auditoría de requerimientos 07](../audits/07-auditoria-requerimientos.md) detectó que el módulo de IA exponía métricas de varias sedes a `Admin_CTIC` y permitía curar términos sin control de autoría. También señaló que el título de una publicación era texto libre sin validar y que varias situaciones límite de la publicación y de la carga no tenían una decisión explícita. Producto respondió el formulario de decisiones el 2026-10-03.

## Decisión

1. **Límite entre sedes.** Lo único que un coordinador ve de otra sede son las gráficas que su coordinador publicó (RN-09, RN-10). Ningún endpoint calcula métricas de otras sedes. `GET /api/ia/prediccion-benchmark-sedes` queda restringido a `Coordinador_Sede` y solo evalúa la sede del JWT. `Admin_CTIC` no accede a la analítica ni a la IA.
2. **Curaduría de habilidades.** La taxonomía curada (`habilidades_curadas`) es institucional y la comparten todas las sedes, porque contiene términos, no datos fuente. Solo `Coordinador_Sede` puede listarla, curarla o revertirla. Un término curado solo lo modifica o revierte su autor; otro coordinador recibe 409.
3. **Anonimización del texto libre de la IA.** Antes de analizarlo, mostrarlo, exportarlo o curarlo, el texto de las preguntas abiertas se anonimiza: se retiran correos, números largos, documento, nombre y apellido del egresado (RN-04).
4. **Un coordinador activo por sede.** Se asume que cada sede tiene un único coordinador activo. Por eso la serie de versiones de una gráfica se identifica por `(sede_id, grafica_key)` y no por coordinador. El backend no impone el supuesto. Si una sede llegara a tener dos coordinadores activos, el segundo que publique la misma gráfica reemplazaría la versión del primero.
5. **Título de la publicación.** El backend rechaza con 422 los títulos que contengan correos, enlaces o secuencias de 5 o más dígitos (aunque estén separadas por puntos o espacios de miles). Los años y rangos de cohorte siguen siendo válidos.
6. **Revelación por diferencia.** El umbral k = 5 de ADR-015 se aplica por celda. La posibilidad de deducir una celda suprimida restando dos publicaciones con filtros solapados se acepta como riesgo residual. El coordinador es responsable de evitarlo al confirmar la revisión de privacidad.
7. **Audiencia.** Un usuario de consulta ve una publicación si tiene `ver_publicaciones`, el permiso del origen y al menos un programa en común con ella. "Compatible" (RF-37) significa eso. La gráfica puede mostrar métricas agregadas de otros programas incluidos en la publicación.
8. **Un archivo por cohorte.** Cada combinación de sede, momento y año de grado se carga en un único archivo consolidado. Una recarga reemplaza la versión vigente completa (RN-12). No se admiten cargas parciales por facultad o programa.

## Consecuencias

- Se actualizan RN-01, RN-07, RN-12, RN-14, RN-24 y RN-25, y se agrega RN-32 (módulo de IA). Se corrigen RF-17, RF-37, RF-71 y RNF-05, HU-02, HU-05, HU-06, HU-10 y HU-13, CU-09 y CU-10, la matriz y la arquitectura.
- `ia_router.py` y `publicaciones_router.py` aplican los puntos 1, 2, 3 y 5, con pruebas en `tests/test_ia_alcance.py` y `tests/test_publicaciones.py`.
- Quedan en el backlog los cambios de interfaz que requieren mockup: el aviso de reemplazo en la carga, el recordatorio de diferencias en la confirmación de privacidad y el retiro de publicaciones de un coordinador anterior.
