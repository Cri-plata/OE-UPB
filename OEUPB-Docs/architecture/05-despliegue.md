# Arquitectura de despliegue

**Estado:** objetivo; no verificado como desplegado en producción

**Fecha:** 2026-09-24

## Topología propuesta

```text
Navegador
   │ HTTPS
   ▼
Nginx / proxy institucional
   ├── Frontend Angular
   └── /api → FastAPI/Uvicorn
                 │ conexión privada
                 ▼
               MySQL
```

## Requisitos mínimos

- Infraestructura institucional aprobada por la UPB.
- HTTPS obligatorio.
- CORS configurado por ambiente, sin comodines productivos.
- Secretos fuera del repositorio.
- Usuario MySQL con mínimo privilegio.
- Migraciones ejecutadas como paso explícito y reversible.
- Backups y restauración probados.
- Logs sin documentos, correos, respuestas abiertas ni tokens completos. El backend enmascara el documento en las rutas del directorio y la imagen desactiva el access log de Uvicorn; el proxy debe registrar la ruta sin query string o enmascarar `/api/directorio/*` y el parámetro `q`.
- Health checks, métricas y procedimiento de rollback.

## Estado actual

El repositorio incluye imágenes Docker no privilegiadas para frontend/backend, composición con MySQL, health checks, proxy HTTPS, CORS por entorno, logs estructurados mínimos con identificador de petición, respaldo lógico y restauración con confirmación explícita. El procedimiento operativo y de rollback está en [`../docs/06-runbook-despliegue.md`](../docs/06-runbook-despliegue.md). El despliegue efectivo y la prueba institucional de restauración siguen siendo actividades del ambiente, no afirmaciones del repositorio.
