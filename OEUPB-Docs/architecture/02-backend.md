# Arquitectura del backend

**Estado:** descripción del código actual

**Verificado:** 2026-09-24

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
| `application/` | Autenticación, hashing, emisión y validación de JWT |
| `infrastructure/` | Engine, sesiones y Base de SQLAlchemy |
| `presentation/` | Routers FastAPI, payloads y parte importante de la lógica de negocio |

La estructura usa nombres de Clean Architecture, pero los límites son parciales. ETL, autorización, persistencia y serialización conviven en routers. Las futuras extracciones deben hacerse con pruebas.

## Routers actuales

| Prefijo | Responsabilidad |
|---|---|
| `/api/auth` | Login |
| `/api/usuarios` | Listado, creación y eliminación de usuarios |
| `/api/carga` | Carga versionada, historial por archivo y eliminación por `carga_id` |
| `/api/reportes` | KPIs, tendencias y explorador |
| `/api/directorio` | Listado, programas y ficha individual |
| `/api/sedes` | Catálogo autenticado de sedes activas |

El inventario exacto se encuentra en `../specs/api/openapi.json`.

## Seguridad actual

- JWT HS256 con expiración configurable.
- El token incluye correo, rol y sede.
- `OAuth2PasswordBearer` protege los endpoints que dependen de `get_current_user`.
- El alta usa el documento como credencial temporal en desarrollo y una credencial aleatoria obligatoria en producción. Solo se conserva el hash; las credenciales vencen, pueden reemitirse con auditoría y el JWT restringido permite únicamente establecer una contraseña personal.
- CORS se configura por ambiente mediante `CORS_ALLOWED_ORIGINS`.

## Deuda relevante

- El arranque fuera de desarrollo exige un secreto JWT de al menos 32 caracteres y credenciales iniciales aleatorias.
- La validación de cuenta vigente y las dependencias de rol están centralizadas; algunas validaciones de alcance específicas permanecen en routers.
- La carga rechaza usuarios que no sean coordinadores, coordinadores sin sede, momentos distintos de 0/1/5 y formatos diferentes de `.xlsx`; las denegaciones y el aislamiento tienen pruebas automatizadas.
- Alembic gestiona el baseline, el catálogo de sedes, las restricciones de nulabilidad, los intentos de medición y el evento inmutable de eliminación de cargas.
- Las pruebas automatizadas viven en `tests/`; los scripts manuales ad hoc de la raíz fueron retirados.
- El modelo representa publicaciones agregadas inmutables y versionadas. `/api/publicaciones` publica, retira, lista las propias y calcula el catálogo autorizado.
- Cada operación protegida contrasta cuenta activa y versión de autorización; bloqueos o reducciones revocan JWT anteriores.

## Modelo y política de mediciones

`Sede` es una entidad de catálogo referenciada por usuarios, cargas y mediciones. Una carga siempre conserva actor y sede; su eliminación física exige motivo y genera primero un `EventoEliminacionCarga` inmutable con la instantánea necesaria para auditoría. Las mediciones conservan `intento` y `fecha_registro`, y enlazan obligatoriamente carga, sede, momento y cohorte.

Los reportes aplican la política explícita de `application/medicion_policy.py`: para registros identificados seleccionan el intento más reciente de cada documento, sede, momento y cohorte; las mediciones anónimas válidas se incluyen. ADR-012 conserva la separación entre identidad (`Egresado`) y respuestas longitudinales (`Medicion`).

Consultar el backlog para prioridad y trazabilidad.

## Frontera de publicación implementada

La publicación entre sedes no habilita consultas a `egresados`, `mediciones.respuestas`, cargas o perfiles ajenos. El backend materializa una instantánea inmutable de métricas numéricas y conserva su definición únicamente para renderizado y auditoría. Una publicación no se recalcula automáticamente cuando cambian los datos fuente; una actualización crea una versión nueva. Cada versión se asocia con:

- coordinador y sede propietarios;
- programas a los que corresponde la gráfica;
- estado de publicación;
- definición de indicador y filtros necesarios;
- fechas de publicación, creación de versión y retiro;
- aprobación manual de privacidad de la versión.

La autorización de lectura se calcula en backend con el rol, los permisos y los programas asignados manualmente al usuario. Las etiquetas rector, profesor y administrativo no participan en la decisión. El cliente no envía una lista manual de destinatarios ni puede ampliar su alcance mediante parámetros.

`Usuario_Consulta` solo puede consultar instantáneas publicadas compatibles con su alcance; no obtiene gráficas privadas de su sede. El dashboard privado deriva la sede del JWT y las publicaciones de otras sedes se exponen mediante una vista y endpoints separados.

El catálogo inicial de permisos contiene `ver_reporte_general`, `ver_tendencias`, `ver_explorador` y `ver_publicaciones`. Los programas asignables se calculan en backend a partir de los nombres distintos presentes en cargas visibles de la sede del coordinador; cualquier valor enviado debe validarse contra esa lista.
