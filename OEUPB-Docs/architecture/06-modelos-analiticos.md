# Modelos de análisis de OE UPB

**Estado:** descripción del código actual (rama `dev-cristian`, commit `46921d7` y posteriores)
**Verificado contra el código:** 2026-10-06
**Decisiones de origen:** ADR-015 (publicación y k = 5), ADR-016 (taxonomía laboral), ADR-019 (modelo de empleabilidad), ADR-020 (alcance de la IA), ADR-021 (denominación como modelo de análisis)

Este documento explica qué calcula cada modelo de análisis, con qué datos, con qué parámetros y qué límites tiene su interpretación. Los valores citados son los del código; si cambian, este documento debe actualizarse en el mismo cambio.

## 1. Mapa de modelos

| # | Modelo | Técnica | Dónde vive | Endpoint | Pantalla |
|---|---|---|---|---|---|
| 1 | Clasificación laboral y KPI | Reglas sobre respuestas OLE | `application/indicadores.py` | `/api/reportes/*` | Reporte general, Tendencias |
| 2 | Comparación entre momentos | Pares del mismo egresado | `application/indicadores.py` | `/api/reportes/comparacion` | Tendencias |
| 3 | Publicación con privacidad | Recálculo y supresión k = 5 | `application/indicadores.py` | `/api/publicaciones` | Todas las gráficas publicables |
| 4 | Competencias y alertas descriptivas | Palabras clave y umbrales | `application/nlp_service.py`, `presentation/analitica_router.py` | `/api/analitica/resumen` | Analítica y alertas |
| 5 | Habilidades demandadas | spaCy y taxonomía curada | `application/ia_service.py` | `/api/ia/habilidades-demandadas` | Co-relaciones |
| 6 | Términos emergentes | TF-IDF sobre texto residual | `application/ia_service.py` | (incluido en el 5) | Co-relaciones |
| 7 | Curaduría humana | Aprobación o descarte de términos | `ia_router.py`, `ia_service.py` | `/api/ia/habilidades/curar*` | Co-relaciones |
| 8 | Reglas de asociación | Apriori (mlxtend) | `application/ia_service.py` | `/api/ia/reglas-asociacion` | Co-relaciones |
| 9 | Comparativa temporal de habilidades | Proporciones por momento | `application/ia_service.py` | `/api/ia/habilidades-comparativa` | Co-relaciones |
| 10 | Modelo de análisis de empleabilidad | Gradient Boosting supervisado | `application/prediccion_service.py` | `/api/ia/prediccion-empleabilidad` | Analítica y alertas |
| 11 | Robustez y validación del modelo | Semáforo, backtesting por cohorte | `application/prediccion_service.py` | (incluido en el 10) y `/api/ia/prediccion-benchmark-sedes` | Analítica y alertas |

Reglas comunes a todos los modelos:

- El filtro de programa de los endpoints de habilidades agrupa las variantes históricas del nombre (mayúsculas, tildes, abreviaturas como "INGENIERIA INFORMATICA" o "COMUNICACION SOCIAL- PERIODISMO") mediante `programas.canonizar_programa` y sus homologaciones institucionales (IA-16, `_variantes_programa_filtro`).

- Solo `Coordinador_Sede` los consume, y siempre con los datos de la sede de su JWT (RN-06, RN-32). `Usuario_Consulta` y `Admin_CTIC` no acceden. Entre sedes solo viajan las publicaciones del modelo 3.
- Las mediciones identificadas se toman en su intento más reciente por documento, sede, momento y cohorte (`medicion_policy.py`).
- Todo el procesamiento es local: ningún texto ni dato sale a servicios externos (RNF-07).

## 2. Datos de entrada

Cada medición guarda las respuestas del cuestionario OLE como JSON (`mediciones.respuestas`), junto con `momento` (0, 1, 5), `anio` (cohorte o año de grado, RN-17), `sede_id` y el documento del egresado (nulo en las mediciones anónimas). El programa sale de `egresados.programa`.

