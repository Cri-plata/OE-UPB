# Auditoría cruzada de requerimientos, especificaciones y arquitectura de OE UPB

**Fecha:** 2026-09-23  
**Alcance:** `requirements/`, `specs/` y `architecture/`  
**Método:** contraste textual de requisitos, historias, reglas de negocio, casos de uso, trazabilidad, OpenAPI, esquema SQL y arquitectura.  
**Criterio:** no se atribuye comportamiento que no esté expresamente documentado. Las referencias a ADR, backlog, código, pruebas o design system son dependencias externas no verificadas en este alcance.

## Resumen Ejecutivo

La política normativa vigente es coherente en su intención principal: `Admin_CTIC` administra coordinadores; cada `Coordinador_Sede` administra los datos y usuarios de consulta de su sede; `Usuario_Consulta` es de solo lectura; y el intercambio entre sedes se limita a gráficas y métricas agregadas publicadas. RN-03 y RN-06 a RN-11, junto con HU-01, HU-03, HU-12 y HU-13, corrigen las contradicciones RBAC que existían en versiones anteriores.

Sin embargo, la documentación todavía no forma una especificación ejecutable de extremo a extremo. Se identificaron **20 inconsistencias o brechas contractuales** y **27 casos de borde no resueltos**. Los riesgos principales son:

1. El esquema canónico permite mediciones sin sede, momento, año o respuestas, a pesar de que sede y momento son invariantes de seguridad y negocio.
2. OpenAPI no representa la política objetivo de cuentas, permisos, programas y publicación, ni documenta respuestas 401/403 por rol.
3. RF-07 exige auditar cada archivo, pero no existe una entidad de carga; además, el caso de uso elimina una carga individual mientras la API elimina por momento/año.
4. Comparación M1/M5, filtros multiselección, CRUD manual, exportaciones e IA carecen de contratos completos.
5. No están definidas fórmulas, taxonomías, atomicidad e idempotencia de carga, precedencia de edición, tratamiento de anónimos ni ciclo de vida de publicaciones.

La prioridad debe ser alinear las invariantes de autorización, sede y carga en OpenAPI y SQL antes de ampliar funcionalidad sobre el modelo actual.

### Seguimiento de remediación — 2026-09-23

La primera corrección posterior a la auditoría dejó **18 hallazgos abiertos o parcialmente abiertos**:

- **C-10 resuelto:** frontend y backend aceptan exclusivamente `.xlsx`; el backend valida el contenido al leerlo y OpenAPI documenta el formato y sus errores.
- **C-19 resuelto:** la descripción de OpenAPI ya declara adopción parcial de Clean Architecture.
- **C-01 parcialmente mitigado:** el backend rechaza momentos distintos de 0/1/5 y cargas de coordinadores sin sede; las restricciones físicas y migraciones siguen pendientes.
- **C-11 parcialmente mitigado:** carga, historial y eliminación ya documentan respuestas de negocio y errores; los endpoints restantes aún requieren esquemas completos.
- Se eliminó el fallback silencioso a sede 1, se restringió carga/historial/eliminación a coordinadores con sede y se añadieron pruebas unitarias para estas validaciones.
- **C-02 y C-03 resueltos:** `cargas` representa cada archivo y el historial/eliminación operan por `carga_id`.
- **C-14 en pausa:** no se implementará la predicción hasta aprobar objetivo y métricas.
- **C-16 y C-17 resueltos normativamente:** se aprobó el catálogo laboral simplificado y se separaron estudios adicionales del estado laboral.
- **C-05 parcialmente mitigado:** se eliminó la contraseña compartida fija y se implementó contraseña temporal aleatoria con cambio inicial obligatorio; permisos y programas de `Usuario_Consulta` siguen pendientes.

Las decisiones necesarias para continuar están registradas en [`03-formulario-decisiones.md`](03-formulario-decisiones.md).

## Contradicciones Identificadas

### C-01 — Sede y momento obligatorios frente a columnas anulables

**Severidad:** Crítica. **Tipo:** regla–datos.

RN-02 solo admite momentos 0, 1 y 5; RN-06 exige aislamiento por sede; y CU-03 establece que las mediciones quedan asociadas a la sede del token (`requirements/03-reglas-negocio.md`, RN-02/RN-06; `requirements/casos-de-uso.md`, CU-03). No obstante, `mediciones.momento`, `anio`, `sede_id` y `respuestas` admiten `NULL`, no existe `CHECK` para momento ni FK de sede (`specs/db/oeupb-schema.sql`, tabla `mediciones`). Las especificaciones permiten estados que las reglas obligatorias rechazan.

