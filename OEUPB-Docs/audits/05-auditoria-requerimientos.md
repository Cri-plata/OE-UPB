# Auditoría de requerimientos 05

**Estado:** Verificada y resuelta el 2026-09-25 (ver [Verificación y resolución](#verificación-y-resolución))
**Fecha:** 2026-09-25
**Alcance:** specs/, requirements/, architecture/

**Método:** lectura completa y análisis cruzado de `specs/README.md`, `specs/api/openapi.json`, `specs/db/oeupb-schema.sql`, `requirements/01-requerimientos.md`, `02-historias-usuario.md`, `03-reglas-negocio.md`, `04-hallazgos-figma.md`, `casos-de-uso.md`, `matriz-trazabilidad.md` y `architecture/00` a `05`. El análisis se basa exclusivamente en el texto de esos archivos; los documentos referenciados fuera del alcance (ADR, BACKLOG, `docs/`) no se usaron como evidencia. Las referencias usan el formato `archivo:línea` relativo a `OEUPB-Docs/`.

---

## Resumen Ejecutivo

La documentación ha cerrado buena parte de las brechas de auditorías anteriores: RBAC, catálogo de permisos, publicación versionada, eliminación auditada de cargas y el modelo de sedes están descritos de forma coherente en reglas, arquitectura, SQL y OpenAPI. Sin embargo, el estado actual del texto presenta **20 contradicciones** y **21 casos de borde** relevantes.

| Severidad | Contradicciones | Casos de borde |
|---|---:|---:|
| Alta | 5 | 6 |
| Media | 10 | 10 |
| Baja | 5 | 5 |
| **Total** | **20** | **21** |

Riesgos principales:

1. **Frontera de privacidad en la publicación.** El contrato de publicación recibe del cliente las métricas, etiquetas y programas (C-02), la aprobación de privacidad es una autodeclaración del mismo coordinador (C-06) y el Explorador, desde el que se publica, ofrece aún variables personales (C-03). Sin umbral mínimo de celdas (B-04), una gráfica agregada puede reidentificar personas en otra sede.
2. **Identidad global del egresado frente al aislamiento por sede.** El UPSERT por documento sobre una tabla `egresados` sin sede permite que la carga de una sede modifique datos personales visibles para otra (C-04), y el alta manual de un documento ya existente puede exponer la identidad a otra sede (B-06). La "custodia institucional" que debe resolver estos conflictos no existe como actor (C-07).
3. **Alcance del `Usuario_Consulta`.** Las historias y casos de uso le asignan vistas analíticas calculadas bajo demanda, mientras que las reglas y la arquitectura lo restringen a instantáneas publicadas (C-01).
4. **Versionado de cargas.** No se define la concurrencia de recargas (B-01), qué versión queda vigente tras eliminar la actual (B-02), ni el destino de los egresados sin mediciones (B-03).
5. **Estado declarado frente a estado descrito.** Varios documentos declaran como implementadas capacidades que otros marcan como parciales o no representadas en el contrato (C-12, C-13).

---

## Contradicciones Identificadas

### C-01 — Alcance del `Usuario_Consulta`: vistas analíticas frente a solo instantáneas publicadas
**Severidad:** Alta · **Componente:** RBAC / Dashboard / Explorador

- `requirements/03-reglas-negocio.md:30` (RN-24): *"solo puede ver instantáneas publicadas… No accede a gráficas privadas ni a datos fuente, incluso dentro de su propia sede."* Igual en `architecture/01-frontend.md:76`, `architecture/02-backend.md:81` y `requirements/casos-de-uso.md:79`.
- Sin embargo, `requirements/02-historias-usuario.md:68-72` (HU-07) le da un panel de métricas con *"datos propios… limitados por sede"*; `:75-79` (HU-08) le permite comparar M1 vs M5; `:82-86` (HU-09) le permite filtrar y *"el frontend solicita al backend un nuevo agregado autorizado… antes de calcularlo"* y *"volver a la vista general de la sede"*; `:102` (HU-11) le asigna el análisis de IA.
- `requirements/casos-de-uso.md:37-38, 43-44, 49-50` (CU-05/06/07) incluyen al Usuario de Consulta como actor de flujos que *"calculan indicadores"* y *"agregan respuestas en backend"*.
- Los permisos `ver_reporte_general`, `ver_tendencias`, `ver_explorador` (`03-reglas-negocio.md:34`) sugieren acceso a esas vistas, pero no se define si habilitan cálculo bajo demanda o solo filtran instantáneas.
- `requirements/matriz-trazabilidad.md:102` niega a Consulta el acceso a datos fuente.

**Impacto:** una misma operación (p. ej. `GET /api/reportes/general`) puede autorizarse o rechazarse según el documento que se siga.

### C-02 — Métricas y programas de la publicación los aporta el cliente, no el backend
**Severidad:** Alta · **Componente:** `/api/publicaciones` / `publicaciones_graficas`

- `architecture/02-backend.md:70`: *"El backend materializa una instantánea inmutable de métricas numéricas"*.
- `requirements/casos-de-uso.md:85`: precondición *"la gráfica se calculó exclusivamente con datos fuente de su sede"*; `requirements/03-reglas-negocio.md:17` (RN-11): *"El cliente no puede ampliar ese alcance enviando una sede, programa o rol diferente."*
- `specs/api/openapi.json:2627-2673` (`PublicacionCreate`) exige al cliente `metricas`, `programas` (array, `minItems: 1`) y `definicion`; `MetricasGrafica.labels` (`:2525-2532`) y `DatasetGrafica.label` (`:1875-1879`) son cadenas libres.
- `architecture/04-modelo-datos.md:134` afirma que el contrato acepta *"exclusivamente etiquetas, series numéricas y metadatos cerrados"*, pero las etiquetas son texto arbitrario.

**Impacto:** el backend no puede demostrar que la instantánea proviene de datos de la sede, ni impedir etiquetas con nombres o documentos (RN-09, `03-reglas-negocio.md:15`), ni que el cliente declare programas ajenos para ampliar la audiencia.

### C-03 — El Explorador expone datos personales y ya permite publicar
**Severidad:** Alta · **Componente:** Explorador / Publicación

- `requirements/casos-de-uso.md:51` (CU-07): *"ofrece datos personales y metadatos no analíticos. Falta aplicar RN-31 en backend"*.
- `requirements/casos-de-uso.md:88` (CU-12) y `architecture/01-frontend.md:79`: la publicación está *"implementada"* en las acciones del Explorador.
- `requirements/03-reglas-negocio.md:37` (RN-31) excluye documentos, nombres, correos, etc. del catálogo publicable; RN-09 (`:15`) prohíbe compartir esos datos.
- `requirements/matriz-trazabilidad.md:30-31` marca RF-21/RF-22 como *Implementado* con evidencia en el Explorador, sin reflejar la brecha de RN-31.
- `specs/api/openapi.json:803-809` (`pregunta` libre) y `:2305-2336` (`ExploradorInitResponse.preguntas`) no restringen el catálogo.

### C-04 — UPSERT global del egresado frente al aislamiento por sede y la protección de correcciones manuales
**Severidad:** Alta · **Componente:** ETL / `egresados`

- `requirements/02-historias-usuario.md:51` (HU-05 CA2): si la cédula existe, *"el sistema actualiza sus datos (UPSERT)"*. `requirements/03-reglas-negocio.md:7` (RN-01) remite a una *"política de precedencia aprobada"* que no está definida en el alcance.
- `architecture/04-modelo-datos.md:109`: *"`egresados` no pertenece directamente a una sede"*; `specs/db/oeupb-schema.sql:51-59` no tiene sede ni procedencia por campo.
- `requirements/03-reglas-negocio.md:12` (RN-06): los egresados *"solo pueden ser consultados o modificados dentro de la sede autorizada"*; `architecture/04-modelo-datos.md:126`: la edición manual *"se bloquea cuando la misma identidad está vinculada a otra sede"*. La carga de otra sede sí puede sobrescribirlos.
- RN-13 (`03-reglas-negocio.md:19`): la corrección manual *"queda protegida frente a cargas posteriores"* (absoluto); HU-05 CA4 (`02-historias-usuario.md:53`): puede sobrescribirse *"con confirmación explícita y registro del conflicto"*. El cuerpo de carga (`openapi.json:1597-1622`) no tiene parámetro de confirmación, el esquema no tiene tabla de conflictos ni marca de campo protegido, y RN-20 (`03-reglas-negocio.md:26`) exige todo-o-nada en una sola petición.

### C-05 — Credencial temporal: cédula frente a credencial aleatoria, vencimiento y reemisión
**Severidad:** Alta · **Componente:** Alta de cuentas / Autenticación

- `requirements/02-historias-usuario.md:15, 18, 120` (HU-01 CA2/CA5, HU-12 CA5), `requirements/03-reglas-negocio.md:24` (RN-18) y `requirements/casos-de-uso.md:18`: la cédula es la contraseña temporal; *"el endurecimiento… está diferido"*.
- `architecture/02-backend.md:47, 52`: la cédula solo aplica en desarrollo; en producción la credencial es *"aleatoria obligatoria"*, *"vencen, pueden reemitirse con auditoría"*.
- `specs/api/openapi.json:3023-3034` (`contrasena_temporal`, `modo_credencial: documento|random`), `:234-290` y `:2777-2798` (reemisión que devuelve la contraseña en claro) contradicen el mensaje de HU-01 CA5 (*"comunica al usuario que su cédula es la credencial temporal"*) y el carácter "diferido" de RN-18.
- No se define el canal por el que se entrega una credencial aleatoria ni el comportamiento con la credencial vencida.

### C-06 — "Aprobación manual de privacidad" autodeclarada en la misma petición
**Severidad:** Media · **Componente:** Publicación

- `requirements/03-reglas-negocio.md:20` (RN-14) y `requirements/02-historias-usuario.md:131` (HU-13 CA6): la publicación *"requiere aprobación manual de privacidad antes de hacerse visible"*.
- `specs/api/openapi.json:2657-2661`: `aprobada_privacidad` es `const: true` en la misma solicitud que publica; `specs/db/oeupb-schema.sql:176` solo admite `publicada|retirada|reemplazada` (sin estado pendiente); `architecture/04-modelo-datos.md:134`: *"Una actualización crea y aprueba una versión nueva."*
- Ningún documento identifica al aprobador ni los criterios; no existe separación entre quien publica y quien aprueba.

### C-07 — "Custodia institucional" sin actor, flujo ni contrato
**Severidad:** Media · **Componente:** Identidad multisede

- `requirements/02-historias-usuario.md:62` (HU-06 CA5) y `requirements/03-reglas-negocio.md:19` (RN-13): la custodia institucional resuelve conflictos multisede.
- Los únicos roles son `Admin_CTIC`, `Coordinador_Sede` y `Usuario_Consulta` (`openapi.json:3068-3072`); `Admin_CTIC` *"no tiene acceso… a los datos de egresados"* (`02-historias-usuario.md:17`, `matriz-trazabilidad.md:102`). Ningún endpoint permite resolver conflictos.
- Consecuencia: las identidades vinculadas a varias sedes quedan sin edición posible (`04-modelo-datos.md:126`).

### C-08 — Encuestas manuales y origen de intentos múltiples sin soporte en el modelo
**Severidad:** Media · **Componente:** `mediciones` / Directorio

- HU-06 CA5 (`02-historias-usuario.md:62`) y RN-13 (`03-reglas-negocio.md:19`): el coordinador *"puede registrar encuestas manuales"*.
- `specs/db/oeupb-schema.sql:114` y `architecture/04-modelo-datos.md:113`: `carga_id` es obligatorio en `mediciones`; `EgresadoManualRequest` (`openapi.json:2097-2155`) no admite momento ni respuestas y no hay otro endpoint de mediciones.
- RN-25 (`03-reglas-negocio.md:31`) admite *"múltiples mediciones válidas para el mismo documento, sede, momento y cohorte"*, pero RN-12 (`:18`) reemplaza toda la carga de igual sede/momento/cohorte y los duplicados intra-archivo se resuelven por otra regla (RN-01, `:7`). El texto no identifica de dónde surgen los intentos 2..n.

### C-09 — Doble titulación: aviso de "registro omitido" frente a carga todo-o-nada
**Severidad:** Media · **Componente:** ETL

- `requirements/04-hallazgos-figma.md:23-24`: ante doble titulación se registra solo la última carrera y el modal de errores debe mostrar *"Doble titulación detectada - Se omitió registro antiguo"*.
- `requirements/03-reglas-negocio.md:26` (RN-20): cualquier error revierte el archivo completo; no se distingue entre advertencia y error, y `CargaResponse` (`openapi.json:1641-1705`) solo tiene `errores`.
- RN-01 (`03-reglas-negocio.md:7`) remite a ADR-006 (fuera del alcance) sin enunciar la regla; `egresados.programa` es una sola columna (`oeupb-schema.sql:55`), por lo que la doble titulación en cargas distintas o sedes distintas sobrescribe el programa.

### C-10 — Invariantes de rol y sede en el alta de cuentas no expresadas en el contrato
**Severidad:** Media · **Componente:** `/api/usuarios`

- HU-01 CA1 (`02-historias-usuario.md:14`) y `04-hallazgos-figma.md:21`: *"El rol no es seleccionable"*. `UsuarioCreateRequest` (`openapi.json:2864-2870, 2921-2926`) exige `rol` elegido por el cliente.
- `architecture/04-modelo-datos.md:110`: `usuarios.sede_id` *"solo es nullable para `Admin_CTIC`"*; `oeupb-schema.sql:21` no tiene restricción que lo garantice; `openapi.json:2872-2882` permite `sede_id: null`; y `openapi.json:577, 613, 668` y `architecture/02-backend.md:54` describen el caso *"coordinador sin sede"*, que la invariante declara imposible.
- HU-12 CA2 (`02-historias-usuario.md:116`) exige permisos y programas; el contrato los deja opcionales y no define su tratamiento cuando `rol = Coordinador_Sede`.

### C-11 — Ciclo de vida de cuentas: borrado excepcional, bloqueo y dobles endpoints
**Severidad:** Media · **Componente:** `/api/usuarios`

- RN-21 (`03-reglas-negocio.md:27`): borrado físico *"excepcional, restringido y auditado"*; CU-02 (`casos-de-uso.md:18`): *"solicitar borrado excepcional"* (una solicitud). `openapi.json:488-544` expone `DELETE /api/usuarios/{id}/permanente` de ejecución directa sin actor aprobador.
- `openapi.json:347-392` (`DELETE /{id}`: *"desactivación recuperable"*) y `:394-440` (`POST /{id}/desactivar`) duplican la misma operación; `:441-487` (`reactivar`) no figura en RN-21.
- RN-07 (`:13`), RN-22 (`:28`) y HU-12 CA1 (`02-historias-usuario.md:115`) hablan de "bloquear"; no existe operación ni estado distinto de `activo` (`oeupb-schema.sql:24`).

### C-12 — Filtros, comparaciones y KPIs exigidos sin representación en el contrato
**Severidad:** Media · **Componente:** `/api/reportes`

- HU-09 CA1-CA3 (`02-historias-usuario.md:84-86`): multiselección de programa y cohorte en el dashboard; HU-07 CA2 (`:71`): comparación con el año anterior; HU-08 CA1 (`:77`): selectores de dos momentos.
- `openapi.json:689-714` (`/reportes/general`) no tiene parámetros; `:727-738` (`/tendencias`) solo `indicador`; `:801-838` (`/explorador`) acepta un único `programa` y `anio` (y `momento`/`anio` como `string`, frente a `integer` en `:1977-2016`).
- HU-07 CA1 (`:70`) exige tasa formal/informal y *"total de encuestados"*; `KpisResponse` (`openapi.json:2440-2474`) expone `total_egresados`, `tasa_empleabilidad` y `promedio_salarial`, y RF-26 (`01-requerimientos.md:213`) pide un *rango*.
- `matriz-trazabilidad.md:30-31, 35` marca RF-21, RF-22 y RF-26 como *Implementado*, mientras `casos-de-uso.md:39, 45` reconoce *"faltan filtros analíticos"* y que el contrato no representa la comparación de momentos.

### C-13 — Estados de implementación inconsistentes entre documentos
**Severidad:** Media · **Componente:** Trazabilidad

- CU-02 (`casos-de-uso.md:20`): *"faltan bloqueo, permisos, programas y enforcement integral"*; frente a CU-11 (`:80`) *"implementada"*, `matriz-trazabilidad.md:45-46` (RF-36/37 *Implementado*), `03-reglas-negocio.md:3` y `architecture/00-proyecto.md:43`.
- CU-04 (`casos-de-uso.md:33`): *"autorización por rol debe endurecerse"*; frente a `architecture/02-backend.md:54` y `matriz-trazabilidad.md:103` (autorización verificada con pruebas).
- RF-35: `matriz-trazabilidad.md:44` *Parcial* (carga infinita); frente a CU-12 (`casos-de-uso.md:88`), `02-historias-usuario.md:3` y `00-proyecto.md:43` (implementada).
- NLP: `04-hallazgos-figma.md:12` *"no está implementada"*; frente a `matriz-trazabilidad.md:81` y `casos-de-uso.md:69` (verificada).
- Fechas: `matriz-trazabilidad.md:3` *"Verificada: 2026-09-24"* incluye un hecho del 2026-09-25 (`:44`); `casos-de-uso.md:5` fecha la revisión el 2026-09-23 pero cita una validación del 2026-09-25 (`:51`).

### C-14 — Módulo de IA: proveedor externo frente a NLP local, actor y contrato
**Severidad:** Media · **Componente:** Analítica / IA

- HU-11 CA2 (`02-historias-usuario.md:105`): *"vía API de OpenAI o NLP local"*; RNF-07 (`01-requerimientos.md:645`): módulo desacoplado *"mediante una API"*; frente a `casos-de-uso.md:71`: *"no usa servicios externos"*.
- Actor: HU-11 (`02-historias-usuario.md:102`) es el Usuario de Consulta; CU-10 (`casos-de-uso.md:67`) y RF-73 (`01-requerimientos.md:637`) son el coordinador.
- `openapi.json:1443-1468` (`/api/analitica/resumen`) no tiene parámetros ni 403, y `CompetenciaResponse` (`:1855-1872`) no refleja el *"top 10"* de HU-11 CA3 (`:106`).
- RNF-07 (`01-requerimientos.md:640-645`) se clasifica como Restricción pero incluye un requisito funcional (sugerir competencias) sin RF propio en la matriz.

### C-15 — Documento de identidad en URLs frente a la prohibición de registrar documentos en logs
**Severidad:** Media · **Componente:** API / Frontend / Despliegue

- `architecture/05-despliegue.md:30`: *"Logs sin documentos, correos, respuestas abiertas ni tokens completos"*.
- `openapi.json:986-1007` (`/perfil/{documento}`), `:1079-1100` y `:1146-1155` (`/egresados/{documento}`) y los parámetros `q` de búsqueda por cédula (`:877-890`, `:1205-1218`) sitúan el documento en la ruta o query string, que suelen registrar los proxies y servidores de acceso descritos en `05-despliegue.md:13-15`.
- `architecture/01-frontend.md:47`: ruta `/perfil/:cedula` (queda en el historial del navegador).

### C-16 — Inventarios de routers, módulos y rutas desactualizados
**Severidad:** Baja · **Componente:** Documentación de arquitectura

- `architecture/02-backend.md:31-38` omite `/api/publicaciones`, `/api/analitica` y `/api/health` (presentes en `openapi.json:1292-1510`) y describe `/api/usuarios` como *"Listado, creación y eliminación"*, frente a las nueve operaciones de `openapi.json:108-544`.
- `architecture/00-proyecto.md:30-32` no menciona publicaciones, analítica, sedes, cargas ni auditoría; `:40` dice que el coordinador *"crea roles inferiores"* (plural) frente a RN-07 (solo `Usuario_Consulta`).
- `architecture/00-proyecto.md:24-25, 33` (Contracts *"en transición"*, *"tipos manuales"*) frente a `architecture/03-contratos.md:9` y `01-frontend.md:33` (tipos generados; Contracts no importados).
- `architecture/01-frontend.md:37-48` no lista ninguna ruta para la vista Analítica que `matriz-trazabilidad.md:81-82` da por implementada.

### C-17 — Diagrama ER incompleto respecto al esquema SQL
**Severidad:** Baja · **Componente:** Modelo de datos

- `architecture/04-modelo-datos.md:11-102` no incluye `auditoria_cuentas` ni `auditoria_egresados` (`oeupb-schema.sql:36-49, 74-87`), aunque `:116` cita la segunda; `EVENTOS_ELIMINACION_CARGA` aparece en relaciones (`:84, 86`) sin atributos.
- `PUBLICACIONES_GRAFICAS` (`:87-101`) omite `titulo`, `coordinador_correo`, `fecha_creacion` y `retirado_por_id` (`oeupb-schema.sql:158-172`).

### C-18 — Contrato de errores y validaciones declarado de forma incompleta
**Severidad:** Baja · **Componente:** OpenAPI

- `architecture/03-contratos.md:16`: errores como objeto con `detail`; las respuestas 400/401/403/404/409 de `openapi.json` (p. ej. `:37-39, 81-89, 573-581, 667-675`) no declaran esquema.
- Endpoints restringidos por rol no declaran 401/403: `/api/usuarios/*` (`:108-544`), `/api/reportes/*`, `/api/directorio/*`, `/api/publicaciones/*`, `/api/analitica/resumen`.
- RN-19 (`03-reglas-negocio.md:25`) exige `@upb.edu.co`; `UsuarioCreateRequest.correo` (`openapi.json:2853-2856`) no tiene patrón.
- El cuerpo de carga declara `momento`/`anio` sin enumeración ni rango (`:1599-1606`), mientras `DefinicionGrafica` restringe `momento ∈ {0,1,5}` y `anio ∈ [1900, 2200]` (`:1977-2016`).

### C-19 — Priorización, clasificación y dependencias de requisitos incoherentes
**Severidad:** Baja · **Componente:** Catálogo de requisitos

- Todos los RF/RNF están marcados *Alta/Esencial* (p. ej. RF-71 en pausa, `01-requerimientos.md:619-621`), mientras `matriz-trazabilidad.md:94` indica que producto *"debe priorizarlas"* y que RF-71 es *"la única capacidad autorizada como pendiente"* pese a 41 RF parciales o no implementados.
- `01-requerimientos.md:5` define `Requerimiento Ligado` como dependencia funcional directa, pero hay enlaces sin relación funcional: RF-45 → RF-44 (`:412`), RF-43 → RF-42 (`:396`), RF-69 → RF-01 (`:604`), RNF-06 → RF-33 (`:324`), RNF-02/RNF-03 → RF-04 (`:268, 276`).
- RF-08 (`:69`): cargar históricos *"desde bases de datos antiguas"*, frente a RN-05 (`03-reglas-negocio.md:11`), que admite exclusivamente `.xlsx`.

### C-20 — Alcance del retiro de una publicación
**Severidad:** Baja · **Componente:** Publicación

- HU-13 CA5 (`02-historias-usuario.md:130`): al retirar, *"deja de estar disponible para usuarios de otras sedes"*.
- RN-24 (`03-reglas-negocio.md:30`) y CU-11 (`casos-de-uso.md:79`): los usuarios de consulta de la **misma** sede también consumen solo instantáneas publicadas, por lo que el retiro también les afecta; CA5 no lo contempla.

---

## Casos de Borde

### B-01 — Recargas concurrentes de la misma sede, momento y cohorte
**Severidad:** Alta · **Origen:** RF-09 (`01-requerimientos.md:77`), RN-12 (`03-reglas-negocio.md:18`), `oeupb-schema.sql:105`, `openapi.json:562-582`.
Dos cargas simultáneas pueden leer la misma versión vigente y crear dos versiones "vigentes". El índice `ix_cargas_alcance` no es único y el endpoint no documenta 409. No se define bloqueo, versión esperada ni idempotencia ante un mismo `hash_archivo`.

### B-02 — Eliminación de la carga vigente y destino de versiones reemplazadas
**Severidad:** Alta · **Origen:** RN-23 (`03-reglas-negocio.md:29`), `04-modelo-datos.md:111`, `openapi.json:673-675`.
No se define si, al eliminar la versión vigente, la anterior (`reemplazada`) vuelve a ser vigente o la cohorte queda vacía. Tampoco se aclara si las mediciones de cargas reemplazadas se conservan ni cómo las excluyen los reportes (`02-backend.md:64` solo describe la selección por intento). El 409 impide eliminar cargas no vigentes, que quedan permanentemente.

### B-03 — Egresados huérfanos tras eliminar cargas
**Severidad:** Alta · **Origen:** RN-23, `04-modelo-datos.md:125-126`, `oeupb-schema.sql:51-59`.
RN-23 borra carga y mediciones, pero no el egresado. Un egresado sin mediciones ni vínculo `egresados_sedes` deja de ser visible para toda sede, y `Admin_CTIC` no accede a datos (`02-historias-usuario.md:17`). Sus datos personales persisten sin ningún actor que pueda consultarlos o eliminarlos.

### B-04 — Reidentificación por celdas pequeñas en agregados compartidos
**Severidad:** Alta · **Origen:** RN-14 (*"No existe todavía un umbral numérico automático"*, `03-reglas-negocio.md:20`), RN-26 (`:32`), `openapi.json:2337-2360`.
Una gráfica por programa y cohorte con un valor igual a 1 (p. ej. salario o ciudad) identifica a una persona concreta en otra sede. La única salvaguarda es la aprobación manual, que es autodeclarada (C-06).

### B-05 — Cambio de sede de una cuenta con sesión activa
**Severidad:** Alta · **Origen:** `openapi.json:3224-3234` (`UsuarioUpdateRequest.sede_id`), HU-03 CA1 (`02-historias-usuario.md:30`), RN-22 (`03-reglas-negocio.md:28`).
El `sede_id` viaja en el JWT y RN-22 solo menciona *"bloqueo o reducción de permisos"*. No se define si cambiar la sede incrementa `version_autorizacion` ni qué ocurre con los programas asignados de la sede anterior (RN-29), ni con las cargas y publicaciones de un coordinador reasignado.

### B-06 — Alta manual de un documento que ya existe en otra sede
**Severidad:** Alta · **Origen:** `openapi.json:1033-1078`, `04-modelo-datos.md:116, 125-126`, RN-06.
El alta manual crea un vínculo `egresados_sedes`, y ese vínculo hace visible al egresado para la sede. Si el documento ya pertenece a otra sede, un coordinador podría obtener nombre, programa y fecha de grado ajenos, o usar la respuesta como oráculo de existencia. No se define la respuesta (¿409?, ¿vínculo?, ¿custodia?).

### B-07 — Visibilidad entre sedes basada en coincidencia textual de programas
**Severidad:** Media · **Origen:** RN-11 (`03-reglas-negocio.md:17`), RN-29 (`:35`), `04-modelo-datos.md:138`, HU-05 CA1 (`02-historias-usuario.md:50`).
Los programas de un `Usuario_Consulta` solo pueden provenir de su sede, y las publicaciones de otra sede llevan sus propios nombres. La visibilidad entre sedes depende de que los textos coincidan tras la normalización (minúsculas, espacios, tildes no definidas). Nombres equivalentes con distinta grafía impiden la visibilidad, y nombres iguales para programas distintos la conceden; `04-modelo-datos.md:138` reconoce el riesgo sin regla.

### B-08 — Programas asignados que dejan de observarse
**Severidad:** Media · **Origen:** RN-29, RN-23, RN-12.
Si se elimina o reemplaza la carga que originó un programa, o este se renombra, la asignación persiste en `usuarios.programas` (`oeupb-schema.sql:28`) sin estar en la lista válida. No se define si se revoca, se conserva o se valida solo al editar.

### B-09 — Coordinador desactivado o sede sin coordinador
**Severidad:** Media · **Origen:** RN-09 (*"Solo el coordinador propietario"*, `03-reglas-negocio.md:15`), RN-21 (`:27`), `oeupb-schema.sql:172, 178-179`.
No se define quién retira publicaciones o gestiona usuarios de consulta cuando el coordinador propietario se desactiva ni si otro coordinador de la misma sede hereda la propiedad (`retirado_por_id` sugiere un actor distinto). Las FK de `cargas`, `publicaciones_graficas`, `egresados_sedes` y las auditorías hacen que el borrado físico *"cuando la integridad referencial lo permita"* sea en la práctica inalcanzable.

### B-10 — Credenciales: vencimiento, cuentas inactivas y recuperación
**Severidad:** Media · **Origen:** HU-02 CA1 (`02-historias-usuario.md:23`), RN-21, `openapi.json:37-39, 53-107`, `01-frontend.md:48`.
No se define la respuesta del login ante credencial temporal vencida o cuenta desactivada (un mensaje distinto permitiría enumerar cuentas). Solo existe el cambio de contraseña temporal (409 si no aplica): no hay cambio voluntario desde `/mi-perfil` ni recuperación, y no se indica quién reemite la credencial de un `Admin_CTIC`.

### B-11 — Comparación longitudinal entre sedes y suficiencia de pares
**Severidad:** Media · **Origen:** RF-52 (`01-requerimientos.md:469`), HU-08 (`02-historias-usuario.md:75-79`), RN-06, RN-15, RN-26.
Si el M0 de un egresado pertenece a la sede A y su M5 a la sede B, el cruce por documento traspasaría el aislamiento. Las mediciones anónimas quedan fuera de la comparación, y RN-26 exige un mínimo de pares por indicador que ningún documento fija para empleabilidad ni salario.

### B-12 — Año de grado de la carga frente a `fecha_grado` del egresado
**Severidad:** Media · **Origen:** RN-17 (`03-reglas-negocio.md:23`), `04-modelo-datos.md:112`, `oeupb-schema.sql:56, 97, 117`, `openapi.json:1603-1606`.
No se define qué prevalece cuando el año de `fecha_grado` difiere del `anio_grado` de la carga, ni cuando el mismo documento aparece en archivos de cohortes distintas. El año de carga no tiene rango, mientras las publicaciones exigen 1900-2200.

### B-13 — Resultado de cargas fallidas, archivos repetidos y volumen
**Severidad:** Media · **Origen:** RF-09, RN-20, `openapi.json:562-582, 1641-1705`.
El detalle por fila (`ErrorFila`) solo existe en la respuesta 200. Una carga revertida por RN-20 no tiene esquema de error definido (400/422 sin cuerpo). No se definen el tamaño máximo, el límite de filas, el tiempo de procesamiento del endpoint síncrono frente al indicador de progreso de HU-04 CA3, ni el tratamiento de un archivo idéntico ya cargado.

### B-14 — Normalización y formato del documento de identidad
**Severidad:** Media · **Origen:** RN-01, `openapi.json:2099-2104` (egresado: 3-50 caracteres libres) frente a `:2857-2863` (usuario: 6-20 dígitos).
No se define cómo se normalizan puntos, espacios, ceros a la izquierda o documentos alfanuméricos (pasaporte, extranjería). Un mismo egresado puede duplicarse con variantes del documento, y una persona con documento alfanumérico no puede tener cuenta.

### B-15 — Permisos vacíos, `permiso_requerido` y semántica de `ver_publicaciones`
**Severidad:** Media · **Origen:** RN-28 (`03-reglas-negocio.md:34`), `openapi.json:2899-2926, 2703-2706`, `oeupb-schema.sql:163`.
Un `Usuario_Consulta` puede crearse sin permisos ni programas. `permiso_requerido` no se envía en `PublicacionCreate` y su derivación a partir de `definicion.origen` no está documentada, y no se define si `ver_publicaciones` es requisito adicional o alternativo a los demás. Una gráfica sin filtro de programa (`definicion.programa = null`) debe declarar al menos un programa (`minItems: 1`), sin regla sobre cuál.

### B-16 — Mediciones anónimas en agregados "aprobados"
**Severidad:** Media · **Origen:** RN-15 (`03-reglas-negocio.md:21`), RN-25 (`:31`), `02-backend.md:64`, `04-modelo-datos.md:136`.
RN-15 limita las anónimas a *"agregados aprobados"* sin definir "aprobado" (¿aprobación de privacidad de RN-14?). Sin embargo, los reportes privados las incluyen. Además, las respuestas anónimas repetidas de una misma persona no pueden deduplicarse, y el total mezcla egresados identificados (último intento) con anónimos (todos), lo que choca con la etiqueta `total_egresados`.

### B-17 — Valores fuera de la taxonomía laboral
**Severidad:** Baja · **Origen:** RN-16 (`03-reglas-negocio.md:22`), RF-17/RF-23/RF-61, HU-08 CA2.
No se define el tratamiento de respuestas vacías o no mapeables a `empleado|independiente|estudiante|sin_empleo`, ni la fórmula de "tasa de empleo" (¿incluye independientes?). RF-17 exige actualizar el estado, pero `EgresadoManualUpdate` (`openapi.json:2156-2219`) no tiene ese campo.

### B-18 — Criterios de las alertas descriptivas
**Severidad:** Baja · **Origen:** RF-73 (`01-requerimientos.md:637`), `openapi.json:1530-1567`, RN-26.
No se definen los "patrones negativos", los umbrales, el catálogo de `severidad` (cadena libre) ni la muestra mínima. Una alerta sobre un programa con pocas respuestas puede ser engañosa o reidentificadora.

### B-19 — Exportaciones fuera del catálogo de permisos
**Severidad:** Baja · **Origen:** RN-28, CU-09 (`casos-de-uso.md:59-63`), RF-70, `openapi.json:1191-1261`.
No se define si un `Usuario_Consulta` puede exportar como PNG las instantáneas de `/publicaciones`. La exportación del directorio (con datos personales) no tiene límite de filas, a diferencia del listado (máx. 100), ni exigencia de auditoría.

### B-20 — Requisitos no funcionales no verificables
**Severidad:** Baja · **Origen:** RNF-01, RNF-03, RNF-04, RNF-06 (`01-requerimientos.md:253, 277, 301, 325`), RNF-02 (`:269`).
Faltan métricas de aceptación ("fácil", "sin ponerse lento", "miles de encuestas"), y RNF-02 depende de una estrategia de pruebas ajena al alcance.

### B-21 — Reutilización de correo de cuentas desactivadas
**Severidad:** Baja · **Origen:** RN-21, `oeupb-schema.sql:30` (`UNIQUE correo`), RN-19.
Una cuenta desactivada bloquea su correo para una cuenta nueva (p. ej. cambio de rol o de sede). No se define si procede reactivar y modificar, ni la sensibilidad a mayúsculas en la unicidad.

---

## Recomendaciones de Mitigación

### P0 — Privacidad y aislamiento (bloqueantes)

- **R-01 (C-02, C-03, B-04):** Hacer que el backend recalcule las métricas de la instantánea a partir de `definicion` y de la sede del JWT, sin aceptar `metricas` ni `programas` del cliente. Restringir etiquetas a valores del catálogo RN-31 y deshabilitar la publicación desde el Explorador hasta aplicar RN-31. Definir un umbral mínimo de celdas por indicador (RN-26) y bloquear o agrupar valores por debajo del umbral.
- **R-02 (C-06):** Decidir quién aprueba la privacidad (el mismo coordinador con confirmación explícita o un segundo actor). Si es un segundo actor, añadir el estado `pendiente_aprobacion` al CHECK de `publicaciones_graficas` y un endpoint de aprobación. Alinear RN-14, HU-13 CA6 y `04-modelo-datos.md:134`.
- **R-03 (C-01):** Publicar una matriz única de operaciones por rol y permiso que indique, para `Usuario_Consulta`, si `ver_reporte_general`, `ver_tendencias` y `ver_explorador` habilitan cálculo bajo demanda o solo filtran instantáneas. Ajustar HU-07/08/09/11 y CU-05/06/07 o RN-24, según la decisión.
- **R-04 (C-04, C-07, B-06, B-11):** Definir la política de precedencia de RN-01 por campo: qué sede puede escribir cada atributo global y cómo se registra el conflicto. Designar el actor de "custodia institucional" (rol, permisos y endpoint) o eliminar esa referencia. Especificar la respuesta del alta manual ante un documento existente en otra sede, que no debe revelar su existencia ni sus datos, y la regla de cruce longitudinal multisede.
- **R-05 (C-15):** Sustituir el documento en rutas y query strings por un identificador opaco, o por POST con cuerpo para la búsqueda. Añadir el enmascaramiento de rutas en logs a los requisitos de `05-despliegue.md`.

### P1 — Integridad de cargas y cuentas

- **R-06 (B-01, B-02, B-13):** Especificar el control de concurrencia de la recarga (restricción única de carga vigente por sede/momento/cohorte o bloqueo optimista) con respuesta 409. Definir la versión vigente tras eliminar la actual, el destino de las mediciones reemplazadas, la idempotencia por `hash_archivo`, los límites de tamaño y filas, y el esquema de error de una carga revertida.
- **R-07 (B-03, B-08):** Definir la limpieza o anonimización de egresados sin mediciones ni vínculos y de las asignaciones de programas que dejan de ser válidas, con el actor responsable.
- **R-08 (C-08, C-09, B-12, B-14):** Decidir si las encuestas manuales existen. Si existen, añadir el endpoint y relajar u orientar `mediciones.carga_id` (p. ej. mediante una carga manual). Enunciar en el alcance la regla de ADR-006 (duplicados intra-archivo y doble titulación) y clasificarla como advertencia no bloqueante compatible con RN-20. Explicar el origen de los intentos múltiples de RN-25. Normalizar el documento y alinear sus validaciones. Definir la precedencia entre `fecha_grado` y `anio_grado`.
- **R-09 (C-05, B-10, B-21):** Unificar RN-18, HU-01 y HU-12 con el comportamiento de `02-backend.md:47`: modo por ambiente, vencimiento, reemisión y canal de entrega de la credencial aleatoria. Definir las respuestas del login ante una credencial vencida o una cuenta inactiva sin permitir enumerar cuentas, el cambio voluntario y la recuperación de contraseña, y el tratamiento del correo de cuentas desactivadas.
- **R-10 (C-10, C-11, B-05, B-09, B-15):** En el contrato, derivar `rol` del actor, exigir `sede_id` para roles no CTIC y hacer `permisos`/`programas` obligatorios para Consulta. Añadir un CHECK de sede por rol en SQL. Consolidar desactivar, eliminar y bloquear en una sola operación. Documentar quién ejecuta el borrado permanente. Declarar que el cambio de sede incrementa `version_autorizacion`. Definir la herencia de propiedad al desactivar un coordinador, la derivación de `permiso_requerido` y la semántica de `ver_publicaciones`.

### P2 — Contratos y analítica

- **R-11 (C-12, B-16, B-17):** Incorporar al contrato de reportes los filtros de programa (múltiple), cohorte y par de momentos. Añadir a `KpisResponse` la tasa formal/informal y el rango salarial, y renombrar o definir `total_egresados`. Documentar el tratamiento de las mediciones anónimas y de los valores fuera de la taxonomía laboral. Revertir a *Parcial* los RF de la matriz que dependan de ello (RF-21, RF-22, RF-26).
- **R-12 (C-14, B-18):** Fijar el proveedor de NLP (local) en HU-11 y RNF-07, el actor de CU-10 y HU-11, el contrato de `/api/analitica/resumen` (filtros, 403, top-N) y los criterios de alerta (umbral, severidad enumerada, muestra mínima).
- **R-13 (C-18, B-19):** Declarar los esquemas de error (`detail`) y los códigos 401/403/404/409 por endpoint, el patrón de correo institucional y los rangos de `momento`/`anio` en la carga y el Explorador. Documentar la política de exportación para Consulta y los límites y auditoría de la exportación del directorio.
- **R-14 (C-20, B-07):** Reformular HU-13 CA5 para incluir a los usuarios de consulta de la propia sede. Definir el catálogo normalizado de programas o la tabla de equivalencias entre sedes que regula la visibilidad cruzada.

### P3 — Calidad documental

- **R-15 (C-13, C-16, C-17):** Reconciliar los estados de CU-02, CU-04, CU-06, CU-12, RF-35 y NLP en una sola fuente (la matriz) y actualizar sus fechas de verificación. Completar los inventarios de routers, módulos y rutas en `00-proyecto.md`, `01-frontend.md` y `02-backend.md`, y el diagrama ER con las tablas y columnas del SQL.
- **R-16 (C-19, B-20):** Asignar prioridades reales a RF/RNF (RF-71 en pausa no puede ser *Alta/Esencial*), corregir los `Requerimiento Ligado` sin relación funcional, separar el componente funcional de RNF-07, aclarar el canal de importación de RF-08 frente a RN-05 y añadir métricas verificables a los RNF.

---

## Verificación y resolución

**Fecha:** 2026-09-25. Los hallazgos anteriores se contrastaron con el código, los ADR (excluidos del alcance del auditor) y el objetivo del proyecto: centralizar las encuestas M0/M1/M5 con aislamiento estricto por sede y compartir entre sedes solo agregados. Producto tomó cuatro decisiones: corregir documentación y código, recalcular las publicaciones en backend con k = 5 (ADR-015), mantener la autoaprobación explícita y sacar del alcance la custodia institucional y las encuestas manuales (ADR-014).

Veredictos: **Confirmado** (el problema existía), **Parcial** (existía, pero el informe lo sobredimensionó), **Documental** (el código ya cumplía; solo el texto estaba desalineado).

| ID | Veredicto | Resolución |
|---|---|---|
| C-01 | Documental | El código ya restringía reportes, tendencias, explorador y analítica a `Coordinador_Sede`. HU-07/08/09/11 y CU-05/06/07 se reescribieron según RN-24; RN-28 define los permisos como filtros por origen de las publicaciones. |
| C-02 | Confirmado | Corregido en código (ADR-015): recálculo en backend, audiencia derivada y campos del cliente ignorados. |
| C-03 | Confirmado | Corregido en código: catálogo RN-31 en init, consulta (422) y publicación (EXP-02 archivado). |
| C-04 | Parcial | La carga no hacía UPSERT de nombre ni programa; solo actualizaba `fecha_grado`. ADR-014 fija la precedencia y ahora protege los egresados con corrección manual auditada. |
| C-05 | Documental | ADR-013 ya lo resolvía. RN-18, HU-01 y HU-12 alineados. |
| C-06 | Confirmado | Decisión: autoaprobación explícita del coordinador propietario (ADR-015). Se reescribieron RN-14, HU-13 CA6 y el texto de confirmación en la interfaz. |
| C-07 | Confirmado | Fuera del alcance (ADR-014). Los mensajes 409 ya no remiten a la custodia. |
| C-08 | Confirmado | Encuestas manuales fuera del alcance (ADR-014). `intento` siempre vale 1 y se conserva por compatibilidad. |
| C-09 | Documental | ADR-006 aplica: la doble titulación es una advertencia en el mensaje de éxito, no un error. Se actualizaron RN-01 y 04-hallazgos-figma. |
| C-10 | Parcial | El backend valida el rol contra el actor y exige sede. Falta el CHECK en SQL (DB-03). |
| C-11 | Parcial | "Bloquear" es desactivar; el borrado físico exige cuenta inactiva, motivo y auditoría. El alias duplicado queda en API-02. |
| C-12 | Confirmado | RF-21, RF-22 y RF-26 pasan a Parcial; implementación en ANA-01. |
| C-13 | Confirmado | Estados y fechas reconciliados en casos de uso, matriz y hallazgos de Figma. |
| C-14 | Documental | El NLP es local (`nlp_service.py`) y el actor es el coordinador; se corrigieron HU-11 y RNF-07. |
| C-15 | Confirmado | Corregido: el log HTTP enmascara el documento y la imagen Docker desactiva el access log de Uvicorn. Se agregó el requisito al proxy en 05-despliegue. |
| C-16 | Confirmado | Inventarios de 00-proyecto, 01-frontend y 02-backend completados. |
| C-17 | Confirmado | Pendiente en DOC-03. |
| C-18 | Parcial | Rango de año y momento validados en la carga y el explorador; esquemas de error y patrón de correo en API-02. |
| C-19 | Parcial | RF-71 reclasificado como Baja/en pausa y RF-08 aclarado frente a RN-05; el resto en DOC-03. |
| C-20 | Documental | HU-13 CA5 ahora incluye a los usuarios de consulta de la propia sede. |
| B-01 | Confirmado | Corregido: bloqueo `FOR UPDATE` por sede y 409 para un archivo idéntico. |
| B-02 | Documental | Comportamiento definido en RN-12 y RN-23: la versión reemplazada no conserva mediciones ni se reactiva, y solo se elimina la vigente. |
| B-03 | Confirmado, con defecto adicional | La limpieza sí existía, pero borraba también los egresados manuales de todas las sedes (y en MySQL fallaba por la FK). Corregido y con prueba. |
| B-04 | Confirmado | Corregido: umbral k = 5 (ADR-015). |
| B-05 | Parcial | El cambio de sede ya incrementaba `version_autorizacion`. Las publicaciones del coordinador reasignado pueden retirarse por otro coordinador de la sede. |
| B-06 | Parcial | El alta responde 409 sin devolver datos; solo revela que el documento existe, riesgo aceptado en ADR-014. |
| B-07, B-08 | Confirmado | PRG-01. |
| B-09 | Confirmado | Corregido para el retiro de publicaciones. El borrado físico con relaciones sigue respondiendo 409 por diseño (RN-21). |
| B-10 | Parcial | El login no permite enumerar cuentas: la credencial vencida solo se informa si la contraseña es correcta. La recuperación la hace el administrador (ADR-013). |
| B-11 | Documental | Las consultas filtran por la sede del JWT, por lo que no hay cruce entre sedes; HU-08 CA3 lo explicita. El mínimo de pares queda en ANA-01. |
| B-12 | Parcial | Rango 1900-2200 validado. Prevalece `anio_grado` de la carga para la cohorte (RN-17) y `fecha_grado` más reciente para la identidad (ADR-014). |
| B-13, B-14 | Confirmado | Idempotencia resuelta; normalización, límites y esquema de error en ETL-01. |
| B-15 | Documental | `permiso_requerido` se deriva del origen y los permisos son acumulativos (RN-28); la audiencia la calcula el backend. |
| B-16 | Parcial | RN-15 define dónde participan las anónimas. El total del KPI cuenta egresados identificados. |
| B-17 | Confirmado | ANA-01. |
| B-18 | Confirmado | ANA-02. |
| B-19 | Documental | Consulta no exporta (RN-28, CU-09). La exportación del directorio es exclusiva del coordinador de la sede. |
| B-20 | Confirmado | DOC-03. |
| B-21 | Documental | Se reactiva y edita la cuenta existente; el correo se normaliza en minúsculas al crearla. |

Verificación: 37 pruebas de backend y 15 de frontend en verde, OpenAPI y tipos regenerados, y validadores de contratos, documentación y arquitectura sin errores.
