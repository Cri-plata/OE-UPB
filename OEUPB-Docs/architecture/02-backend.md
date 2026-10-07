# Arquitectura del backend

**Estado:** descripción del código actual

**Verificado:** 2026-09-25

## Stack

- Python 3.
- FastAPI 1.0.0 como aplicación HTTP.
- SQLAlchemy + PyMySQL para MySQL.
- Pydantic para payloads.
- Pandas para ETL de Excel.
- PyJWT + bcrypt para autenticación.

`requirements.txt` declara las dependencias usadas por la carga (`pandas`, `numpy` y `openpyxl`). La reproducibilidad completa todavía requiere fijar versiones y verificar la instalación desde cero.

## Capas

| Carpeta | Responsabilidad actual |
|---|---|
| `domain/` | Modelos ORM; actualmente dependen de SQLAlchemy, por lo que el dominio no es puro |
| `application/` | Autenticación y JWT, política de intentos, indicadores, taxonomía laboral, filtros, comparación, catálogo analítico y umbral de publicación (`indicadores.py`), normalización del documento (`documentos.py`), NLP descriptivo (`nlp_service.py`), pipeline de habilidades, emergentes, curaduría y reglas de asociación (`ia_service.py`), modelo de análisis de empleabilidad (`prediccion_service.py`, nombre histórico), cachés en memoria (`model_cache.py`), canonización de programas (`programas.py`). Detalle en [`06-modelos-analiticos.md`](06-modelos-analiticos.md) |
| `infrastructure/` | Engine, sesiones y Base de SQLAlchemy |
| `presentation/` | Routers FastAPI, payloads y parte importante de la lógica de negocio |

La estructura usa nombres de Clean Architecture, pero los límites son parciales. ETL, autorización, persistencia y serialización conviven en routers. Las futuras extracciones deben hacerse con pruebas.

## Routers actuales

| Prefijo | Responsabilidad |
|---|---|
| `/api/auth` | Login y cambio de contraseña temporal |
| `/api/usuarios` | Listado, alta, edición, desactivación/reactivación, reemisión de credencial, programas asignables y borrado físico auditado |
| `/api/carga` | Carga versionada, historial por archivo y eliminación por `carga_id` |
| `/api/reportes` | Filtros disponibles, KPIs con filtros, tendencias, comparación de momentos y explorador |
| `/api/directorio` | Listado, programas, ficha individual, CRUD manual auditado y exportación Excel |
| `/api/sedes` | Catálogo autenticado de sedes activas |
| `/api/publicaciones` | Publicar (con recálculo), retirar, listar propias y catálogo autorizado |
| `/api/analitica` | Resumen NLP y alertas descriptivas de la sede |
| `/api/ia` | Habilidades demandadas, reglas de asociación, comparativa temporal, curaduría, modelo de análisis de empleabilidad, robustez del modelo y exportaciones Excel; solo coordinador y sede propia (RN-32) |
| `/api/health` | Liveness y readiness |

El inventario exacto se encuentra en `../specs/api/openapi.json`.

## Seguridad actual

- JWT HS256 con expiración configurable.
- El token incluye `sub` (correo), `usuario_id`, `rol`, `sede_id`, `debe_cambiar_contrasena` y `version_autorizacion`; cada operación protegida compara esa versión y el estado de la cuenta con la base (RN-22).
- El contrato declara el esquema `HTTPBearer` para todos los endpoints que dependen de `get_current_user`.
- El alta usa el documento como credencial temporal en desarrollo y una credencial aleatoria obligatoria en producción. Solo se conserva el hash; las credenciales vencen, pueden reemitirse con auditoría y el JWT restringido permite únicamente establecer una contraseña personal.
- CORS se configura por ambiente mediante `CORS_ALLOWED_ORIGINS`.
- El log HTTP sustituye el documento de las rutas del directorio por `{documento}` y la imagen Docker desactiva el access log de Uvicorn, que registraría rutas y query strings completos.

## Deuda relevante

