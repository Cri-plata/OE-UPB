# Design system de OE UPB

**Estado:** tokens globales implementados y validados

**Fecha:** 2026-09-24

## Principios

- Interfaz institucional clara y sobria.
- Información analítica legible antes que decoración.
- Acciones destructivas y errores distinguibles sin depender únicamente del color.
- Componentes responsivos y navegables con teclado.
- Tokens globales antes que colores hexadecimales dentro de componentes.

## Tokens base

```scss
:root {
  --color-brand: #c8102e;
  --color-brand-dark: #a00d25;
  --color-background: #f4f6f9;
  --color-background-subtle: #f8f9fa;
  --color-banner: #e9ecef;
  --color-surface: #ffffff;
  --color-navigation: #1a1a1a;
  --color-text: #121212;
  --color-text-heading: #212529;
  --color-text-body: #495057;
  --color-text-muted: #6c757d;
  --color-border: #dee2e6;
  --color-border-control: #ced4da;
  --color-success: #1e7e34;
  --color-info: #0056b3;
  --color-error: #c8102e;
  --radius-sm: 4px;
  --radius-md: 8px;
  --radius-lg: 12px;
  --space-1: 4px;
  --space-2: 8px;
  --space-3: 12px;
  --space-4: 16px;
  --space-6: 24px;
  --space-8: 32px;
}
```

Los componentes consumen estos tokens mediante `var(...)`. Las paletas de Chart.js se centralizan en `presentation/shared/chart-palette.ts`. `tools/validate_frontend_architecture.py` impide HTTP directo desde Presentation y hexadecimales repetidos fuera de tokens.

## Tipografía

- Familia actual: Segoe UI con fallbacks del sistema.
- Texto base recomendado: 16 px.
- Etiquetas y ayudas: mínimo 14 px.
- Indicadores KPI pueden usar mayor tamaño, conservando etiqueta accesible.

## Componentes

- **Botón primario:** fondo brand, texto blanco, foco visible.
- **Botón destructivo:** color error y confirmación para operaciones irreversibles.
- **Campos:** etiqueta persistente, error asociado y contraste AA.
- **Tarjetas KPI:** título, valor, unidad y contexto temporal.
- **Gráficas:** leyenda, texto alternativo/resumen tabular y paleta distinguible.
- **Tablas:** encabezados claros, paginación y estados vacío/carga/error.

## Reglas

1. No añadir nuevos hexadecimales en componentes si existe token semántico.
2. No usar color como único indicador de estado.
3. Todo control debe tener foco visible y nombre accesible.
4. Los cambios globales deben validarse al menos en login, dashboard, carga y directorio.
5. `requirements/04-hallazgos-figma.md` es evidencia histórica, no el sistema de diseño vigente.
