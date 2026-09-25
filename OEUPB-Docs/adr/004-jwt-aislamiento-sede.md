# ADR-004 — JWT y aislamiento por sede

**Estado:** Aceptado

**Fecha de registro:** 2026-09-22

## Decisión

El backend emite JWT HS256 con identidad, rol y `sede_id`. Toda autorización de datos fuente usa el token validado y aplica el filtro de sede en cada consulta pertinente. El aislamiento cubre egresados, mediciones, respuestas individuales, archivos, historiales y perfiles.

La única visibilidad entre sedes permitida es la consulta de gráficas y métricas agregadas que el coordinador propietario haya publicado conforme a ADR-008. Esa publicación no amplía el alcance del JWT sobre los datos fuente.

## Consecuencias

- El cliente no puede elegir una sede para ampliar permisos.
- Los filtros deben aplicarse también en subconsultas e historiales.
- Una cuenta sin sede debe rechazarse en operaciones locales; nunca caer por defecto en sede 1.
- Los permisos de consulta y programas deben validarse en backend además del rol y la sede.
- La matriz normativa se mantiene en RN-03 y RN-06 a RN-11.
