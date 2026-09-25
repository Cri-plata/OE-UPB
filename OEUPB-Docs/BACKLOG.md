# Backlog activo de OE UPB

**Última verificación contra el código:** 2026-09-25

**Última decisión de producto incorporada:** 2026-09-25
**Regla:** este archivo contiene solo trabajo pendiente. Al completar o descartar un ítem, moverlo a [`BACKLOG_ARCHIVE.md`](BACKLOG_ARCHIVE.md) con evidencia.

## P0 — Privacidad del Explorador

- [ ] **EXP-02 — Restringir variables graficables.** Aplicar en backend un catálogo de variables analíticas permitidas y excluir identificadores, datos personales y metadatos administrativos del selector, las consultas y las publicaciones. Cubrir los campos reportados y los alias de columnas con pruebas. Ver [`audits/04-hallazgos-explorador-publicaciones.md`](audits/04-hallazgos-explorador-publicaciones.md#h-exp-01--variables-personales-y-administrativas-aparecen-como-graficables).

## P1 — Flujo de publicación

- [ ] **PUB-01 — Cerrar correctamente el estado de publicación.** La acción `Publicar gráfica` debe finalizar en éxito/error, impedir duplicados, actualizar inmediatamente el estado visible y permitir reintento controlado.
- [ ] **PUB-02 — Corregir la carga del catálogo publicado.** La vista debe resolver listas con datos, vacías y errores; debe reflejar el ciclo publicar → consultar → retirar sin perder las restricciones de audiencia.

## P1 — Alineación del sistema de diseño

- [ ] **UI-01 — Migrar el frontend al sistema canónico.** Alinear tokens, tipografía, layout, estados e iconografía del frontend con `design/design.md` usando los mockups aprobados como contrato. Sustituir iconografía ad hoc por Lucide sin iniciar cambios visuales que carezcan de mockup y entrada en `mockups/screen-map.md`.

## P2 — Comparación en el Explorador

- [ ] **EXP-03 — Permitir varias gráficas simultáneas.** Añadir `Crear otra gráfica` y mantener configuraciones, estados y acciones independientes para comparar varias visualizaciones en la misma pantalla.

## P2 — Decisión de producto en pausa

- [ ] **IA-01 — Modelo predictivo (en pausa).** No iniciar implementación hasta que producto apruebe objetivo, métricas, población, horizonte y criterios de aceptación conforme a ADR-009.