Los modelos localizan las preguntas por **fragmentos normalizados del nombre de la columna** (minúsculas, sin tildes y con `_` entre palabras), no por posición. Por eso un cambio de redacción del cuestionario puede romper la clasificación; ANA-03 deja pendiente verificarlo con datos reales de M5.

| Concepto | Fragmento que se busca en la columna |
|---|---|
| Actividad remunerada (M1/M5) | `realiza_alguna_actividad_remunerada` |
| Posición laboral (M1/M5) | `actividad_remunerada_que_usted_realiza_actualmente_es` |
| Tipo de contrato (M1/M5) | `que_tipo_de_contrato_tiene` |
| Trabaja además de estudiar (M0) | `aparte_de_estudiar_usted_se_dedica_a_trabajar` |
| Posición laboral (M0) | `en_este_trabajo_usted_es` |
| Ingreso | contiene `ingreso_mensual` y `smlv`, `smmlv` o `salarios_minimos` |
| Satisfacción | contiene `califique su nivel de satisfacci` (aplicación de conocimientos, retos, estabilidad, ascenso) |

### 2.1 Diccionario de ubicación (DIVIPOLA)

Las preguntas de lugar llegan como tres columnas con el mismo enunciado y los sufijos `(DEPARTAMENTO)`, `(MUNICIPIO)` y `(PAIS)`. Por ejemplo: residencia actual (M0 pregunta 52, M1 pregunta 10), residencia al graduarse del colegio, residencia durante la carrera, residencia al primer empleo, lugar de nacimiento de la madre y ubicación de la empresa propia.

- **Códigos:** departamento y municipio usan los códigos DIVIPOLA del DANE. Excel suele quitarles el cero inicial (`5` por `05`, `5001` por `05001`) o agregarles `.0`; `application/divipola.py` los normaliza.
- **Diccionario:** `application/data/divipola.json` reúne 33 departamentos (listado DANE 2012) y 1.121 municipios: 1.120 del listado DIVIPOLA 2007 más Norosí (13490), un municipio posterior que aparece en las encuestas.
- **Cobertura:** sobre los datos locales del 2026-10-06 reconoce el 99,95 % de las respuestas de municipio. Las no reconocidas son valores inválidos y el departamento `00` ("sin dato").
- **Uso:** el Explorador, y por tanto las publicaciones, muestra "Bucaramanga (Santander)" o "Santander" en lugar del código. La ficha del egresado (`respuestas_completas`) recibe las mismas etiquetas. Si un municipio ya nombra a su departamento (Bogotá, San Andrés), el departamento no se repite.
- **Códigos desconocidos:** un código que no está en el diccionario se muestra tal cual; nunca se inventa un lugar.
- **País:** la columna `(PAIS)` usa códigos ISO 3166 numéricos (`170` es Colombia) y no se traduce. Además está excluida del catálogo analítico (RN-31).
- **Datos guardados:** las respuestas originales en `mediciones.respuestas` no se modifican; la traducción solo se aplica al mostrarlas.

## 3. Clasificación laboral y KPI (modelo 1)

**Estado laboral (RN-16, ADR-016).** Cada medición se clasifica en `empleado`, `independiente`, `estudiante` o `sin_empleo`; si no hay información suficiente, en ninguno:

- **M1 y M5:** si `realiza_alguna_actividad_remunerada` es "no", la medición es `sin_empleo`. Si es "sí", se mira la posición: practicante o pasante cuenta como `estudiante`; independiente, contratista, cuenta propia o propietario, como `independiente`; empleado, dependiente o familiar, como `empleado`.
- **M0:** si no trabaja además de estudiar, la medición es `estudiante`; si trabaja, se clasifica por su posición con las mismas reglas.

**Indicadores.**

