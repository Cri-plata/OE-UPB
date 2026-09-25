# Auditoría cruzada de requerimientos, especificaciones y arquitectura de OE UPB

**Fecha de corte:** 2026-09-23  
**Alcance:** `requirements/`, `specs/` y `architecture/`  
**Método:** comparación textual cruzada de los 15 artefactos contenidos en los tres directorios.  
**Criterio de evidencia:** el informe no atribuye comportamientos que no estén expresamente documentados. Las menciones a código, backlog, ADR, pruebas, mockups o design system se tratan como referencias externas y no como evidencia verificada dentro de este alcance.

## Resumen Ejecutivo

La documentación presenta una intención normativa consistente en sus principios centrales: aislamiento de datos fuente por sede, autorización en backend, administración jerárquica de cuentas, uso de un rol técnico de consulta y publicación exclusiva de resultados agregados. También distingue explícitamente entre el sistema actual y el modelo objetivo pendiente, lo que evita interpretar varias brechas conocidas como capacidades ya implementadas.

No obstante, los tres niveles auditados todavía no forman una especificación implementable y verificable de extremo a extremo. Se identificaron **22 contradicciones, inconsistencias o brechas contractuales** y **35 casos de borde sin resolución explícita**. Cinco riesgos concentran la mayor criticidad:

1. Las invariantes de sede, momento, año y procedencia no están materializadas de forma consistente en el esquema SQL canónico.
2. El contrato OpenAPI vigente no representa la política objetivo de roles, cuentas, permisos, programas ni publicaciones y, además, declara un flujo OAuth2 incompatible con el payload real de login.
3. Los contratos de reportes no permiten cumplir los filtros, comparaciones y reglas de audiencia descritos en las historias de usuario; varias respuestas están definidas como objetos sin esquema.
4. La edición manual, la eliminación y la identidad global del egresado carecen de un modelo suficiente de propiedad, precedencia y auditoría.
5. La publicación versionada se declara como instantánea, pero no se define qué queda congelado, cómo se actualiza, qué audiencia conserva ni cómo se evita la reidentificación en grupos pequeños.

La documentación reconoce expresamente varias de estas brechas en `architecture/02-backend.md`, `architecture/04-modelo-datos.md` y `requirements/matriz-trazabilidad.md`. Ese reconocimiento reduce el riesgo de una falsa afirmación de implementación, pero no reemplaza las decisiones, contratos y criterios de aceptación necesarios para construir y probar la solución objetivo.

### Seguimiento de correcciones — 2026-09-23

- **C-03 corregido:** la autenticación protegida declara HTTP Bearer en código y OpenAPI, compatible con el login JSON existente.
- **C-07 corregido parcialmente:** `LoginResponse.usuario` quedó tipado con identidad, rol, sede y estado de cambio de contraseña; permisos y programas continúan pendientes del modelo objetivo.
- **C-10 corregido normativamente:** HU-09 exige recalcular agregados en backend y limita el frontend a renderizar métricas ya autorizadas.
- **C-13 mitigado:** una carga exitosa retorna ID, versión, estado y cantidad de registros; la política de archivos parcialmente válidos sigue pendiente.
- **C-14 corregido:** el año del historial es obligatorio, en concordancia con `cargas.anio_grado`.
- **C-18 corregido normativamente:** la publicación conserva métricas inmutables; su definición solo sirve para renderizado y auditoría, y una actualización crea otra versión con nueva aprobación.
- **C-19 mitigado:** RN-10/RN-11 distinguen explícitamente el acceso general del coordinador y el alcance granular de `Usuario_Consulta`; falta decidir si este último accede a gráficas privadas de su sede.
- **C-20 y C-22 corregidos:** los casos de uso analíticos se marcan parciales y el documento de Figma diferencia representación visual de implementación.
- **C-05 resuelto normativamente:** la operación ordinaria desactiva cuentas; el borrado físico queda como proceso excepcional, restringido y auditado. Estado y versión de autorización siguen pendientes de implementación.
- **C-15 resuelto normativamente:** la eliminación física de carga y mediciones será transaccional y conservará primero un evento inmutable en una entidad separada.
- **C-19 resuelto:** `Usuario_Consulta` solo accede a instantáneas publicadas compatibles; nunca a gráficas privadas de su sede.
- **E-04/E-05 decididos:** la cédula será la credencial temporal objetivo y los cambios de permisos tendrán vigencia inmediata. El mecanismo de cédula se reconoce como riesgo transitorio y se implementará después de RBAC.
- **E-12/E-20/E-25/E-28 decididos:** carga todo-o-nada, múltiples mediciones válidas sujetas al diccionario de indicadores, suficiencia definida por indicador y dashboard privado sin selector de sede.
- Las decisiones 1 a 25 están consolidadas en [`03-formulario-decisiones.md`](03-formulario-decisiones.md). El catálogo inicial contiene cuatro permisos por módulo, los programas se derivan de cargas visibles de la sede y las etiquetas rector/profesor/administrativo no conceden privilegios implícitos.

