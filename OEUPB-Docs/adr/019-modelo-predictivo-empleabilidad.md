# ADR-019 — Modelo predictivo de empleabilidad y reactivación de IA-01

**Estado:** Aceptado. Reactiva y resuelve el punto 9 de [ADR-009](009-carga-y-gobierno-datos.md).

**Fecha de registro:** 2026-09-30

## Contexto

El punto 9 de ADR-009 mantuvo en pausa el modelo predictivo de empleabilidad (RF-71 / IA-01) hasta que se aprobaran de forma explícita sus objetivos, métricas, población de entrenamiento, horizonte temporal y criterios éticos y de aceptación.

El 2026-09-30, producto aprobó formalmente la especificación y diseño del modelo predictivo con las siguientes definiciones:
1. **Variable objetivo dual:**
   - Clasificación multiclase de estado laboral (`empleado`, `independiente`, `estudiante`, `sin_empleo`).
   - Clasificación ordinal de rango salarial (`< 2 SMLV`, `2–4 SMLV`, `> 4 SMLV`, `Sin ingreso / No reporta`).
2. **Población y horizonte temporal:**
   - Egresados con trayectorias longitudinales emparejadas por documento entre mediciones (M0 → M1 a 1 año de egreso, o M0/M1 → M5 a 5 años de egreso).
   - Umbral de confiabilidad estadística mínima: se exige un piso de 30 trayectorias longitudinales para entrenar el modelo. Si una sede u horizonte cuenta con menos de 30 egresados con seguimiento, el sistema conmuta a un estado informativo limpio (`insuficiente_datos`), evitando alucinaciones o sobreajuste espurio.
3. **Restricciones éticas y de privacidad:**
   - Prohibido el uso de identificadores personales (cédula, nombres, correo) en la matriz de features.
   - El modelo se entrena on-demand en backend filtrando por la sede del coordinador autenticado; no se persisten modelos estáticos globales.
   - Los resultados se presentan exclusivamente agregados por programa académico (probabilidades medias y semáforo de riesgo).
   - Transparencia algorítmica: exposición del ranking ponderado de importancia de variables (*feature importance*).
4. **Ubicación en UI:**
   - Integrado en la pantalla de **Analítica y alertas** como sección especializada con controles de horizonte temporal y filtros curriculares.

## Decisión

1. Se implementa el servicio predictivo en `OEUPB-Backend/application/prediccion_service.py` utilizando `GradientBoostingClassifier` de scikit-learn.
2. La validación del rendimiento se ejecuta mediante validación cruzada estratificada (*Stratified K-Fold*), reportando Accuracy, F1-Score Macro y matriz de confusión.
3. Se expone el endpoint protegido `GET /api/ia/prediccion-empleabilidad` en `presentation/ia_router.py`, restringido a coordinadores de sede.
4. El cliente frontend en `data/api/ia.api.ts` provee el método `prediccionEmpleabilidad()`.
5. La vista `features/dashboard/analitica` incorpora:
   - Cuatro tarjetas KPI resumen (Precisión, Trayectorias, Programas evaluados, Egresados en riesgo).
   - Gráfico de barras de importancia de factores de empleabilidad.
   - Alertas críticas de riesgo predictivo cuando la probabilidad de desempleo por programa supera el 30%.
   - Tabla de proyecciones por programa académico con barras de probabilidad y semáforo de riesgo.
   - Conmutador interactivo entre horizonte M1 (1 año) y M5 (5 años).

## Consecuencias

- RF-71 pasa de estado `En pausa` a `Implementado` en la matriz de trazabilidad y casos de uso.
- IA-01 se traslada a las tareas completadas en `BACKLOG.md`.
- El sistema cuenta con cobertura total de pruebas automatizadas en backend (`test_prediccion_empleabilidad.py`) y frontend (`analitica.spec.ts`).
