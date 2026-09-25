# ADR-002 — FastAPI como backend oficial

**Estado:** Aceptado

**Fecha de registro:** 2026-09-22

## Decisión

FastAPI es el framework HTTP oficial. Se retira la ambigüedad documental “FastAPI/Flask”.

## Consecuencias

- OpenAPI se genera desde FastAPI.
- Pydantic define los payloads implementados.
- Uvicorn es el servidor local; producción debe usar una configuración supervisada detrás de proxy.