### Distribución de hallazgos

| Severidad | Cantidad | Enfoque principal |
|---|---:|---|
| Crítica | 5 | autorización, aislamiento por sede, contratos de cuentas y publicación |
| Alta | 10 | integridad, trazabilidad, reportes, edición y ciclo de vida |
| Media | 7 | semántica, errores, estados documentales y contrato incompleto |

## Contradicciones Identificadas

### C-01 — Invariantes obligatorias frente a columnas anulables

**Severidad:** Crítica. **Tipo:** reglas de negocio–modelo de datos.

RN-02 limita `momento` a 0, 1 o 5 y RN-06 exige que toda medición pertenezca al alcance de una sede (`requirements/03-reglas-negocio.md:8,12`). CU-03 afirma que las mediciones quedan asociadas a la sede del token (`requirements/casos-de-uso.md:22-27`). La arquitectura solo justifica nulabilidad histórica para `carga_id` y `cargas.usuario_id`, además de permitir `egresado_documento` nulo para anónimos (`architecture/04-modelo-datos.md:33-40,61-68`). Sin embargo, el esquema canónico admite `NULL` en `mediciones.momento`, `mediciones.anio`, `mediciones.sede_id` y `mediciones.respuestas`, y no incluye `CHECK` para el momento ni FK para sede (`specs/db/oeupb-schema.sql:51-58,70-74`). El esquema permite estados que las reglas obligatorias no contemplan.

### C-02 — El esquema no puede demostrar la política de edición manual

**Severidad:** Alta. **Tipo:** regla–datos.

RN-13 exige proteger correcciones manuales frente a cargas posteriores y auditar actor, fecha, procedencia y campos modificados (`requirements/03-reglas-negocio.md:19`). HU-05 CA4 y HU-06 CA5 convierten esa regla en criterio de aceptación (`requirements/02-historias-usuario.md:46-61`). El esquema solo contiene `egresados`, `mediciones`, `cargas` y `usuarios`; no registra revisiones por campo, procedencia manual, confirmación de conflicto ni custodio (`specs/db/oeupb-schema.sql:5-68`). Además, `architecture/04-modelo-datos.md:68` reserva `carga_id = NULL` para datos históricos sin procedencia recuperable, por lo que tampoco existe una representación inequívoca para una encuesta manual nueva.

### C-03 — Login JSON declarado como flujo OAuth2 Password

**Severidad:** Alta. **Tipo:** inconsistencia interna de OpenAPI.

`POST /api/auth/login` exige un cuerpo JSON `LoginRequest` con `correoInstitucional` y `contrasena` (`specs/api/openapi.json:9-25,900-916`). El esquema de seguridad, en cambio, declara un flujo OAuth2 `password` cuyo `tokenUrl` es ese mismo endpoint (`specs/api/openapi.json:1124-1133`). El flujo Password de OpenAPI presupone credenciales con el formato estándar del flujo, mientras el endpoint canónico publica un JSON propio. Las herramientas cliente no pueden inferir correctamente cómo obtener el token.

### C-04 — El contrato de creación permite decidir el rol y omitir la sede

**Severidad:** Crítica. **Tipo:** RBAC–API.

HU-01 establece que CTIC crea exclusivamente coordinadores, con sede obligatoria y rol fijo `Coordinador_Sede`; HU-12 establece que el coordinador crea exclusivamente `Usuario_Consulta` de su sede, con permisos y programas (`requirements/02-historias-usuario.md:11-18,111-118`). RN-07 y RN-08 hacen obligatorias esas restricciones en backend (`requirements/03-reglas-negocio.md:13-14`). `UsuarioCreateRequest` expone `rol` como cadena libre requerida, deja `sede` opcional y no representa permisos ni programas (`specs/api/openapi.json:950-982`). El contrato canónico permite solicitudes incompatibles con la política y no expresa las solicitudes válidas completas.

### C-05 — Ciclo de vida de cuentas sin estado ni operaciones equivalentes

**Severidad:** Crítica. **Tipo:** requisito–API/datos.

