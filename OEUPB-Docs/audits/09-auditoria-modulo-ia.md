# Auditoría Técnica del Módulo de Inteligencia Artificial (Auditoría 09)

**Fecha:** 2026-10-06  
**Componente:** Módulo de Inteligencia Artificial (NLP & Machine Learning Predictivo)  
**Alcance:** `ia_service.py`, `prediccion_service.py`, `ia_router.py`, `nlp_service.py`, `analitica_router.py`, `model_cache.py`, `programa_normalizer.py`, `programas.py`, y componentes frontend asociados.  
**Estado:** Abierta / Recomendaciones priorizadas.

---

## 1. Resumen Ejecutivo

El módulo de Inteligencia Artificial del Observatorio de Egresados UPB se encuentra **plenamente operativo y funcional** en su lógica de negocio central:
* Extrae habilidades blandas y técnicas con PLN local (`spaCy` + `TF-IDF`), cumpliendo con la restricción de anonimización y no dependencia de APIs externas.
* Implementa minería de reglas de asociación con `Apriori` (`mlxtend`).
* Soporta curaduría en caliente (*Human-in-the-Loop*, IA-15 / RN-32) con persistencia en base de datos.
* Cuenta con un modelo supervisado (`GradientBoostingClassifier`, RF-71) calibrado contra el desbalance de clases mediante aprendizaje sensible al costo (*Cost-Sensitive Learning*), validación cruzada estratificada (5 folds) y backtesting temporal por cohortes (IA-17).
* Genera exportaciones ejecutivas en formato Excel estructurado tanto para NLP como para el modelo predictivo.

No obstante, esta auditoría profunda de código ha identificado **incoherencias arquitectónicas, redundancias de patrones y un defecto silencioso en el subsistema de caché en memoria**, los cuales se detallan a continuación clasificados por severidad.

---

## 2. Matriz de Hallazgos

| ID | Severidad | Tipo | Componente | Descripción |
|---|---|---|---|---|
| **IA-AUD-01** | **Alta** | **Defecto (Bug)** | `model_cache.py` | `ModelCache.set()` no almacena la entrada en el diccionario; las predicciones nunca se guardan en caché. |
| **IA-AUD-02** | **Media** | **Seguridad / Aislamiento** | `prediccion_service.py` / `model_cache.py` | La clave de caché del modelo predictivo no incluye `sede_id`; riesgo teórico de colisión inter-sedes si coinciden conteos de mediciones. |
| **IA-AUD-03** | **Media** | **Incoherencia Funcional** | `nlp_service.py` vs `ia_service.py` | Coexisten dos motores de NLP paralelos: `/api/analitica/resumen` usa 7 categorías estáticas sin límites de palabra, mientras `/api/ia` usa 25+ habilidades con spaCy. |
| **IA-AUD-04** | **Media** | **Incoherencia de Filtro** | `ia_router.py` vs `programas.py` | Los endpoints de `/api/ia` filtran por igualdad estricta SQL (`Egresado.programa == programa`), ignorando variantes no canonizadas presentes en la base de datos. |
| **IA-AUD-05** | **Baja** | **Redundancia** | `ia_router.py` & `prediccion_service.py` | Las listas `_OPEN_PATTERNS` y `_EXCLUDE_PATTERNS` están duplicadas literalmente en ambos archivos. |
| **IA-AUD-06** | **Baja** | **Inconsistencia de Nomenclatura** | `ia_router.py` | `/api/ia/prediccion-benchmark-sedes` se llama en plural pero solo calcula 1 sede por la restricción de aislamiento de sede (ADR-020). |
| **IA-AUD-07** | **Baja** | **Rendimiento** | `ia_router.py` | Se consulta `db.query(Egresado).all()` sin filtrar por la sede actual, trayendo a memoria egresados de otras sedes innecesariamente. |
| **IA-AUD-08** | **Baja** | **Deuda Técnica** | Raíz `OEUPB-Backend` | Persisten 4 scripts de prueba manuales (`test_diagnostico.py`, `test_ia_pipeline.py`, etc.) que usan la base de `.env` en lugar de la suite `tests/` (ítem TST-01). |

---

## 3. Detalle de Hallazgos

### IA-AUD-01: Defecto en `ModelCache.set()` (Bug Silencioso de Caché)
* **Ubicación:** `OEUPB-Backend/application/model_cache.py:70-84`
* **Diagnóstico:**
  En la función `ModelCache.set()`, se computa la clave hash y se ejecuta la lógica de desalojo (eviction) para liberar espacio si se supera `max_entries`. Sin embargo, **se omitió la línea de asignación real** `self._cache[key] = { "data": data, ... }` (la cual sí existe correctamente en el método hermano `set_by_key`).
