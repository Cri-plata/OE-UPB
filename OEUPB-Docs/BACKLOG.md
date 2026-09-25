# Backlog activo de OE UPB

**Última verificación contra el código:** 2026-09-25

**Última decisión de producto incorporada:** 2026-09-25 (ADR-014 y ADR-015)
**Regla:** este archivo contiene solo trabajo pendiente. Al completar o descartar un ítem, moverlo a [`BACKLOG_ARCHIVE.md`](BACKLOG_ARCHIVE.md) con evidencia.

## P1 — Flujo de publicación

- [ ] **PUB-01 — Cerrar correctamente el estado de publicación.** La acción `Publicar gráfica` debe finalizar en éxito/error, impedir duplicados, actualizar inmediatamente el estado visible y permitir reintento controlado. Desde ADR-015 el backend puede rechazar con 422 por datos insuficientes; la interfaz debe mostrar ese motivo sin quedar cargando.
  - **Implementado el 2026-09-25, pendiente de validación manual.** Causa: la aplicación es zoneless y el estado se guardaba en campos simples, así que la vista no se refrescaba hasta otra interacción. `presentation/shared/publicacion-control.ts` concentra el estado en signals, bloquea duplicados, muestra errores HTTP y de red en la gráfica con reintento, y reconcilia el 409 del retiro. Pruebas: `publicacion-control.spec.ts`.
- [ ] **PUB-02 — Corregir la carga del catálogo publicado.** La vista debe resolver listas con datos, vacías y errores; debe reflejar el ciclo publicar → consultar → retirar sin perder las restricciones de audiencia.
  - **Implementado el 2026-09-25, pendiente de validación manual.** La misma causa zoneless. `/publicaciones` usa signals, muestra los estados de datos, vacío y error con `Reintentar`, y tiene un botón `Actualizar`. Pruebas: `publicaciones.spec.ts`, más la prueba de backend `test_ciclo_publicar_consultar_retirar_para_consulta`.
  - **Para cerrar ambos:** validar el flujo en el entorno local (ver la lista de `docs/07-estado-funcional-actual.md`, sección 8) y archivarlos con la evidencia.

## P1 — Alineación del sistema de diseño

- [ ] **UI-01 — Migrar el frontend al sistema canónico.** Alinear tokens, tipografía, layout, estados e iconografía del frontend con `design/design.md` usando los mockups aprobados como contrato. Sustituir iconografía ad hoc por Lucide sin iniciar cambios visuales que carezcan de mockup y entrada en `mockups/screen-map.md`.

## P2 — Analítica

- [ ] **ANA-03 — Verificar el mapeo laboral con datos de M5.** ADR-016 supone que el cuestionario de M5 usa la misma redacción que M1. Cuando exista una carga de M5, confirmar los nombres de las preguntas y sus opciones de respuesta (sin leer datos personales) y ajustar `application/indicadores.py` si difieren.

## P3 — Validación de producto

- [ ] **PRD-01 — Validar las prioridades y los criterios RNF propuestos.** El 2026-09-25 se propusieron la prioridad de los RF/RNF y los criterios verificables de RNF-01 a RNF-06 (`requirements/01-requerimientos.md`). Producto debe confirmarlos o ajustarlos, y después hay que automatizar la medición de RNF-06 (rendimiento con 50.000 mediciones).

## P2 — Decisión de producto en pausa

- [ ] **IA-01 — Modelo predictivo (en pausa).** No iniciar implementación hasta que producto apruebe objetivo, métricas, población, horizonte y criterios de aceptación conforme a ADR-009.