CU-01 presupone una cuenta existente y activa; CU-02, HU-01 y HU-12 permiten crear, modificar, bloquear y eliminar dentro del alcance jerárquico (`requirements/casos-de-uso.md:7-20`; `requirements/02-historias-usuario.md:11-18,111-118`). OpenAPI solo lista, crea y elimina usuarios (`specs/api/openapi.json:105-221`), y la tabla `usuarios` no contiene estado, fecha de bloqueo, baja lógica o versión (`specs/db/oeupb-schema.sql:5-17`). No existe semántica documentada para distinguir cuenta activa, bloqueada y eliminada ni para revocar sus sesiones.

### C-06 — El rol objetivo no está cerrado en API ni SQL

**Severidad:** Alta. **Tipo:** autorización–modelo.

RN-03 y RN-07 normalizan los roles técnicos a `Admin_CTIC`, `Coordinador_Sede` y `Usuario_Consulta` (`requirements/03-reglas-negocio.md:9,13`). La arquitectura reconoce que `Directivo` y `Profesor` son heredados y que `Usuario_Consulta` aún no existe en el modelo actual (`architecture/00-proyecto.md:35-45`). Tanto OpenAPI como SQL aceptan cualquier cadena en `rol`, sin enum ni restricción (`specs/api/openapi.json:960-963`; `specs/db/oeupb-schema.sql:10`). Esta brecha está declarada, pero el contrato canónico no permite validar la política objetivo ni impedir roles fuera de catálogo.

### C-07 — La respuesta de login no garantiza los atributos exigidos

**Severidad:** Alta. **Tipo:** historia de usuario–contrato.

HU-02 CA2 exige que la sesión disponga de rol y `sede_id`, y que permisos y programas se obtengan o validen en backend (`requirements/02-historias-usuario.md:20-25`). `LoginResponse.usuario` es un objeto abierto sin propiedades definidas (`specs/api/openapi.json:918-935`). El contrato no garantiza rol, sede, estado de cambio de contraseña ni un mecanismo documentado para recuperar permisos/programas.

### C-08 — Operaciones de usuarios no documentan denegaciones de autorización

**Severidad:** Crítica. **Tipo:** seguridad–contrato.

RN-07 exige denegar la administración fuera de jerarquía y sede (`requirements/03-reglas-negocio.md:13`). Los endpoints de usuarios solo documentan 200 y, cuando hay cuerpo o parámetro, 422; no declaran 401, 403, 404 ni 409 (`specs/api/openapi.json:105-221`). El uso de Bearer acredita autenticación, pero el contrato no especifica la autorización que distingue CTIC, coordinadores y usuarios de consulta.

### C-09 — Los reportes no pueden expresar los filtros y comparaciones aprobados

**Severidad:** Alta. **Tipo:** requisitos–API.

HU-08 exige dos momentos independientes para comparar M1 y M5; HU-09 exige multiselección de programa y cohorte (`requirements/02-historias-usuario.md:73-85`). `GET /api/reportes/general` no recibe filtros; `/tendencias` solo recibe `indicador`; `/explorador` admite un único `momento`, `programa` y `anio`, todos como cadenas (`specs/api/openapi.json:358-524`). El contrato vigente no puede representar los criterios de aceptación descritos.

### C-10 — Recalcular en frontend es ambiguo frente a la frontera de autorización

**Severidad:** Alta. **Tipo:** privacidad–arquitectura.

HU-09 CA2 permite recalcular gráficas en el frontend usando “datos filtrados en memoria” (`requirements/02-historias-usuario.md:80-85`). RN-06, RN-09 y la arquitectura limitan el intercambio entre sedes a gráficas y métricas agregadas, y asignan al backend el cálculo de audiencia (`requirements/03-reglas-negocio.md:12,15`; `architecture/00-proyecto.md:55-64`). No se define si los datos en memoria son filas, respuestas o agregados autorizados. Interpretado como datos fuente, el criterio contradice la frontera de privacidad; interpretado como agregados, no se especifican las operaciones válidas.

### C-11 — Respuestas 200 vacías impiden validar capacidades declaradas

**Severidad:** Alta. **Tipo:** estrategia de contratos.

La arquitectura declara OpenAPI como fuente canónica y exige revisar breaking changes (`architecture/03-contratos.md:5-27`). Sin embargo, tendencias, inicialización y consulta del explorador, tabla y perfil del directorio tienen respuestas 200 con esquema `{}` (`specs/api/openapi.json:408-415,437-444,504-511,595-602,664-671`). CU-05 a CU-08 y RF-13 a RF-30 requieren estructuras y resultados concretos (`requirements/casos-de-uso.md:35-57`; `requirements/01-requerimientos.md:103-245`). Un esquema abierto no permite comprobar consumidores, privacidad de campos ni compatibilidad.

