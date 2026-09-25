---
name: Academic Analytics & Observatorio
colors:
  surface: '#f9f9f7'
  surface-dim: '#dadad8'
  surface-bright: '#f9f9f7'
  surface-container-lowest: '#ffffff'
  surface-container-low: '#f4f4f2'
  surface-container: '#eeeeec'
  surface-container-high: '#e8e8e6'
  surface-container-highest: '#e2e3e1'
  on-surface: '#1a1c1b'
  on-surface-variant: '#5d3f3c'
  inverse-surface: '#2f3130'
  inverse-on-surface: '#f1f1ef'
  outline: '#926f6b'
  outline-variant: '#e7bdb8'
  surface-tint: '#c00014'
  primary: '#ba0013'
  on-primary: '#ffffff'
  primary-container: '#e31e24'
  on-primary-container: '#fffafa'
  inverse-primary: '#ffb4ab'
  secondary: '#785a00'
  on-secondary: '#ffffff'
  secondary-container: '#fdc008'
  on-secondary-container: '#6c5000'
  tertiary: '#5e5b5a'
  on-tertiary: '#ffffff'
  tertiary-container: '#777373'
  on-tertiary-container: '#fffbfa'
  error: '#ba1a1a'
  on-error: '#ffffff'
  error-container: '#ffdad6'
  on-error-container: '#93000a'
  primary-fixed: '#ffdad6'
  primary-fixed-dim: '#ffb4ab'
  on-primary-fixed: '#410002'
  on-primary-fixed-variant: '#93000d'
  secondary-fixed: '#ffdf9d'
  secondary-fixed-dim: '#f9bd00'
  on-secondary-fixed: '#251a00'
  on-secondary-fixed-variant: '#5b4300'
  tertiary-fixed: '#e7e1e1'
  tertiary-fixed-dim: '#cbc5c5'
  on-tertiary-fixed: '#1d1b1b'
  on-tertiary-fixed-variant: '#494646'
  background: '#f9f9f7'
  on-background: '#1a1c1b'
  surface-variant: '#e2e3e1'
  panel-dark-surface: '#1A1818'
  panel-dark-surface-elevated: '#232121'
  panel-dark-border: '#27272A'
  panel-dark-text-primary: '#FFFFFF'
  panel-dark-text-secondary: '#E4E4E7'
  panel-dark-text-muted: '#A1A1AA'
  surface-canvas: '#F4F4F2'
  surface-card: '#FFFFFF'
  surface-card-subtle: '#ECECE8'
  text-primary-light: '#1A1818'
  text-muted-light: '#5C5857'
  status-success: '#137A47'
  ai-indigo: '#6366F1'
typography:
  display-lg:
    fontFamily: Plus Jakarta Sans
    fontSize: 36px
    fontWeight: '700'
    lineHeight: 44px
    letterSpacing: -0.02em
  display-lg-mobile:
    fontFamily: Plus Jakarta Sans
    fontSize: 28px
    fontWeight: '700'
    lineHeight: 36px
    letterSpacing: -0.015em
  headline-lg:
    fontFamily: Plus Jakarta Sans
    fontSize: 28px
    fontWeight: '700'
    lineHeight: 36px
    letterSpacing: -0.015em
  headline-md:
    fontFamily: Plus Jakarta Sans
    fontSize: 22px
    fontWeight: '600'
    lineHeight: 28px
    letterSpacing: -0.01em
  headline-sm:
    fontFamily: Plus Jakarta Sans
    fontSize: 18px
    fontWeight: '600'
    lineHeight: 24px
  title-md:
    fontFamily: Plus Jakarta Sans
    fontSize: 16px
    fontWeight: '600'
    lineHeight: 22px
  body-lg:
    fontFamily: Plus Jakarta Sans
    fontSize: 15px
    fontWeight: '400'
    lineHeight: 22px
  body-md:
    fontFamily: Plus Jakarta Sans
    fontSize: 13px
    fontWeight: '400'
    lineHeight: 18px
  body-sm:
    fontFamily: Plus Jakarta Sans
    fontSize: 12px
    fontWeight: '400'
    lineHeight: 16px
  metric-stat:
    fontFamily: Plus Jakarta Sans
    fontSize: 32px
    fontWeight: '700'
    lineHeight: 36px
    letterSpacing: -0.03em
  label-md:
    fontFamily: Plus Jakarta Sans
    fontSize: 12px
    fontWeight: '600'
    lineHeight: 16px
    letterSpacing: 0.02em
  label-sm:
    fontFamily: Plus Jakarta Sans
    fontSize: 11px
    fontWeight: '500'
    lineHeight: 14px
    letterSpacing: 0.04em
