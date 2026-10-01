# Backlog activo de OE UPB

**Última verificación contra el código:** 2026-09-30

**Última decisión de producto incorporada:** 2026-09-25 (ADR-014 y ADR-015)
**Regla:** este archivo contiene solo trabajo pendiente. Al completar o descartar un ítem, moverlo a [`BACKLOG_ARCHIVE.md`](BACKLOG_ARCHIVE.md) con evidencia.

## P1 — Alineación del sistema de diseño

- [ ] **UI-01 — Migrar el frontend al sistema canónico.** Alinear tokens, tipografía, layout, estados e iconografía del frontend con `design/design.md` usando los mockups aprobados como contrato. Sustituir iconografía ad hoc por Lucide sin iniciar cambios visuales que carezcan de mockup y entrada en `mockups/screen-map.md`.

- [ ] **UI-02 — Migrar la iconografía a `lucide-angular`.** Sustituir las máscaras CSS que cargan Lucide desde `unpkg.com` (barra lateral) y los SVG escritos a mano (KPI y carga) por `lucide-angular`, con el mapeo de iconos de `design.md`. Requiere añadir la dependencia (auditoría 06).
- [ ] **UI-03 — Pasar a signals el estado asíncrono restante.** Reporte General, Tendencias, Carga y Administración refrescan la vista con un `ChangeDetectorRef` inyectado, que queda inválido tras un reemplazo en caliente (HMR) y deja la pantalla en "Cargando…". Migrar su estado a signals, como el Explorador, Publicaciones, el Directorio y la Ficha del egresado (auditoría 06, U-12/UI-03). Observado el 2026-09-30: además, el endpoint de HMR de `ng serve` (`@ng/component`) puede seguir entregando una plantilla anterior incluso tras una recarga completa; si una pantalla no refleja un cambio de plantilla, reiniciar `ng serve`.

## P2 — Autenticación

- [ ] **FE-05 — Mostrar el rechazo de correos no institucionales en el login.** `LoginUseCase.execute` lanza un error síncrono cuando el correo no contiene `@upb.edu.co`; `LoginComponent.onSubmit` no lo captura, así que el botón queda en "Procesando…" y no aparece ningún mensaje. El caso de uso debe devolver un `Observable` con error (o el componente capturar la excepción) y la pantalla mostrar el motivo. Observado el 2026-09-30 durante la validación de PUB-01/PUB-02.

## P2 — Analítica

- [ ] **ANA-03 — Verificar el mapeo laboral con datos de M5.** ADR-016 supone que el cuestionario de M5 usa la misma redacción que M1. Cuando exista una carga de M5, confirmar los nombres de las preguntas y sus opciones de respuesta (sin leer datos personales) y ajustar `application/indicadores.py` si difieren.

## P3 — Validación de producto

- [ ] **PRD-01 — Validar las prioridades y los criterios RNF propuestos.** El 2026-09-25 se propusieron la prioridad de los RF/RNF y los criterios verificables de RNF-01 a RNF-06 (`requirements/01-requerimientos.md`). Producto debe confirmarlos o ajustarlos, y después hay que automatizar la medición de RNF-06 (rendimiento con 50.000 mediciones).

## P2 — Decisión de producto en pausa

- [ ] **IA-01 — Modelo predictivo (en pausa).** No iniciar implementación hasta que producto apruebe objetivo, métricas, población, horizonte y criterios de aceptación conforme a ADR-009.
