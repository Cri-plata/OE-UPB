# Especificaciones canónicas

Esta carpeta contiene artefactos técnicos verificables, no ejemplos narrativos.

- [`api/openapi.json`](api/openapi.json): contrato generado desde FastAPI.
- [`db/oeupb-schema.sql`](db/oeupb-schema.sql): representación versionada del modelo SQLAlchemy actual.

## Actualización

Después de cambiar rutas o payloads, regenerar OpenAPI desde `OEUPB-Backend`:

```powershell
$env:DATABASE_URL = 'sqlite:///./openapi-generation.db'
python -c "import json; from main import app; json.dump(app.openapi(), open('../OEUPB-Docs/specs/api/openapi.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=2)"
```

El archivo usa SQLite únicamente para importar la aplicación y generar el esquema; no representa la base de datos productiva. Revisar el diff antes de aceptar cambios.

