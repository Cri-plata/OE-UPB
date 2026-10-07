# ADR-021 — El modelo de empleabilidad es un modelo de análisis, no predictivo

**Estado:** Aceptado. Precisa la denominación usada en ADR-019 sin cambiar su diseño.

**Fecha:** 2026-10-06

## Contexto

ADR-019 introdujo el "modelo predictivo de empleabilidad" (RF-71 / IA-01), y la documentación, la interfaz y el informe Excel lo presentaron como un modelo que predice o proyecta la inserción laboral.

La revisión del código (`application/prediccion_service.py`) para documentar los modelos de análisis mostró otra cosa:

- El modelo se entrena con trayectorias cuyo resultado en el seguimiento ya se conoce.
- Las probabilidades por programa son el promedio de lo que el modelo estima para esas mismas trayectorias.
- La matriz de confusión se calcula sobre los datos de entrenamiento.
- No existe ningún flujo que estime la situación futura de graduandos que todavía no tienen seguimiento.

El equipo de producto confirmó el 2026-10-06 que la denominación correcta es **modelo de análisis**.

## Decisión

1. El componente se denomina **modelo de análisis de empleabilidad**. En documentación, presentaciones e interfaz se habla de **estimaciones** o **probabilidades estimadas**, no de predicciones, proyecciones ni pronósticos.
2. Su propósito es analizar retrospectivamente cómo se relacionan las condiciones de origen de un egresado (estado laboral, salario, satisfacción, habilidades, cohorte y programa) con su situación laboral y rango salarial en el seguimiento, y resumirlo por programa con un semáforo de riesgo.
3. El diseño técnico de ADR-019 no cambia: Gradient Boosting con ponderación de clases, validación cruzada estratificada, mínimo de 30 trayectorias, agregación por programa y prohibición de usar identificadores personales.
4. Los identificadores técnicos conservan el nombre histórico para no romper el contrato HTTP ni los clientes: `prediccion_service.py`, `/api/ia/prediccion-empleabilidad`, `/api/ia/prediccion-export`, `/api/ia/prediccion-benchmark-sedes` y `PrediccionEmpleabilidadResponse`.

## Consecuencias

- La documentación vigente usa la nueva denominación: requisitos (RF-71, HU-10), casos de uso, matriz, arquitectura (`06-modelos-analiticos.md`), estado funcional, estudio del proyecto, seguridad, pruebas y `CLAUDE.md`. Los registros históricos (ADR-019, auditorías y entradas antiguas del changelog) no se reescriben.
- Queda pendiente alinear los textos visibles de la pantalla Analítica, el informe Excel y las descripciones del OpenAPI (IA-02). El cambio de la pantalla exige actualizar primero el mockup `mockups/analitica.html` y `mockups/screen-map.md`, según las reglas de interfaz.

**Actualización 2026-10-06:** IA-02 completado. La interfaz, el informe Excel y el OpenAPI ya no presentan el modelo como predictivo. Las referencias a "proyección" se conservan cuando describen el estudio de proyección por programa.
