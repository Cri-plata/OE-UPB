# Comandos de desarrollo

**Verificado:** 2026-09-24

Ejecutar cada comando desde el componente indicado; no existe un build único en la raíz.

## Backend — PowerShell

```powershell
cd OEUPB-Backend
py -3.13 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
Copy-Item .env.example .env
# Editar .env con la conexión MySQL y un SECRET_KEY local.
python -m alembic upgrade head
python seed_db.py
python -m unittest discover -s tests -v
uvicorn main:app --reload --port 8000
```

- API: `http://localhost:8000`
- Swagger: `http://localhost:8000/docs`
- OpenAPI: `http://localhost:8000/openapi.json`

`requirements.txt` fija las versiones verificadas. `seed_db.py` crea el administrador inicial solo si no existe y muestra su contraseña temporal una sola vez; debe guardarse en un canal seguro.

Para generar un Excel totalmente sintético de carga:

```powershell
python scripts/dev/generate_excel_fixtures.py .tmp/encuestas.xlsx --rows 100
```

## Frontend — PowerShell

```powershell
cd OEUPB-Frontend
npm ci
npm run check:api
npm run check:architecture
npm test -- --watch=false
npm run build
npm run start
```

- Aplicación: `http://localhost:4200`
- Build: `npm run build`
- Pruebas: `npm run test`

## Inicialización reproducible desde cero

Prerrequisitos verificados en CI: Python 3.13, Node.js 24, npm con `package-lock.json` y una instancia MySQL accesible. El procedimiento es:

```powershell
Copy-Item OEUPB-Backend/.env.example OEUPB-Backend/.env
# Crear la base indicada en DATABASE_URL y editar las credenciales locales.
cd OEUPB-Backend
python -m pip install -r requirements.txt
python -m alembic upgrade head
python seed_db.py
python -m alembic current
cd ../OEUPB-Frontend
npm ci
npm run check:api
npm run check:architecture
npm test -- --watch=false
npm run build
```

La revisión esperada de Alembic es `g4c82a9d1e30 (head)`. Los secretos y el archivo `.env` nunca se versionan. En producción se requieren `APP_ENV=production`, un `SECRET_KEY` de al menos 32 caracteres e `INITIAL_CREDENTIAL_MODE=random`.

## Regenerar OpenAPI

```powershell
cd OEUPB-Backend
$env:DATABASE_URL = 'sqlite:///./openapi-generation.db'
python -c "import json; from main import app; json.dump(app.openapi(), open('../OEUPB-Docs/specs/api/openapi.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=2)"
```

La importación no crea tablas ni conecta con MySQL. Revisar el diff generado.
