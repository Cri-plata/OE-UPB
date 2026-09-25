# CLAUDE.md — contexto canónico de OE UPB

**Estado:** Vigente

**Última verificación:** 2026-09-25

**Alcance:** todo el monorepo OE UPB.

Este es el único archivo canónico de contexto para asistentes y nuevos integrantes. El `CLAUDE.md` de la raíz solo debe apuntar a este documento y no duplicar sus reglas.

## Qué es OE UPB

OE UPB es el Observatorio de Egresados de la Universidad Pontificia Bolivariana. Centraliza encuestas de los momentos 0, 1 y 5, procesa archivos Excel, mantiene un directorio de egresados y presenta indicadores y tendencias por sede.

## Organización del monorepo

| Ruta | Responsabilidad | Tecnología vigente |
|---|---|---|
| `OEUPB-Frontend/` | Aplicación web y dashboards | Angular 22.1, TypeScript 6, SCSS, Chart.js |
| `OEUPB-Backend/` | API, autenticación, ETL y analítica | Python 3, FastAPI, SQLAlchemy, Pandas |
| `OEUPB-Contracts/` | DTO heredados de frontend/backend | TypeScript y Pydantic; no son fuente canónica hasta sincronizarlos con OpenAPI |
| `OEUPB-Docs/` | Documentación transversal | Markdown, OpenAPI y SQL |

## Fuentes de verdad

| Tema | Fuente canónica |
|---|---|
| Navegación documental | [`README.md`](README.md) y [`SUMMARY.md`](SUMMARY.md) |
| Pendientes activos | [`BACKLOG.md`](BACKLOG.md) |
| Trabajo completado/descartado | [`BACKLOG_ARCHIVE.md`](BACKLOG_ARCHIVE.md) |
| Requisitos | [`requirements/`](requirements/) |
| Estado real de implementación | Código + [`requirements/matriz-trazabilidad.md`](requirements/matriz-trazabilidad.md) |
| Contrato HTTP | [`specs/api/openapi.json`](specs/api/openapi.json) |
| Modelo persistente actual | [`specs/db/oeupb-schema.sql`](specs/db/oeupb-schema.sql) |
| Decisiones arquitectónicas | [`adr/INDEX.md`](adr/INDEX.md) |
| Diseño visual | [`design/design.md`](design/design.md) |
| Inventario y flujo de pantallas | [`mockups/screen-map.md`](mockups/screen-map.md) |
| Cambios de documentación | [`CHANGELOG.md`](CHANGELOG.md) |
| Cambios globales del producto | [`../CHANGELOG.md`](../CHANGELOG.md) |

Cuando la documentación contradiga el código, no se debe ocultar la diferencia. Se documentan por separado el **estado actual** y el **estado objetivo**, y se eleva la decisión al equipo.

## Reglas críticas de negocio y seguridad

1. El documento de identidad identifica de forma única al egresado cuando está disponible.
2. Los momentos admitidos son 0, 1 y 5.
3. El aislamiento por `sede_id` debe aplicarse en backend a todos los datos fuente; nunca se confía solo en filtros del frontend.
4. Los textos enviados a servicios externos de IA deben anonimizarse.
5. La doble titulación dentro de una misma carga conserva el registro con fecha de grado más reciente.
6. Los archivos de carga se validan antes de persistirlos y aceptan exclusivamente `.xlsx`.
7. La matriz RBAC aprobada usa `Admin_CTIC`, `Coordinador_Sede` y `Usuario_Consulta`. CTIC administra coordinadores; cada coordinador administra usuarios de consulta de su sede con permisos y programas.
8. Nunca registrar secretos, contraseñas reales ni datos personales de egresados en documentación, fixtures o logs.
9. Entre sedes solo se comparten gráficas y métricas agregadas que el coordinador propietario publique. Nunca se comparten filas, respuestas individuales, archivos, directorios o perfiles.
10. La audiencia de gráficas se calcula en backend según permisos y programas; el coordinador no selecciona destinatarios manualmente por gráfica.
11. Las métricas y programas de una publicación los recalcula el backend a partir de su definición (el cliente no los envía) y ninguna celda publicada representa menos de 5 observaciones (ADR-015).

