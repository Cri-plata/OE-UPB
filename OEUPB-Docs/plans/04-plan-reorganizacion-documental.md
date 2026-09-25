# Plan de reorganización documental de OE UPB

**Fecha:** 2026-09-22

**Estado:** Ejecutado. Las decisiones de gobierno están cerradas; RF-71 permanece en pausa como decisión de producto separada.

**Entrada:** [`../audits/01-auditoria-organizacion-documental.md`](../audits/01-auditoria-organizacion-documental.md).

**Principio:** primero consolidar las fuentes de verdad; después mover, renombrar o retirar archivos.

## 1. Objetivo

Organizar la documentación de OE UPB con una estructura inspirada en VIAL/Nevi, ajustada al tamaño del monorepo, de modo que sea navegable, verificable y coherente con el código real.

La ejecución del plan no debe modificar funcionalidad de frontend, backend ni base de datos. Cualquier contradicción de negocio debe convertirse en una decisión explícita del equipo antes de actualizar el código.

### Resultado de ejecución — 2026-09-22

Completado:

- Fuentes canónicas de contexto, navegación, backlog e historiales.
- Arquitectura vigente de frontend, backend, contratos, datos y despliegue.
- OpenAPI generado desde FastAPI y esquema SQL de referencia.
- Casos de uso y matriz inicial de trazabilidad.
- ADR, design system y documentación operativa.
- Inventario y clasificación de scripts temporales.
- Validación local de enlaces y del contrato OpenAPI.

Cierre posterior verificado el 2026-09-24:

- RBAC y publicación agregada implementados conforme a ADR-008.
- Nulabilidad, modelo de datos y versionado resueltos por ADR-011 y ADR-012.
- Alembic, pruebas funcionales y controles CI incorporados.
- Scripts históricos revisados y retirados; herramientas reutilizables organizadas.
- RF-01 a RF-73 auditados individualmente en la matriz de trazabilidad.
- Ocho decisiones abiertas cerradas en `audits/03-cierre-decisiones-abiertas.md`.

## 2. Estructura objetivo

```text
OEUPB-Docs/
├── README.md                         # Dónde buscar qué
├── SUMMARY.md                        # Índice navegable
├── CLAUDE.md                         # Único contexto canónico para IA
├── CHANGELOG.md                      # Solo cambios de documentación
├── BACKLOG.md                        # Solo tareas activas
├── BACKLOG_ARCHIVE.md                # Tareas terminadas o descartadas
├── architecture/
│   ├── 00-proyecto.md
│   ├── 01-frontend.md
│   ├── 02-backend.md
│   ├── 03-contratos.md
│   ├── 04-modelo-datos.md
│   └── 05-despliegue.md
├── requirements/
│   ├── requerimientos.md
│   ├── historias-usuario.md
│   ├── reglas-negocio.md
│   ├── casos-de-uso.md
│   └── matriz-trazabilidad.md
├── specs/
│   ├── README.md
│   ├── api/openapi.yaml
│   └── db/oeupb-schema.sql
├── design/
│   └── design-system.md
├── adr/
│   ├── INDEX.md
│   └── NNN-decision.md
├── docs/
│   ├── 00-comandos-desarrollo.md
│   ├── 01-configuracion-local.md
│   ├── 02-datos-prueba.md
│   ├── 03-estrategia-pruebas.md
│   └── 04-seguridad-privacidad.md
├── audits/
│   ├── 01-auditoria-organizacion-documental.md
│   └── ...
├── plans/
│   ├── 01-plan-backend.md
│   ├── 02-plan-frontend.md
│   ├── 03-plan-despliegue.md
│   └── 04-plan-reorganizacion-documental.md
└── archive/                         # Documentos reemplazados, conservados como historia
```

En la raíz del monorepo deben permanecer únicamente una portada corta y, si se desea, un `CLAUDE.md` de redirección que indique con claridad dónde vive la fuente canónica. No debe duplicar su contenido.

## 3. Fases de ejecución

### Fase 0 — Congelar y respaldar la estructura actual

**Objetivo:** evitar pérdida de contexto durante la reorganización.

Tareas:

- [ ] Crear una rama `codex/reorganizacion-documental` o la rama de trabajo acordada por el equipo.
- [ ] Registrar el inventario de documentos y su última modificación.
- [ ] Confirmar que no haya cambios locales de otros integrantes antes de mover archivos.
- [ ] Definir responsables de aprobación: producto, backend, frontend y datos.
- [ ] No eliminar archivos en esta fase.

**Salida:** inventario reproducible y reorganización aislada.

### Fase 1 — Establecer fuentes canónicas

**Objetivo:** eliminar la ambigüedad más peligrosa antes de mejorar el formato.

Tareas:

- [ ] Elegir un único `OEUPB-Docs/CLAUDE.md` canónico.
- [ ] Convertir `/CLAUDE.md` en una referencia corta al archivo canónico o retirarlo después de validar enlaces y herramientas.
- [ ] Consolidar los dos changelogs y definir su alcance.
- [ ] Revisar `BACKLOG.md` ítem por ítem contra el código.
- [ ] Crear `BACKLOG_ARCHIVE.md` y mover allí lo terminado, con fecha y evidencia.
- [ ] Definir una convención de estados: `Propuesto`, `Vigente`, `Implementado parcialmente`, `Implementado`, `Reemplazado`, `Archivado`.

