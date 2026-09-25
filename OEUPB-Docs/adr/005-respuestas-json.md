# ADR-005 — Respuestas dinámicas en JSON

**Estado:** Aceptado

**Fecha de registro:** 2026-09-22

## Decisión

Conservar las respuestas variables del instrumento en `mediciones.respuestas` como JSON y mantener columnas relacionales para identidad, momento, año y sede.

## Consecuencias

- Cambios de preguntas no requieren una columna nueva por respuesta.
- Las variables usadas frecuentemente pueden requerir índices o proyecciones futuras.
- Debe existir un diccionario de preguntas para evitar depender de textos inconsistentes.
