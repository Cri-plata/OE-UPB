# ADR-016 — Clasificación laboral y formalidad a partir de los cuestionarios OLE

**Estado:** Aceptado

**Fecha:** 2026-09-25

## Contexto

RN-16 exige clasificar el estado laboral en `empleado`, `independiente`, `estudiante` y `sin_empleo`, y tratar la formalidad como un atributo separado. El cálculo anterior solo usaba "¿realiza alguna actividad remunerada?", una pregunta que no existe en el cuestionario del momento 0. Además, la pregunta de ingreso del momento 0 dice "SMMLV", así que el filtro `smlv` la omitía (ANA-01). Los nombres de las preguntas y sus opciones de respuesta se verificaron en la base local el 2026-09-25, sin leer datos personales.

## Decisión

1. **Seguimiento (M1 y M5)**, "¿realiza alguna actividad remunerada?":
   - `NO` → `sin_empleo`.
   - `SI` → se clasifica según la posición ("En la actividad remunerada que usted realiza actualmente es"): `Empleado` → `empleado`; contratista por prestación de servicios, cuenta propia o propietario → `independiente`.
2. **Momento 0**, "aparte de estudiar, ¿se dedica a trabajar…?":
   - `No` → `estudiante`.
   - `Si` → se clasifica según "¿En este trabajo usted es?": empleado dependiente o empresa familiar → `empleado`; trabajador independiente → `independiente`; practicante o pasante → `estudiante`.
3. Una medición sin información suficiente queda sin clasificar y no entra en los denominadores.
4. **Tasa de empleabilidad** = (empleado + independiente) / clasificados.
5. **Formalidad**, solo en el seguimiento, que es donde se pregunta el tipo de contrato: `formal` = empleado con contrato laboral (término indefinido, fijo u obra labor); `no_formal` = independiente. Un empleado sin tipo de contrato informado no se clasifica. En M0 la formalidad es `null`.
6. **Salario**: se reconoce la pregunta de ingreso mensual en "SMLV", "SMMLV" o "salarios mínimos". Un rango se resume en su punto medio, y el reporte muestra el promedio, el mínimo, la mediana y el máximo.
7. **Comparación entre momentos (HU-08)**: solo se emparejan egresados identificados de la misma sede y cohorte, y cada programa necesita al menos 5 pares con dato en ambos momentos (RN-26).

## Consecuencias

- Las preguntas se reconocen por fragmentos de su nombre normalizado, no por su número, porque la numeración cambia entre cuestionarios.
- El mapeo de M5 supone la misma redacción que M1; debe verificarse cuando existan datos de M5.
- Si cambia la redacción de los cuestionarios del OLE, hay que actualizar `application/indicadores.py` y `tests/test_reportes_analiticos.py`.