**Criterio de salida:** existe una sola respuesta inequívoca para contexto, historial y pendientes.

### Fase 2 — Crear navegación y gobierno documental

**Objetivo:** que cualquier integrante sepa dónde buscar y dónde escribir.

Tareas:

- [ ] Crear `OEUPB-Docs/README.md` con una tabla “Quiero... / Voy a...”.
- [ ] Crear `SUMMARY.md` con todos los documentos vigentes.
- [ ] Añadir a cada documento crítico metadatos de fecha, estado, propietario y fuente de verificación.
- [ ] Documentar reglas para crear, reemplazar y archivar documentos.
- [ ] Corregir referencias antiguas a `BACKLOG.md` en la raíz.

**Criterio de salida:** todo documento vigente es alcanzable desde `README.md` o `SUMMARY.md`.

### Fase 3 — Verificar la realidad técnica

**Objetivo:** alinear documentación y código sin asumir que uno de los dos es automáticamente correcto.

Tareas de backend:

- [ ] Inventariar routers, payloads, códigos HTTP y reglas de autorización reales.
- [ ] Documentar FastAPI como framework vigente y retirar la ambigüedad “FastAPI/Flask”.
- [ ] Registrar estructura de capas real y desviaciones frente a Clean Architecture.
- [ ] Verificar manejo de `sede_id` en todos los endpoints.

Tareas de frontend:

- [ ] Registrar Angular 22.1 y TypeScript 6.0 como versiones actuales.
- [ ] Inventariar rutas, servicios, interceptores y roles visibles.
- [ ] Verificar qué partes cumplen las capas Domain/Data/Presentation y cuáles están acopladas.

Tareas de datos:

- [ ] Comparar modelos SQLAlchemy, base de datos y modelo narrativo.
- [ ] Resolver si el diseño objetivo usa `Medicion` o `encuestas_laborales` + `historial_academico`.
- [ ] Definir la nulabilidad correcta de `usuarios.sede_id` para `Admin_CTIC`.
- [ ] Formalizar migraciones; evitar scripts ad hoc como mecanismo principal de evolución.

**Criterio de salida:** cada documento técnico indica “estado actual” y, si aplica, “estado objetivo”.

### Fase 4 — Canonizar contratos y esquema de datos

**Objetivo:** impedir que frontend, backend y documentación diverjan.

Tareas:

- [ ] Exportar el OpenAPI actual de FastAPI como línea base.
- [ ] Revisar y versionar el contrato en `specs/api/openapi.yaml`.
- [ ] Decidir si las rutas se mantienen bajo `/api/*` o migran a `/api/v1/*`; no documentar la migración como realizada antes de implementarla.
- [ ] Validar o generar los tipos TypeScript desde OpenAPI.
- [ ] Mantener Pydantic como implementación del contrato, no como una segunda fuente independiente.
- [ ] Crear un esquema SQL canónico a partir de migraciones verificadas.
- [ ] Añadir validación automática de OpenAPI y detección de cambios incompatibles.

**Criterio de salida:** cada endpoint y entidad pública tiene una sola definición canónica verificable.

### Fase 5 — Reorganizar requisitos y trazabilidad

**Objetivo:** conectar necesidades de negocio con la implementación real.

Tareas:

- [ ] Normalizar identificadores RF, RNF, RN, HU y CU.
- [ ] Corregir enlaces incorrectos entre historias y requisitos.
- [ ] Crear `casos-de-uso.md` para los flujos críticos.
- [ ] Crear `matriz-trazabilidad.md` con las columnas:
  - ID de requisito.
  - Historia/caso de uso.
  - Regla de negocio.
  - Rol.
  - Endpoint.
  - Pantalla/componente.
  - Prueba asociada.
  - Estado real.
  - Evidencia y fecha de verificación.
- [x] Aprobar una matriz RBAC para `Admin_CTIC`, `Coordinador_Sede` y `Usuario_Consulta`; rector, profesor y administrativo son alcances configurables del rol de consulta. Aprobada el 2026-09-23.
- [ ] Distinguir explícitamente requisitos objetivo de comportamiento implementado.

**Criterio de salida:** no hay funcionalidad marcada como implementada sin evidencia en código o pruebas.

### Fase 6 — Documentar decisiones y operación

**Objetivo:** capturar el conocimiento que hoy vive de forma informal.

ADRs iniciales sugeridos:

- [ ] ADR-001: Clean Architecture y límites entre capas.
- [ ] ADR-002: FastAPI como backend oficial.
- [ ] ADR-003: MySQL y estrategia de migraciones.
- [ ] ADR-004: JWT, roles y aislamiento por sede.
- [ ] ADR-005: almacenamiento JSON de respuestas dinámicas.
- [ ] ADR-006: regla de doble titulación.
- [ ] ADR-007: contrato OpenAPI como fuente de verdad.
- [x] ADR-008: publicación de gráficas agregadas y audiencia automática por permisos/programas.

