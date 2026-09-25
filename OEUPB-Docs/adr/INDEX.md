# Índice de decisiones arquitectónicas

Los ADR registran decisiones relevantes y sus consecuencias. Una decisión reemplazada no se borra: cambia a estado `Reemplazado` y apunta al ADR nuevo.

| ADR | Decisión | Estado |
|---|---|---|
| [001](001-arquitectura-limpia.md) | Arquitectura por capas como dirección del proyecto | Aceptado |
| [002](002-fastapi-backend.md) | FastAPI como framework backend | Aceptado |
| [003](003-mysql-migraciones.md) | MySQL con migraciones formales | Aceptado |
| [004](004-jwt-aislamiento-sede.md) | JWT y aislamiento por sede en backend | Aceptado |
| [005](005-respuestas-json.md) | Respuestas dinámicas almacenadas en JSON | Aceptado |
| [006](006-doble-titulacion.md) | Conservar la titulación más reciente por carga | Aceptado |
| [007](007-openapi-canonico.md) | OpenAPI como contrato HTTP canónico | Aceptado |
| [008](008-publicacion-graficas-permisos.md) | Publicar métricas agregadas con audiencia automática por permisos y programas | Aceptado |
| [009](009-carga-y-gobierno-datos.md) | Carga auditable, reemplazo transaccional y gobierno de datos | Aceptado |
| [010](010-contrasena-temporal.md) | Contraseña temporal aleatoria con cambio obligatorio | Reemplazado por ADR-013 |
| [011](011-versionado-api-compatible.md) | Mantener `/api/*` con evolución compatible | Aceptado |
| [012](012-modelo-egresado-medicion.md) | Conservar `Egresado`–`Medicion` y modelar intentos explícitos | Aceptado |
| [013](013-ciclo-vida-credenciales-temporales.md) | Ciclo de vida, expiración y recuperación de credenciales temporales | Aceptado |