rounded:
  sm: 0.25rem
  DEFAULT: 0.5rem
  md: 0.75rem
  lg: 1rem
  xl: 1.5rem
  full: 9999px
spacing:
  gutter: 1rem
  gutter-lg: 1.5rem
  margin: 1rem
  margin-md: 1.5rem
  margin-lg: 2rem
  space-xs: 0.25rem
  space-sm: 0.5rem
  space-md: 0.75rem
  space-lg: 1.25rem
  space-xl: 2rem
---

## Governance

**Status:** canonical and mandatory for mockups and implemented UI.

- This file replaces `design-system.md` as the single source of visual rules.
- Any design-system change updates this file before it changes mockups or application code.
- Mockups are the required design contract for UI implementation and are indexed in `../mockups/screen-map.md`.

## Brand & Style

The design system establishes a high-performance institutional analytics environment for monitoring alumni employment, postgraduate trajectories, regional impact, and academic accreditation indicators. It unites institutional prestige with contemporary data architecture, projecting authority, analytical rigor, and functional clarity.

### Personality & Tone
- **Scholarly & Authoritative:** Reflects academic heritage and institutional credibility without bureaucratic friction.
- **Analytical & Precise:** Tuned for high-density tabular and graphical displays, rapid scannability, and structured hierarchy.
- **Bifurcated & Ergonomic:** Bridges an expansive, high-luminance analytical canvas with a focused, high-contrast dark institutional sidebar for global orientation and filtering.

### Aesthetic Movement: Dual-Zone Architectural Modernism
The design system draws from **Corporate / Modern** principles paired with **High-Contrast Data-Driven** aesthetics:
- **Navigation Anchor (Left Sidebar in `#1A1818`):** A persistent institutional pillar housing global routing, campus selection (multi-sede), and master analytical filters. It leverages crisp white typography, muted neutral accents, active states anchored by primary red (`#E31E24`), and subtle milestone details in golden yellow (`#FFC20E`).
- **Primary Analytics Canvas (`#F4F4F2` with `#FFFFFF` Cards):** A daylight-balanced workspace providing ergonomic readability during prolonged data review, detailed cohort tables, and dimensional charts.

## Colors

The system uses an intentional four-token hierarchy engineered for distinct operational zones:

### Palette Roles
- **Primary Red (`#E31E24`):** The primary brand anchor for active navigation indicators, essential calls to action, selected interactive filters, and alert states.
- **Secondary Yellow (`#FFC20E`):** Analytical highlight tone applied to critical milestones, metric badges, progress summaries, and observational alerts.
- **Tertiary Dark Graphite (`#1A1818`):** The dominant base for the left navigation rail, ensuring clear structural separation between the navigation shell and the data work area.
- **Neutral Canvas (`#F4F4F2`):** Soft, low-glare surface for the main viewport, providing high contrast against elevated `#FFFFFF` analytical widgets.

### Architectural Dual-Zone Color Model
1. **Left Navigation Rail (`#1A1818` Ground):**
   - Background set to `#1A1818` with elevated items and hover wells at `#232121` and structural dividers in `#27272A`.
   - Text hierarchy: `#FFFFFF` for primary labels and active links, `#E4E4E7` for standard navigation items, and `#A1A1AA` for section metadata, counts, and breadcrumb chips.
   - Active navigation items display a left accent bar or solid highlight in `#E31E24`, accented with milestone tags in `#FFC20E`.
