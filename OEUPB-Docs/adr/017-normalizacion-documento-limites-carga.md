# ADR-017 — Normalización del documento de identidad y límites de carga

**Estado:** Aceptado

**Fecha:** 2026-09-25

## Contexto

RN-01 usa el documento como identificador único, pero había dos validaciones distintas (egresado: 3-50 caracteres libres; usuario: 6-20 dígitos) y ninguna normalización, así que "1.098.765.432" y "1098765432" eran egresados distintos. La carga no tenía límites y respondía 200 con errores cuando rechazaba un archivo (auditoría 05: B-13, B-14).

## Decisión

1. **Normalización única** (`application/documentos.py`): se eliminan espacios, puntos y guiones, y el texto pasa a mayúsculas. Se conservan las letras (pasaporte, cédula de extranjería) y los ceros a la izquierda. El resultado debe tener entre 5 y 20 letras o números.
2. La regla aplica a las cargas, al directorio manual (incluidas las rutas `/{documento}`) y al alta de cuentas. Pandas lee la columna `NUMERO_DOCUMENTO` como texto para no perder ceros ni letras.
3. **Límites de carga:** 25 MB (413) y 50.000 filas con datos (422).
4. **Rechazo de una carga:** 422 con el cuerpo `{"detail": {"mensaje", "errores": [{fila, columna, error}]}}`. Las filas usan la numeración de Excel (el encabezado es la fila 1). Un documento inválido rechaza el archivo completo (RN-20).
5. La migración `i6e04c1f3a52` normaliza los documentos existentes en `egresados`, `mediciones`, `egresados_sedes` y `auditoria_egresados`. Se detiene si dos documentos quedarían iguales y no se puede revertir.

## Consecuencias

- Una persona con documento alfanumérico puede tener cuenta.
- Los documentos de menos de 5 caracteres, que se aceptaban antes, ahora se rechazan.
- Los documentos que ya estaban persistidos y siguen siendo inválidos tras normalizarlos se conservan sin cambios.
