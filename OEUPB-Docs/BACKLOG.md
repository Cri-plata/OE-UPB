# Backlog activo de OE UPB

**Última verificación contra el código:** 2026-09-30

**Última decisión de producto incorporada:** 2026-10-03 (ADR-020)
**Regla:** este archivo contiene solo trabajo pendiente. Al completar o descartar un ítem, moverlo a [`BACKLOG_ARCHIVE.md`](BACKLOG_ARCHIVE.md) con evidencia.

## P1 — Alineación del sistema de diseño

- [ ] **UI-01 — Migrar el frontend al sistema canónico.** Alinear tokens, tipografía, layout, estados e iconografía del frontend con `design/design.md` usando los mockups aprobados como contrato. Sustituir iconografía ad hoc por Lucide sin iniciar cambios visuales que carezcan de mockup y entrada en `mockups/screen-map.md`.

- [ ] **UI-02 — Migrar la iconografía a `lucide-angular`.** Sustituir las máscaras CSS que cargan Lucide desde `unpkg.com` (barra lateral) y los SVG escritos a mano (KPI y carga) por `lucide-angular`, con el mapeo de iconos de `design.md`. Requiere añadir la dependencia (auditoría 06).
- [ ] **UI-03 — Pasar a signals el estado asíncrono restante.** Reporte General, Tendencias, Carga y Administración refrescan la vista con un `ChangeDetectorRef` inyectado, que queda inválido tras un reemplazo en caliente (HMR) y deja la pantalla en "Cargando…". Migrar su estado a signals, como el Explorador, Publicaciones, el Directorio y la Ficha del egresado (auditoría 06, U-12/UI-03). Observado el 2026-09-30: además, el endpoint de HMR de `ng serve` (`@ng/component`) puede seguir entregando una plantilla anterior incluso tras una recarga completa; si una pantalla no refleja un cambio de plantilla, reiniciar `ng serve`.

## P2 — Publicaciones y carga (auditoría 07)

- [ ] **PUB-03 — Retirar desde la interfaz la publicación de un coordinador anterior.** RN-09 y el backend permiten que un coordinador retire la publicación de un propietario inactivo o reasignado, pero la sección "Publicadas por otros coordinadores" de `/publicaciones` no ofrece la acción (C-06). Requiere actualizar primero `mockups/publicaciones.html` y `screen-map.md`.
- [ ] **PUB-04 — Confirmación de privacidad informada.** El coordinador confirma la privacidad antes de que el backend aplique k = 5, sin ver la instantánea que se publicará (B-05). El diálogo debe recordar además el riesgo residual de publicar la misma métrica con filtros solapados (ADR-020, punto 6). Requiere mockup del diálogo.
- [ ] **CAR-01 — Avisar que una recarga reemplaza la cohorte.** La pantalla de carga debe advertir que un archivo con la misma sede, momento y año sustituye la versión vigente completa y que cada cohorte se carga en un único archivo consolidado (ADR-020, punto 8). Requiere mockup.
- [ ] **PUB-05 — Publicaciones derivadas de cargas eliminadas o reemplazadas.** Una instantánea sigue vigente aunque se elimine o reemplace la carga de la que salió (B-06). Producto debe decidir si se retira, se marca como desactualizada o se notifica al propietario.

## P2 — Calidad

- [ ] **TST-01 — Retirar los scripts de prueba de la raíz del backend.** `test_diagnostico.py`, `test_ia_pipeline.py`, `test_prediccion_empleabilidad.py` y `test_reglas_asociacion.py` usan la base configurada en `.env` y no corren con `unittest discover`. Pasar sus casos a `tests/` sobre SQLite en memoria (como `test_ia_alcance.py`) o retirarlos (estudio del proyecto, 2026-10-06).

## P2 — Autenticación

- [ ] **AUT-01 — Ciclo de vida de cuentas CTIC y de sedes.** No hay flujo para crear, desactivar o recuperar una cuenta `Admin_CTIC` ni para desactivar una sede, y no se define el efecto sobre usuarios, cargas y publicaciones (B-12, B-13). Tampoco hay política de contraseña personal, cambio voluntario ni límite de intentos (B-18).

- [ ] **FE-05 — Mostrar el rechazo de correos no institucionales en el login.** `LoginUseCase.execute` lanza un error síncrono cuando el correo no contiene `@upb.edu.co`; `LoginComponent.onSubmit` no lo captura, así que el botón queda en "Procesando…" y no aparece ningún mensaje. El caso de uso debe devolver un `Observable` con error (o el componente capturar la excepción) y la pantalla mostrar el motivo. Observado el 2026-09-30 durante la validación de PUB-01/PUB-02.

## P2 — Analítica

- [ ] **ANA-03 — Verificar el mapeo laboral con datos de M5.** ADR-016 supone que el cuestionario de M5 usa la misma redacción que M1. Cuando exista una carga de M5, confirmar los nombres de las preguntas y sus opciones de respuesta (sin leer datos personales) y ajustar `application/indicadores.py` si difieren.

## P3 — Validación de producto

- [ ] **PRD-01 — Validar las prioridades y los criterios RNF propuestos.** El 2026-09-25 se propusieron la prioridad de los RF/RNF y los criterios verificables de RNF-01 a RNF-06 (`requirements/01-requerimientos.md`). Producto debe confirmarlos o ajustarlos, y después hay que automatizar la medición de RNF-06 (rendimiento con 50.000 mediciones). Incluye revisar el campo "Requerimiento Ligado", que tiene dependencias no funcionales y prioridades invertidas (RF-14 ← RF-13, RF-29 ← RF-28, RF-56 ← RF-55, RF-58 ← RF-57; auditoría 07, C-19).

## Completadas recientemente
 
- [x] **IA-01 — Modelo predictivo de empleabilidad.** Implementado y validado conforme a ADR-019 y RF-71 con `GradientBoostingClassifier`, validación cruzada estratificada, endpoint `/api/ia/prediccion-empleabilidad` y visualización institucional por programa en la vista de Analítica y alertas.