2. **Main Workspace Canvas (`#F4F4F2` Ground / `#FFFFFF` Containers):**
   - High legibility with neutral separation borders (`#ECECE8`).
   - Primary metric numerals and titles render in `#1A1818`, with descriptive labels and metadata in `#5C5857`.

## Typography

The typography leverages **Plus Jakarta Sans** consistently across navigation, data displays, and editorial text blocks.

### Rules for Numerical and Analytical Display
- **Tabular Figures:** Always apply `font-variant-numeric: tabular-nums` to tables, metric tickers, cohort percentages, and date filters to prevent horizontal shifting during live data reloads.
- **Metric Presentation:** Core statistical callouts use `metric-stat` with tight tracking (`-0.03em`) for optical stability.
- **Section Headers & Captions:** Sidebar section titles, badge text, and column headers employ uppercase styling via `label-sm` or `label-md` with expanded letter-spacing (`0.02em` to `0.04em`) to maintain legibility on the dark `#1A1818` background.

## Layout & Spacing

The layout is structured around an asymmetrical split architecture with a persistent left navigation rail and a fluid analytical work area.

### Viewport Structure
- **Left Navigation Sidebar (`#1A1818`):** Fixed width of `280px` on desktop viewports (`>= 1280px`), collapsing to an icon-rail format (`72px`) on tablet screens (`768px - 1279px`), and transforming into an off-canvas drawer on mobile (`< 768px`).
- **Main Workspace Canvas (`#F4F4F2`):** Spans the remaining viewport width, hosting an adaptable 12-column grid system with `gutter-lg` (`1.5rem`) and `margin-lg` (`2rem`) padding.
- **Rhythm & Padding:** Component interiors follow an 8px modular cadence (`space-xs` = 4px, `space-sm` = 8px, `space-md` = 12px, `space-lg` = 20px, `space-xl` = 32px). Sidebar navigation rows maintain a compact 40px height with `space-sm` vertical spacing.

## Elevation & Depth

Visual hierarchy is maintained through crisp surface planes and tonal layering, avoiding heavy, diffuse shadows.

### Elevation Levels
- **Level 0 (Base Foundation):** Flush `#F4F4F2` for the main workspace; continuous `#1A1818` for the navigation sidebar.
- **Level 1 (Cards & Data Panels):** `#FFFFFF` surfaces on the canvas bordered with `1px solid rgba(26, 24, 24, 0.08)` and subtle diffusion: `0 1px 3px rgba(26, 24, 24, 0.04), 0 1px 2px rgba(26, 24, 24, 0.02)`. In the sidebar, grouped sections and flyouts sit on `#232121` with `1px solid #27272A`.
- **Level 2 (Hover & Active States):** Navigation items on hover shift to `#232121`. Active cards in the canvas elevate slightly with `0 4px 12px rgba(26, 24, 24, 0.06)`.
- **Level 3 (Modals & Command Drawers):** Overlays sit on `0 16px 32px rgba(0, 0, 0, 0.2)` accompanied by a backdrop filter (`rgba(26, 24, 24, 0.6)` with `backdrop-filter: blur(4px)`).

## Shapes

The design system enforces a **Rounded** shape language (`roundedness: 2`, base radius 8px) balancing administrative rigor with modern usability.

### Corner Radius System
- **Buttons, Form Inputs, Sidebar Nav Links:** 0.5rem (8px).
- **Analytical Cards, Chart Containers (`rounded-lg`):** 0.75rem (12px).
- **Modals, Floating Panels, Popover Shells (`rounded-xl`):** 1.0rem (16px).
- **Status Pills, Cohort Tags, Filter Chips (`rounded-full`):** 9999px.

## Components

