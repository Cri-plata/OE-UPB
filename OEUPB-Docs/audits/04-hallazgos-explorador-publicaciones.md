# Hallazgos del Explorador y publicación de gráficas

**Fecha del reporte:** 2026-09-25  
**Estado:** pendiente de corrección y verificación técnica.  
**Origen:** validación manual de usuario en entorno local.

Este documento registra el comportamiento observado sin asumir todavía su causa técnica. Los ítems ejecutables viven en el backlog activo.

## H-EXP-01 — Variables personales y administrativas aparecen como graficables

**Prioridad:** P0 — privacidad y minimización de datos.

### Comportamiento observado

El selector **“¿Qué pregunta deseas graficar? (Eje X)”** ofrece campos que no constituyen preguntas analíticas y que pueden contener identificadores, información personal o metadatos administrativos:

- celular;
- código de estado;
- código de encuesta;
- código IES;
- correo o email;
- email opcional;
- estado de encuesta;
- fecha de nacimiento;
- fecha de grado;
- fecha de respuesta;
- ID de respuesta;
- IES;
- nivel académico;
- nivel de formación;
- número de documento;
- país;
- primer nombre;
- primer apellido.

### Resultado esperado

1. El backend debe entregar al Explorador exclusivamente variables analíticas autorizadas.
2. Documento, nombres, apellidos, correos, celular, fechas personales, identificadores y códigos administrativos nunca deben ser opciones graficables ni formar parte de una publicación.
3. La restricción debe aplicarse en backend; ocultar opciones solo en Angular no es suficiente.
4. La selección debe basarse en un catálogo o clasificación estable de columnas, no únicamente en comparaciones frágiles del texto visible.
5. Si un cliente intenta solicitar una variable prohibida, el backend debe rechazarla con una respuesta controlada.
6. Los nombres de categorías y etiquetas de una gráfica publicada no deben contener datos personales.

### Verificación mínima

- Prueba backend del catálogo permitido y de rechazo para cada familia prohibida.
- Prueba frontend que confirme que el selector no muestra variables excluidas.
- Prueba de publicación que confirme que definición, etiquetas y métricas no contienen PII.

## H-EXP-02 — Falta comparación simultánea de varias gráficas

**Prioridad:** P2 — experiencia analítica.

### Comportamiento observado

El Explorador mantiene una sola configuración y una sola gráfica. Al crear una nueva perspectiva se reemplaza la anterior, por lo que no pueden compararse resultados en la misma pantalla.

### Resultado esperado

1. Debajo de la gráfica debe existir una acción clara, por ejemplo **“Crear otra gráfica”**.
2. Cada gráfica debe conservar de manera independiente pregunta, momento, programa, cohorte, tipo de visualización y estado de publicación.
3. Las gráficas deben permanecer visibles simultáneamente para comparación.
4. Cada bloque debe poder actualizarse, retirarse o eliminarse de la vista sin modificar los demás.
5. Los estados de carga y error deben pertenecer al bloque correspondiente.

### Verificación mínima

- Crear al menos dos gráficas con filtros diferentes y confirmar que ambas permanecen visibles.
- Modificar o retirar una gráfica sin alterar la otra.
- Confirmar comportamiento utilizable en escritorio y móvil.

## H-PUB-01 — Publicar deja un indicador de carga permanente

**Prioridad:** P1 — flujo funcional bloqueado.

### Comportamiento observado

Al pulsar **“Publicar gráfica”**, la interfaz permanece cargando. Al interactuar posteriormente con otro control, la gráfica puede aparecer como publicada, lo que sugiere que la operación puede completarse en backend sin que la interfaz cierre o sincronice correctamente su estado.

### Resultado esperado

1. La acción debe finalizar su estado de carga tanto en éxito como en error.
2. En éxito debe mostrarse inmediatamente el estado **Publicado** y quedar disponible la acción de retirar.
3. En error debe mostrarse un mensaje accionable y permitir reintentar.
4. Mientras exista una solicitud en curso deben impedirse envíos duplicados.
5. La UI debe reconciliarse con la respuesta real del backend, sin depender de otra interacción del usuario.

### Verificación mínima

- Pruebas frontend para respuesta exitosa, error HTTP y error de red.
- Prueba de integración que confirme una sola publicación por acción y actualización inmediata del estado.

## H-PUB-02 — La vista de gráficas publicadas queda cargando

**Prioridad:** P1 — consulta funcional bloqueada.

### Comportamiento observado

Después de publicar y abrir **Gráficas publicadas**, la vista permanece en estado de carga y no presenta catálogo, estado vacío ni error.

### Resultado esperado

1. La carga debe terminar para respuestas con elementos, respuestas vacías y errores.
2. Una respuesta vacía debe mostrar el estado “No hay gráficas publicadas compatibles”.
3. Un error debe mostrarse de forma controlada, con opción de reintento.
4. Una publicación recién creada y autorizada debe aparecer al ingresar o refrescar el catálogo.
5. El backend debe conservar los filtros de audiencia por rol, permisos y programas.

### Verificación mínima

- Pruebas frontend para lista con datos, lista vacía y error.
- Prueba de integración publicar → consultar catálogo → retirar → dejar de visualizar.
- Confirmar que corregir el indicador no amplía la audiencia ni expone datos fuente.

## Criterio de cierre conjunto

Los cuatro hallazgos solo se consideran cerrados cuando existen pruebas automatizadas, validación manual del flujo completo y actualización de la matriz de trazabilidad. La corrección de publicación debe preservar las reglas RN-09, RN-10, RN-11, RN-14 y RN-24.

