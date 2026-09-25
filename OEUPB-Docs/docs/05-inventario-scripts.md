# Inventario de scripts y artefactos temporales

**Fecha de cierre:** 2026-09-24  
**Estado:** ejecutado y verificado.

## Resultado

La revisión individual confirmó que los parches, diagnósticos hardcodeados y generadores numerados ya habían cumplido su propósito o fueron sustituidos por código, pruebas y migraciones formales. Se retiraron 73 scripts históricos de reparación/diagnóstico/desarrollo; su recuperación permanece disponible en el historial de Git.

También se retiraron tres pruebas manuales de raíz que ya habían sido convertidas a la suite automatizada.

| Clasificación | Decisión |
|---|---|
| `patch_*`, `fix_*`, `create_explorador_*` | Retirados; el resultado ya vive en el producto |
| `check_*` con rutas o datos incorporados | Retirados; las comprobaciones vigentes viven en pruebas/validadores |
| `fill_fake_data*.py` y `generar_excels.py` | Sustituidos por `OEUPB-Backend/scripts/dev/generate_excel_fixtures.py` |
| `add_column.py`, `init_db.py`, `limpiar_db.py` | Retirados; Alembic y los runbooks son la vía autorizada |
| pruebas manuales de raíz | Retiradas tras su conversión a `OEUPB-Backend/tests/` |
| `read_pptx.py`, `update_changelog.py` | Retirados por no tener flujo vigente parametrizado |

## Herramientas conservadas

- `tools/validate_docs.py`: enlaces y estructura documental.
- `tools/validate_contracts.py`: OpenAPI, tipos y consumidores.
- `tools/validate_frontend_architecture.py`: límites frontend.
- `tools/generate_api_types.py`: generación reproducible de contratos.
- `OEUPB-Backend/scripts/dev/generate_excel_fixtures.py`: datos sintéticos parametrizables.
- `OEUPB-Backend/seed_db.py`: alta operativa idempotente del administrador inicial.
- `OEUPB-Backend/backup_database.py` y `restore_database.py`: respaldo/restauración protegida.

## Reglas permanentes

1. No crear `patch_*`, `fix_*`, `check_*` ni variantes numeradas en la raíz.
2. Las herramientas reutilizables viven en `tools/` o `<componente>/scripts/`, aceptan argumentos y no contienen rutas absolutas.
3. Los cambios de esquema se realizan exclusivamente con Alembic.
4. Los datos de desarrollo son sintéticos, reproducibles y no incorporan secretos ni información personal.
5. Una reparación puntual se implementa directamente, con prueba y revisión; Git conserva su historia.

