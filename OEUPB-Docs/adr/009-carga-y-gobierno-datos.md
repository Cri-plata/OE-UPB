# ADR-009 — Carga auditable y gobierno de datos

**Estado:** Aceptado

**Fecha de registro:** 2026-09-23

## Contexto

La auditoría de requerimientos detectó que el sistema agrupaba el historial por sede, momento y año sin representar el archivo cargado. Tampoco estaban definidas la recarga, la precedencia de correcciones manuales, el uso de encuestas anónimas ni la semántica del año.

## Decisión

1. Cada archivo cargado constituye una entidad auditable con ID, nombre/huella, fecha, actor, sede, momento, año de grado, estado, versión, resultado y mediciones afectadas.
2. Una nueva carga para la misma sede, momento y año de grado reemplaza la versión vigente dentro de una sola transacción. Si falla cualquier validación o persistencia, la versión anterior permanece intacta.
3. El año informado en la carga representa el año de grado o cohorte.
4. Una corrección manual prevalece sobre una carga posterior. El conflicto debe informarse y requerir confirmación explícita para sobrescribirla.
5. Existe custodia institucional sobre la identidad global del egresado para resolver conflictos entre sedes. Un coordinador puede registrar encuestas manuales y corregir información de egresados visibles para su sede; toda modificación queda auditada.
6. Las mediciones anónimas participan únicamente en agregados que superen la revisión de privacidad. No aparecen en directorios, perfiles ni emparejamientos longitudinales.
7. El catálogo laboral principal es: `empleado`, `independiente`, `estudiante` y `sin_empleo`. La formalidad es un atributo separado aplicable a la ocupación.
8. Una gráfica publicada es una instantánea versionada. Cada publicación requiere aprobación manual de privacidad; no se define por ahora un umbral numérico automático.
9. El módulo predictivo de IA queda en pausa hasta aprobar objetivo, métricas, población, horizonte y criterios de aceptación.

## Consecuencias

- Se requiere una migración formal para `cargas` y su relación con `mediciones`.
- Historial y eliminación deben operar por `carga_id`, manteniendo trazabilidad de cargas reemplazadas o retiradas.
- La importación debe dejar de confirmar transacciones por fila.
- La edición manual necesita auditoría de campos, actor, fecha y procedencia.
- Los documentos de requisitos y trazabilidad deben marcar IA como pausada, no como funcionalidad en implementación activa.
- La invitación de cuentas se resolverá en una decisión separada cuando se confirme el proveedor de correo institucional.
