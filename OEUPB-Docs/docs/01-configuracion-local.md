# Configuración local

## Requisitos

- Python compatible con las dependencias del backend.
- Node.js compatible con Angular 22 y npm 11.
- MySQL accesible localmente.

## Variables del backend

Crear `OEUPB-Backend/.env` a partir de `.env.example`. Nunca versionar secretos reales.

| Variable | Uso |
|---|---|
| `DATABASE_URL` | URL SQLAlchemy para MySQL |
| `SECRET_KEY` | Firma JWT; debe ser aleatoria y privada |
| `ALGORITHM` | Algoritmo JWT, actualmente HS256 |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | Duración del access token |

## Orden de arranque

1. Iniciar MySQL y crear la base local.
2. Ejecutar `alembic upgrade head` desde `OEUPB-Backend`. Para adoptar Alembic sobre una base preexistente, seguir `OEUPB-Backend/migrations/README` y verificar un respaldo antes de usar `stamp`.
3. Iniciar FastAPI en `:8000`.
4. Iniciar Angular en `:4200`.
5. Abrir Swagger y verificar el endpoint raíz antes de probar la UI.

## Configuración verificada

- Angular obtiene la URL de API desde sus archivos `environment` y `api.config.ts`.
- CORS se configura mediante entorno; producción no acepta el origen local por defecto.
- Alembic es el único mecanismo de creación y evolución del esquema.
- Python fija dependencias en `requirements.txt` y Angular usa `package-lock.json` con `npm ci`.
