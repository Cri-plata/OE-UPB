# ADR-001 — Arquitectura por capas

**Estado:** Aceptado

**Fecha de registro:** 2026-09-22

## Decisión

Mantener una dirección de Clean Architecture: frontend con Domain/Data/Presentation y backend con Domain/Application/Infrastructure/Presentation.

## Contexto

Las carpetas ya existen, pero el cumplimiento es parcial: componentes Angular llaman HTTP directamente y routers FastAPI contienen lógica de negocio y persistencia.

## Consecuencias

- Las nuevas capacidades deben respetar las fronteras.
- La deuda existente se refactoriza gradualmente y con pruebas.
- No se afirmará que la arquitectura es “completa” mientras las dependencias reales no lo demuestren.