- **Tasa de empleabilidad:** (empleado + independiente) / mediciones clasificadas × 100.
- **Formalidad (solo M1/M5):** empleado con un contrato que contiene "contrato" cuenta como formal; independiente, como no formal. La tasa se calcula sobre formales más no formales.
- **Salario:** rango de SMLV convertido a número. "Entre a y b" toma el punto medio, "menos de 1" vale 0,8 y "más de 10" vale 12. Se informan promedio, mínimo, mediana y máximo.
- **Satisfacción:** promedio de 1 a 5 por categoría.

Las mediciones anónimas solo entran en los KPI del reporte general sin filtro de programa. Tendencias y Explorador usan solo mediciones identificadas (RN-15). Tendencias muestra los 5 programas con más datos.

## 4. Comparación entre momentos (modelo 2)

Un par es el mismo egresado identificado, en la misma sede y cohorte, con medición en los dos momentos elegidos. Se compara la empleabilidad o el salario por programa, y un programa con menos de 5 pares muestra "Datos insuficientes para la comparación seleccionada" (RN-26). Comparar un momento consigo mismo responde 422.

## 5. Publicación con privacidad (modelo 3)

El cliente envía solo la definición de la gráfica. El backend recalcula las métricas con la sede del JWT (`construir_publicacion`) y aplica el umbral `UMBRAL_MINIMO_PUBLICACION = 5`:

- Las categorías con menos de 5 observaciones se agrupan en "Otros (agrupados por privacidad)"; si aun agrupadas no llegan a 5, se omiten.
- Las tasas o promedios con un denominador menor que 5 se publican vacíos.
- Si no queda ninguna celda, la publicación se rechaza con 422.

Además, el Explorador y la publicación rechazan variables personales o administrativas (RN-31): documento, nombres, correo, teléfono, dirección, fechas, identificadores, códigos y columnas sin nombre. El título se valida contra correos, enlaces y secuencias de 5 o más dígitos (ADR-020).

**Riesgo residual aceptado:** el umbral es por celda, así que publicar la misma métrica con filtros solapados permite deducir por diferencia una celda suprimida (ADR-020, punto 6).

## 6. Competencias y alertas descriptivas (modelo 4)

`/api/analitica/resumen` es un modelo **descriptivo por palabras clave**, independiente del pipeline de spaCy del modelo 5.

- **Textos:** columnas cuyo nombre contiene `coment`, `observ`, `competenc`, `habilidad`, `suger`, `porque`, `por que` o `abierta`. Antes de clasificarlos se anonimizan: se reemplazan correos y números largos, y el documento, el nombre y el apellido del egresado.
- **Competencias:** 7 categorías (Comunicación, Liderazgo, Trabajo en equipo, Tecnología y datos, Idiomas, Gestión de proyectos, Adaptabilidad). Cada texto suma 1 a cada categoría cuyas palabras clave contiene.
- **Alertas de empleabilidad (ANA-02):** solo M1 y M5, con al menos 5 mediciones clasificadas por programa y momento. Empleabilidad menor al 70 % da severidad media y menor al 50 %, alta.
- **Alertas de texto:** al menos 5 textos del programa y al menos 3 con expresiones negativas ("desemple", "sin empleo", "no encuentro", "dificil conseguir", "pocas oportunidades", "salario bajo", "inestabilidad").

Las alertas describen lo observado; no son predicciones ni decisiones automáticas. Como las competencias de este modelo y las del modelo 5 usan taxonomías distintas, sus conteos no coinciden.

## 7. Pipeline de habilidades demandadas (modelos 5, 6 y 7)

### 7.1 Extracción y anonimización

- **Textos:** se toman las preguntas abiertas reconocidas por patrones (tarea principal, aspectos a mejorar, qué le faltó, sugerencia, recomendación, observación, comentario, curso, seminario, "(otro)"). Se excluyen preguntas cerradas conocidas (canal de búsqueda, tipo de contrato, ingreso, sector, etc.) y textos de menos de 5 caracteres.
- **Anonimización (RN-04):** cada texto se anonimiza antes de cualquier análisis (`ia_service.extraer_textos_libres_encuesta`, función única que usan el router y el modelo de empleabilidad; sus patrones son `PATRONES_PREGUNTAS_ABIERTAS` y `PATRONES_EXCLUSION_PREGUNTAS`): correos por `[CORREO]`, números de 8 o más caracteres por `[DATO_NUMERICO]`, y documento, nombre y apellido del egresado por `[PERSONA]`.

