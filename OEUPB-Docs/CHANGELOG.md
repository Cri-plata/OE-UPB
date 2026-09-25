# Historial de Cambios (Changelog)

Este documento registra únicamente cambios de la documentación canónica. Los cambios funcionales del monorepo se registran en `../CHANGELOG.md`.

## [2026-09-25] - P3 Calidad de contrato y documentación

* **Modelo:** el diagrama ER coincide con el esquema SQL (auditorías, eventos de eliminación y columnas de publicaciones).
* **Requisitos:** prioridad propuesta para los 81 RF/RNF, `Requerimiento Ligado` corregidos y criterios verificables propuestos para RNF-01 a RNF-06 (validación pendiente en PRD-01).
* **Reglas:** RN-29 define la clave normalizada de programas y el tratamiento de programas sin datos actuales.
* **Contratos:** 03-contratos documenta `ErrorResponse`, los códigos por endpoint y las operaciones obsoletas.
* **Backlog:** API-02, PRG-01, ANA-02 y DOC-03 se archivaron; se agregó PRD-01.

## [2026-09-25] - P2 Analítica y contratos

* **ADR-016:** mapeo de los cuestionarios OLE a la taxonomía laboral, la formalidad, el salario y la comparación de momentos.
* **ADR-017:** normalización del documento de identidad, límites de carga y rechazo con detalle por fila.
* **Requisitos:** RF-21, RF-22, RF-23, RF-25, RF-26 y RF-61 pasan a Implementado. RN-01, RN-16, RN-26 y RN-31, HU-07 y CU-05 a CU-07 se actualizaron.
* **Backlog:** EXP-03, ANA-01, DB-03 y ETL-01 se archivaron; se agregó ANA-03 y se amplió ANA-02.

## [2026-09-25] - Corrección integral de mockups según auditoría

* **Tokens y espaciado:** se expuso la cadencia modular de espaciado (`--space-2xs` a `--space-3xl`), radios (`--radius-sm` a `--radius-full`) y padding dinámico en `mockups.css`.
* **Sidebar responsive:** implementación del rail iconográfico de 72 px en tablet (`768–1279 px`) y drawer overlay para móvil (`< 768 px`) con barra superior institucional (`.mobile-header`), toggle accesible y backdrop oscuro.
* **Contención horizontal:** se creó `.table-scroll` y se fijaron anchos mínimos específicos para Directorio (900 px), Gestión de usuarios (1000 px) e Historial de carga (650 px), retirando recortes invisibles en `.table-card`.
* **Jerarquía de acciones:** botones compactos de tabla a 32 px; acciones destructivas de fila (`Eliminar`, `Desactivar`, `Retirar`) migradas a estilo outline sutil (`.table-action.btn-danger`), reservando el relleno sólido para confirmaciones en modal.
* **Formularios y modales:** etiquetas accesibles visibles en login y cambio de contraseña; panel de control del Explorador reestructurado en dos filas; modales con contención vertical, scroll interno y apilamiento en móvil.
* **Mapa de pantallas:** `screen-map.md` actualizado con matriz de anchos de referencia responsive y registro exhaustivo de variantes por pantalla.
* **Regla de tarjetas sin bordes de acento:** se prohibieron explícitamente los bordes de acento de color laterales (izquierdo/derecho) o superiores en tarjetas y paneles en `design/design.md`, `CLAUDE.md` y `screen-map.md`, retirando la clase `border-alert` en `analitica.html` y bordes laterales de contenedores.

## [2026-09-25] - Mockups de las pantallas actuales

* **Diseño:** `design/design.md` reemplaza formalmente a `design-system.md` como fuente canónica y obligatoria para mockups y frontend. Se añadieron reglas de iconografía Lucide, estados, modales, gráficos, tablas, carga de archivos y el bloqueo de implementación sin mockup previo.
* **Mockups:** se añadieron HTML/CSS navegables de las pantallas existentes en `mockups/`, junto con un mapa de pantallas, roles y flujos. Cada pantalla tiene un HTML estilizado en la misma carpeta que `mockups.css`; los dos modales implementados se documentan en variantes con y sin modal y las tablas muestran datos sintéticos para revisión visual.
* **Gobierno UI:** `screen-map.md` pasa a ser obligatorio en todo cambio de pantalla o flujo y se prohíben emojis y pictogramas Unicode como sustitutos de iconos.

## [2026-09-25] - Actualización de verificación

* **Pruebas:** la estrategia y el estado funcional reflejan 38 pruebas de backend y 23 de frontend, los casos de privacidad de publicación y la convención de pruebas zoneless.
* **Estado:** se actualizaron CU-12, la fecha de corte funcional y las fechas de verificación del modelo de datos y del despliegue.

## [2026-09-25] - Corrección del flujo de publicación

* **PUB-01/PUB-02:** se documentó la causa (detección de cambios zoneless con estado fuera de signals), la corrección, las pruebas y la lista de validación manual. RF-35 sigue Parcial hasta esa validación.
* **Arquitectura frontend:** se registró la convención de usar signals para el estado asíncrono.

## [2026-09-25] - Auditoría de requerimientos 05

* **Auditoría:** se ejecutó `audits/auditoria_requerimientos.md` (20 contradicciones y 21 casos de borde) y se verificó cada hallazgo contra código y ADR en `audits/05-auditoria-requerimientos.md`.
* **Decisiones:** ADR-014 saca del alcance la custodia institucional y las encuestas manuales y fija la precedencia de cargas. ADR-015 exige recálculo en backend, umbral k = 5 y autoaprobación explícita de las publicaciones.
* **Requisitos:** se alinearon RN-01, 07, 09, 12-15, 18, 22-24, 26, 28 y 31, HU-01, 05-09 y 11-13, y CU-02 a CU-12 con RN-24, ADR-013, ADR-014 y ADR-015. RF-21, RF-22 y RF-26 pasan a Parcial.
* **Arquitectura y operación:** se completaron inventarios de routers y rutas, frontera de publicación, invariantes del modelo y enmascaramiento de logs.
* **Backlog:** EXP-02 archivado; nuevos ítems ANA-01, DB-03, ETL-01, API-02, PRG-01, ANA-02 y DOC-03.