### C-12 — `KpisResponse` no cubre el dashboard descrito

**Severidad:** Media. **Tipo:** funcional–contrato.

HU-07 exige total, empleo formal e informal y salario promedio, además de comparación con el año anterior (`requirements/02-historias-usuario.md:66-71`). `KpisResponse` solo define `total_egresados`, una `tasa_empleabilidad`, un `promedio_salarial`, distribución de programas y satisfacción; no representa formal/informal por separado ni comparación temporal (`specs/api/openapi.json:865-898`). RF-26, además, habla de “rango de salario promedio” (`requirements/01-requerimientos.md:207-213`), expresión cuya salida tampoco está definida.

### C-13 — La carga auditable no está expuesta en su respuesta

**Severidad:** Alta. **Tipo:** requisito–API.

RF-07 exige identificador, fecha/hora, actor, sede, momento, año, archivo, estado, versión, resultado y mediciones afectadas; HU-04 CA4 exige que cada archivo reciba identificador (`requirements/01-requerimientos.md:55-61`; `requirements/02-historias-usuario.md:38-44`). El modelo `cargas` contiene parte importante de esa información (`specs/db/oeupb-schema.sql:29-49`), pero `CargaResponse` solo garantiza `mensaje` y una lista de errores (`specs/api/openapi.json:749-768`). El cliente no tiene un identificador contractual ni un resumen estructurado que permita trazabilidad posterior.

### C-14 — El historial admite un año nulo que la carga y SQL exigen

**Severidad:** Media. **Tipo:** inconsistencia API–datos.

La carga requiere `anio`, descrito como año de grado o cohorte (`specs/api/openapi.json:705-729`), y `cargas.anio_grado` es `NOT NULL` (`specs/db/oeupb-schema.sql:29-42`). No obstante, `HistorialCargaItem.anio` admite `null` y ni siquiera figura entre sus campos requeridos (`specs/api/openapi.json:806-863`). No se explica qué tipo de carga vigente carecería de año.

### C-15 — Eliminar una carga y conservar el evento no tiene soporte canónico

**Severidad:** Alta. **Tipo:** caso de uso–datos.

CU-04 exige retirar únicamente las mediciones de la carga y sede, “conservando la trazabilidad del evento” (`requirements/casos-de-uso.md:29-33`). La API usa `DELETE /api/carga/archivo/{carga_id}` (`specs/api/openapi.json:302-356`), mientras el esquema no contiene marca de eliminación, evento de auditoría ni regla `ON DELETE` para las FK desde `mediciones` y desde cargas reemplazantes (`specs/db/oeupb-schema.sql:47-48,62-67`). Una eliminación física puede fallar por integridad o destruir la entidad que debía conservar la traza; una baja lógica no está especificada.

### C-16 — CRUD manual de egresados sin operaciones canónicas

**Severidad:** Alta. **Tipo:** cobertura funcional.

RF-10 a RF-12 y HU-06 exigen crear, corregir y borrar egresados, además de registrar encuestas manuales (`requirements/01-requerimientos.md:79-101`; `requirements/02-historias-usuario.md:54-61`). OpenAPI solo lista el directorio, programas y un perfil (`specs/api/openapi.json:526-684`). No existen contratos de creación, edición, borrado, registro manual de medición ni auditoría del cambio.

### C-17 — Publicación, permisos y programas carecen de modelo y API

**Severidad:** Crítica. **Tipo:** arquitectura objetivo–especificación.

RF-35 a RF-37, RN-08 a RN-11, HU-12/HU-13 y CU-11/CU-12 definen asignación de programas y permisos, publicación, retiro, versionado y cálculo de audiencia (`requirements/01-requerimientos.md:327-349`; `requirements/03-reglas-negocio.md:14-17`; `requirements/casos-de-uso.md:73-87`). La arquitectura enumera la extensión pendiente (`architecture/04-modelo-datos.md:81-90`) y el backend confirma que no existen endpoints ni entidades (`architecture/02-backend.md:49-71`). Ni SQL ni OpenAPI representan estas capacidades. Es una brecha reconocida, pero bloquea la verificabilidad de toda la política aprobada.

### C-18 — Instantánea publicada frente a reproducción no delimitada

**Severidad:** Media. **Tipo:** semántica de publicación.

