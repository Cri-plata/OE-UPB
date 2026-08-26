# Hallazgos y Análisis de Mockups (OE UPB)

Tras analizar los 8 nuevos mockups (UI en Modo Claro / Blanco con colores institucionales UPB) y cruzarlos con las Actas de Reunión del 19 de Agosto, se han encontrado las siguientes correspondencias y faltantes:

## 1. Correspondencia Directa (Mockups vs Requerimientos)
*   **Ficha del Egresado:** Cumple con la visualización individual. Muestra la línea de tiempo de momentos (0, 1 y 5).
*   **Reporte General (Dashboard):** Cumple con los filtros requeridos (Sede, Facultad, Cohorte) y muestra las métricas de empleabilidad y salarios.
*   **Administración de Datos:** Cumple perfectamente con la carga (Drag & Drop) y permite seleccionar explícitamente el Momento de la encuesta y la Sede (Filtros), como se exigió en el Acta 1.
*   **Tendencias por Momento:** Cumple con el cruce de variables M1 vs M5 requerido en el Acta 2.
*   **Inteligencia Artificial:** Excelente representación gráfica del word cloud / barras para NLP y las alertas de riesgo de desempleo.
*   **Gestión de Usuarios:** Se incluyó la pantalla para el Administrador CTIC. Muestra los roles (Decano, Coordinador, Administrador) y la asignación de sedes (Silos de datos).
*   **Modal de Errores Excel:** Gran adición funcional. Cumple con la regla de negocio de rechazar "Cédulas duplicadas" y "Cédulas vacías", permitiendo descargar el reporte de errores.

## 2. Pantallas / Estados Faltantes (Brechas)
A pesar de la alta fidelidad de los nuevos mockups, faltan las siguientes pantallas críticas mencionadas en el **Acta 2 (19 de Agosto - 5:14 p.m.)**:

1.  **Formulario de "Nuevo Usuario" (Admin CTIC):**
    *   *Contexto:* Existe el botón "Nuevo usuario" en la vista de Gestión de Usuarios, pero no hay un mockup del formulario en sí.
    *   *Faltante:* Falta el diseño del formulario donde el Admin CTIC ingresa el Correo, Nombre, Rol y, lo más importante, selecciona la **Sede o Facultad** a la que quedará anclado el usuario.
2.  **Lógica Visual de "Doble Titulación":**
    *   *Contexto:* El Acta 2 menciona que ante un caso de doble titulación en un mismo momento, solo se registrará la última carrera obtenida.
    *   *Recomendación:* Asegurarse de que el modal de errores del Excel (Mockup 8) esté preparado para arrojar un error del tipo "Doble titulación detectada - Se omitió registro antiguo" si llega a pasar.

## 3. Elementos Diferidos (Proyecto de Grado)
*   **Verificación de Dos Pasos (2FA/OTP):** Aunque el Acta 2 sugiere implementar un sistema de verificación con código al correo (estilo SIGA), se ha decidido con el cliente que este requerimiento no es un bloqueante funcional para PI3. Si el tiempo de desarrollo lo permite, se integrará; de lo contrario, queda oficialmente diferido para la fase de **Proyecto de Grado**. Por ende, **NO es obligatorio** diseñar su mockup actualmente.


