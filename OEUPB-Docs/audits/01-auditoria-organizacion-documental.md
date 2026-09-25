# Auditoría de organización documental de OE UPB

**Fecha:** 2026-09-22

**Alcance:** organización, vigencia, trazabilidad y relación entre documentación y código.

**Referencia comparativa:** estructura documental de VIAL/Nevi.

**Resultado:** OE UPB tiene documentación útil, pero carece de una fuente canónica única y de mecanismos para distinguir el sistema objetivo del sistema realmente implementado.

## 1. Resumen ejecutivo

El principal problema de OE UPB no es la ausencia total de documentación. El problema es que existen varias versiones de la verdad distribuidas entre la raíz y `OEUPB-Docs/`, algunas se contradicen y otras quedaron atrás frente al código.

La estructura actual permite entender la idea inicial del proyecto, pero dificulta responder con seguridad preguntas básicas:

- ¿Cuál `CLAUDE.md` es el vigente?
- ¿Qué funcionalidades están realmente implementadas?
- ¿Cuál es el contrato actual de la API?
- ¿Qué tareas continúan pendientes?
- ¿Qué decisiones arquitectónicas siguen vigentes y por qué se tomaron?
- ¿Qué changelog representa el estado actual?

VIAL/Nevi resuelve mejor estas preguntas mediante una portada navegable, una fuente canónica por tipo de información, separación entre backlog activo e histórico, contratos ejecutables, auditorías, ADR, documentación operativa y estados de implementación verificados contra el código.

## 2. Fortalezas actuales de OE UPB

Antes de reorganizar, conviene conservar lo que ya funciona:

- Existe una visión general del producto y de sus roles.
- Los 73 requerimientos funcionales están documentados.
- Hay historias de usuario y reglas de negocio explícitas.
- El aislamiento de información por sede está reconocido como regla crítica.
- Existen documentos separados para arquitectura, modelo de datos y planes iniciales.
- El proyecto mantiene contratos compartidos para frontend y backend.
- Hay registro histórico de varios cambios funcionales.
- La estructura principal ya separa frontend, backend, contratos y documentación.

La reorganización propuesta no busca copiar toda la complejidad de VIAL, sino adoptar las prácticas que resuelven problemas reales de OE UPB.

## 3. Hallazgos críticos

### H-01. Dos archivos `CLAUDE.md` compiten como fuente de verdad

**Evidencia:**

- `/CLAUDE.md` exige Clean Architecture, Angular 17+, Python, MySQL y una lectura obligatoria de 12 documentos.
- `/OEUPB-Docs/CLAUDE.md` contiene reglas diferentes: declara un enfoque Local-First y limita los usuarios activos a administradores/coordinadores.
- `architecture/02-arquitectura-tecnica.md` niega expresamente el enfoque Local-First y describe una arquitectura siempre conectada.

**Riesgo:** dos desarrolladores o asistentes pueden aplicar reglas incompatibles según el archivo que encuentren primero.

**Corrección requerida:** declarar un único `CLAUDE.md` canónico. El archivo alterno debe eliminarse o convertirse en un enlace corto al canónico, sin repetir reglas.

### H-02. Existen dos changelogs desalineados

**Evidencia:**

- `/CHANGELOG.md` contiene cambios recientes hasta septiembre de 2026.
- `/OEUPB-Docs/CHANGELOG.md` termina principalmente en agosto de 2026 y describe un estado anterior.

**Riesgo:** no hay forma inmediata de saber cuál historial consultar o actualizar.

**Corrección requerida:** consolidar el historial en un changelog canónico y establecer si registra cambios de todo el monorepo o únicamente de la documentación. Si se requieren historiales por componente, deben tener alcance explícito.

### H-03. El backlog no representa el estado real

**Evidencia:** `OEUPB-Docs/BACKLOG.md` mantiene como pendientes el login, CRUD de usuarios, carga de Excel, dashboard y contratos; el código y los changelogs muestran que esas capacidades ya existen al menos parcialmente.

**Riesgo:** se puede repetir trabajo, priorizar tareas terminadas u ocultar deuda real.

**Corrección requerida:** verificar cada ítem contra el código, dejar en `BACKLOG.md` solo tareas activas y mover lo completado a un `BACKLOG_ARCHIVE.md` con fecha y evidencia.

### H-04. Los contratos documentados no coinciden con la API implementada

**Evidencia:**

- `architecture/03-apicontract.md` afirma que todas las rutas comienzan con `/api/v1/`.
- El backend implementa rutas como `/api/auth/login`, `/api/carga/excel`, `/api/reportes/general`, `/api/reportes/tendencias` y `/api/directorio/*`.
- El contrato documentado usa `/api/v1/data/upload` y `/api/v1/dashboard/stats`, que no corresponden a los routers actuales.