### Left Navigation Sidebar (`#1A1818`)
- **Structure:** Solid `#1A1818` background, right-side border `1px solid #27272A`, full viewport height with an independent scroll container.
- **Institutional Header:** Institutional branding lockup displaying the observatory insignia, white primary title, and `#A1A1AA` metadata caption.
- **Navigation Links:** Text in `#E4E4E7` (`13px`, medium weight), 8px border-radius, left-to-right flex alignment with 20px icons.
- **Active Navigation State:** Background `#232121`, text `#FFFFFF`, left accent indicator `3px solid #E31E24`, with an optional right-aligned pill counter in `#FFC20E` text over `rgba(255, 194, 14, 0.15)` fill.
- **Sede Context:** The sidebar may show the session's assigned sede as read-only context in a `#232121` container. It is never a selector for expanding data scope; access to source data remains fixed by the authenticated session.

### Analytical Cards (`#F4F4F2` Workspace)
- **Container:** Pure `#FFFFFF` surface, 12px radius, uniform perimeter border `1px solid rgba(26, 24, 24, 0.08)`, inner padding `space-lg`.
- **Prohibición de bordes de acento:** Están estrictamente prohibidos los bordes de color laterales (izquierdo o derecho) o superiores como franjas de alerta o estado en tarjetas y paneles. Las tarjetas conservan su perímetro neutro uniforme; cualquier estado de alerta, éxito o seguimiento debe comunicarse mediante badges, pills o encabezados semánticos en el contenido interno.
- **Header:** Title in `headline-sm` (`#1A1818`), paired with action slots for time-range selectors or CSV export triggers.

### Buttons & Interactive Controls
- **Primary Institutional Button:** `#E31E24` background, `#FFFFFF` text, 8px radius. Hover shifts to `#C41419`. Focus ring: 2px offset in `#E31E24`.
- **Secondary Neutral Button:** `#FFFFFF` background, `1px solid rgba(26, 24, 24, 0.15)`, text `#1A1818`. Hover state fills `#F4F4F2`.
- **Sidebar Action Button:** High-priority actions within the sidebar use `#FFC20E` text with `rgba(255, 194, 14, 0.12)` background and `1px solid #FFC20E` border.

### Chips & Filter Tags
- **General Filter Chips:** Background `#ECECE8`, text `#5C5857`, 9999px radius. When selected: `#E31E24` background, `#FFFFFF` text.
- **Sidebar Milestone Badges:** 9999px pill, `#232121` background, `#FFC20E` text, border `1px solid rgba(255, 194, 14, 0.3)`.

### Form Fields & Inputs
- **Text & Select Fields:** `#FFFFFF` background, border `1px solid rgba(26, 24, 24, 0.15)`, text `#1A1818`, height 40px, radius 8px. Focus state outlines in `#E31E24` with zero displacement.
- **Sidebar Search & Filters:** Dark input style with background `#232121`, border `1px solid #27272A`, placeholder text `#A1A1AA`, and value text `#FFFFFF`.

### Data Tables
- **Header Row:** Background `#ECECE8`, typography `label-sm` in `#5C5857` uppercase, active sort indicators highlighted in `#E31E24`.
- **Data Rows:** Alternating row highlight (pure `#FFFFFF` to `#F9F9F7`), bottom hairline divider `1px solid #ECECE8`, numeric values set with `tabular-nums`.

## Iconography

- **Standard library:** Lucide is the only general-purpose icon library for mockups and frontend. Angular implementations use `lucide-angular`; static mockups use the matching Lucide web distribution.
- **No emoji:** emojis, Unicode pictograms and decorative symbols are prohibited as UI content or icon substitutes.
- **Sizes:** navigation and inline icons use 20px; compact table actions use 16px; empty states and upload areas may use 40–48px.
- **Color:** icons inherit the surrounding text color. Brand red is reserved for selected navigation, destructive emphasis and primary actions; yellow is reserved for milestones and warnings.
- **Accessibility:** decorative icons use `aria-hidden="true"`. Icon-only actions require `aria-label`; actions with visible text do not repeat that text for assistive technology.
- **Consistency:** the same action must use the same Lucide icon across every screen. Initial mapping: search=`search`, add=`plus`, edit=`pencil`, delete=`trash-2`, upload=`upload`, download/export=`download`, publish=`send`, withdraw=`undo-2`, profile=`user-round`, users=`users`, report=`chart-no-axes-combined`, trends=`chart-spline`, explorer=`sliders-horizontal`, alerts=`triangle-alert`, directory=`contact-round`, logout=`log-out`.

