# Scripts mantenidos

Este directorio contiene herramientas reutilizables que no forman parte del arranque de la API.

- `dev/generate_excel_fixtures.py`: genera archivos `.xlsx` sintéticos para probar la carga.
- `../seed_db.py`: se conserva en la raíz del backend como punto de entrada operativo para crear el administrador inicial.
- `../backup_database.py` y `../restore_database.py`: se conservan en la raíz por ser comandos operativos documentados.

No se admiten parches de reemplazo textual ni scripts con rutas, credenciales o datos personales incorporados. Los cambios de esquema se realizan con Alembic.