### 7.2 Preprocesamiento doble

Con el modelo de spaCy `es_core_news_md` (sin `parser` ni `ner`), cada texto produce dos formas:

- **Lematizada:** el lema en minúsculas y sin tildes. Los nombres propios conservan su forma original.
- **Cruda normalizada:** la palabra en minúsculas y sin tildes.

En ambas se quitan stopwords, puntuación, números y palabras de un carácter, y el resultado se memoriza (`lru_cache` de 16.384 entradas). Si el modelo no está instalado, se usa una tokenización simple sin lematización; por eso la imagen lo instala desde `requirements.txt`.

### 7.3 Taxonomía y coincidencia

- **Taxonomía base:** 33 categorías (12 blandas y 21 duras) con 143 variantes, de propósito general y sin lógica por programa.
- **Patrones:** cada variante se preprocesa igual que los textos y se compila como expresión regular con límites de palabra.
- **Coincidencia (longest match first):** las frases más largas se buscan primero y un tramo ya reconocido no puede reutilizarse.
- **Conteo:** una habilidad cuenta una vez por respuesta, aunque se repita o aparezca con sinónimos. Se combinan las detecciones de las dos formas.

### 7.4 Términos emergentes (TF-IDF)

- **Texto residual:** las partes del texto que no correspondieron a ninguna habilidad conocida.
- **TF-IDF:** se aplica a ese residuo con unigramas y bigramas (`ngram_range=(1, 2)`) y `min_df=1`.
- **Filtrado:** se quitan las stopwords de encuesta y los términos descartados por curaduría.
- **Puntaje:** cada término toma su máximo TF-IDF entre respuestas y se devuelven los mejores (15 por defecto, hasta 50).

Limitación: con `min_df=1`, un término que aparece en una sola respuesta puede encabezar la lista. Por eso la anonimización previa es obligatoria.

### 7.5 Curaduría humana (IA-15)

Un coordinador puede **aprobar** un término emergente o **descartarlo**:

- **Aprobar** lo agrega a la taxonomía con su etiqueta canónica, su tipo y sus variantes.
- **Descartar** lo añade a las stopwords dinámicas para que no vuelva a sugerirse.

La taxonomía curada es institucional y compartida por todas las sedes (`habilidades_curadas`). Solo el autor de una curaduría puede modificarla (los demás reciben 409) o revertirla (403).

**Sincronización entre procesos.** El backend corre con 2 workers y cada uno guarda la taxonomía en memoria. En cada consulta, `sincronizar_curadurias_bd` calcula una firma (SHA-256) de las curadurías en la base. Si la firma cambió, reconstruye la taxonomía desde la base fija más las curadurías vigentes, de modo que una reversión deja de aplicarse. La firma también forma parte de la clave de caché de resultados.

## 8. Reglas de asociación (modelo 8)

- **Canasta:** el conjunto de habilidades de cada egresado identificado, unificando todas sus respuestas abiertas. Solo cuentan las canastas con 2 o más habilidades; las mediciones anónimas no se agrupan entre sí.
- **Algoritmo:** Apriori (`mlxtend`) con `max_len=2`, es decir, reglas de un antecedente y un consecuente. Si `mlxtend` falla, se usa un cálculo equivalente en Python.
- **Parámetros por defecto:** soporte mínimo 0,01 en la API y 0,4 de confianza mínima. La pantalla envía confianza 0,5; la exportación usa confianza 0,4. Se exigen al menos 2 ocurrencias y se devuelven hasta 20 reglas.
- **Orden:** lift, luego confianza y luego soporte.