### C-02 — Fecha por archivo sin entidad persistente de carga

**Severidad:** Alta. **Tipo:** requisito–datos.

RF-07 exige registrar la fecha exacta de subida de cada archivo y CU-04 requiere listar y seleccionar cargas (`requirements/01-requerimientos.md`, RF-07; `requirements/casos-de-uso.md`, CU-04). El esquema solo contiene usuarios, egresados y mediciones; no registra archivo, fecha, actor, resultado ni relación carga-medición (`specs/db/oeupb-schema.sql`). No existe representación canónica para demostrar RF-07 o distinguir dos archivos de igual sede, momento y año.

### C-03 — Eliminar una carga frente a eliminar por momento/año

**Severidad:** Alta. **Tipo:** flujo–API.

CU-04 describe “listar cargas → seleccionar → confirmar eliminación”; OpenAPI solo ofrece `DELETE /api/carga/momento/{momento}/{anio}` (`requirements/casos-de-uso.md`, CU-04; `specs/api/openapi.json`). Sin identificador de carga, dos archivos de la misma clasificación no son direccionables por separado.

### C-04 — Ciclo de vida de cuentas sin soporte técnico

**Severidad:** Crítica. **Tipo:** RBAC–API/datos.

RN-07, HU-12 y CU-02 contemplan crear, modificar, bloquear y eliminar cuentas; CU-01 presupone una cuenta activa. OpenAPI solo lista, crea y elimina usuarios, y `usuarios` no contiene estado ni baja lógica (`requirements/03-reglas-negocio.md`, RN-07; `requirements/02-historias-usuario.md`, HU-12; `requirements/casos-de-uso.md`, CU-01/CU-02; `specs/api/openapi.json`, `/api/usuarios/*`; `specs/db/oeupb-schema.sql`). “Bloquear”, “eliminar” y “activa” no tienen correspondencia documentada.

### C-05 — `UsuarioCreateRequest` no satisface los formularios objetivo

**Severidad:** Crítica. **Tipo:** requisito–API.

HU-01 exige nombre, correo y sede para coordinadores; HU-12 añade permisos y programas para usuarios de consulta; HU-01 CA2 exige cifrar una contraseña. `UsuarioCreateRequest` solo requiere `nombre`, `correo` y `rol`, acepta `sede` como nombre opcional y no incluye contraseña, permisos ni programas (`requirements/02-historias-usuario.md`, HU-01/HU-12; `specs/api/openapi.json`, `UsuarioCreateRequest`). El modelo, además, persiste `sede_id` entero (`specs/db/oeupb-schema.sql`). No se documenta generación automática de credenciales.

### C-06 — Roles normalizados frente a cadenas libres y roles heredados

**Severidad:** Alta. **Tipo:** autorización–contrato.

RN-03/RN-07 normalizan `Admin_CTIC`, `Coordinador_Sede` y `Usuario_Consulta`. La arquitectura reconoce que `Directivo` y `Profesor` siguen presentes y que `Usuario_Consulta` aún no existe en el modelo actual (`requirements/03-reglas-negocio.md`; `architecture/00-proyecto.md`, Roles observados). OpenAPI y SQL admiten cualquier cadena como rol, sin separar rol técnico de alcance rector/profesor/administrativo (`specs/api/openapi.json`; `specs/db/oeupb-schema.sql`).

### C-07 — CRUD manual de egresados ausente

**Severidad:** Alta. **Tipo:** cobertura funcional.

RF-10 a RF-12 y HU-06 exigen crear, modificar y borrar egresados. OpenAPI solo ofrece listar, obtener programas y leer perfiles en `/api/directorio/*`; no contiene POST, PUT/PATCH o DELETE de egresados (`requirements/01-requerimientos.md`; `requirements/02-historias-usuario.md`, HU-06; `specs/api/openapi.json`). La matriz reconoce cobertura parcial (`requirements/matriz-trazabilidad.md`, RF-10–RF-12).

### C-08 — Comparación M1/M5 y multiselección no contratadas

**Severidad:** Alta. **Tipo:** experiencia–API.

HU-08 exige dos momentos independientes; HU-09, multiselección de programas y cohortes. `/api/reportes/tendencias` solo recibe un indicador, `/general` no declara filtros y `/explorador` acepta un único momento, programa y año (`requirements/02-historias-usuario.md`, HU-08/HU-09; `specs/api/openapi.json`). Ningún endpoint representa los criterios de aceptación completos.

### C-09 — Momento y año tienen tipos incompatibles

**Severidad:** Alta. **Tipo:** inconsistencia interna del contrato.