RN-14 define una publicación como “instantánea versionada” y HU-13 indica que una actualización produce una versión nueva (`requirements/03-reglas-negocio.md:20`; `requirements/02-historias-usuario.md:120-128`). A la vez, HU-13 CA2 y la arquitectura hablan de conservar definición, filtros y métricas “necesarias para reproducir” o de “materializar o reproducir” la gráfica (`requirements/02-historias-usuario.md:124`; `architecture/02-backend.md:61-69`). No se determina si una consulta reproduce valores congelados, recalcula sobre datos actuales o solo reconstruye la presentación de métricas congeladas. Las alternativas producen resultados y obligaciones de auditoría diferentes.

### C-19 — Audiencia de coordinadores y usuarios no está completamente discriminada

**Severidad:** Media. **Tipo:** autorización–ambigüedad.

RN-10 y la matriz indican que todo coordinador ve todas las publicaciones de otras sedes, mientras el usuario de consulta depende de alcance y programas (`requirements/03-reglas-negocio.md:16`; `requirements/matriz-trazabilidad.md:40-49`). RN-11 afirma de manera general que la visibilidad se deriva de publicación, sede, programas y permisos “del usuario” (`requirements/03-reglas-negocio.md:17`). No se explicita si coordinadores omiten siempre programas/permisos, si requieren un permiso implícito o si el término usuario excluye coordinadores. Tampoco se define con precisión si `Usuario_Consulta` puede ver gráficas privadas de su propia sede: la matriz lo permite “según permisos y programas”, pero RN-09/RN-10 solo formalizan el intercambio mediante publicación.

### C-20 — Estados de implementación sobreestimados en casos de uso

**Severidad:** Media. **Tipo:** gobernanza documental.

CU-05, CU-06 y CU-07 se etiquetan como “existente” (`requirements/casos-de-uso.md:35-51`). La matriz califica los mismos rangos como parciales o no verificados (`requirements/matriz-trazabilidad.md:20,27-28`), y la arquitectura confirma que no existen `Usuario_Consulta`, permisos ni publicaciones (`architecture/02-backend.md:49-57`). Los endpoints base existen, pero los actores y filtros descritos por los casos de uso no. El estado debería distinguir “endpoint existente” de “caso de uso completo”.

### C-21 — Contrato de errores incompleto respecto de los flujos descritos

**Severidad:** Media. **Tipo:** API–experiencia.

HU-02 exige un error de credenciales indistinto (`requirements/02-historias-usuario.md:20-25`), pero login solo documenta 200 y 422 (`specs/api/openapi.json:26-47`). Reportes y directorio no documentan 401/403/404 según corresponda (`specs/api/openapi.json:358-684`). `architecture/03-contratos.md:16` establece que los errores usan `detail`, pero las respuestas 400/401/403/404/409 declaradas en carga y cambio de contraseña no incluyen un esquema de cuerpo. El contrato no permite implementar de manera uniforme los estados de error.

### C-22 — Evidencia histórica de Figma mezcla cumplimiento visual con capacidad funcional

**Severidad:** Media. **Tipo:** trazabilidad de diseño.

El documento se identifica como evidencia histórica (`requirements/04-hallazgos-figma.md:1-5`), pero afirma que tendencias M1/M5 “cumple” y que IA tiene una “excelente representación” (`requirements/04-hallazgos-figma.md:7-14`). OpenAPI no ofrece comparación M1/M5 y la matriz marca IA como no implementada (`specs/api/openapi.json:384-429`; `requirements/matriz-trazabilidad.md:28-31,36`). Un mockup puede cumplir una intención visual sin demostrar el flujo o la implementación; la palabra “cumple” no delimita esa diferencia.

## Casos de Borde

### Identidad, autenticación y cuentas

**E-01 — Normalización del correo institucional.** No se define dominio permitido, uso de mayúsculas, espacios, alias, cambio de correo ni colisiones después de normalizar (`requirements/02-historias-usuario.md:14,21-24`; `specs/db/oeupb-schema.sql:8,14`).

**E-02 — Política de contraseña personal.** El endpoint documenta un error 400 cuando la contraseña no cumple la política, pero ni OpenAPI ni los requisitos del alcance definen longitud, complejidad, reutilización o coincidencia (`specs/api/openapi.json:78-85,731-747`).

**E-03 — Entrega de contraseña temporal.** HU-01 delega a quien crea la cuenta la entrega por un “canal seguro”, sin identificar canal, expiración, reemisión, pérdida antes del primer uso ni evidencia de entrega (`requirements/02-historias-usuario.md:15,18`).

**E-04 — Contraseña temporal expirada o ya utilizada.** Solo se define el conflicto cuando la cuenta no requiere cambio; no se especifican caducidad, reintentos, bloqueo o recuperación (`requirements/03-reglas-negocio.md:24`; `specs/api/openapi.json:78-86`).

