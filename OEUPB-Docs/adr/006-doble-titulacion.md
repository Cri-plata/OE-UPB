# ADR-006 — Tratamiento de doble titulación

**Estado:** Aceptado

**Fecha de registro:** 2026-09-22

## Decisión

Dentro de una carga, cuando un documento aparece varias veces, ordenar por `FECHA_GRADO` y conservar el registro más reciente. Las filas anónimas se procesan por separado para no colapsarlas entre sí.

## Consecuencias

- El resultado debe informar cuántos casos fueron resueltos.
- La regla necesita pruebas para fechas inválidas, empates y programas diferentes.
- No define por sí sola cómo modelar múltiples títulos históricos; esa decisión pertenece a DB-02.