La carga recibe momento/año enteros; la eliminación recibe momento entero y año cadena; el explorador recibe ambos como cadenas; SQL los guarda como enteros (`specs/api/openapi.json`; `specs/db/oeupb-schema.sql`, `mediciones`). No se documentan conversión, formato o rango.

### C-10 — Formato `.xlsx` no expresado por OpenAPI

**Severidad:** Media. **Tipo:** validación–contrato.

RN-05 exige validar extensión y contenido en frontend y backend, y HU-04 limita a `.xlsx`. OpenAPI solo describe un binario multipart, sin formato admitido ni errores específicos (`requirements/03-reglas-negocio.md`, RN-05; `requirements/02-historias-usuario.md`, HU-04; `specs/api/openapi.json`, `POST /api/carga/excel`).

### C-11 — Fuente canónica con respuestas de negocio sin esquema

**Severidad:** Alta. **Tipo:** estrategia de contratos.

`architecture/03-contratos.md` declara OpenAPI como autoridad y exige detectar breaking changes. Sin embargo, historial, eliminación, tendencias, explorador, directorio y perfil tienen respuestas 200 sin esquema de negocio concreto (`specs/api/openapi.json`). CU-04 a CU-08 requieren estructuras específicas (`requirements/casos-de-uso.md`). Un esquema vacío no permite validar consumidores ni cambios incompatibles.

### C-12 — Publicación y permisos sin API ni modelo

**Severidad:** Crítica. **Tipo:** arquitectura objetivo–especificación actual.

RF-35/RF-37, RN-08 a RN-11, HU-12/HU-13 y CU-11/CU-12 definen permisos, programas, publicación, retiro y audiencia. La arquitectura exige propietario, sede, programas, definición, estado y marcas de tiempo (`architecture/02-backend.md`, Frontera objetivo; `architecture/04-modelo-datos.md`, Extensión pendiente). OpenAPI y SQL no representan ninguna de estas capacidades. La brecha está reconocida, pero aún no existe un contrato implementable.

### C-13 — Recálculo en memoria frente a la frontera de privacidad

**Severidad:** Alta. **Tipo:** arquitectura/privacidad.

HU-09 CA2 permite recalcular gráficas en frontend con “datos filtrados en memoria”. RN-06/RN-09 y la arquitectura limitan el intercambio a gráficas y métricas agregadas sin filas ni respuestas individuales (`requirements/02-historias-usuario.md`, HU-09; `requirements/03-reglas-negocio.md`, RN-06/RN-09; `architecture/00-proyecto.md`, Principios). No se define si “datos” significa filas o agregados ni qué recálculos son seguros.

### C-14 — La variable objetivo de IA no es única

**Severidad:** Alta. **Tipo:** contradicción funcional.

RF-71 pide probabilidad de **empleo formal**; HU-10 se refiere alternativamente a riesgo de **desempleo**, probabilidad de **empleabilidad** y riesgo superior al 30 % (`requirements/01-requerimientos.md`, RF-71; `requirements/02-historias-usuario.md`, HU-10). Estas variables no son complementarias si existen empleo informal, emprendimiento o estudio.

### C-15 — Actor del análisis predictivo indeterminado

**Severidad:** Media. **Tipo:** autorización.

HU-10 asigna predicción al coordinador; CU-10 permite ejecutar IA al coordinador o usuario de consulta; RN-03 declara al usuario de consulta siempre de solo lectura (`requirements/02-historias-usuario.md`, HU-10; `requirements/casos-de-uso.md`, CU-10; `requirements/03-reglas-negocio.md`, RN-03). No se distingue consultar un resultado ya calculado de iniciar una inferencia.

### C-16 — Taxonomía laboral incompatible

**Severidad:** Alta. **Tipo:** semántica analítica.

RF-17 usa trabajando/emprendiendo/estudiando/desempleado; RF-23, empleado/sin empleo/independiente; RF-25 introduce formalidad; RF-61 omite desempleo; HU-07 exige tasas formal e informal (`requirements/01-requerimientos.md`, RF-17/RF-23/RF-25/RF-61; `requirements/02-historias-usuario.md`, HU-07). Sin catálogo o equivalencias, tasas y gráficas pueden clasificar distinto el mismo dato.

### C-17 — RF-20 mezcla estudios y situación laboral

**Severidad:** Media. **Tipo:** contradicción interna.

RF-20 solicita gráficos de estudios adicionales, pero su aclaración pide porcentajes de trabajando, emprendiendo, posgrado o desempleado (`requirements/01-requerimientos.md`, RF-20). No queda definido si es distribución académica, laboral o cruce de dimensiones.