- El arranque fuera de desarrollo exige un secreto JWT de al menos 32 caracteres y credenciales iniciales aleatorias.
- La validación de cuenta vigente y las dependencias de rol están centralizadas; algunas validaciones de alcance específicas permanecen en routers.
- La carga rechaza usuarios que no sean coordinadores, coordinadores sin sede, momentos distintos de 0/1/5 y formatos diferentes de `.xlsx`; las denegaciones y el aislamiento tienen pruebas automatizadas.
- Alembic gestiona el baseline, el catálogo de sedes, las restricciones de nulabilidad, los intentos de medición y el evento inmutable de eliminación de cargas.
- Las pruebas automatizadas viven en `tests/` y usan SQLite en memoria. Los scripts operativos están en `scripts/ops/` y los diagnósticos manuales en `scripts/dev/`; en la raíz del backend solo quedan los puntos de entrada que exigen las herramientas (`main.py`, `alembic.ini`, `requirements.txt`, `Dockerfile`).
- El modelo representa publicaciones agregadas inmutables y versionadas. `/api/publicaciones` publica, retira, lista las propias y calcula el catálogo autorizado.
- Cada operación protegida contrasta cuenta activa y versión de autorización; desactivaciones, cambios de sede o reducciones de permisos incrementan la versión y revocan JWT anteriores.
- Las cargas de una sede se serializan con `SELECT ... FOR UPDATE` sobre la fila de la sede; en SQLite (pruebas) el bloqueo no aplica.

## Modelo y política de mediciones

`Sede` es una entidad de catálogo referenciada por usuarios, cargas y mediciones. Una carga siempre conserva actor y sede; su eliminación física exige motivo y genera primero un `EventoEliminacionCarga` inmutable con la instantánea necesaria para auditoría. Las mediciones conservan `intento` y `fecha_registro`, y enlazan obligatoriamente carga, sede, momento y cohorte.

Los reportes aplican la política explícita de `application/medicion_policy.py`: para registros identificados seleccionan el intento más reciente de cada documento, sede, momento y cohorte. Las mediciones anónimas solo entran en los KPI del reporte general sin filtro de programa; Tendencias, Explorador y comparación usan solo mediciones identificadas (RN-15). ADR-012 conserva la separación entre identidad (`Egresado`) y respuestas longitudinales (`Medicion`).

Consultar el backlog para prioridad y trazabilidad.

## Frontera de publicación implementada

La publicación entre sedes no habilita consultas a `egresados`, `mediciones.respuestas`, cargas o perfiles ajenos. El backend recalcula la gráfica con `application/indicadores.py` a partir de la definición y la sede del JWT, suprime celdas con menos de 5 observaciones, materializa una instantánea inmutable y conserva la definición únicamente para renderizado y auditoría (ADR-015). Una publicación no se recalcula automáticamente cuando cambian los datos fuente; una actualización crea una versión nueva. Cada versión se asocia con:

- coordinador y sede propietarios;
- programas a los que corresponde la gráfica;
- estado de publicación;
- definición de indicador y filtros necesarios;
- fechas de publicación, creación de versión y retiro;
- confirmación explícita de privacidad del coordinador propietario.

La autorización de lectura se calcula en backend con el rol, los permisos y los programas asignados manualmente al usuario. Las etiquetas rector, profesor y administrativo no participan en la decisión. El cliente no envía destinatarios, métricas ni programas: los programas de audiencia se derivan del cálculo y `permiso_requerido` del origen de la gráfica.

`Usuario_Consulta` solo puede consultar instantáneas publicadas compatibles con su alcance; no obtiene gráficas privadas de su sede. El dashboard privado deriva la sede del JWT y las publicaciones se exponen mediante una vista y endpoints separados: para un coordinador, `GET /api/publicaciones/mias` devuelve las propias y `GET /api/publicaciones/` las de los demás coordinadores de cualquier sede (ADR-018).

El catálogo inicial de permisos contiene `ver_reporte_general`, `ver_tendencias`, `ver_explorador` y `ver_publicaciones`. Los programas asignables se calculan en backend a partir de los nombres distintos presentes en cargas visibles de la sede del coordinador; cualquier valor enviado debe validarse contra esa lista.