**E-05 — Cambio de permisos con JWT activo.** No se define revocación, versión de sesión, relectura de permisos ni momento efectivo cuando una cuenta se bloquea o cambia de programas (`requirements/03-reglas-negocio.md:14,17`).

**E-06 — Usuario sin sede o sede inexistente.** `usuarios.sede_id` es nulo y carece de FK; solo se explica el nulo de CTIC. No se determina la reacción para un coordinador o usuario de consulta con sede nula/eliminada (`architecture/04-modelo-datos.md:64-65`; `specs/db/oeupb-schema.sql:11`).

### Carga, limpieza y versionado

**E-07 — Documento vacío o mal interpretado por Excel.** No se define el tratamiento de nulos, notación científica, ceros iniciales, separadores, espacios, tipos numéricos ni documentos extranjeros (`requirements/03-reglas-negocio.md:7`).

**E-08 — Colisión por normalización.** No se determina qué hacer si dos valores distintos convergen al mismo documento normalizado.

**E-09 — Duplicados dentro del archivo.** RN-01 remite a ADR-006, fuera del alcance auditado; los tres directorios no especifican primera/última fila, combinación, rechazo ni reporte (`requirements/03-reglas-negocio.md:7`).

**E-10 — Normalización indiscriminada de texto.** HU-05 ordena llevar texto a minúsculas, pero no delimita columnas; aplicada a nombres, programas o respuestas abiertas puede alterar la representación original (`requirements/02-historias-usuario.md:46-51`).

**E-11 — Libro `.xlsx` no procesable.** No se especifican hoja objetivo, encabezados, fórmulas, celdas combinadas, archivos cifrados/corruptos, libros sin filas, tamaño máximo o protección contra archivos de descompresión costosa (`requirements/03-reglas-negocio.md:11`).

**E-12 — Archivo parcialmente válido.** `CargaResponse` puede contener mensaje y errores, pero no define si hay persistencia parcial, reversión total o estado de carga fallida (`specs/api/openapi.json:749-768`).

**E-13 — Reintento idéntico.** Existe `hash_archivo`, pero no se especifica si el mismo hash se rechaza, reutiliza, crea nueva versión o reemplaza la vigente (`specs/db/oeupb-schema.sql:31-45`).

**E-14 — Cargas concurrentes del mismo alcance.** No hay regla de bloqueo, nivel de aislamiento o unicidad que impida dos versiones vigentes para sede/momento/cohorte (`requirements/03-reglas-negocio.md:18`; `specs/db/oeupb-schema.sql:45`).

**E-15 — Fallo después de marcar reemplazo.** La atomicidad se exige, pero no se especifican estados intermedios, compensación o recuperación tras interrupción del proceso (`requirements/01-requerimientos.md:71-77`).

**E-16 — Año inválido o futuro.** `anio` solo tiene tipo entero; no se define rango, cero, negativos, año futuro o diferencia permitida respecto de `fecha_grado` (`specs/api/openapi.json:711-715`).

**E-17 — Eliminación de versión antigua.** El endpoint devuelve 409 si ya no está vigente, pero no se define si una versión reemplazada puede purgarse, restaurarse o consultarse (`specs/api/openapi.json:339-344`).

### Egresados, mediciones y privacidad

**E-18 — Una identidad visible en varias sedes.** `egresados` es global y la sede pertenece a la medición. RN-13 delega conflictos a una “custodia institucional” sin actor, flujo, SLA ni regla de precedencia (`architecture/04-modelo-datos.md:61-68`; `requirements/03-reglas-negocio.md:19`).

**E-19 — Borrado con mediciones relacionadas.** RF-12 permite borrar registros, pero no define rechazo, cascada, anonimización o baja lógica; las FK SQL tampoco declaran cascada (`requirements/01-requerimientos.md:95-101`; `specs/db/oeupb-schema.sql:62-67`).

**E-20 — Medición repetida.** No existe unicidad por documento/sede/momento/cohorte ni una regla sobre múltiples respuestas válidas de la misma persona (`specs/db/oeupb-schema.sql:51-68`).

**E-21 — Medición anónima.** RN-15 permite usarla solo en agregados “aprobados”, pero no define quién aprueba, cómo se marca el agregado ni cómo se evita que aparezca en exploraciones no longitudinales (`requirements/03-reglas-negocio.md:21`).

**E-22 — Doble titulación.** El documento histórico propone conservar la última carrera, pero no define fecha de orden, desempate, auditoría ni efecto en mediciones previas; el esquema solo tiene un campo `programa` (`requirements/04-hallazgos-figma.md:22-24`; `specs/db/oeupb-schema.sql:23`).

