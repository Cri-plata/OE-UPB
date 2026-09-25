# ADR-011 — Mantener rutas `/api/*` con evolución compatible

**Estado:** Aceptado

**Fecha de registro:** 2026-09-24

## Contexto

Todos los consumidores actuales usan `/api/*`. Introducir `/api/v1/*` ahora duplicaría rutas o exigiría una migración coordinada sin existir todavía una segunda versión incompatible del producto.

## Decisión

Mantener `/api/*` como contrato público vigente. Los cambios deben ser compatibles y verificarse contra el OpenAPI canónico. Solo se introducirá una versión de URL cuando exista un cambio incompatible que no pueda evolucionar mediante campos opcionales o una transición controlada.

## Consecuencias

- No se publican alias `/api/v1/*` sin una necesidad concreta.
- CI rechaza rutas fuera de `/api/*` y tipos frontend desactualizados.
- Una futura versión deberá coexistir temporalmente, documentar deprecación y contar con pruebas de ambos contratos.
