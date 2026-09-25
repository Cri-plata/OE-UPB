# ADR-012 — Conservar `Egresado`–`Medicion` y modelar intentos explícitos

**Estado:** Aceptado

**Fecha de registro:** 2026-09-24

## Contexto

El modelo implementado, los endpoints y el ETL operan sobre `Egresado` y `Medicion`. La propuesta histórica de separar `historial_academico` y `encuestas_laborales` no dispone de reglas de migración completas y supondría reescribir cálculos sin beneficio probado para el alcance actual.

## Decisión

Conservar `Egresado`–`Medicion`. Cada medición tiene carga, sede, momento, cohorte, número de intento, fecha de registro y respuestas JSON. Se permiten múltiples intentos identificados y cada indicador declara su política de selección; inicialmente se usa el intento más reciente y se conservan todas las mediciones anónimas en agregados autorizados.

## Consecuencias

- `historial_academico` y `encuestas_laborales` no forman parte del modelo objetivo vigente.
- La doble titulación de una misma carga continúa resolviéndose conforme a ADR-006.
- Cualquier normalización futura requiere un ADR nuevo, migración verificable y equivalencia demostrada de indicadores.