**Riesgo:** frontend, backend, pruebas y documentación pueden divergir silenciosamente.

**Corrección requerida:** sustituir el contrato narrativo como fuente principal por un OpenAPI canónico generado o validado contra FastAPI. Los modelos TypeScript y Pydantic deben derivarse o verificarse contra ese contrato.

### H-05. El modelo de datos documentado difiere del modelo real

**Evidencia:**

- `architecture/04-modelo-datos.md` describe `historial_academico` y `encuestas_laborales`.
- El backend actual define principalmente `Usuario`, `Egresado` y `Medicion`.
- El documento exige `sede_id` para todos los usuarios; el modelo real permite `NULL` para `Admin_CTIC`.

**Riesgo:** migraciones, consultas, reglas de negocio y documentación pueden basarse en entidades inexistentes o restricciones incorrectas.

**Corrección requerida:** crear un esquema SQL canónico o documentación generada desde migraciones; separar claramente el modelo objetivo del modelo actualmente desplegado.

### H-06. Stack y decisiones técnicas desactualizados o ambiguos

**Evidencia:**

- La documentación habla de Angular 17+, pero `package.json` usa Angular 22.1 y TypeScript 6.0.
- Se menciona “FastAPI/Flask”, aunque la implementación usa FastAPI.
- La documentación alterna entre Clean Architecture y una descripción genérica N-Capas.

**Riesgo:** nuevas implementaciones pueden usar convenciones o dependencias equivocadas.

**Corrección requerida:** documentar versiones reales y decisiones vigentes, incluyendo fecha de verificación.

### H-07. Requerimientos e historias presentan problemas de trazabilidad

**Evidencia:**

- Las historias enlazan varios criterios con números de RF que no corresponden al contenido descrito.
- Se usan referencias `RN-*` en historias mientras el archivo formal usa `RNF-*` para restricciones y `RN-*` para reglas de negocio, sin una convención transversal clara.
- No existe una matriz única RF → HU → regla de negocio → endpoint → pantalla → prueba → estado.

**Riesgo:** es difícil demostrar cobertura o detectar requisitos sin implementación.

**Corrección requerida:** normalizar identificadores y crear una matriz de trazabilidad con estado real verificado.

### H-08. Las reglas de acceso documentadas no reflejan la evolución del producto

**Evidencia:**

- `requirements/03-reglas-negocio.md` afirma que solo `Admin_CTIC` puede administrar cuentas.
- El changelog reciente y `usuarios_router.py` permiten que coordinadores creen ciertos roles dentro de su sede.
- La documentación principal enumera `Directivo`, mientras el changelog incorpora también `Profesores`.

**Riesgo:** una corrección basada en documentación antigua podría eliminar una regla nueva o reabrir una vulnerabilidad.

**Corrección requerida:** aprobar una matriz RBAC vigente y reflejarla en requisitos, arquitectura, contratos y pruebas.

### H-09. Falta una portada documental navegable

**Evidencia:** `OEUPB-Docs/` no tiene un `README.md` que responda “dónde buscar qué”, ni un `SUMMARY.md` que indexe el contenido.

**Riesgo:** los documentos existen, pero descubrirlos depende de conocer previamente sus nombres y rutas.

**Corrección requerida:** crear una portada y un índice mantenibles, similares conceptualmente a los de VIAL.

### H-10. No existen registros formales de decisiones arquitectónicas

**Evidencia:** decisiones como Clean Architecture, JWT, almacenamiento JSON, aislamiento por sede, manejo de doble titulación y estrategia de despliegue aparecen dispersas, sin estado ni consecuencias documentadas.

**Riesgo:** las decisiones se reabren repetidamente o se cambian sin conocer sus efectos.

**Corrección requerida:** incorporar `adr/` con un índice y ADR pequeños para decisiones que afecten varias áreas.

### H-11. Falta separar documentación vigente, auditorías e historia

**Evidencia:** planes iniciales, hallazgos de Figma, cambios implementados y tareas futuras se mezclan sin marcar claramente si son activos, históricos, reemplazados o verificados.

**Riesgo:** un plan antiguo puede interpretarse como instrucción vigente.

**Corrección requerida:** usar carpetas y estados explícitos: `audits/`, `plans/`, `archive/`, y encabezados con `Estado`, `Fecha` y `Reemplaza/Reemplazado por`.

### H-12. La raíz del monorepo contiene artefactos temporales

**Evidencia:** hay numerosos archivos `patch_*`, `check_*`, `fill_*` y `create_*` tanto en la raíz como dentro de backend y frontend.

**Riesgo:** no se distingue entre herramientas vigentes, scripts de migración, pruebas manuales y residuos de sesiones anteriores.

**Corrección requerida:** auditar cada script; mover los reutilizables a `tools/` o `scripts/`, transformar migraciones reales en una solución formal y archivar o eliminar de manera controlada los artefactos desechables.