## Page Composition

- Every authenticated desktop screen uses the 280px dark sidebar and a `#F4F4F2` workspace. Page content uses a maximum readable width while charts and tables may span the available canvas.
- Page headers contain one `headline-lg` title, optional body text and only the actions that affect the entire page. Local actions remain inside their card or table.
- Filters precede the affected result and use the same card plane, spacing rhythm and 40px controls defined above.
- Authentication screens omit the sidebar and center a single card on the neutral canvas.

## Interaction States

Every interactive component and data region must define the following applicable states in both mockup and implementation:

- **Default, hover, focus-visible, active and disabled.** Focus uses a visible 2px primary ring and cannot rely on color alone.
- **Loading:** preserve the final layout dimensions. Use a neutral skeleton or a concise loading label; disable actions that would duplicate the request.
- **Empty:** explain what is absent and, when authorized, offer one clear recovery or creation action. Never fabricate records or metrics.
- **Error:** use `error-container` with `on-error-container`, state what failed and expose retry when safe.
- **Success:** use `status-success` for confirmation text or a compact status pill; do not turn whole cards green.
- **Validation:** place field errors directly below the related control and provide a summary only when the form has multiple invalid sections.

## Modals and Overlays

- Modals use a 16px radius, `#FFFFFF` surface, maximum width appropriate to the task, Level 3 shadow and a `rgba(26, 24, 24, 0.6)` backdrop with 4px blur.
- The title and consequence appear before form content. Actions are right-aligned on desktop and stack on narrow screens; the primary action appears last in reading order.
- Destructive confirmation names the target and consequence. Credential dialogs never display real credentials in mockups or documentation.
- Every screen that can present a modal must maintain separate mockups for the base state and each materially different modal state.

## Charts and Analytical Data

- Chart series use a stable accessible palette derived from primary red, secondary yellow, `status-success`, `ai-indigo` and neutral graphite. Meaning may not rely on hue alone.
- Axes, legends, tooltips and empty/loading/error states are mandatory where applicable. Numbers use tabular figures.
- Chart type selectors and export/publication actions live in the chart header. A chart card must not change size when its state changes.
- Published visualizations show origin, version and update date without exposing individual records.

## Tables, Pagination and Density

- Tables remain readable at 320px through horizontal containment or a documented responsive alternative; columns must not overlap or silently disappear.
- Pagination appears below the table and includes current page, total pages and total records when available.
- Row actions use visible text or Lucide icons with accessible labels. Destructive actions are visually distinct and never represented only by color.
- Empty and loading rows span the full table width and preserve the header structure.

## File Upload

- Upload areas use a 2px dashed neutral border, 12px radius and a Lucide `upload` or `file-spreadsheet` icon. Drag-over, selected, validating, success and error states are required.
- Accepted formats and size constraints appear before selection. OE UPB accepts only `.xlsx`; mockups must not advertise `.xls`.
- The selected filename is visible, but mockups and documentation never use real personal filenames.

## Mockup and Implementation Gate

1. A new screen or visual change starts in `mockups/` and is registered in `mockups/screen-map.md`.
2. The mockup must use this design system and include relevant responsive, loading, empty, error and modal variants.
3. UI implementation begins only after the corresponding mockup exists and its intended flow is documented.
4. The Angular implementation uses the same semantic tokens and Lucide mapping; hard-coded substitutes and emojis are not accepted.
5. A UI change is incomplete until mockup, screen map, implementation and tests agree.
