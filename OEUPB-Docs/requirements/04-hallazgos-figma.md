# Hallazgos y Análisis de Mockups (OE UPB)

> **Estado:** evidencia histórica de diseño. La fuente vigente para estilos y componentes es [`../design/design-system.md`](../design/design-system.md). La selección manual de sede durante la carga y el rechazo genérico de cédulas duplicadas quedaron reemplazados por RN-01, RN-06 y ADR-006. La publicación entre sedes ocurre desde cada gráfica, no desde la pantalla de carga.

Tras analizar los 8 nuevos mockups (UI en Modo Claro / Blanco con colores institucionales UPB) y cruzarlos con las Actas de Reunión del 19 de Agosto, se han encontrado las siguientes correspondencias y faltantes:

## 1. Correspondencia Directa (Mockups vs Requerimientos)
*   **Ficha del Egresado:** Representa visualmente la ficha individual y una línea de tiempo de momentos (0, 1 y 5). Esta evidencia visual no verifica el filtrado por sede ni la implementación del flujo.
*   **Reporte General (Dashboard):** Representa visualmente filtros históricos de Sede, Facultad y Cohorte, además de métricas de empleabilidad y salarios. La política vigente exige derivar la sede propia del JWT y separar las publicaciones agregadas de otras sedes.
*   **Administración de Datos:** El mockup histórico permite seleccionar Momento y Sede. La política vigente conserva la selección de Momento, pero la sede debe derivarse del JWT del coordinador y no puede seleccionarse para ampliar alcance.
*   **Tendencias por Momento:** Representa visualmente el cruce M1 vs M5 requerido en el Acta 2; no demuestra que el contrato o la comparación longitudinal estén implementados.
*   **Inteligencia Artificial:** Representa visualmente un word cloud / barras para NLP y alertas de riesgo de desempleo. La clasificación NLP local está implementada (RF-72) y la predicción permanece en pausa.
*   **Gestión de Usuarios:** Se incluyó una pantalla con roles históricos (Decano, Coordinador, Administrador). La política vigente usa `Admin_CTIC`, `Coordinador_Sede` y `Usuario_Consulta`; este último recibe permisos y programas al crear la cuenta.
*   **Modal de Errores Excel:** El mockup contempla cédulas duplicadas y vacías. La política vigente distingue duplicados dentro de la carga, resueltos según ADR-006, de documentos ya persistidos, que reciben la medición sin sobrescribir sus datos personales según RN-01 y ADR-014.

## 2. Pantallas / Estados Faltantes (Brechas)
A pesar de la alta fidelidad de los nuevos mockups, faltan las siguientes pantallas críticas mencionadas en el **Acta 2 (19 de Agosto - 5:14 p.m.)**:

1.  **Formulario de "Nuevo Coordinador" (Admin CTIC):**
    *   *Contexto:* Existe el botón "Nuevo usuario" en la vista de Gestión de Usuarios, pero no hay un mockup del formulario en sí.
    *   *Faltante vigente:* Falta el diseño del formulario donde el Admin CTIC ingresa correo y nombre, y selecciona la **Sede**. El rol no es seleccionable: se asigna siempre `Coordinador_Sede`, conforme a HU-01 y RN-07. La referencia histórica a “Facultad” no forma parte de la política vigente.
2.  **Lógica Visual de "Doble Titulación":**
    *   *Contexto:* El Acta 2 menciona que ante un caso de doble titulación en un mismo momento, solo se registrará la última carrera obtenida.
    *   *Estado vigente:* la doble titulación no es un error y no revierte la carga (RN-20). El resultado exitoso informa cuántos casos se resolvieron conservando la fecha de grado más reciente (ADR-006).

## 3. Elementos Diferidos (Proyecto de Grado)
*   **Verificación de Dos Pasos (2FA/OTP):** Aunque el Acta 2 sugiere implementar un sistema de verificación con código al correo (estilo SIGA), se ha decidido con el cliente que este requerimiento no es un bloqueante funcional para PI3. Si el tiempo de desarrollo lo permite, se integrará; de lo contrario, queda oficialmente diferido para la fase de **Proyecto de Grado**. Por ende, **NO es obligatorio** diseñar su mockup actualmente.