**E-23 — Evolución del cuestionario JSON.** No existe versión de cuestionario, catálogo de claves, tipos, unidades, alias o migración para `mediciones.respuestas` (`architecture/04-modelo-datos.md:59-68`).

### Reportes y analítica

**E-24 — Fórmulas y denominadores.** No se fijan población, nulos, momento elegido, duplicados, moneda, atípicos o denominadores para empleo, formalidad, salario, satisfacción y dispersión (`requirements/01-requerimientos.md:199-245,495-597`).

**E-25 — “Datos insuficientes”.** HU-08 no define mínimo de observaciones, emparejamiento M1/M5, cohorte común, pérdida de seguimiento ni mensaje para ausencia total (`requirements/02-historias-usuario.md:73-78`).

**E-26 — Estado laboral y formalidad.** RN-16 separa la formalidad, pero no determina su valor para independiente, estudiante o sin empleo ni cómo entra en la tasa formal/informal (`requirements/03-reglas-negocio.md:22`).

**E-27 — Programas renombrados o fusionados.** La audiencia y los filtros dependen de programas, pero no hay catálogo ni identificador estable para alias, cambios de nombre o programas cerrados (`requirements/03-reglas-negocio.md:14,16`; `specs/db/oeupb-schema.sql:23`).

**E-28 — Filtro de sede en dashboard.** El mockup histórico muestra un filtro de sede, mientras la sede propia deriva del JWT y las demás solo pueden aportar publicaciones agregadas. No se define si ese filtro cambia datos propios, selecciona publicaciones o debe retirarse (`requirements/04-hallazgos-figma.md:7-10`).

**E-29 — Exportación vacía, grande o revocada.** CU-09 no define límites, asincronía, formato de fechas/moneda, metadatos, nombre de archivo, conjunto vacío ni qué ocurre si el permiso se revoca durante la generación (`requirements/casos-de-uso.md:59-63`).

### Publicación y compartición

**E-30 — Grupos pequeños reidentificables.** RN-14 reconoce que no hay umbral automático; no se define tamaño mínimo, supresión de celdas, combinación de filtros o revisión ante una sola persona (`requirements/03-reglas-negocio.md:20`).

**E-31 — Retiro con caché o sesión abierta.** No se define el efecto del retiro sobre pestañas abiertas, caché, solicitudes en curso, enlaces, capturas o exportaciones ya generadas (`requirements/02-historias-usuario.md:127`).

**E-32 — Cambio de audiencia entre versiones.** No se establece si una versión conserva los programas/permisos originales, hereda los vigentes o requiere nueva aprobación de privacidad.

**E-33 — Publicación sin datos o con métricas erróneas.** No se define si puede publicarse una gráfica vacía, fallida, basada en datos reemplazados o afectada por una corrección manual posterior.

### IA, operación y despliegue

**E-34 — Fallos de IA y evidencia.** Para NLP no se definen timeout, reintentos, indisponibilidad del proveedor, cancelación, versión del modelo, retención, costo ni evidencia de anonimización (`requirements/02-historias-usuario.md:100-105`; `requirements/01-requerimientos.md:623-653`).

**E-35 — Límites operativos medibles.** RNF-02, RNF-03, RNF-05 y RNF-06 no fijan navegadores/versiones, dispositivos, volumen, concurrencia, latencia o recuperación. La arquitectura de despliegue exige health checks, backups y rollback, pero no define objetivos verificables (`requirements/01-requerimientos.md:263-277,303-325`; `architecture/05-despliegue.md:21-35`).

## Recomendaciones de Mitigación

### P0 — Seguridad, integridad y decisiones bloqueantes

1. **Materializar invariantes de sede y medición.** Mediante migración formal, hacer obligatorios sede, momento, año y respuestas cuando corresponda; agregar catálogo/FK de sedes y `CHECK (momento IN (0,1,5))`. Documentar de forma separada cualquier excepción histórica.
2. **Cerrar el modelo RBAC.** Definir enums de rol técnico, estado de cuenta, alcance de consulta y permisos; separar rol de alcance rector/profesor/administrativo y establecer la rama de autorización aplicable a coordinadores.
3. **Corregir el esquema de autenticación OpenAPI.** Publicar un flujo Bearer compatible con el login JSON o adaptar el endpoint al flujo OAuth2 declarado. Tipar completamente `LoginResponse` y todos los errores 401/403.
4. **Separar contratos de alta por actor.** Crear solicitudes específicas para alta de coordinador y de usuario de consulta, sin rol libre; derivar la sede del actor cuando proceda e incluir programas/permisos con validación en backend.
5. **Resolver propiedad y edición multisede.** Sustituir “custodia institucional” por un flujo explícito: autoridad, estados, precedencia, trazabilidad y efecto de una corrección sobre otras sedes.
6. **Definir privacidad cuantitativa de publicaciones.** Aprobar umbral o regla de supresión, combinaciones de filtros prohibidas y evidencia de revisión antes de habilitar compartición.