**Lectura:** "Si menciona A, también menciona B" con una confianza P(B|A). Un **lift** mayor que 1 significa que A y B aparecen juntos más de lo esperado por azar. Son co-ocurrencias, no causalidad.

## 9. Comparativa temporal de habilidades (modelo 9)

Para cada habilidad se calcula su porcentaje sobre las respuestas con al menos una habilidad en M0, M1 y M5, y el delta M1 − M0. La respuesta incluye `m0_pct`, `m1_pct` y `m5_pct`, y sus alias `m0_porcentaje`, `m1_porcentaje` y `m5_porcentaje` (IA-06). La tendencia se clasifica así:

| Tendencia | Condición |
|---|---|
| `emergente_en_m1` | sin menciones en M0 y con menciones en M1 |
| `emergente_en_m5` | sin menciones en M0 ni en M1 y con menciones en M5 |
| `crece` | delta ≥ 4 puntos porcentuales |
| `decrece` | delta ≤ −4 puntos porcentuales |
| `estable` | resto |

## 10. Modelo de análisis de empleabilidad (modelo 10)

**Es un modelo de análisis, no un modelo predictivo (ADR-021).** Aprende la relación entre la situación del egresado en un momento y su situación en el seguimiento, y la resume por programa sobre trayectorias ya observadas. No pronostica la situación futura de graduandos sin seguimiento. Los identificadores técnicos conservan el nombre histórico "predicción" (`prediccion_service.py`, `/api/ia/prediccion-empleabilidad`, `PrediccionEmpleabilidadResponse`) para no romper el contrato HTTP.

### 10.1 Objetivo y población (ADR-019)

El modelo analiza, por programa, cómo se relacionan las condiciones de origen con la **situación laboral** y el **rango salarial** en un momento de seguimiento, a partir de la situación del egresado en un momento anterior.

- **Horizontes:** M0 → M1 (1 año, por defecto) o M0 → M5 (5 años); el origen y el destino son parámetros del endpoint.
- **Trayectoria:** un egresado identificado de la sede con medición en el momento de origen y en el de destino, y con estado laboral clasificable en ambos. No se exige que las dos mediciones sean de la misma cohorte.
- **Mínimo:** 30 trayectorias (`UMBRAL_MINIMO_TRAYECTORIAS`). Con menos, la respuesta es `insuficiente_datos` y no se entrena ningún modelo.
- **Filtros opcionales:** programa (comparado por su forma canónica) y cohorte (la trayectoria entra si el origen o el destino pertenece a esa cohorte).

### 10.2 Variables

| Variable | Origen | Codificación |
|---|---|---|
| Estado laboral inicial | Medición de origen | Ordinal: sin_empleo 0, estudiante 1, independiente 2, empleado 3 |
| Salario inicial | Medición de origen | SMLV numérico; 0 si no reporta |
| Satisfacción académica | Medición de origen | Promedio 1-5; 3,0 si no hay respuesta |
| Habilidades blandas | Texto abierto de origen | Número de detecciones de la taxonomía |
| Habilidades duras | Texto abierto de origen | Número de detecciones de la taxonomía |
| Cohorte de origen | `mediciones.anio` | Numérica |
| Programa | `egresados.programa` | One-hot de los 8 programas más frecuentes más "Otros" |

No se usan documento, nombres ni correo como variables (RNF-08, ADR-019); el documento solo sirve para emparejar las dos mediciones.

### 10.3 Variables objetivo

- **Estado laboral de destino:** multiclase, con las categorías de RN-16.
- **Rango salarial de destino:** `< 2 SMLV`, `2–4 SMLV`, `> 4 SMLV` o `Sin ingreso / No reporta` (también para `sin_empleo`).

### 10.4 Entrenamiento