* **Impacto:**
  Cada vez que un usuario consulta `/api/ia/prediccion-empleabilidad`, `prediccion_model_cache.get()` siempre retorna `None` (miss). El modelo de Gradient Boosting y la validación cruzada estratificada se reentrenan en cada petición, consumiendo entre 800 ms y 2 s de CPU innecesariamente cuando los datos no han cambiado.
* **Solución propuesta:**
  Agregar dentro del bloque `with self._lock:` de `set()` la asignación del payload con su marca temporal y expiración:
  ```python
  self._cache[key] = {
      "data": data,
      "created_at": time.time(),
      "expires_at": time.time() + ttl,
  }
  ```

---

### IA-AUD-02: Aislamiento Multisede en la Clave de Caché del Modelo Predictivo
* **Ubicación:** `OEUPB-Backend/application/prediccion_service.py:659-667`
* **Diagnóstico:**
  La clave generada por `prediccion_model_cache._generate_key` combina:
  `f"{mediciones_count}_{max_medicion_id}_{momento_origen}_{momento_destino}_{filtro_programa}_{filtro_anio}_{extra_tag}"`.
  En `predecir_empleabilidad_servicio()`, no se pasa `sede_id` ni en los parámetros ni en `extra_tag`.
* **Impacto:**
  Si dos coordinadores de sedes distintas (ej. Bucaramanga y Medellín) tienen por azar el mismo número de mediciones y el mismo ID máximo, la primera sede en consultar podría servir su resultado en caché a la segunda sede, violando la regla de aislamiento estricto por sede (RN-06, ADR-020).
* **Solución propuesta:**
  Pasar el `sede_id` (o `extra_tag=f"sede_{mediciones[0].sede_id}"` si hay mediciones) en la consulta y almacenamiento de la caché.

---

### IA-AUD-03: Coexistencia de Dos Motores de NLP Desacoplados y Discordantes
* **Ubicación:** `OEUPB-Backend/application/nlp_service.py` vs `application/ia_service.py`
* **Diagnóstico:**
  * En el endpoint `/api/analitica/resumen` (consumido por la pestaña "Analítica"): se utiliza `nlp_service.py`, el cual tiene un diccionario estático y rudimentario de 7 categorías (`Comunicación`, `Liderazgo`, `Trabajo en equipo`, `Tecnología y datos`, `Idiomas`, `Gestión de proyectos`, `Adaptabilidad`) y realiza matching de subcadenas básico (`palabra in normal`), sin lematización, sin stopwords contextuales y sin integración con curadurías.
  * En los endpoints `/api/ia/habilidades-*` (consumidos por "Habilidades Demandadas"): se utiliza `ia_service.py`, con taxonomía formal de 25+ habilidades, spaCy `es_core_news_md`, doble pasada (cruda + lema), reglas Apriori y realimentación de curaduría (`HabilidadCurada`).
* **Impacto:**
  Un coordinador o directivo observa frecuencias y categorías de competencias en la tarjeta superior de **Analítica** que no concuerdan con los gráficos y tablas de **Habilidades Demandadas**, dando una sensación de contradicción interna en los resultados analíticos.
* **Solución propuesta:**
  Migrar `analitica_router.py:resumen` para que consuma las competencias detectadas por `ia_service.py` o unificar ambos servicios bajo una misma fuente de verdad.

---

### IA-AUD-04: Filtrado Estricto SQL de Programa vs Canonización Institucional
* **Ubicación:** `OEUPB-Backend/presentation/ia_router.py:347, 422, 488, 540`
* **Diagnóstico:**
  En las consultas de `ia_router.py`, el filtro opcional de programa se aplica como:
  `query = query.join(Medicion.egresado).filter(Egresado.programa == programa)`
  Se compara con igualdad estricta SQL. Sin embargo, en la base de datos existen variaciones históricas no normalizadas (por ejemplo, `INGENIERIA DE SISTEMAS E INFORMATICA` en mayúsculas sin tilde vs `Ingeniería de Sistemas e Informática`).
  En contraste, `prediccion_service.py` sí aplica `canonizar_programa()` en memoria para homologar registros.
* **Impacto:**
  Si el usuario selecciona en la interfaz la opción canónica con tildes, la consulta SQL para habilidades demandadas podría ignorar egresados que en la base de datos están almacenados en mayúsculas sin tildes o con abreviaturas.
* **Solución propuesta:**
  Utilizar en `ia_router.py` las variantes del mapa canónico (`programas.py:construir_mapa_canonico` o `in_([v for v in db_programas if canonizar_programa(v) == programa])`), tal como se diseñó en IA-16.

---

### IA-AUD-05: Redundancia en Patrones de Preguntas Abiertas
* **Ubicación:** `ia_router.py:228-266` y `prediccion_service.py:39-76`
* **Diagnóstico:**
  Las listas `_OPEN_PATTERNS` (15 patrones) y `_EXCLUDE_PATTERNS` (17 patrones) están duplicadas exactamente con los mismos strings en dos módulos diferentes.
  Además, mientras `ia_router.py` aplica `anonimizar()` a los textos extraídos, `prediccion_service.py` no llama a `anonimizar()` (aunque en su caso solo cuenta frecuencias de habilidades predefinidas).