### C-18 — `sede_id` de respuesta no coincide con SQL

**Severidad:** Media. **Tipo:** API–datos.

`UsuarioResponse.sede_id` admite cadena, entero o nulo; SQL solo entero o nulo; la creación recibe `sede` como nombre (`specs/api/openapi.json`; `specs/db/oeupb-schema.sql`; `architecture/03-contratos.md`, Discrepancias). No se documenta qué significa la variante de cadena.

### C-19 — Estado de Clean Architecture incompatible

**Severidad:** Baja. **Tipo:** estado arquitectónico.

OpenAPI describe la API como “aplicando Clean Architecture”; `architecture/00-proyecto.md` y `02-backend.md` indican cumplimiento parcial y lógica mezclada en routers. La descripción presenta como consolidado lo que la arquitectura considera incompleto.

### C-20 — Figma histórico conserva una instrucción obsoleta

**Severidad:** Baja. **Tipo:** gobernanza documental.

El encabezado de `requirements/04-hallazgos-figma.md` declara históricos los roles, pero “Pantallas / Estados Faltantes” todavía pide que Admin CTIC seleccione “Rol” y “Sede o Facultad”. HU-01/RN-07 fijan el rol en `Coordinador_Sede` y requieren sede. La recomendación pendiente no marca esos campos como sustituidos.

## Casos de Borde

### E-01 — Documento ausente o mal normalizado

RN-01 no define nulos, ceros iniciales, espacios, separadores, notación numérica de Excel ni colisiones producidas por normalización (`requirements/03-reglas-negocio.md`, RN-01).

### E-02 — Duplicados intrarchivo

RN-01 delega el caso a ADR-006, fuera del alcance auditado. Estos directorios no indican primera/última fila, rechazo, combinación o reporte de conflicto.

### E-03 — Medición repetida

No hay unicidad por documento, sede, momento y año. No se define si una recarga reemplaza, versiona, suma o rechaza (`specs/db/oeupb-schema.sql`, `mediciones`).

### E-04 — Carga parcialmente válida

`CargaResponse` puede contener mensaje y errores, pero no aclara si persiste filas válidas, revierte todo o permite reintentar sin duplicación (`specs/api/openapi.json`, `CargaResponse`).

### E-05 — `.xlsx` inválido por contenido

RN-05 no define hojas, encabezados, libro corrupto o protegido, fórmulas, macros, firma ni tamaño máximo.

### E-06 — Cargas concurrentes

No se especifican bloqueo, idempotency key u orden de UPSERT cuando llegan cargas coincidentes.

### E-07 — Edición manual frente a UPSERT posterior

HU-05/HU-06 no fijan precedencia, auditoría ni protección de correcciones manuales.

### E-08 — Borrado de egresado con mediciones

RF-12 permite borrar, pero la FK no declara cascada. No se define rechazo, baja lógica, anonimización o borrado relacionado.

### E-09 — Eliminación concurrente

No se define transacción, recuperación o consistencia cuando la eliminación por momento/año coincide con carga o consulta.

### E-10 — Un egresado visible en varias sedes

`egresados` es global y la sede pertenece a la medición. No se define quién puede modificar los datos personales compartidos (`architecture/04-modelo-datos.md`).

### E-11 — Mediciones anónimas

La arquitectura permite documento nulo, pero RF-52 une momentos por documento. No se define su participación en KPIs, perfiles o análisis longitudinal.

### E-12 — Doble titulación

El documento de Figma conserva solo la “última” carrera, sin criterio temporal, desempate, auditoría ni compatibilidad con el único campo `programa`.

### E-13 — Año de encuesta frente a cohorte

`mediciones.anio` y `egresados.fecha_grado` pueden producir años distintos; RF-22 no determina cuál alimenta el filtro.

### E-14 — Año inválido o futuro

No existe rango ni regla para negativos, cero, más de cuatro dígitos o años futuros.

### E-15 — Usuario sin sede o sede inexistente

`usuarios.sede_id` es anulable y no tiene FK. No se define el rechazo de operaciones de datos con sede nula o inválida.

### E-16 — Navegación prohibida, 401 y 403

El frontend no tiene guards y OpenAPI no documenta 401/403. No se define la experiencia para sesión expirada, token inválido o privilegio insuficiente.

### E-17 — Correo institucional

No se especifican dominio, normalización de mayúsculas/espacios, alias, cambio de correo o colisión con la restricción única.

### E-18 — Cambio de permisos con JWT activo

No se define invalidación de tokens, relectura de permisos ni cuándo pierde acceso un usuario bloqueado o reasignado.

