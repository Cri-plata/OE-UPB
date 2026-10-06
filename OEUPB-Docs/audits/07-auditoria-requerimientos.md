# Auditoría de requerimientos 07

**Estado:** Verificada y resuelta el 2026-10-03 (ver [Verificación y resolución](#verificación-y-resolución)); quedan ítems en el backlog
**Fecha:** 2026-10-03
**Alcance:** specs/, requirements/, architecture/

**Método:** lectura completa y análisis cruzado de `specs/README.md`, `specs/api/openapi.json`, `specs/db/oeupb-schema.sql`, `requirements/01-requerimientos.md`, `02-historias-usuario.md`, `03-reglas-negocio.md`, `04-hallazgos-figma.md`, `casos-de-uso.md`, `matriz-trazabilidad.md` y `architecture/00` a `05`, según el prompt de [`auditoria_requerimientos.md`](auditoria_requerimientos.md). Los documentos referenciados fuera del alcance (ADR, BACKLOG, `docs/`, auditorías anteriores) no se usaron como evidencia. Los hallazgos ya resueltos en la auditoría 05 se volvieron a contrastar con el texto vigente y solo se reportan cuando el texto todavía muestra el problema. Las referencias usan el formato `archivo:línea` relativo a `OEUPB-Docs/`.

---

## Resumen Ejecutivo

Desde la auditoría 05, la frontera de publicación (recálculo en backend, k = 5, catálogo RN-31), el RBAC y el versionado de cargas están descritos de forma coherente en reglas, historias, arquitectura, SQL y OpenAPI. Los problemas nuevos se concentran en el **módulo de inteligencia artificial**, que el contrato HTTP expone con capacidades que los requisitos no contemplan o declaran en pausa, y en **casos de borde de la publicación agregada** que el umbral por celda no cubre. El texto vigente presenta **20 contradicciones** y **21 casos de borde**.

| Severidad | Contradicciones | Casos de borde |
|---|---:|---:|
| Alta | 3 | 3 |
| Media | 8 | 12 |
| Baja | 9 | 6 |
| **Total** | **20** | **21** |

Riesgos principales:

1. **Módulo de IA fuera del marco de requisitos.** El modelo predictivo (RF-71) figura a la vez en pausa e implementado (C-01). El contrato expone un benchmark de métricas entre sedes que contradice el aislamiento por sede (C-02), una curaduría de términos sin sede que habilita a `Admin_CTIC` (C-03) y siete operaciones sin requisito, historia ni caso de uso que las respalde (C-04).
2. **Privacidad de las publicaciones más allá de la celda.** El umbral k = 5 se aplica por celda, pero cada combinación de filtros es una publicación distinta, lo que permite deducir celdas suprimidas por diferencia (B-01). La regla de "al menos un programa en común" expone métricas de programas no asignados (B-02). El título de la publicación es texto libre del cliente (C-07).
3. **Reemplazo de cargas por cohorte.** La clave de reemplazo (sede, momento, año) hace que dos archivos complementarios de la misma cohorte se sustituyan entre sí (B-03).
4. **Identidad global del egresado.** La carga actualiza `id_estudiante` y `fecha_grado` en una tabla sin sede, en contra de RN-01, y esos valores quedan visibles para otras sedes (C-08).
5. **Inventario documental desalineado.** La arquitectura no lista el router `/api/ia`, y la matriz, los casos de uso y los requisitos describen estados distintos para la misma capacidad (C-01, C-04).

---

## Contradicciones Identificadas

### C-01 — Modelo predictivo (RF-71): en pausa frente a implementado
**Severidad:** Alta · **Componente:** RF-71 / HU-10 / CU-10 / `/api/ia/prediccion-empleabilidad`

- `requirements/01-requerimientos.md:617-623` (RF-71): *"En pausa por decisión de producto. No se implementará un modelo predictivo hasta aprobar la variable objetivo, las métricas, la población, el horizonte y los criterios de aceptación."* La convención de prioridad (`:7`) clasifica las "capacidades en pausa" como Baja.
- `requirements/02-historias-usuario.md:93` (HU-10) y `requirements/04-hallazgos-figma.md:12` (*"la predicción permanece en pausa"*) mantienen el mismo estado.
- Por el contrario, `requirements/matriz-trazabilidad.md:80` marca RF-71 como *"Implementado, Gradient Boosting longitudinal con Stratified CV"*, `:94` afirma que *"RF-71 ha sido implementado y verificado"* y `:91` reporta 0 requisitos en pausa. `requirements/casos-de-uso.md:68-69` (CU-10) describe el entrenamiento y el "semáforo de riesgo por programa" como flujo implementado.
- `specs/api/openapi.json:3114-3120` expone `GET /api/ia/prediccion-empleabilidad`, que *"entrena modelos supervisados (GradientBoostingClassifier)"*, y `:3233` su exportación.
- Ningún documento del alcance define la variable objetivo, las métricas, la población, el horizonte ni los criterios de aceptación que RF-71 exige como condición previa. `architecture/01-frontend.md:46` describe `/analitica` solo como *"Clasificación NLP y alertas descriptivas"*.

**Impacto:** no es posible determinar si la capacidad está autorizada ni contra qué criterios se acepta. La matriz, que es la fuente del estado real, contradice al documento de requisitos.

### C-02 — Benchmark de métricas entre sedes frente al aislamiento por sede
**Severidad:** Alta · **Componente:** `/api/ia/prediccion-benchmark-sedes`

- `specs/api/openapi.json:3356-3362`: *"Benchmark Inter-Sedes… Permite contrastar la capacidad predictiva y métricas entre sedes institucionales."* `BenchmarkSedeItem` (`:3809`) devuelve por cada sede `sede_id`, `sede_nombre`, `total_trayectorias`, `probabilidad_empleo_promedio` y `egresados_en_riesgo`.
- `requirements/03-reglas-negocio.md:12` (RN-06): los datos fuente solo se consultan dentro de la sede del JWT. `:15` (RN-09) y `requirements/01-requerimientos.md:329-335` (RF-35): entre sedes solo se comparte lo que el coordinador propietario publica. `:33` (RN-27): *"El dashboard privado deriva siempre la sede del JWT… Las publicaciones agregadas de otras sedes se consultan en una vista separada."*
- `architecture/00-proyecto.md:57`: *"Compartir entre sedes significa publicar gráficas y métricas agregadas; nunca habilitar consultas a filas o respuestas de otra sede."*
- `requirements/01-requerimientos.md:313-319` (RF-34): *"Los datos fuente no pueden cruzar sedes."*

**Impacto:** la operación calcula y entrega métricas de otras sedes sin publicación, sin confirmación de privacidad y sin el umbral k = 5 de RN-14. Elude el único mecanismo de intercambio entre sedes que permite la documentación.

### C-03 — Curaduría de habilidades: acceso de `Admin_CTIC` y alcance sin sede
**Severidad:** Alta · **Componente:** `/api/ia/habilidades/curar` / `habilidades_curadas`

- `specs/api/openapi.json:3500`: la curaduría está *"Disponible para Coordinador_Sede y Admin_CTIC"*; `:3567`: *"Admin_CTIC puede revertir cualquiera"*.
- `requirements/02-historias-usuario.md:17` (HU-01 CA4): el Administrador CTIC *"no tiene acceso al dashboard ni a los datos de egresados"*. `architecture/00-proyecto.md:39`: *"no accede a datos ni gráficas"*. `requirements/matriz-trazabilidad.md:106`: analítica para Admin CTIC = "No".
- Los términos que se curan son las `candidatas_emergentes` extraídas de las respuestas abiertas de los egresados (`openapi.json:2593`, `CandidataEmergente`).
- `specs/db/oeupb-schema.sql:185-202` y `architecture/04-modelo-datos.md:108-118` definen `habilidades_curadas` sin `sede_id`, con `termino_original` único global (`oeupb-schema.sql:196`). `GET /api/ia/habilidades/curadas` (`openapi.json:3443`) lista todas las curadurías sin filtro de sede. Esto choca con RN-06 (`03-reglas-negocio.md:12`), porque un término derivado de respuestas de una sede queda visible y se aplica en las demás.

**Impacto:** un rol sin acceso a datos de egresados opera sobre texto derivado de ellos, y la decisión de curaduría de una sede altera el análisis de las otras.

### C-04 — Capacidades de IA expuestas sin requisito ni trazabilidad
**Severidad:** Media · **Componente:** `/api/ia/*` / inventario de arquitectura

- El contrato define `habilidades-demandadas` (`openapi.json:2593`), `reglas-asociacion` (`:2720`), `habilidades-comparativa` (`:2888`, "IA-06"), `habilidades-export` (`:2997`, "IA-07"), `prediccion-export` (`:3233`, "IA-14"), `prediccion-benchmark-sedes` (`:3356`, "IA-08") y la curaduría (`:3443-3567`, "IA-15"). Los identificadores IA-xx no aparecen en ningún documento de requisitos, historias, casos de uso ni reglas.
- `requirements/01-requerimientos.md:641-647` (RNF-07): *"La sugerencia de competencias demandadas es un requisito funcional pendiente de priorizar como RF propio"*, pero la operación ya existe en el contrato.
- `architecture/02-backend.md:29-41` enumera los routers y omite `/api/ia`. `architecture/00-proyecto.md:31` limita el backend a *"analítica NLP"*.
- `requirements/casos-de-uso.md:63` (CU-09) solo reconoce como exportaciones el *"directorio filtrado en Excel y gráficas privadas como PNG"*, y `requirements/matriz-trazabilidad.md:78` (RF-69) indica *"exporta Directorio, no toda analítica"*. Sin embargo, el contrato ofrece dos exportaciones Excel de IA.

**Impacto:** hay funcionalidad sin criterio de aceptación, sin actor autorizado documentado y fuera de las reglas de privacidad aplicables. La matriz no puede verificar su cobertura.

### C-05 — "Dashboard" para `Usuario_Consulta` frente a acceso exclusivo a publicaciones
**Severidad:** Media · **Componente:** HU-02 / navegación inicial

- `requirements/02-historias-usuario.md:25` (HU-02 CA3): *"Coordinador/Usuario de Consulta → Dashboard"*. `architecture/01-frontend.md:78`: *"`Usuario_Consulta` recibe un dashboard de solo lectura"*.
- `requirements/03-reglas-negocio.md:30` (RN-24): *"No accede a gráficas privadas, al dashboard privado, a la analítica ni a datos fuente"*. `02-historias-usuario.md:68` (HU-07): *"El Usuario de Consulta no accede a este panel"*.
- `03-reglas-negocio.md:34` (RN-28): sin `ver_publicaciones` o sin programas el usuario *"no ve ninguna gráfica"*. No se define a qué pantalla se redirige a ese usuario.

**Impacto:** el destino posterior al inicio de sesión del rol de consulta es ambiguo, y para una cuenta sin permisos no existe destino definido.

### C-06 — Retiro de publicaciones por otro coordinador de la sede
**Severidad:** Media · **Componente:** RN-09 / interfaz de publicaciones

- `requirements/03-reglas-negocio.md:15` (RN-09), `requirements/02-historias-usuario.md:130` (HU-13 CA5), `requirements/casos-de-uso.md:84` (CU-12) y `requirements/matriz-trazabilidad.md:104`: si el propietario está inactivo o fue reasignado, otro coordinador activo de la sede propietaria puede retirar la publicación.
- `architecture/01-frontend.md:76`: la acción `Publicar`/`Retirar publicación` se muestra *"únicamente al coordinador propietario"*. `:79` solo ubica `Retirar publicación` en "Mis publicaciones"; la sección "Publicadas por otros coordinadores" no incluye esa acción.

**Impacto:** la regla de negocio que resuelve el caso del propietario inactivo no tiene una ruta operable en la interfaz descrita.

### C-07 — El cliente aporta título y clave libres en la publicación
**Severidad:** Media · **Componente:** `PublicacionCreate`

- `requirements/02-historias-usuario.md:127` (HU-13 CA2): *"El cliente envía solo la definición de la gráfica."* `requirements/03-reglas-negocio.md:20` (RN-14) y `architecture/02-backend.md:84` refuerzan que el cliente no aporta métricas ni programas.
- `specs/api/openapi.json:5721` (`PublicacionCreate`) exige además `titulo` (texto libre de 3 a 180 caracteres) y `grafica_key`. `PublicacionResponse` devuelve ese título a coordinadores y usuarios de consulta de otras sedes.
- `03-reglas-negocio.md:15` (RN-09) prohíbe compartir nombres, documentos o correos. Ningún documento define validación del título frente a esa prohibición, y el catálogo RN-31 (`:37`) solo cubre variables.

**Impacto:** el único texto libre que cruza sedes no está cubierto por las reglas de privacidad. La afirmación "solo la definición" es inexacta.

### C-08 — La carga actualiza atributos de identidad que RN-01 declara inmutables
**Severidad:** Media · **Componente:** `egresados` / ETL

- `requirements/03-reglas-negocio.md:7` (RN-01): ante un documento ya persistido, la carga *"solo puede actualizar `fecha_grado`"*. `:19` (RN-13): una corrección manual queda protegida frente a cargas posteriores.
- `architecture/04-modelo-datos.md:170`: `id_estudiante` *"cada carga lo actualiza"*.
- `architecture/04-modelo-datos.md:167`: *"`egresados` no pertenece directamente a una sede"*. `PerfilEgresadoResponse` (`openapi.json:5510`) expone `id_estudiante` y `fecha_grado` a cualquier sede con una medición o vínculo visible (`04-modelo-datos.md:185`).
- En consecuencia, una carga de la sede B modifica valores (`id_estudiante`, `fecha_grado`) que la sede A ve en su directorio. Esto contradice RN-06 (`03-reglas-negocio.md:12`), que limita la modificación de datos fuente a la sede autorizada.

**Impacto:** existe un atributo actualizable fuera de RN-01 y una vía indirecta de influencia y revelación entre sedes. No se especifica si `id_estudiante` está protegido por RN-13.

### C-09 — Actualización manual de la situación laboral frente a la ausencia de encuestas manuales
**Severidad:** Media · **Componente:** RF-17 / HU-06 / RN-13

- `requirements/01-requerimientos.md:137-143` (RF-17): *"permitir actualizar el estado principal del egresado usando el catálogo"*. `requirements/02-historias-usuario.md:56` (HU-06): *"modificar o agregar su información manualmente en caso de omisiones en el Excel"*.
- `requirements/03-reglas-negocio.md:19` (RN-13): *"No existen encuestas manuales"*. El estado laboral reside en `mediciones.respuestas` (`02-historias-usuario.md:52`).
- `EgresadoManualUpdate` (`openapi.json:4679`) solo admite nombre, apellido, programa y fecha de grado. `requirements/matriz-trazabilidad.md:26` marca RF-17 como Parcial, no como descartado.

**Impacto:** según las reglas vigentes, RF-17 no puede completarse nunca, pero sigue figurando como brecha pendiente.

### C-10 — Participación de mediciones anónimas en Tendencias y Explorador
**Severidad:** Media · **Componente:** RN-15 / política de mediciones

- `requirements/03-reglas-negocio.md:21` (RN-15): *"Tendencias y Explorador usan solo mediciones identificadas."*
- `architecture/02-backend.md:69`: *"Los reportes aplican la política explícita…; las mediciones anónimas válidas se incluyen"*, sin distinguir el origen. `architecture/04-modelo-datos.md:197`: los indicadores *"conservan todas las mediciones anónimas permitidas en agregados"*.
- RN-15 también admite anónimas en *"las publicaciones que superan RN-14"*, sin precisar si eso aplica a publicaciones con origen `tendencias` o `explorador`.

**Impacto:** el mismo indicador puede calcularse con denominadores distintos según el documento que se siga, y una publicación puede diferir de la vista privada por un motivo distinto del umbral k = 5.

### C-11 — Alta de sedes "sin cambios de código" frente a un catálogo gestionado por migraciones
**Severidad:** Media · **Componente:** RNF-05 / `sedes`

- `requirements/01-requerimientos.md:305-311` (RNF-05): *"Una sede nueva se habilita solo con un registro en el catálogo `sedes`, sin cambios de código."*
- `architecture/02-backend.md:59`: *"Alembic gestiona… el catálogo de sedes"*. El contrato solo ofrece `GET /api/sedes/` (`openapi.json:2246`). Ningún rol tiene asignada la creación o desactivación de sedes (RN-07, `03-reglas-negocio.md:13`).

**Impacto:** el criterio verificable de RNF-05 no puede cumplirse con el mecanismo descrito, y no hay actor responsable del ciclo de vida de una sede (ver B-12).

### C-12 — Longitud del documento de identidad
**Severidad:** Baja · **Componente:** RN-01 / contrato / esquema

- `requirements/03-reglas-negocio.md:7` (RN-01): documento normalizado *"de 5 a 20 letras o números"*.
- `specs/api/openapi.json:4623` (`EgresadoManualRequest`) y `:6045` (`UsuarioCreateRequest`) admiten `maxLength: 40`. `specs/db/oeupb-schema.sql:53, 66, 83, 118` usan `VARCHAR(50)`.
- El contrato no declara el error para un valor que, ya normalizado, tenga entre 21 y 40 caracteres.

### C-13 — Dos sistemas de alertas con criterios incompatibles
**Severidad:** Baja · **Componente:** RF-73 / HU-10 / CU-10

- `requirements/matriz-trazabilidad.md:82` (RF-73): criterios *"M1/M5, muestra ≥ 5, severidad enumerada"*. `AlertaResponse` (`openapi.json:3690`) enumera `severidad` como `media | alta`.
- `AlertaRiesgoItem` (`openapi.json:3747`), de la predicción, tiene `severidad` y `nivel_riesgo` (`PrediccionProgramaItem`, `:5673`) como texto libre y `tamano_muestra` sin mínimo.
- `requirements/02-historias-usuario.md:99` (HU-10 CA3) fija un umbral del 30 %. `requirements/casos-de-uso.md:68` (CU-10) menciona un "semáforo" sin umbrales.

### C-14 — Semántica del parámetro `anio` en IA
**Severidad:** Baja · **Componente:** `/api/ia/*`

- `requirements/03-reglas-negocio.md:23` (RN-17) y `requirements/01-requerimientos.md:177-183` (RF-22): el año es siempre año de grado o cohorte, *"no el año de aplicación de la encuesta"*.
- `specs/api/openapi.json:2638, 2765` describen `anio` como *"Filtrar por año de carga"*. La predicción lo describe como *"cohorte / año"*.

### C-15 — Declaración de errores y restricciones en el contrato
**Severidad:** Baja · **Componente:** `openapi.json` / `03-contratos.md`

- `architecture/03-contratos.md:16`: el 422 de Pydantic conserva `HTTPValidationError`; *"la carga y la publicación documentan su propio 422"*.
- `GET /api/reportes/comparacion` (`openapi.json:1467`) y `GET /api/reportes/explorador` (`:1634`) declaran el 422 como `ErrorResponse`, aunque sus parámetros tienen restricciones de Pydantic (por ejemplo, `anio` entre 1900 y 2200). No figuran en la excepción.
- `DELETE /api/ia/habilidades/curar/{curada_id}` (`:3561`) no declara 404. `POST /api/usuarios/` responde 200 (`:279`), mientras las demás altas responden 201.
- El parámetro `momento` de Explorador y de IA es un entero sin enumeración, mientras `DefinicionGrafica.momento` (`:4401`) restringe a `0 | 1 | 5` (RN-02, `03-reglas-negocio.md:8`).

### C-16 — Mecanismo y contenido del token
**Severidad:** Baja · **Componente:** autenticación

- `architecture/02-backend.md:48-49`: el token incluye *"correo, rol y sede"* y lo protege `OAuth2PasswordBearer`.
- `specs/api/openapi.json:6633` declara un único esquema `HTTPBearer`, que usan las 42 operaciones protegidas.
- `requirements/03-reglas-negocio.md:28` (RN-22) y `architecture/02-backend.md:62` exigen contrastar la versión de autorización. No se documenta si esa versión viaja en el token ni cómo se compara.

### C-17 — Diferencias entre el diagrama ER y el SQL canónico
**Severidad:** Baja · **Componente:** `auditoria_cuentas`

- `architecture/04-modelo-datos.md:134-138` declara `USUARIOS ||--o{ AUDITORIA_CUENTAS` y `actor_id FK`.
- `specs/db/oeupb-schema.sql:37-50` define `auditoria_cuentas` sin ninguna clave foránea.
- `oeupb-schema.sql:2` declara *"Verificado: 2026-09-24"* y `architecture/03-contratos.md:3` *"verificado el 2026-09-24"*. Esas fechas son anteriores a la verificación de `04-modelo-datos.md` (2026-09-25) y no permiten saber si el inventario de `/api/ia` y `habilidades_curadas` se revisó.

### C-18 — RN-25 describe un escenario inalcanzable
**Severidad:** Baja · **Componente:** RN-25 / `mediciones.intento`

- `requirements/03-reglas-negocio.md:31` (RN-25): *"Pueden existir múltiples mediciones válidas para el mismo documento, sede, momento y cohorte."*
- RN-01 (`:7`) deja una sola fila por documento dentro de un archivo. RN-12 (`:18`) reemplaza la versión anterior de la misma sede, momento y cohorte y elimina sus mediciones. RN-13 (`:19`) excluye las encuestas manuales.
- Con esas reglas no existe flujo que produzca un segundo intento. Sin embargo, `oeupb-schema.sql:131` y `architecture/02-backend.md:69` diseñan la selección del "intento más reciente".

### C-19 — Dependencias y prioridades invertidas en "Requerimiento Ligado"
**Severidad:** Baja · **Componente:** `01-requerimientos.md`

- La convención (`01-requerimientos.md:5`) define el campo como *"dependencias funcionales directas"*. Varias dependencias no son funcionales o contradicen la prioridad:
  - RF-14, búsqueda por nombre (Alta), depende de RF-13, ceremonia (Media, Parcial) (`:113-119`).
  - RF-10, alta manual (Alta), depende de RF-09, resultado de carga (`:81-87`).
  - RF-29 (Media) depende de RF-28, dispersión (Baja, No implementado) (`:233-239`).
  - RF-56 (Media) depende de RF-55 (Baja, No implementado) (`:497-503`).
  - RF-58 (Media) depende de RF-57 (Baja, No implementado) (`:513-519`).
  - RNF-04, menús (`:297-303`), depende de RF-01, carga.

### C-20 — Resumen de carga exigido frente a la respuesta del contrato
**Severidad:** Baja · **Componente:** `CargaResponse`

- `requirements/02-historias-usuario.md:53` (HU-05 CA4): *"el resumen informa cuántos registros se conservaron"*. `requirements/04-hallazgos-figma.md:24`: el resultado *"informa cuántos casos se resolvieron"* por doble titulación.
- `CargaResponse` (`openapi.json:3943`) solo tiene `mensaje`, `errores`, `carga_id`, `version`, `estado` y `registros`. Los conteos solo podrían viajar dentro del texto libre de `mensaje`.

---

## Casos de Borde

### B-01 — Revelación por diferencia entre publicaciones
**Severidad:** Alta · **Componente:** RN-14 / clave de publicación

RN-14 (`03-reglas-negocio.md:20`) aplica k = 5 por celda. `architecture/01-frontend.md:83` indica que la clave incluye un hash de los filtros, *"para que cada combinación sea una gráfica distinta"*. Un coordinador puede publicar la misma métrica con `programas = [A, B]` y con `programas = [A]`, o con cohortes que se solapan. Cada celda supera el umbral, pero la resta entre publicaciones revela una celda menor que 5. Lo mismo ocurre entre versiones sucesivas y entre un total publicado y celdas "omitidas". No se define ningún control sobre publicaciones solapadas ni sobre la coherencia de totales.

### B-02 — Alcance de "al menos un programa en común"
**Severidad:** Alta · **Componente:** RN-24 / RF-37

RN-24 (`03-reglas-negocio.md:30`) concede visibilidad con *"al menos un programa en común"*. Una publicación sin filtro de programa (por ejemplo, la distribución por programas del Reporte General) contiene métricas de todos los programas de la sede. Un usuario autorizado solo para un programa vería las de los demás. RF-37 (`01-requerimientos.md:345-351`) habla de gráficas *"compatibles con los permisos y programas asignados"* sin definir esa compatibilidad. Tampoco se especifica si los programas cuyas celdas se suprimen por k = 5 permanecen en `programas` de la publicación.

### B-03 — Varios archivos para la misma cohorte
**Severidad:** Alta · **Componente:** RN-12 / RF-09

RN-12 (`03-reglas-negocio.md:18`) y RF-09 (`01-requerimientos.md:73-79`) reemplazan la versión vigente por (sede, momento, año de grado). Si la información de una cohorte llega en archivos complementarios (por facultad o por programa), cada archivo elimina las mediciones del anterior. No se define cómo cargar una cohorte en partes ni qué ocurre con filas cuyo `FECHA_GRADO` pertenece a un año distinto del informado en la carga (RN-17, `:23`).

### B-04 — Propiedad de una publicación con clave compartida en la sede
**Severidad:** Media · **Componente:** `publicaciones_graficas`

La unicidad es `(sede_id, grafica_key, version)` (`oeupb-schema.sql:177`), no por coordinador, y la clave se deriva de los filtros (`01-frontend.md:83`). Si dos coordinadores de una sede publican la misma gráfica, el segundo crea una versión nueva y marca la del primero como `reemplazada` (`04-modelo-datos.md:193`). RN-09 (`03-reglas-negocio.md:15`) dice que *"solo el coordinador propietario puede activarla"*. No se define si se reasigna la propiedad, si se rechaza la operación ni qué muestra `/api/publicaciones/mias` a cada coordinador. Tampoco se define si un propietario reasignado a otra sede conserva el derecho de retiro ("puede retirarla el propietario o, si este… fue reasignado, otro coordinador").

### B-05 — Confirmación de privacidad antes del recálculo
**Severidad:** Media · **Componente:** CU-12 / HU-13 CA6

El flujo de CU-12 (`casos-de-uso.md:84`) es: confirmar la privacidad, y después el backend recalcula y aplica k = 5. `architecture/01-frontend.md:83` reconoce que la instantánea *"puede diferir de la vista privada"*. El coordinador confirma la revisión de una gráfica que no es la que se publica, y no existe paso de vista previa de la instantánea suprimida.

### B-06 — Publicaciones basadas en cargas eliminadas o reemplazadas
**Severidad:** Media · **Componente:** RN-14 / RN-23

RN-14 (`:20`) impide el recálculo automático y RN-23 (`:29`) elimina físicamente una carga y sus mediciones. Si una carga errónea se publicó y luego se elimina o reemplaza, la instantánea sigue vigente con métricas de datos que ya no existen. No se define si debe retirarse, marcarse como desactualizada o notificarse al propietario.

### B-07 — Corrección manual de un egresado creado por carga
**Severidad:** Media · **Componente:** RN-13 / RN-23 / `egresados_sedes`

El vínculo `egresados_sedes` solo se crea en el alta manual (`04-modelo-datos.md:176`). Si un coordinador corrige un egresado que llegó por carga y luego elimina esa carga, RN-23 (`:29`) borra los egresados *"sin mediciones y sin vínculo manual"*, y con ellos la corrección que RN-13 (`:19`) declara protegida. Además, el esquema no tiene ningún atributo que marque un egresado como "corregido manualmente" (`oeupb-schema.sql:52-62`). No se especifica cómo se determina la protección.

### B-08 — Egresados no corregibles ni eliminables
**Severidad:** Media · **Componente:** RN-13 / RF-11 / RF-12

RN-13 (`:19`) bloquea la edición de un egresado *"vinculado a más de una sede"*, y no existe custodia institucional. Un error en su nombre o programa no puede corregirse por ningún actor. "Vinculado" no se define: puede referirse a mediciones, a `egresados_sedes` o a ambos. `04-modelo-datos.md:186` bloquea la eliminación mientras existan mediciones. Retirar los datos de una sola persona exige eliminar la carga completa de su cohorte, pese a RF-12 (`01-requerimientos.md:97-103`, *"borrar registros si es necesario"*).

### B-09 — Doble titulación con la misma fecha o en la misma cohorte
**Severidad:** Media · **Componente:** RN-01

RN-01 (`:7`) conserva la fila con `FECHA_GRADO` más reciente. No define el desempate cuando ambas filas tienen la misma fecha (dos programas en la misma ceremonia). Tampoco reconoce que la fila descartada elimina la medición de un programa, lo que reduce los conteos por programa (RF-16, RF-56).

### B-10 — Fuente del programa en los indicadores
**Severidad:** Media · **Componente:** `egresados.programa` / filtros

`egresados.programa` es global, lo fija la primera carga (RN-01) y es editable manualmente (RN-13). RN-29 (`:35`) obtiene los programas *"de los valores… observados en cargas"*. HU-06 CA4 (`02-historias-usuario.md:61`) exige que el cambio manual se refleje *"instantáneamente en los Dashboards"*. No se define si los filtros por programa (RF-21), los pares por programa (RN-26) y la audiencia de publicaciones usan el programa del egresado o el registrado en la medición. Si se usa el del egresado, una persona con programas distintos en dos sedes se clasifica en ambas con el programa de la primera.

### B-11 — Catálogo RN-31 basado solo en el nombre de columna
**Severidad:** Media · **Componente:** Explorador / publicación

RN-31 (`:37`) clasifica las variables por el nombre normalizado de la columna y excluye documentos, nombres, correos, teléfonos, fechas personales e identificadores. No contempla direcciones, empleador, cargo, nombres de terceros ni respuestas abiertas de texto libre. Tampoco contempla columnas con nombres genéricos ("Pregunta 12") que contengan esos datos. `04-modelo-datos.md:195` admite como etiquetas publicadas *"respuestas a variables del catálogo RN-31 con al menos 5 observaciones"*.

### B-12 — Ciclo de vida de una sede
**Severidad:** Media · **Componente:** `sedes.activa`

`sedes` tiene un indicador `activa` (`oeupb-schema.sql:9`) y el catálogo devuelve solo las activas (`02-backend.md:38`). No se define el efecto de desactivar una sede sobre sus coordinadores y usuarios de consulta, la carga, el directorio ni sus publicaciones vigentes. Tampoco se define quién puede hacerlo (ver C-11).

### B-13 — Administración de cuentas `Admin_CTIC`
**Severidad:** Media · **Componente:** RN-07 / HU-01

`UsuarioCreateRequest.rol` (`openapi.json:6031`) solo admite `Coordinador_Sede` y `Usuario_Consulta`. RN-07 (`:13`) no asigna a nadie la creación, desactivación o reemisión de credenciales de una cuenta CTIC. HU-01 CA5 (`02-historias-usuario.md:18`) dice que *"solo el administrador autorizado puede reemitirla"*, pero no identifica quién lo hace para el propio CTIC. Tampoco se contempla la pérdida o el vencimiento de la última cuenta CTIC.

### B-14 — Cambio de sede de un usuario de consulta
**Severidad:** Media · **Componente:** `PATCH /api/usuarios/{id}`

`UsuarioUpdateRequest` (`openapi.json:6413`) admite `sede_id`. RN-08 (`:14`) indica que el coordinador *"asigna… sede"*, mientras RN-07 (`:13`) le prohíbe crear usuarios de otra sede, y CU-11 (`casos-de-uso.md:75`) habla de *"sede propia"*. No se define si un coordinador puede trasladar un usuario de consulta a otra sede, ni qué ocurre con sus programas, que provienen de la sede anterior (RN-29). `UsuarioCreateRequest.sede_id` es opcional, sin regla para el valor nulo o distinto.

### B-15 — Entrenamiento del modelo en cada solicitud
**Severidad:** Media · **Componente:** `/api/ia/prediccion-*`

La descripción de `prediccion-empleabilidad` (`openapi.json:3120`) indica que la operación entrena modelos en cada GET, y `prediccion-export` (`:3233`) recibe los mismos parámetros. No se define si la exportación reutiliza el resultado mostrado o vuelve a entrenar, ni si los resultados son deterministas entre llamadas. No se especifica cómo se cumple RNF-07 (`01-requerimientos.md:641-647`, desacoplamiento del dashboard). Tampoco se especifica cómo se cumple RNF-08 (`:649-655`, entrenamiento solo con datos anonimizados) cuando las trayectorias se unen por documento (RF-52).

### B-16 — Huella repetida frente a versiones no vigentes o a otro momento o año
**Severidad:** Baja · **Componente:** RN-12

RN-12 (`:18`) rechaza con 409 solo la huella igual a la de *la versión vigente*. No se define el tratamiento de un archivo idéntico a una versión `reemplazada` (posible reversión), ni el de un mismo archivo cargado con otro momento o año. En este último caso se duplicarían mediciones bajo una cohorte incorrecta.

### B-17 — Registro de cargas rechazadas y estados de carga
**Severidad:** Baja · **Componente:** RF-07 / RN-20 / `cargas`

RF-07 (`01-requerimientos.md:57-63`) exige registrar *cada archivo* con estado y resultado, y `cargas.errores` existe (`oeupb-schema.sql:104`). RN-20 (`:26`) revierte el archivo completo ante un error. No se define si un archivo rechazado deja un registro de carga. Los valores de `cargas.estado` no están enumerados ni restringidos (`oeupb-schema.sql:101`). Nada en el esquema garantiza una única versión vigente por (sede, momento, año): depende del bloqueo, que no aplica en SQLite (`02-backend.md:63`).

### B-18 — Política de la contraseña personal
**Severidad:** Baja · **Componente:** autenticación

`CambioContrasenaTemporalRequest` (`openapi.json:3889`) no declara longitud ni complejidad. No existe una operación para que el usuario cambie voluntariamente su contraseña, aunque existe `/mi-perfil` (`01-frontend.md:50`), ni se definen límites de intentos de inicio de sesión. RN-18 (`:24`) solicita la cédula al crear cualquier cuenta, pero fuera de desarrollo no se usa como credencial y no se documenta su finalidad.

### B-19 — Combinaciones inválidas en la comparación de momentos
**Severidad:** Baja · **Componente:** `/api/reportes/comparacion`

HU-08 (`02-historias-usuario.md:75-79`) se titula "M1 vs M5", y CU-06 (`casos-de-uso.md:45`) admite dos momentos cualesquiera. No se define el comportamiento con `momento_inicial = momento_final` ni con un orden invertido (M5 → M1). Tampoco se define qué ocurre con el indicador de formalidad en M0, donde RN-16 (`:22`) no lo clasifica.

### B-20 — "Frente al año anterior" en el panel principal
**Severidad:** Baja · **Componente:** HU-07 CA2

HU-07 CA2 (`02-historias-usuario.md:71`) pide comparar el estado laboral *"frente al año anterior"*. Con RN-17 (`:23`), el año es una cohorte. No se define si la comparación es entre cohortes consecutivas o entre aplicaciones de la encuesta, y `KpisResponse` (`openapi.json:5289`) no tiene un campo para ella.

### B-21 — Exportaciones con datos personales sin auditoría definida
**Severidad:** Baja · **Componente:** CU-09 / exportaciones

`GET /api/directorio/exportar.xlsx` (`openapi.json:2155`) entrega documentos y nombres de egresados. Las exportaciones de IA incluyen términos extraídos de respuestas abiertas. RF-07 solo define auditoría para cargas, y RN-13 y RN-23 para egresados y eliminaciones. No se define si una exportación queda registrada, ni quién la ejecutó y con qué filtros.

---

## Recomendaciones de Mitigación

### P0 — Aislamiento y privacidad (bloqueantes)

1. **Benchmark entre sedes (C-02):** retirarlo del contrato o restringirlo a métricas que cada coordinador propietario haya publicado, con k = 5. Documentar la decisión en RN-06 y RN-27.
2. **Curaduría de habilidades (C-03):** decidir si es por sede (agregar `sede_id` y filtrar el listado) o institucional (definir el actor responsable y declarar la excepción a RN-06). Retirar el acceso de `Admin_CTIC` o actualizar HU-01 CA4 y la matriz de autorización.
3. **Publicaciones solapadas (B-01, B-02):** definir en RN-14 un control de diferencia entre publicaciones de la misma métrica. Puede ser supresión complementaria, filtros de programa o cohorte en bloques fijos, o el rechazo de publicaciones que se solapen con otras vigentes. Precisar en RN-24 qué significa "compatible" para gráficas con varios programas.
4. **Título de la publicación (C-07):** generarlo en el backend a partir de la definición o validarlo con las exclusiones de RN-31. Corregir HU-13 CA2.

### P1 — Estado del producto e integridad de datos

1. **RF-71 (C-01):** producto debe decidir entre levantar la pausa (redactar en RF-71 y HU-10 la variable objetivo, las métricas, la población, el horizonte y los criterios de aceptación) o mantenerla (retirar o desactivar los endpoints y corregir la matriz y CU-10).
2. **Capacidades IA-xx (C-04):** crear los RF, HU y CU correspondientes o retirarlos del contrato. Agregar `/api/ia` al inventario de `02-backend.md`, `00-proyecto.md` y `01-frontend.md`, y actualizar CU-09 y RF-69.
3. **Reemplazo por cohorte (B-03, B-16):** decidir si una cohorte admite varios archivos (por ejemplo, con alcance por programa en la clave de reemplazo) y documentar el tratamiento de las huellas repetidas.
4. **Identidad global (C-08, B-07, B-08, B-10):** incluir `id_estudiante` en RN-01, definir si está protegido por RN-13, modelar explícitamente la protección por corrección manual y definir la fuente del programa en los indicadores y la audiencia.
5. **Publicaciones huérfanas y propiedad (B-04, B-06):** definir la propiedad por coordinador o por sede y el efecto de eliminar o reemplazar una carga sobre las publicaciones que derivan de ella.

### P2 — Contrato, cuentas y operación

1. Agregar una vista previa de la instantánea suprimida antes de la confirmación de privacidad (B-05) y exponer el retiro por otro coordinador en la interfaz (C-06).
2. Definir el destino posterior al inicio de sesión del rol de consulta, incluido el caso sin permisos (C-05).
3. Definir el ciclo de vida de las sedes y de las cuentas CTIC, y la regla de cambio de sede de los usuarios de consulta (C-11, B-12, B-13, B-14).
4. Alinear el contrato: longitud del documento (C-12), esquemas de 422 y códigos de respuesta (C-15), enumeración de `momento`, semántica de `anio` en IA (C-14), esquema de seguridad y versión de autorización (C-16), y campos estructurados de resumen en `CargaResponse` (C-20).
5. Unificar los criterios de las alertas descriptivas y predictivas (C-13). Definir la reproducibilidad del modelo y su cumplimiento de RNF-07 y RNF-08 (B-15).
6. Definir la política de contraseñas, el cambio voluntario y los límites de intentos (B-18), así como la auditoría de exportaciones (B-21).

### P3 — Calidad documental

1. Reconciliar RN-15 con `02-backend.md:69` y `04-modelo-datos.md:197` (C-10).
2. Reclasificar RF-17 como descartado o redefinirlo en coherencia con RN-13 (C-09).
3. Eliminar o reformular RN-25 (C-18) y revisar las dependencias del campo "Requerimiento Ligado" (C-19).
4. Sincronizar el diagrama ER con el SQL y actualizar las fechas de verificación (C-17). Enumerar los estados de `cargas` y decidir el registro de cargas rechazadas (B-17).
5. Precisar HU-07 CA2 (B-20), las combinaciones de momentos de HU-08 (B-19) y el desempate de doble titulación de RN-01 (B-09).
6. Ampliar RN-31 con criterios para cuasi-identificadores y texto libre (B-11).

---

## Verificación y resolución

**Fecha:** 2026-10-03. Los hallazgos se contrastaron con el código y con los ADR, que estaban fuera del alcance del auditor. Producto respondió un formulario de decisiones, recogidas en [ADR-020](../adr/020-decisiones-auditoria-07.md): el límite entre sedes son las publicaciones; la curaduría es institucional y solo de coordinadores; se asume un coordinador activo por sede; el título se valida en backend; la revelación por diferencia es un riesgo aceptado; se mantiene la audiencia por programa en común; y cada cohorte se carga en un único archivo.

Veredictos: **Confirmado** (el problema existía en el código), **Documental** (el código ya cumplía o la decisión ya existía; solo el texto estaba desalineado), **Decisión** (resuelto por ADR-020), **Pendiente** (con ítem de backlog) y **Abierto** (baja prioridad, sin ítem).

| ID | Veredicto | Resolución |
|---|---|---|
| C-01 | Documental | ADR-019 ya había levantado la pausa. Se reescribieron RF-71, HU-10, CU-10 y los hallazgos de Figma. |
| C-02 | Confirmado | Los coordinadores ya veían solo su sede, pero `Admin_CTIC` recibía las métricas de todas. Ahora el endpoint es solo para coordinadores y sede propia. |
| C-03 | Confirmado, con defecto adicional | Se retiró a `Admin_CTIC`. Solo el autor modifica (409 para otro coordinador) o revierte (403) su curaduría. Además, `creado_por_correo` se guardaba siempre como "desconocido" porque leía un campo inexistente; corregido. |
| C-04 | Confirmado | Sin RF nuevos: las capacidades IA-xx se trazan a RF-69, RF-71, RF-72 y RF-73 en la matriz y en CU-09 y CU-10. Se agregó RN-32 y `/api/ia` al inventario de arquitectura. |
| C-05 | Confirmado, con defecto adicional | El login enviaba al usuario de consulta a `/mi-perfil`, mientras los guards y el mapa de pantallas usaban `/publicaciones`. Corregido con prueba; HU-02 CA3 y `01-frontend.md` alineados. |
| C-06 | Pendiente | PUB-03 (requiere mockup). `01-frontend.md` documenta la brecha. |
| C-07 | Confirmado | El backend rechaza con 422 los títulos con correos, enlaces o secuencias de 5 o más dígitos (ADR-020). |
| C-08 | Documental | La actualización de `id_estudiante` en cada carga es intencional (ID institucional que no se edita a mano). RN-01 y `04-modelo-datos.md` lo recogen. |
| C-09 | Documental | RF-17 y HU-06 reescritos según ADR-014: el estado laboral solo proviene de las cargas. |
| C-10 | Documental | El código ya cumplía RN-15. Se corrigieron `02-backend.md`, `04-modelo-datos.md` y la declaración de `medicion_policy.py`. |
| C-11 | Documental | RNF-05 precisa que la sede se crea con una migración de datos, sin cambios en el código de la aplicación. El actor queda en AUT-01. |
| C-12 | Documental | Los 40 caracteres del contrato son la entrada antes de normalizar; el backend exige 5 a 20 después (`documentos.py`). Sin cambios. |
| C-13 | Documental | RF-71 y CU-10 fijan el umbral del 30 % de ADR-019. La severidad de texto libre de la predicción se mantiene. |
| C-14 | Confirmado | Las descripciones de `anio` en `/api/ia/*` ahora dicen "año de grado o cohorte (RN-17)". |
| C-15 | Documental | `03-contratos.md` documenta las dos formas de 422. La curaduría declara 400, 404 y 409. `POST /api/usuarios/` mantiene el 200 para no romper el contrato. |
| C-16 | Documental | `02-backend.md` lista los claims reales del token y el esquema `HTTPBearer`. |
| C-17 | Documental | El diagrama ER ya no marca FK en `auditoria_cuentas.actor_id`. Fechas de verificación actualizadas en `03-contratos.md` y `04-modelo-datos.md`; el SQL no se contrastó con una base real. |
| C-18 | Documental | RN-25 reformulada: el modelo admite varios intentos, aunque hoy cada carga produce uno. |
| C-19 | Pendiente | PRD-01. |
| C-20 | Documental | Los conteos viajan en `mensaje`; HU-05 CA4 lo precisa. |
| B-01 | Decisión | Riesgo residual aceptado (RN-14, ADR-020). El recordatorio en el diálogo de confirmación queda en PUB-04. |
| B-02 | Decisión | Se mantiene "al menos un programa en común"; RN-24 y RF-37 definen "compatible". |
| B-03 | Decisión | Un archivo por cohorte (RN-12). El aviso en la pantalla de carga queda en CAR-01. |
| B-04 | Decisión | Se asume un coordinador activo por sede (RN-07, ADR-020), sin imponerlo en backend. |
| B-05 | Pendiente | PUB-04. |
| B-06 | Pendiente | PUB-05. |
| B-07 | Documental | `04-modelo-datos.md` describe cómo se deriva la protección y que la corrección se pierde (salvo en la auditoría) si se elimina la carga de un egresado sin vínculo manual. |
| B-08 | Documental | Consecuencia aceptada de ADR-014 (sin custodia institucional). |
| B-09 | Documental | Ante un empate se conserva la última fila del archivo; RN-01 lo indica. |
| B-10 | Documental | Los filtros, pares y audiencia usan `egresados.programa`; documentado en `04-modelo-datos.md`. |
| B-11 | Abierto | Ampliar RN-31 a cuasi-identificadores y texto libre requiere decisión de producto. |
| B-12, B-13 | Pendiente | AUT-01. |
| B-14 | Documental | El backend ya ignoraba el cambio de sede de un usuario de consulta; RN-08 lo explicita. |
| B-15 | Documental | `prediccion_model_cache` reutiliza el resultado mientras las mediciones y los filtros no cambien, así que pantalla y exportación coinciden. ADR-019 fija la anonimización de las variables. |
| B-16 | Abierto | Huella repetida frente a versiones reemplazadas o a otro momento o año. |
| B-17 | Documental | Un archivo rechazado no deja fila en `cargas`; documentado en `04-modelo-datos.md`. |
| B-18 | Pendiente | AUT-01. |
| B-19, B-20, B-21 | Abierto | Combinaciones de momentos, comparación "frente al año anterior" y auditoría de exportaciones. |

Verificación: pruebas nuevas en `tests/test_ia_alcance.py` (benchmark, curaduría y anonimización), en `tests/test_publicaciones.py` (título) y en `login.spec.ts` (redirección del rol de consulta). Se regeneraron el OpenAPI y los tipos del frontend.

