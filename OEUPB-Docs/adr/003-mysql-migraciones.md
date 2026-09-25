# ADR-003 — MySQL y migraciones formales

**Estado:** Aceptado

**Fecha de registro:** 2026-09-22

## Decisión

MySQL continúa como base de datos. Toda evolución futura debe gestionarse mediante migraciones versionadas, preferiblemente Alembic.

## Estado

MySQL y SQLAlchemy están implementados. Alembic contiene un baseline, migraciones incrementales verificadas y el procedimiento de adopción para bases existentes. Los scripts ad hoc de esquema fueron retirados.

## Consecuencias

- Alembic es el único mecanismo de evolución del esquema.
- El esquema SQL documental continúa como referencia revisable del estado esperado.
- Las operaciones deben respaldar la base antes de una migración productiva y seguir el runbook de rollback.
