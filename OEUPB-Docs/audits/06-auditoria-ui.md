# Auditoría de diseño UI 06

**Estado:** Resuelta, con dos pendientes registrados en el backlog (UI-02 y UI-03)
**Fecha:** 2026-09-25
**Referencia:** [`../design/design.md`](../design/design.md), [`../mockups/`](../mockups/) y [`../mockups/screen-map.md`](../mockups/screen-map.md)

## Método

- La app se recorrió con una sesión de coordinador y datos locales, y los 13 mockups se sirvieron por HTTP. Ambos se midieron en 1440, 1024 y 375 px.
- Un script de medición detectó elementos que salían de la ventana o cuyo contenido superaba a su contenedor, excluyendo `.table-scroll`, que se desplaza a propósito. También comparó estilos computados (alto, radio, tipografía y bordes) entre el mockup y la pantalla real.
- Se revisó estáticamente el cumplimiento de `design.md`: emojis, paleta de gráficas, iconografía y estados.
- También se midieron los tiempos reales de los endpoints desde el navegador, porque una pantalla que tarda en cargar no permite validar su diseño.

## Hallazgos y resolución

| ID | Hallazgo | Severidad | Resolución |
|---|---|---|---|
| U-01 | Reporte General: la grilla de gráficas medía 1.816 px dentro de un contenedor de 1.088 px y la página llegaba a 2.128 px a 1440. Causa: pistas `1fr` que toman el ancho mínimo del `<canvas>` de Chart.js. | Alta | `repeat(2, minmax(0, 1fr))` y `min-width: 0` en tarjetas. |
| U-02 | Administración de usuarios desbordaba en los tres anchos (1.738, 1.138 y 1.058 px): la tabla de 1.000 px de ancho mínimo agrandaba la columna `1fr`. **El mockup tenía el mismo defecto.** | Alta | `minmax(320px, 380px) minmax(0, 1fr)` en la app y en `mockups.css`. |
| U-03 | Carga de datos desbordaba a 375 px (708 px). | Alta | `340px minmax(0, 1fr)` y colapso a `minmax(0, 1fr)`; mismo ajuste en `upload-grid` del mockup. |
| U-04 | Explorador: el selector de pregunta tomaba el ancho de la opción más larga (1.007 px) a 1024 y 375. | Alta | `min-width: 0` en el grupo y el select, y `display: block` en el host del bloque. |
| U-05 | Las casillas de permisos se veían como controles de 201×40 px: la regla global `.form-group input` también se aplicaba a los checkbox. | Media | La regla excluye `checkbox`/`radio`; casillas de 16 px con `accent-color` de marca. |
| U-06 | Los controles de la cabecera de gráfica usaban `.table-action` (32 px, radio de 4 px), reservado para filas de tabla; el mockup define 34 px, radio de 8 px y fondo `background-subtle`. | Media | Regla global `.chart-actions` idéntica a `mockups.css`. |
| U-07 | Reporte General con 4 KPI en una grilla de 3 columnas: la cuarta tarjeta caía a una fila aparte, y a 1280 px los textos se partían en tres líneas. | Media | 4 columnas a partir de 1440 px, 2×2 por debajo y 1 columna en móvil. Valor en 28/700 con `tabular-nums` y `-0.03em`, como en el mockup. |
| U-08 | Los filtros analíticos no seguían el patrón canónico: controles de alto variable, radio de 6 px y botones con estilo propio. "Limpiar filtros" caía a otra línea. | Media | Reescritos con el patrón `filters-card` / `filter-group` del Directorio: etiquetas de 13 px, controles de 40 px con radio de 8 px, `btn-primary` y `btn-secondary`. |
| U-09 | La paleta de gráficas (`#c8102e`, `#1d3557`…) no derivaba de `design.md`. | Media | Rojo, índigo, verde de estado, amarillo, grafito y variantes, igual en el frontend (`CHART_PALETTE`) y en el backend (`PALETA`, `COLORES_TENDENCIAS`). |
| U-10 | El icono del KPI azul usaba `rgb(2,136,209)`, ajeno al sistema. | Baja | Token nuevo `--ai-indigo` (`#6366f1`). |
| U-11 | La pantalla de carga usaba el pictograma "✕" como botón, prohibido por `design.md`. | Baja | Botón de texto "Cancelar". |
| U-12 | Rendimiento: la inicialización del Explorador tardaba 20 s, la Analítica 9,1 s, el Reporte General 2,1 s y Tendencias 4,7 s. Las pantallas se quedaban en "Cargando…". | Alta | Memoización de la normalización de nombres de pregunta (`lru_cache`) y una sola consulta para todo el Reporte General. Tiempos resultantes: 0,4–1,4 s. |
| U-13 | Las pantallas nuevas (filtros, comparación de momentos, varias gráficas, formalidad, estado laboral y programas sin datos) no tenían mockup ni entrada en `screen-map.md`, como exige el gate de `design.md`. | Media | Mockups de Reporte General, Tendencias, Explorador y Gestión de usuarios actualizados, con las clases en `mockups.css` y las filas y la regla `minmax(0, 1fr)` en `screen-map.md`. |

Después de las correcciones, las 9 pantallas de la app y los 13 mockups no desbordan en 1440, 1024 ni 375 px.

## Pendientes

- **UI-02 — Iconografía con `lucide-angular`.** La barra lateral carga los SVG de Lucide en tiempo de ejecución desde `unpkg.com` mediante máscaras CSS, y los KPI y la carga usan SVG escritos a mano. `design.md` exige `lucide-angular`, que no está instalado. La migración requiere añadir esa dependencia.
- **UI-03 — Estado asíncrono en signals.** Reporte General, Tendencias, Carga, Administración y Directorio actualizan la vista con un `ChangeDetectorRef` inyectado. Con el reemplazo en caliente del servidor de desarrollo (HMR), ese `ChangeDetectorRef` queda apuntando a una vista destruida y la pantalla se queda en "Cargando…" aunque la API responda. Se verificó con `destroyed: true` y las peticiones `@ng/component`. No afecta a producción ni a un `ng serve` recién iniciado, pero confirma la convención de `architecture/01-frontend.md`: el estado asíncrono debe vivir en signals, como ya ocurre en el Explorador y en Publicaciones.