### H-13. Las pruebas y comandos operativos no están organizados ni documentados

**Evidencia:** el backend tiene archivos `test_*.py` en su raíz, sin una estructura clara de pruebas; no hay una guía consolidada de instalación, variables, base de datos, ejecución, pruebas y datos semilla.

**Riesgo:** la reproducibilidad depende del conocimiento informal del equipo.

**Corrección requerida:** crear documentación operativa y una estrategia de pruebas; organizar pruebas en directorios estándar y registrar comandos verificables.

### H-14. Los contratos están duplicados manualmente

**Evidencia:** `OEUPB-Contracts` mantiene interfaces TypeScript y esquemas Pydantic separados, mientras la documentación agrega una tercera representación narrativa.

**Riesgo:** el mismo payload puede tener tres definiciones distintas.

**Corrección requerida:** elegir un contrato canónico, preferiblemente OpenAPI, y generar o validar las representaciones consumidoras.

### H-15. Faltan documentos esenciales presentes en una documentación madura

OE UPB no cuenta todavía con:

- Casos de uso formales.
- Matriz de trazabilidad.
- Design system canónico.
- Índice de ADR.
- Especificación OpenAPI canónica.
- Esquema SQL o migraciones declaradas como fuente de verdad.
- Guía de desarrollo local y solución de problemas.
- Estrategia de pruebas.
- Política de seguridad y privacidad operativa.
- Auditoría técnica consolidada.
- Archivo histórico del backlog.
- Convención de estados documentales.
- CI que compruebe enlaces, contratos, pruebas y formato.

## 4. Comparación resumida con VIAL/Nevi

| Capacidad documental | VIAL/Nevi | OE UPB actual | Acción recomendada |
|---|---|---|---|
| Fuente de contexto para IA | Un `CLAUDE.md` canónico | Dos versiones incompatibles | Consolidar |
| Portada “dónde buscar qué” | Sí | No | Crear |
| Índice global | `SUMMARY.md` | No | Crear |
| Backlog solo activo | Sí, con archivo histórico | Mezcla pendientes y completados | Depurar y archivar |
| Arquitectura por componente | Sí | Parcial | Crear deep-dives breves |
| Contratos ejecutables | OpenAPI YAML | DTO duplicado + contrato narrativo | Canonizar OpenAPI |
| Esquema de BD canónico | SQL versionado | Modelo narrativo divergente | Generar desde migraciones |
| ADR | Sí | No | Incorporar solo decisiones relevantes |
| Auditorías | Separadas y archivables | No formalizadas | Crear sección `audits/` |
| Requisitos con estado real | Sí | No | Añadir estado y evidencia |
| Casos de uso | Sí | No | Crear |
| Design system | Sí | Hallazgos de Figma, no sistema | Crear |
| Documentación operativa | Sí | Dispersa o ausente | Crear |
| Historial documental | Changelog con alcance definido | Dos changelogs ambiguos | Consolidar |

## 5. Riesgos de copiar VIAL literalmente

OE UPB es un monorepo más pequeño y no necesita reproducir toda la estructura de VIAL. En particular:

- No es necesario separar inmediatamente la documentación en otro repositorio.
- No se necesitan deep-dives extensos para cada carpeta si un documento breve es suficiente.
- Los ADR solo deben cubrir decisiones importantes, no cada cambio técnico.
- `SUMMARY.md` es útil como índice, pero no obliga a adoptar mdBook.
- La reorganización no debe cambiar reglas de negocio ni comportamiento del código por accidente.

## 6. Orden recomendado de atención

| Prioridad | Hallazgos | Motivo |
|---|---|---|
| P0 | H-01, H-02, H-03, H-04, H-05, H-08 | Existen fuentes incompatibles que pueden inducir cambios incorrectos o inseguros |
| P1 | H-06, H-07, H-09, H-14 | Impiden trazabilidad, navegación y coordinación confiable |
| P2 | H-10, H-11, H-13, H-15 | Mejoran mantenibilidad y capacidad de auditoría |
| P3 | H-12 | Requiere revisar scripts uno por uno antes de mover o eliminar |

## 7. Criterio de éxito de la reorganización

La documentación estará organizada cuando una persona nueva pueda, sin conocimiento oral previo:

1. Encontrar en menos de cinco minutos cómo levantar y probar el sistema.
2. Identificar una sola fuente vigente para contexto, contratos, modelo de datos y backlog.
3. Distinguir requisitos objetivo de funcionalidades implementadas.
4. Trazar una funcionalidad desde el requisito hasta su endpoint, pantalla y prueba.
5. Conocer las decisiones arquitectónicas que no debe romper.
6. Ver qué está pendiente sin encontrarse tareas ya terminadas.
7. Confirmar mediante validaciones automáticas que enlaces, contratos y documentación básica siguen vigentes.