- **Modelo de estado:** `GradientBoostingClassifier(n_estimators=50, max_depth=3, random_state=42)`.
- **Balanceo de clases (Cost-Sensitive Learning, commit `46921d7`):**
  - Peso de cada muestra: `w = balanced(y) ^ 0.65`, normalizado para que el promedio sea 1.
  - `balanced(y)` es el peso de scikit-learn, n / (k × n_clase). El exponente 0,65 suaviza la penalización de la clase mayoritaria.
  - Los pesos se aplican en el ajuste final, en cada pliegue de la validación cruzada y en el backtesting temporal.
- **Comparativa de algoritmos (IA-10):** también se evalúan Random Forest (`n_estimators=50`, `max_depth=5`, `class_weight="balanced"`) y Regresión Logística estandarizada (`class_weight="balanced"`). Es solo informativa: el modelo en producción es siempre Gradient Boosting, aunque otro obtenga mejores métricas.
- **Modelo salarial:** `GradientBoostingClassifier(n_estimators=40, max_depth=3, random_state=42)`, sin balanceo. Solo se entrena si hay más de un rango.
- **Determinismo:** con `random_state=42`, los mismos datos producen el mismo resultado.

### 10.5 Validación y métricas

- **Validación cruzada estratificada:** `StratifiedKFold` con `n_splits = max(2, min(5, tamaño de la clase más pequeña))`, barajada y con semilla 42. Se informan **accuracy** (exactitud) y **F1 macro**, el promedio del F1 por clase, que es más honesto cuando hay desbalance.
- **Matriz de confusión:** se calcula con el modelo final **sobre los mismos datos de entrenamiento**, así que es optimista. Las métricas válidas son las de validación cruzada.
- **Importancia de variables:** `feature_importances_` del Gradient Boosting, en porcentaje. Se muestran las 8 primeras con nombres legibles.

### 10.6 Agregación por programa y semáforo de riesgo

El modelo calcula la probabilidad de cada estado para cada trayectoria y la promedia por programa:

| Nivel de riesgo | Probabilidad promedio de `sin_empleo` |
|---|---|
| Alto (genera alerta) | ≥ 30 % |
| Medio | ≥ 18 % y < 30 % |
| Bajo | < 18 % |

El rango salarial estimado de cada programa es el más frecuente entre las estimaciones del modelo. **"Egresados en riesgo"** suma todos los egresados de los programas en nivel Alto; no cuenta personas con riesgo individual alto.

### 10.7 Robustez estadística (IA-13)

| Dimensión | Verde | Amarillo | Rojo |
|---|---|---|---|
| Muestra (trayectorias) | ≥ 100 | 30–99 | < 30 |
| Balance (clase minoritaria) | ≥ 10 % | 5–10 % | < 5 % |
| Exactitud en CV | ≥ 75 % | 55–75 % | < 55 % |

El nivel general es **Baja** si hay 2 o más rojos (o muestra y exactitud en rojo), **Alta** si hay 2 o más verdes y ningún rojo, y **Media** en otro caso.

### 10.8 Validación temporal (IA-17)

Este backtesting entrena con las cohortes anteriores y evalúa sobre la cohorte de origen más reciente. Requiere al menos 2 cohortes, 15 trayectorias de entrenamiento y 5 de prueba. La estabilidad se diagnostica por la diferencia de exactitud con la validación cruzada:

| Diferencia | Diagnóstico |
|---|---|
| ≤ 6 puntos | Alta |
| ≤ 14 puntos | Moderada |
| Mayor | Sensible (ciclo económico anual) |

### 10.9 Robustez de la sede (IA-08)

`/api/ia/prediccion-benchmark-sedes` aplica el mismo modelo **solo a la sede del coordinador** (ADR-020). Devuelve sus trayectorias, la exactitud, la probabilidad promedio de empleo, los egresados en riesgo, el factor principal y la robustez. No compara con otras sedes.

### 10.10 Cómo interpretar el resultado (y qué no afirmar)

En una presentación conviene hablar de **estimaciones** o **probabilidades estimadas por el modelo de análisis**, no de predicciones ni proyecciones.


