# Cierre de decisiones abiertas de reorganización

**Fecha:** 2026-09-24  
**Estado:** cerrado.

Esta auditoría resuelve las ocho preguntas de gobierno que quedaron abiertas en el plan de reorganización. No redefine producto: enlaza decisiones ya aprobadas y formaliza el estado operativo vigente.

| # | Pregunta | Resolución | Evidencia |
|---:|---|---|---|
| 1 | ¿Admin CTIC tiene sede? | `Admin_CTIC.sede_id` es nulo; no consume datos fuente. Coordinadores y usuarios de consulta requieren sede. | ADR-004, ADR-012, migraciones y modelos |
| 2 | ¿Quién administra usuarios? | CTIC administra coordinadores; cada coordinador administra consulta de su sede. | ADR-008, RF-36, pruebas RBAC |
| 3 | ¿Profesor es un rol? | No. Rector/profesor/administrativo son etiquetas informativas de `Usuario_Consulta`; privilegios vienen de permisos/programas. | ADR-008, RF-37 |
| 4 | ¿Modelo `Egresado`–`Medicion` o reemplazo normalizado? | Se conserva `Egresado`–`Medicion`, con intentos, carga y respuestas JSON explícitos. | ADR-005 y ADR-012 |
| 5 | ¿Se adopta `/api/v1`? | Se mantienen rutas `/api/*`; la evolución debe ser compatible y OpenAPI es canónico. | ADR-007 y ADR-011 |
| 6 | ¿Conectado o Local-First? | El producto vigente es cliente-servidor conectado. No existe alcance offline/Local-First aprobado. | arquitectura y despliegue vigentes |
| 7 | ¿Cómo se reparten los changelogs? | `/CHANGELOG.md` registra producto; `OEUPB-Docs/CHANGELOG.md` registra documentación. | `CLAUDE.md` |
| 8 | ¿Dónde vive la documentación? | Permanece dentro del monorepo bajo `OEUPB-Docs/`; una separación futura requeriría un nuevo ADR. | README, SUMMARY y CI documental |

## Decisiones diferidas formalmente

RF-71 no es una ambigüedad documental: ADR-009 e IA-01 lo mantienen **en pausa** hasta que producto defina objetivo, población, horizonte, métricas y aceptación. Las brechas Parcial/No implementado de la matriz RF-01–RF-73 son alcance candidato, no compromisos automáticos de desarrollo.

No quedan preguntas abiertas del plan de reorganización. Cualquier cambio a estas resoluciones debe documentarse mediante un ADR nuevo o reemplazante.

