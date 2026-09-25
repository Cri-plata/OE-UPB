# Estrategia de contratos HTTP

**Estado:** verificado el 2026-09-24

## Fuente canónica

El contrato HTTP canónico es [`../specs/api/openapi.json`](../specs/api/openapi.json), generado desde la aplicación FastAPI actual.

Angular consume `src/app/data/api/generated-api.models.ts`, generado desde OpenAPI mediante `tools/generate_api_types.py`. Los archivos de `OEUPB-Contracts/` quedan como compatibilidad histórica y no son importados por el frontend.

## Convenciones actuales

- Base local del backend: `http://localhost:8000`.
- Rutas actuales: `/api/*`, decisión cerrada por ADR-011.
- Autenticación: `Authorization: Bearer <JWT>`.
- Errores: esquema `ErrorResponse` con `detail` (texto, u objeto `{codigo, mensaje}` cuando el cliente debe distinguir el caso). Cada router protegido declara 401/403 y cada endpoint sus códigos propios (`presentation/errores.py`). El 422 de validación de Pydantic conserva el esquema `HTTPValidationError`; la carga y la publicación documentan su propio 422.
- Operaciones obsoletas: se marcan con `deprecated: true` y se conservan por compatibilidad (por ejemplo, `DELETE /api/usuarios/{id}`).
- Cargas: `multipart/form-data`.

## Flujo de cambio de contrato

1. Escribir/actualizar prueba del endpoint.
2. Cambiar modelos y router FastAPI.
3. Regenerar OpenAPI.
4. Revisar el diff por breaking changes.
5. Actualizar tipos del frontend o adaptadores.
6. Ejecutar pruebas de ambos componentes.
7. Actualizar trazabilidad y changelog.

## Validación automática

- `npm run generate:api` regenera tipos.
- `npm run check:api` detecta tipos desactualizados.
- `python tools/validate_contracts.py` verifica rutas, respuestas tipadas, ausencia de URLs duplicadas y consumidores heredados.
- `test_openapi_contract.py` compara la aplicación FastAPI con el archivo canónico.
