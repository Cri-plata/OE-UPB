# ADR-007 — OpenAPI como contrato canónico

**Estado:** Aceptado

**Fecha de registro:** 2026-09-22

## Decisión

Usar el OpenAPI generado por FastAPI como fuente de verdad del contrato HTTP. Los DTO TypeScript/Pydantic duplicados deben generarse o validarse contra él.

## Consecuencias

- Todo cambio de endpoint incluye regeneración y revisión del contrato.
- La documentación narrativa explica intención, pero no redefine payloads.
- El versionado se resuelve en ADR-011: se mantiene `/api/*` hasta que exista una incompatibilidad que justifique otra versión.
