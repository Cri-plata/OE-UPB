# ADR-014 — Alcance de la identidad del egresado y precedencia de datos

**Estado:** Aceptado

**Fecha:** 2026-09-25

**Reemplaza parcialmente:** ADR-009, puntos 4 y 5.

## Contexto

ADR-009 prometía una "custodia institucional" para resolver conflictos de identidad entre sedes, el registro de encuestas manuales por el coordinador y la sobrescritura de correcciones manuales con confirmación explícita. La auditoría 05 (C-04, C-07, C-08) confirmó que ninguna de esas capacidades tenía actor, contrato ni modelo: no existe un rol de custodia, `mediciones.carga_id` es obligatorio y el cuerpo de la carga no admite confirmaciones. Producto decidió sacarlas del alcance el 2026-09-25.

## Decisión

1. **Sin custodia institucional.** No existe un actor que edite identidades compartidas. Un egresado vinculado a más de una sede (por mediciones o por `egresados_sedes`) no puede editarse ni eliminarse manualmente; el backend responde 409. Sus datos solo cambian mediante cargas.
2. **Sin encuestas manuales.** Toda medición proviene de una carga Excel. El directorio manual administra únicamente datos básicos de identidad (nombre, apellido, programa y fecha de grado).
3. **Precedencia de la carga sobre un egresado existente.** Una carga nunca sobrescribe nombre, apellido ni programa de un documento ya persistido. Solo puede actualizar `fecha_grado` cuando la fecha recibida es más reciente (coherente con ADR-006).
4. **Protección de correcciones manuales.** Si el documento tiene al menos un evento en `auditoria_egresados`, la carga no modifica ninguno de sus datos personales y el resultado informa cuántos registros se conservaron. No existe sobrescritura con confirmación.
5. **Limpieza tras eliminar cargas.** Al eliminar una carga solo se borran los egresados que quedan sin mediciones y sin vínculo manual en `egresados_sedes`. Los registros del directorio manual se conservan.
6. **Intentos múltiples.** Con una sola fuente de mediciones (la carga) y el reemplazo por alcance de RN-12, cada carga produce `intento = 1`. La columna `intento` y la política de selección de ADR-012 se conservan para compatibilidad y para una futura fuente de intentos aprobada mediante un ADR nuevo.

## Consecuencias

- RN-01, RN-13 y RN-25, HU-05, HU-06 y CU-08 se reescriben con esta política.
- El alta manual de un documento existente responde 409 sin devolver sus datos. La respuesta sigue confirmando que el documento existe, un riesgo bajo que se acepta porque solo lo ven los coordinadores autenticados.
- Un error en los datos de identidad compartidos debe corregirse en el archivo fuente de la sede y volver a cargarse.
- Si producto retoma la custodia o las encuestas manuales, deberá aprobar un ADR con actor, permisos, endpoints y migración.