### P1 — Contratos, trazabilidad y carga

7. **Completar OpenAPI.** Añadir esquemas cerrados para reportes, explorador, directorio, perfil e historial; documentar 400/401/403/404/409 con cuerpo común y ejemplos; incluir enums, formatos y límites.
8. **Exponer la identidad de carga.** Hacer que `CargaResponse` retorne `carga_id`, versión, alcance, estado, contadores y resultado; especificar carga parcial frente a rollback total.
9. **Asegurar versionado concurrente.** Definir idempotencia por hash o clave, unicidad de la versión vigente, bloqueo transaccional y recuperación ante interrupciones.
10. **Modelar auditoría manual.** Incorporar entidad de revisión/cambio con actor, fecha, origen, campos, valor anterior/nuevo y resolución de conflicto; representar encuestas manuales sin abusar de nulabilidad histórica.
11. **Definir baja lógica de carga y cuenta.** Alinear `DELETE`, FK, conservación de evidencia, restauración y revocación de sesiones. Evitar que eliminar la entidad destruya la trazabilidad exigida.
12. **Especificar el ETL.** Publicar diccionario de columnas, hoja, tipos, normalización, duplicados, doble titulación, tamaños, fórmulas, archivos protegidos y política de errores.

### P2 — Reportes, publicación e IA

13. **Diseñar contratos de filtros y comparación.** Representar listas de programas/cohortes, momento inicial/final y respuestas tipadas. Todo filtro debe validarse nuevamente contra sede, programas y permisos en backend.
14. **Crear un diccionario de indicadores.** Para cada RF analítico: fuente, población, fórmula, denominador, nulos, unidad, moneda, momento, cohorte, tratamiento de anónimos y umbral de privacidad.
15. **Restringir el estado del frontend a agregados autorizados.** Reescribir HU-09 CA2 para enumerar qué agregados pueden recalcularse localmente y cuándo debe consultarse de nuevo al backend.
16. **Precisar la instantánea publicada.** Definir qué valores se congelan, si “reproducir” significa renderizar o recalcular, cómo nace una versión, qué audiencia aplica y qué sucede tras cambios de datos o permisos.
17. **Modelar publicación y permisos.** Incorporar propietario, sede, programas estables, definición, métricas, versión, aprobación de privacidad, estado y marcas de tiempo; añadir endpoints de publicar, retirar, listar y consultar.
18. **Convertir IA en especificación verificable antes de activarla.** Para NLP, definir proveedor o interfaz, datos permitidos, anonimización verificable, estados asíncronos, timeout, reintentos, auditoría y retención. Mantener predicción en pausa hasta cerrar los criterios ya enumerados en RF-71.

### P3 — Calidad documental y verificabilidad

19. **Normalizar estados de implementación.** Usar al menos: contrato existente, flujo parcial, política objetivo y flujo completo verificado. Corregir CU-05 a CU-07 para que coincidan con la matriz.
20. **Desagregar la trazabilidad.** Crear filas RF/HU/CU/RN → endpoint → request/response → tabla/campo → prueba → estado, evitando rangos amplios que ocultan requisitos no comprobados.
21. **Separar evidencia visual de funcional.** En el documento de Figma, reemplazar “cumple” por “representa visualmente” cuando no exista contrato o implementación verificada.
22. **Hacer medibles los RNF.** Fijar navegadores y versiones, resoluciones/dispositivos, WCAG, volumen anual, concurrencia, percentiles de latencia, RPO/RTO y criterios de rollback.
23. **Automatizar controles documentales.** Validar en CI identificadores, enlaces, enums, nulabilidad, respuestas sin esquema, correspondencia OpenAPI–SQL y cobertura de errores/autorización.

### Criterio de cierre

La auditoría puede considerarse atendida cuando cada C-01 a C-22 tenga una decisión aprobada, cambio de contrato o exclusión explícita; cada E-01 a E-35 se convierta en regla, criterio de aceptación o riesgo aceptado; y la matriz enlace cada decisión con evidencia técnica y pruebas de autorización, integridad y privacidad.
