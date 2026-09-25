# Runbook de despliegue, respaldo y rollback

## Preparación

1. Copiar `.env.docker.example` a `.env` fuera del control de versiones y reemplazar todos los valores.
2. Instalar certificados institucionales como `deploy/tls/fullchain.pem` y `deploy/tls/privkey.pem`.
3. Ejecutar `python backup_database.py` y conservar la ruta, tamaño y SHA-256 reportados.
4. Ejecutar `alembic upgrade head` en una tarea única antes de aumentar réplicas.
5. Ejecutar `docker compose build` y `docker compose up -d`.

## Verificación

- `GET /api/health/live` confirma que el proceso responde.
- `GET /api/health/ready` confirma acceso a MySQL.
- Verificar login, un reporte de una sede y que los logs contengan `request_id`, estado y duración, pero no PII ni cuerpos.
- Probar periódicamente los respaldos en una base aislada; generar el respaldo no demuestra que sea restaurable.

## Rollback

1. Detener ingreso de datos y conservar logs e identificador de la imagen fallida.
2. Si no hubo migración destructiva, desplegar la imagen anterior y comprobar ambos health checks.
3. Si debe revertirse la base, crear antes un respaldo del estado fallido y ejecutar `python restore_database.py --backup <archivo.sql> --confirm-database <nombre>` con el cliente `mysql` disponible.
4. No ejecutar `alembic downgrade` en producción sin revisión de la migración. Restaurar el respaldo es la vía aprobada para pérdida o transformación irreversible.
5. Registrar responsable, hora, versión, motivo, respaldo usado y resultado de las comprobaciones.

El nombre de host del proxy y los certificados del ejemplo son placeholders; deben sustituirse por la infraestructura aprobada por UPB.