## Arquitectura vigente

- Frontend standalone con rutas en `src/app/app.routes.ts`.
- Separación `domain/`, `data/` y `presentation/`; el acceso HTTP y la construcción de rutas viven en Data, y Presentation consume clientes tipados.
- Guards funcionales protegen sesión y navegación por rol; el backend continúa siendo la autoridad de autorización.
- Backend FastAPI con capas `domain/`, `application/`, `infrastructure/` y `presentation/`.
- MySQL mediante SQLAlchemy y Alembic. El modelo incluye usuarios, catálogo de sedes, egresados, cargas, mediciones con intentos y eventos inmutables de auditoría.
- JWT HS256 emitido por el backend; incluye `sub`, `rol` y `sede_id`.
- API actual sin prefijo de versión: `/api/auth`, `/api/usuarios`, `/api/carga`, `/api/reportes`, `/api/directorio`, `/api/sedes` y `/api/publicaciones`.
- Respuestas extensas de encuestas almacenadas como JSON en `mediciones.respuestas`.

## Flujo obligatorio de trabajo

1. Leer este archivo, `BACKLOG.md` y los documentos específicos del área afectada.
2. Revisar el estado de Git y preservar cambios ajenos.
3. Para nueva lógica, escribir o actualizar pruebas antes de implementar cuando la infraestructura de pruebas lo permita; si no existe, registrar la deuda en el backlog.
4. Mantener contratos, trazabilidad, backlog y changelog sincronizados con cambios funcionales.
5. No editar artefactos archivados; crear una nota nueva o actualizar la fuente vigente.
6. No crear scripts `patch_*`, `fix_*` o `check_*` en la raíz. Las herramientas reutilizables pertenecen a `tools/` o al directorio `scripts/` del componente.

## Reglas obligatorias de interfaz

1. [`design/design.md`](design/design.md) es la única fuente vigente para tokens, componentes, composición visual, estados e iconografía. Aplica tanto a los mockups como al frontend implementado.
2. No se inicia ni se acepta un desarrollo de UI si la pantalla o el cambio visual no cuenta primero con un mockup correspondiente aprobado o actualizado en [`mockups/`](mockups/).
3. [`mockups/screen-map.md`](mockups/screen-map.md) debe actualizarse en el mismo cambio cuando se crea, elimina, renombra o modifica una pantalla, variante, modal o transición de navegación.
4. Está prohibido utilizar emojis como contenido, decoración o sustituto de iconos en mockups y frontend. La iconografía se toma exclusivamente de la librería estándar definida en `design/design.md` y debe incluir un nombre accesible cuando comunique una acción o estado.
5. Todo cambio visual debe mantener sincronizados, en este orden: `design/design.md` cuando cambie el sistema, el mockup afectado, `mockups/screen-map.md`, la implementación Angular y sus pruebas pertinentes.
6. Están estrictamente prohibidos los bordes de acento de color laterales (izquierdo o derecho) o superiores en tarjetas y paneles (`card`, `panel`, `box`). Toda tarjeta conserva su borde perimetral neutro uniforme (`1px solid rgba(26, 24, 24, 0.08)`); los estados de alerta, advertencia o seguimiento se comunican exclusivamente con badges, pills de estado o encabezados semánticos en el contenido interno.

## Lectura según el tipo de tarea

- Arquitectura general: `architecture/00-proyecto.md`.
- Frontend: `architecture/01-frontend.md`, `design/design.md` y `mockups/screen-map.md`.
- Backend: `architecture/02-backend.md`.
- API: `architecture/03-contratos.md` y `specs/api/openapi.json`.
- Datos: `architecture/04-modelo-datos.md` y `specs/db/oeupb-schema.sql`.
- Requisitos: `requirements/` y `requirements/matriz-trazabilidad.md`.
- Seguridad: `docs/04-seguridad-privacidad.md` y ADR-004.
- Despliegue: `architecture/05-despliegue.md`.
- Comandos: `docs/00-comandos-desarrollo.md`.