- **Es un análisis retrospectivo.** El modelo se entrena con trayectorias cuyo destino ya se conoce, y las probabilidades por programa son el promedio de lo que el modelo estima para esas mismas trayectorias. Resume qué tan determinada está la situación en el seguimiento por las condiciones de origen. No es un pronóstico sobre graduandos que aún no tienen seguimiento.
- **No hay estimaciones individuales:** solo se publican agregados por programa (ADR-019) y no se guardan modelos entre consultas.
- **Calidad de los datos:** la calidad depende de la cantidad de trayectorias y del balance de clases; el semáforo de robustez lo indica en cada consulta. Con muestras pequeñas o desbalance severo, las cifras deben presentarse con cautela.
- **Lectura de las importancias:** la importancia de una variable indica cuánto la usa el modelo, no una causa.

## 11. Caché y rendimiento

| Caché | Alcance | Clave | Vigencia |
|---|---|---|---|
| `prediccion_model_cache` | Por worker | Sede (`tag_sede`), número y máximo id de mediciones, momentos y filtros | 300 s, 50 entradas |
| `habilidades_cache` | Por worker | Firma de curadurías, sede, filtros y número de mediciones | 300 s, 100 entradas |
| `_preprocesar_dual` y extracción por texto | Por worker | Texto | Hasta 16.384 textos |

Hasta la auditoría 09, `ModelCache.set()` no guardaba ninguna entrada, así que estas cachés no tenían efecto; desde entonces funcionan. La primera consulta de cada worker tras un reinicio carga spaCy (unos 3 s) y preprocesa todas las respuestas abiertas (unos 3 ms por texto distinto). En la auditoría 08 tardó unos 40 s con 31.000 respuestas; en caliente responde en 2-7 s. Se recomienda calentar Analítica y Co-relaciones antes de una demostración.

## 12. Cómo se verifica

- **Pruebas automatizadas** (`OEUPB-Backend/tests/`, SQLite en memoria):
  - `test_prediccion_empleabilidad.py`: entrenamiento, robustez, datos insuficientes, endpoint y balanceo.
  - `test_ia_alcance.py`: sede propia, curaduría por autor, reversión entre workers, anonimización, exportación y campo de balanceo.
  - `test_habilidades_comparativa.py`: contrato de la comparativa temporal (IA-06).
  - `test_divipola.py`: normalización de códigos, nombres, códigos desconocidos, etiquetas del Explorador y de las publicaciones, y ficha del egresado.
  - `test_programa_normalizer.py`: canonización y homologación de programas (IA-16).
  - `test_curaduria_habilidades.py`, `test_nlp_service.py`, `test_reportes_analiticos.py` y `test_indicadores.py`: NLP, alertas, KPI, comparación y publicación.
- **Diagnósticos manuales** (`OEUPB-Backend/scripts/dev/diagnostico_ia/`): imprimen el resultado del pipeline sobre textos de ejemplo, sin base de datos.

## 13. Parámetros principales

| Parámetro | Valor | Ubicación |
|---|---|---|
| Umbral de privacidad por celda | 5 | `indicadores.UMBRAL_MINIMO_PUBLICACION` |
| Pares mínimos de comparación | 5 | `indicadores.MINIMO_PARES_COMPARACION` |
| Muestra mínima de alertas | 5 | `analitica_router.MUESTRA_MINIMA_ALERTA` |
| Umbrales de empleabilidad en alertas | 70 % / 50 % | `analitica_router` |
| Trayectorias mínimas del modelo | 30 | `prediccion_service.UMBRAL_MINIMO_TRAYECTORIAS` |
| Suavizado del balanceo | 0,65 | `calcular_pesos_balanceados` |
| Riesgo alto / medio | 30 % / 18 % | `agregar_predicciones_por_programa` |
| Delta de tendencia de habilidades | ± 4 puntos | `comparar_habilidades_temporales` |
| Vigencia de las cachés | 300 s | `model_cache.py` |

Cambiar cualquiera de estos valores es una decisión de producto: debe registrarse en un ADR y actualizar este documento y sus pruebas.