Documentación operativa:

- [ ] Comandos para instalar, levantar, probar y construir cada componente.
- [ ] Variables de entorno requeridas, sin secretos reales.
- [ ] Creación y migración de la base de datos.
- [ ] Datos semilla y cuentas de prueba seguras.
- [ ] Estrategia de pruebas unitarias, integración y end-to-end.
- [ ] Política de anonimización, Habeas Data y tratamiento de archivos cargados.
- [ ] Procedimiento de despliegue y rollback.

**Criterio de salida:** una persona nueva puede reproducir el entorno usando únicamente el repositorio.

### Fase 7 — Ordenar scripts y artefactos temporales (completada 2026-09-24)

**Objetivo:** limpiar la raíz sin perder herramientas que todavía sean útiles.

Clasificación propuesta para cada script:

| Categoría | Destino |
|---|---|
| Herramienta reutilizable | `/tools/` o `<componente>/scripts/` |
| Migración de base de datos | Sistema formal de migraciones |
| Generador de fixtures | `<componente>/scripts/dev/` |
| Prueba automatizada | Directorio estándar `tests/` |
| Evidencia o script de una sola ocasión | `archive/` antes de eliminación posterior |
| Duplicado o residuo sin valor | Eliminar solo tras revisión y aprobación |

Tareas:

- [x] Revisar individualmente archivos `patch_*`, `check_*`, `fill_*`, `create_*` y `fix_*`.
- [x] Prohibir nuevos scripts temporales en la raíz.
- [x] Crear un README breve para herramientas que se conserven.
- [x] Asegurar que ningún script conservado contenga secretos o datos personales.

**Criterio de salida:** la raíz muestra la estructura del producto, no el historial accidental de reparaciones.

### Fase 8 — Automatizar controles mínimos

**Objetivo:** impedir que la documentación vuelva a degradarse.

Tareas:

- [ ] Verificar enlaces Markdown en CI.
- [ ] Validar OpenAPI en CI.
- [ ] Ejecutar pruebas de backend y frontend.
- [ ] Comprobar formato de Markdown y convenciones básicas.
- [ ] Detectar referencias a archivos inexistentes.
- [ ] Añadir checklist de pull request para actualizar contratos, ADR, backlog y changelog cuando corresponda.

**Criterio de salida:** una contradicción básica o un enlace roto impide integrar el cambio.

## 4. Secuencia recomendada de entregas

| Entrega | Contenido | Dependencias |
|---|---|---|
| E1 — Gobierno mínimo | CLAUDE canónico, changelog consolidado, backlog depurado y archivo histórico | Ninguna |
| E2 — Navegación | README, SUMMARY, estados y enlaces corregidos | E1 |
| E3 — Estado real | Arquitectura frontend/backend/datos verificada | E1 |
| E4 — Fuentes técnicas | OpenAPI y esquema de BD canónicos | E3 |
| E5 — Negocio trazable | IDs corregidos, casos de uso, RBAC y matriz de trazabilidad | E3 y E4 |
| E6 — Operación | ADR, comandos, pruebas, seguridad y despliegue | E3 |
| E7 — Higiene | Scripts clasificados y raíz limpia | E1; revisión manual |
| E8 — Prevención | CI documental y checklist de cambios | E2 y E4 |

## 5. Decisiones que requerían aprobación del equipo

Las ocho decisiones quedaron resueltas o formalmente delimitadas el 2026-09-24. La evidencia y consecuencias se consolidan en [`../audits/03-cierre-decisiones-abiertas.md`](../audits/03-cierre-decisiones-abiertas.md). RF-71 continúa en pausa conforme a ADR-009 y no bloquea el cierre documental.

## 6. Reglas para ejecutar el plan con seguridad

- No borrar ni mover masivamente archivos sin verificar referencias y estado de Git.
- Hacer cambios pequeños y revisables por fase.
- Conservar documentos reemplazados en `archive/` durante la transición.
- No convertir una descripción objetivo en “implementado” sin evidencia.
- No cambiar reglas de negocio para hacer coincidir el código; elevar la contradicción al equipo.
- Cada entrega debe actualizar el changelog documental.
- Las modificaciones de comportamiento deben incluir pruebas; la reorganización documental por sí sola no autoriza cambios funcionales.

## 7. Definición de terminado

El plan estará completo cuando:

- Exista un solo `CLAUDE.md` canónico.
- Exista un solo backlog activo y un archivo histórico.
- La portada y el índice alcancen toda la documentación vigente.
- OpenAPI y el esquema de datos sean las fuentes técnicas canónicas.
- Requisitos, roles y estados estén verificados y trazables.
- La arquitectura documente versiones y componentes reales.
- Los scripts temporales hayan sido clasificados.
- Los controles automáticos eviten enlaces rotos y contratos inválidos.
- El equipo pueda incorporar a una persona nueva sin depender de explicaciones orales para operar el proyecto.
