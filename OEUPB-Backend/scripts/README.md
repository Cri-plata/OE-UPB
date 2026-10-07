# Scripts mantenidos

Este directorio contiene herramientas reutilizables que no forman parte del arranque de la API. Se ejecutan desde `OEUPB-Backend/` con el entorno virtual activo; cada script resuelve por sí mismo la raíz del backend y su `.env`.

## `ops/` — operación

- `ops/seed_db.py`: crea el administrador inicial si no existe y muestra su credencial temporal una sola vez.
- `ops/backup_database.py`: respaldo lógico de la base de `DATABASE_URL`, fuera del repositorio.
- `ops/restore_database.py`: restauración con confirmación explícita del nombre de la base.

## `dev/` — desarrollo

- `dev/generate_excel_fixtures.py`: genera archivos `.xlsx` sintéticos para probar la carga.
- `dev/diagnostico_ia/`: diagnósticos manuales del pipeline NLP (`diagnostico_fragmentos.py`, `diagnostico_pipeline.py`, `diagnostico_reglas_asociacion.py`). Usan textos de ejemplo en memoria, imprimen resultados y no se conectan a la base. No son pruebas automatizadas: estas viven en `../tests/`.

No se admiten parches de reemplazo textual ni scripts con rutas, credenciales o datos personales incorporados. Los cambios de esquema se realizan con Alembic.