* **Solución propuesta:**
  Extraer `_OPEN_PATTERNS`, `_EXCLUDE_PATTERNS` y la función `extraer_textos_libres_abiertos()` a un módulo compartido (`application/encuesta_utils.py` o dentro de `ia_service.py`), garantizando anonimización uniforme por defecto.

---

### IA-AUD-06: Nomenclatura del Endpoint de Benchmark
* **Ubicación:** `OEUPB-Backend/presentation/ia_router.py:651`
* **Diagnóstico:**
  La ruta se denomina `/api/ia/prediccion-benchmark-sedes` (en plural) y devuelve una lista `List[BenchmarkSedeItem]`. Sin embargo, tras la auditoría 07 (hallazgo C-02) y la decisión ADR-020, por estricto respeto a la privacidad y aislamiento entre sedes, el backend filtra exclusivamente por `current_user["sede_id"]`, devolviendo siempre una lista con un único elemento correspondiente a la sede del usuario.
* **Recomendación:**
  Documentar explícitamente en el docstring de OpenAPI que el benchmark opera como autodiagnóstico de robustez institucional de la sede propia, o en una futura iteración de versión de API (v2) simplificar el contrato a `BenchmarkSedePropiaResponse`.

---

### IA-AUD-07: Consulta No Filtrada de Todos los Egresados
* **Ubicación:** `OEUPB-Backend/presentation/ia_router.py:600, 632`
* **Diagnóstico:**
  Para el cálculo predictivo se ejecuta:
  ```python
  mediciones = query.all()
  egresados = db.query(Egresado).all()
  ```
  Se recuperan todos los registros de la tabla `Egresado` de la base de datos sin filtrar, aunque solo se necesiten los egresados correspondientes a las mediciones filtradas de la sede.
* **Impacto:**
  Con el volumen actual de pruebas (centenares de egresados) es imperceptible, pero ante un volumen de 50.000 egresados (requisito RNF-06), serializar toda la tabla en cada ejecución consumirá memoria y tiempo de red con la base de datos innecesariamente.
* **Solución propuesta:**
  Cargar los egresados mediante relación `joinedload(Medicion.egresado)` o filtrar:
  ```python
  docs_sede = {m.egresado_documento for m in mediciones if m.egresado_documento}
  egresados = db.query(Egresado).filter(Egresado.numero_documento.in_(docs_sede)).all()
  ```

---

### IA-AUD-08: Scripts de Prueba Residuales en Raíz (Ítem TST-01)
* **Ubicación:** Raíz de `OEUPB-Backend/`:
  - `test_diagnostico.py`
  - `test_ia_pipeline.py`
  - `test_prediccion_empleabilidad.py`
  - `test_reglas_asociacion.py`
* **Diagnóstico:**
  Fueron creados como scripts de verificación rápida durante las fases iniciales de desarrollo. Utilizan `SessionLocal()` conectándose directamente a la base de datos configurada en `.env`, en lugar del motor de pruebas con SQLite en memoria y fixtures aisladas que utiliza la suite oficial en `tests/`.
* **Recomendación:**
  Tal como establece el ítem `TST-01` del backlog activo, retirar estos scripts de la raíz una vez sus casos de uso estén cubiertos dentro de `tests/test_ia_alcance.py` y `tests/test_prediccion_empleabilidad.py`.

---

## 4. Aspectos Destacados Positivos (Buenas Prácticas Observadas)

1. **Aprendizaje Sensible al Costo (Cost-Sensitive Learning):**
   La ponderación de muestras implementada con `factor_suavizado=0.65` en `calcular_pesos_balanceados()` demuestra un diseño riguroso: evita la sobre-penalización agresiva de la clase mayoritaria (*Empleado*) mientras eleva la detección de egresados en condición de desempleo.
2. **Backtesting Longitudinal Temporal (IA-17):**
   La partición por cohorte histórica más reciente para medir la estabilidad temporal (`evaluar_validacion_temporal`) aporta transparencia científica de primer nivel de cara a comités curriculares y procesos de acreditación.
3. **Mecanismo de Desempate y Doble Pasada en NLP:**
   La estrategia de `longest-match-first` con máscara de caracteres previene eficazmente que términos compuestos (ej. *"trabajo en equipo"*) sean fragmentados por unigramas sueltos (*"equipo"*), y la combinación de forma lematizada con forma cruda normalizada protege contra inconsistencias morfológicas de spaCy.
4. **Resiliencia de Taxonomía Multi-Worker:**
   La inclusión de la firma hash de curadurías (`_FIRMA_CURADURIAS`) garantiza que las decisiones tomadas por un coordinador se reflejen inmediatamente en cualquier proceso worker de Uvicorn.
