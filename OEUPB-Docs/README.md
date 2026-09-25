# Documentación de OE UPB

Documentación transversal del monorepo **OE UPB — Observatorio de Egresados UPB**.

## Dónde buscar qué

| Quiero... | Voy a... |
|---|---|
| Entender el proyecto y sus módulos | [`architecture/00-proyecto.md`](architecture/00-proyecto.md) |
| Conocer las reglas obligatorias para trabajar | [`CLAUDE.md`](CLAUDE.md) |
| Saber qué falta | [`BACKLOG.md`](BACKLOG.md) |
| Ver tareas terminadas o retiradas | [`BACKLOG_ARCHIVE.md`](BACKLOG_ARCHIVE.md) |
| Revisar el frontend real | [`architecture/01-frontend.md`](architecture/01-frontend.md) |
| Revisar el backend real | [`architecture/02-backend.md`](architecture/02-backend.md) |
| Consultar endpoints y contratos | [`architecture/03-contratos.md`](architecture/03-contratos.md) y [`specs/api/openapi.json`](specs/api/openapi.json) |
| Consultar el modelo de datos | [`architecture/04-modelo-datos.md`](architecture/04-modelo-datos.md) |
| Levantar o probar el proyecto | [`docs/00-comandos-desarrollo.md`](docs/00-comandos-desarrollo.md) |
| Revisar requisitos y reglas | [`requirements/`](requirements/) |
| Ver cobertura requisito–código | [`requirements/matriz-trazabilidad.md`](requirements/matriz-trazabilidad.md) |
| Entender decisiones arquitectónicas | [`adr/INDEX.md`](adr/INDEX.md) |
| Aplicar estilos y componentes | [`design/design.md`](design/design.md) |
| Revisar pantallas y flujos antes de desarrollar UI | [`mockups/index.html`](mockups/index.html) y [`mockups/screen-map.md`](mockups/screen-map.md) |
| Revisar hallazgos documentales | [`audits/01-auditoria-organizacion-documental.md`](audits/01-auditoria-organizacion-documental.md) y [`audits/02-auditoria-requerimientos.md`](audits/02-auditoria-requerimientos.md) |
| Consultar el plan de organización | [`plans/04-plan-reorganizacion-documental.md`](plans/04-plan-reorganizacion-documental.md) |

## Convenciones

- Todo documento debe indicar si describe el estado actual, el objetivo o ambos.
- `BACKLOG.md` contiene únicamente trabajo activo.
- Las tareas terminadas se mueven a `BACKLOG_ARCHIVE.md`.
- Los documentos reemplazados se conservan en `archive/` durante la transición.
- Las decisiones relevantes se registran como ADR y no se reescriben retroactivamente.
- El contrato OpenAPI y el esquema SQL versionado prevalecen sobre ejemplos narrativos antiguos.
- Los cambios de esta carpeta se registran en `CHANGELOG.md`; los cambios globales del producto, en el changelog de la raíz.

El índice completo está en [`SUMMARY.md`](SUMMARY.md).