### E-19 — Gráficas con grupos identificables

RN-09 prohíbe datos personales, pero no fija tamaño mínimo ni supresión de celdas pequeñas cuando un filtro deja una sola persona.

### E-20 — Actualización de una publicación

No se decide si una gráfica publicada es instantánea o se recalcula, cómo se versiona ni qué ocurre durante su actualización.

### E-21 — Retiro y caché

HU-13 no define efecto sobre pestañas abiertas, cachés, solicitudes en curso o exportaciones ya generadas.

### E-22 — Programas renombrados

La audiencia depende de programas, pero no existe catálogo o identificador estable para alias, cambios de nombre o programas cerrados.

### E-23 — Fórmulas y denominadores

No se fijan fórmulas, nulos, moneda, atípicos, medición elegida o denominadores para empleabilidad, salario, satisfacción y dispersión.

### E-24 — “Datos insuficientes”

HU-08 no define tamaño mínimo, cobertura, emparejamiento de egresados, cohorte común ni pérdida de seguimiento.

### E-25 — Evolución del JSON

No hay versión de cuestionario, catálogo de claves, tipos, unidades, alias o migración para `mediciones.respuestas`.

### E-26 — Exportaciones

CU-09 no define filtros, nombre, metadatos, límite, conjunto vacío, generación asíncrona ni contenido permitido de una gráfica publicada.

### E-27 — Fallos y evidencia de IA

RNF-07/RNF-08 no definen estados, timeout, reintentos, cancelación, indisponibilidad, versión del modelo ni evidencia de anonimización e inferencia.

## Recomendaciones de Mitigación

### P0 — Seguridad e integridad

1. Hacer no nulos los campos críticos de medición; crear catálogo/FK de sedes y restricción de momento `{0,1,5}` mediante migración formal.
2. Centralizar autorización en backend; documentar 401/403 y probar cada denegación de la matriz RBAC.
3. Cerrar el dominio de roles y modelar por separado alcance rector/profesor/administrativo, permisos y programas.
4. Diseñar el modelo de publicación con propietario, sede, programas, definición/versionado, métricas, estado y marcas de tiempo.
5. Definir propiedad y edición de egresados con mediciones en varias sedes.

### P1 — Contratos y carga

6. Modelar cada carga con ID, huella/archivo, fecha, actor, sede, momento, año, estado, errores y mediciones afectadas; eliminar por ID o declarar la operación masiva.
7. Completar OpenAPI con esquemas de respuesta, errores, enums y operaciones de cuentas, CRUD manual, permisos, publicación, filtros, exportación e IA.
8. Unificar tipos y semántica de `anio`, `momento` y `sede_id`; separar año de encuesta y cohorte.
9. Especificar si la contraseña se recibe, genera o activa mediante invitación, y su entrega/restablecimiento.
10. Definir el ETL: columnas, normalización, formato real, duplicados, UPSERT, atomicidad, idempotencia, doble titulación y errores.
11. Aprobar precedencia entre datos históricos, cargas nuevas y edición manual, conservando origen, actor y fecha.
12. Separar bloqueo, baja lógica y eliminación de carga, medición y egresado; alinear FK y recuperación.

### P2 — Analítica e IA

13. Normalizar catálogos de estado laboral, programas, sedes, preguntas y versiones de encuesta.
14. Crear un diccionario de indicadores con fuente, población, fórmula, denominador, nulos, unidad, moneda, momento, cohorte y umbral de privacidad.
15. Limitar el estado del frontend a agregados autorizados y documentar los recálculos permitidos.
16. Elegir una variable objetivo de IA y fijar horizonte, población, salida, umbral, versión, datos mínimos y actores.
17. Definir estados asíncronos, reintentos, timeout, cancelación, auditoría e indisponibilidad para IA.
18. Especificar exportaciones seguras, incluyendo contenido, filtros, permisos, límites y conjuntos vacíos.

### P3 — Gobernanza

19. Marcar dentro de cada sección de Figma las recomendaciones sustituidas por la política vigente.
20. Desagregar la matriz a filas RF → HU/CU → RN → endpoint → campo → prueba → estado.
21. Hacer medibles los RNF con navegadores, dispositivos, accesibilidad, volumen, concurrencia, latencia y recuperación.
22. Automatizar validación de identificadores, enlaces, enums, nulabilidad, respuestas OpenAPI y correspondencia SQL.

La auditoría se considera cerrada cuando C-01 a C-20 tengan una decisión o corrección trazable y E-01 a E-27 se conviertan en regla, criterio de aceptación o exclusión explícita.
