# Estado funcional actual de OE UPB

**Fecha de corte:** 2026-09-24  
**Estado:** referencia funcional verificada contra código, pruebas y migraciones  
**Versión de base de datos esperada:** `g4c82a9d1e30 (head)`

## 1. Propósito del proyecto

OE UPB es una aplicación web para que la Universidad Pontificia Bolivariana centralice y analice información de sus egresados. Reemplaza el manejo aislado de archivos por un flujo controlado de carga, consulta, análisis y publicación de resultados.

La solución está compuesta por:

- un frontend Angular para la interacción de los usuarios;
- una API FastAPI que aplica autenticación, permisos y reglas de negocio;
- MySQL para usuarios, sedes, egresados, cargas, mediciones y auditorías;
- Pandas para validar y procesar archivos Excel;
- Chart.js para presentar y exportar visualizaciones.

## 2. Roles y alcance esperado

| Rol | Qué puede hacer | Qué no puede hacer |
|---|---|---|
| `Admin_CTIC` | Iniciar sesión; crear, modificar, desactivar, reactivar y eliminar excepcionalmente coordinadores; consultar sedes. | No puede consultar directorios, mediciones, cargas ni reportes de una sede. |
| `Coordinador_Sede` | Administrar usuarios de consulta de su sede; cargar y retirar datos; consultar reportes y egresados; gestionar registros manuales; exportar; publicar gráficas; consultar analítica y alertas. | No puede consultar datos fuente de otra sede ni administrar usuarios pertenecientes a otra sede. |
| `Usuario_Consulta` | Consultar las gráficas publicadas para las que coincidan sus permisos y programas. | No accede al directorio, perfiles, archivos, respuestas individuales, dashboards privados ni administración. |

La etiqueta rector, profesor o administrativo es informativa. No concede privilegios por sí sola.

## 3. Autenticación y cuentas

Actualmente debería funcionar lo siguiente:

1. El usuario inicia sesión con correo institucional y contraseña.
2. El backend rechaza cuentas inexistentes, contraseñas incorrectas y cuentas inactivas.
3. El alta solicita el documento: en desarrollo se utiliza como credencial temporal y en producción se genera obligatoriamente una alternativa aleatoria.
4. La credencial vence y, en el primer ingreso, debe reemplazarse antes de utilizar las demás funciones.
5. Desactivar una cuenta o modificar su autorización invalida las sesiones anteriores.
6. El frontend oculta y protege las rutas que no corresponden al rol; el backend vuelve a comprobar todos los permisos.
7. Fuera de desarrollo, el backend rechaza el arranque si falta un secreto robusto o si se configura una credencial inicial predecible.

CTIC puede recuperar el acceso de coordinadores y cada coordinador el de usuarios de consulta de su sede. La nueva credencial es aleatoria, se muestra una sola vez, vence, revoca la anterior y deja auditoría con motivo.

## 4. Administración de usuarios

### Administrador CTIC

Debería poder crear y administrar únicamente coordinadores. Cada coordinador debe quedar asociado a una sede válida.

### Coordinador de sede

Debería poder crear y administrar usuarios `Usuario_Consulta` exclusivamente para su propia sede. Al crear o modificar la cuenta puede asignar:

- una etiqueta informativa;
- permisos de visualización;
- programas académicos observados en los datos de su sede;
- estado activo o inactivo.

Las operaciones sensibles conservan auditoría con actor, objetivo, sede, motivo y fecha.

## 5. Carga y administración de datos

El coordinador debería poder cargar archivos `.xlsx` indicando momento y año de cohorte. Los momentos válidos son 0, 1 y 5.

Durante la carga el backend:

1. valida el tipo y el contenido del archivo;
2. procesa las filas con Pandas;
3. resuelve dobles titulaciones conservando el registro con fecha de grado más reciente dentro de la carga;
4. guarda egresados y mediciones en una transacción; un documento existente no pierde nombre, apellido ni programa, y un egresado con corrección manual auditada conserva todos sus datos personales (ADR-014);
5. registra archivo, huella SHA-256, actor, sede, momento, cohorte, versión, estado y cantidad de registros;
6. reemplaza transaccionalmente la versión vigente cuando se vuelve a cargar el mismo alcance, serializa las cargas de la sede y rechaza con 409 un archivo idéntico a la versión vigente.

El historial solo debe mostrar las cargas de la sede autenticada. La eliminación se realiza por identificador de carga, solo aplica a la versión vigente, exige un motivo y conserva un evento de auditoría aun después de eliminar físicamente la carga. La versión reemplazada no se reactiva, y los egresados del directorio manual se conservan.

## 6. Directorio y perfil del egresado

El coordinador debería poder:

- buscar por documento, nombre o apellido;
- filtrar por programa;
- paginar el directorio;
- abrir la ficha de un egresado y consultar solamente las mediciones de su sede;
- crear un egresado manualmente;
- corregir nombre, apellido, programa o fecha de grado;
- eliminar un registro manual sin mediciones;
- exportar el directorio filtrado a Excel.

Las altas, ediciones y eliminaciones manuales exigen un motivo y se auditan. Una edición se bloquea si la misma identidad está vinculada a otra sede, y un egresado con mediciones no puede eliminarse desde el CRUD manual porque su origen debe corregirse o retirarse mediante la carga correspondiente.

Un registro manual pertenece al directorio de la sede que lo creó y no debe aparecer en otra sede.

## 7. Reportes y exploración

### Reporte general

Debería presentar, con datos de la sede autenticada:

- total de egresados;
- tasa descriptiva de empleabilidad;
- promedio salarial cuando existan respuestas utilizables;
- distribución por programa;
- indicadores disponibles de satisfacción.

### Tendencias

Debería comparar los momentos 0, 1 y 5 para los programas con mayor cantidad de datos. Permite alternar indicadores como empleabilidad, salario y satisfacción.

### Explorador de datos

Debería permitir seleccionar una pregunta y filtrar por momento, programa y año. El resultado se presenta como conteos agregados para Chart.js.

El backend solo ofrece y acepta variables del catálogo analítico RN-31; documentos, nombres, correos, teléfonos, fechas, identificadores y códigos administrativos se excluyen y se rechazan con 422 (EXP-02, cerrado el 2026-09-25).

**Desviación vigente:** solo mantiene una gráfica y no permite comparar varias visualizaciones simultáneamente (EXP-03).

Cuando existen varios intentos identificados para una persona y alcance, los indicadores actuales usan el intento más reciente. Las mediciones anónimas permitidas se conservan en los agregados.

Las gráficas de Reporte General, Tendencias y Explorador deberían poder descargarse como imágenes PNG.

## 8. Publicación de gráficas

Un coordinador debería poder publicar o retirar una gráfica agregada desde los dashboards privados.

Cada publicación conserva:

- sede y coordinador propietarios;
- programas incluidos;
- permiso requerido;
- definición de visualización;
- etiquetas y métricas numéricas recalculadas por el backend;
- versión, estado y fechas;
- confirmación explícita de privacidad del coordinador propietario.

El frontend envía solo la definición de la gráfica. El backend recalcula las métricas con los datos de la sede autenticada, deriva los programas de audiencia y agrupa u omite las celdas con menos de 5 observaciones; si no queda ninguna, rechaza la publicación con 422 (ADR-015). Por eso la gráfica publicada puede diferir de la privada.

La publicación nunca debe contener documentos, nombres, correos, respuestas abiertas ni archivos fuente. Los coordinadores pueden consultar las publicaciones vigentes y los usuarios de consulta solo reciben aquellas compatibles con sus permisos y programas. Una actualización crea una versión nueva y conserva la anterior como reemplazada.

**Corrección del 2026-09-25 (PUB-01/PUB-02), pendiente de validación manual:** publicar y retirar terminan siempre en éxito o error, el botón muestra `Publicando…`/`Retirando…`, no admite doble envío y, tras un error, ofrece `Reintentar publicación` con el motivo del backend (por ejemplo, datos insuficientes para el umbral). La vista de publicaciones resuelve datos, vacío o error con `Reintentar` y ofrece `Actualizar`.

Validación manual sugerida:

1. Como coordinador, publicar una gráfica: el botón cambia a `Publicando…` y luego muestra `Publicada vN` y `Retirar publicación` sin otra interacción.
2. Publicar un filtro con pocos datos: aparece el mensaje de datos insuficientes y el botón `Reintentar publicación`.
3. Detener el backend y publicar: aparece el mensaje de conexión y la acción puede reintentarse.
4. Como usuario de consulta autorizado, abrir `Gráficas publicadas`: aparece la gráfica. Con un usuario sin permiso o programa aparece el estado vacío.
5. Retirar la publicación y pulsar `Actualizar` como usuario de consulta: la gráfica deja de aparecer.

## 9. Analítica de textos y alertas

La pantalla **Analítica y alertas** debería funcionar para coordinadores y procesar únicamente datos de su sede.

El flujo implementado:

1. selecciona respuestas de campos abiertos;
2. anonimiza correos, números que puedan identificar a una persona y datos conocidos del egresado;
3. clasifica localmente menciones de comunicación, liderazgo, trabajo en equipo, tecnología y datos, idiomas, gestión de proyectos y adaptabilidad;
4. muestra únicamente conteos agregados;
5. genera alertas descriptivas cuando un programa tiene al menos tres respuestas válidas y empleabilidad inferior al 70 %, o cuando se repiten al menos tres expresiones negativas de inserción laboral.

Este procesamiento no envía texto a servicios externos y no devuelve las respuestas originales. Las alertas no son predicciones ni decisiones automáticas.

## 10. Capacidades operativas

El repositorio contiene:

- Dockerfiles separados para frontend y backend;
- Docker Compose con MySQL, frontend, backend y proxy;
- Nginx con redirección a HTTPS y HSTS;
- CORS configurable mediante `CORS_ALLOWED_ORIGINS`;
- endpoints `/api/health/live` y `/api/health/ready`;
- identificador de petición, estado y duración en logs, sin registrar cuerpos ni datos personales;
- respaldo lógico mediante `backup_database.py`;
- restauración con confirmación explícita mediante `restore_database.py`;
- procedimiento de despliegue y rollback documentado.

La infraestructura Docker no se ejecutó en el equipo de desarrollo porque Docker no está instalado. Los certificados, dominio, secretos y la prueba periódica de restauración deben configurarse y verificarse en el ambiente institucional.

## 11. Verificación disponible

La última revisión aprobó:

- 26 pruebas de backend;
- 15 pruebas de frontend;
- compilación productiva de Angular;
- sincronización entre FastAPI, OpenAPI y tipos TypeScript;
- validación de capas frontend, guards y tokens visuales;
- validación de enlaces y documentación;
- migración local aplicada hasta `g4c82a9d1e30`.

La compilación Angular mantiene advertencias no bloqueantes por tamaño del paquete inicial y del SCSS de carga de datos.

## 12. Lo que todavía no debe considerarse terminado

| Pendiente | Estado |
|---|---|
| Modelo predictivo RF-71 | En pausa. Producto debe aprobar objetivo, población, horizonte, métricas y criterios de aceptación conforme a ADR-009. |
| Auditoría individual RF-01 a RF-73 | La matriz agrupa capacidades; falta revisar cada requisito individualmente. |
| Simulacro Docker y restauración | Requiere infraestructura con Docker, certificados y una base aislada. |

## 13. Lista mínima de comprobación funcional

En un ambiente correctamente configurado deberían aprobarse estas comprobaciones:

1. Crear o sembrar el administrador y cambiar su contraseña temporal.
2. Crear un coordinador asociado a una sede.
3. Ingresar como coordinador y crear un usuario de consulta con permisos y programas.
4. Cargar un `.xlsx` válido y comprobar su aparición en el historial.
5. Confirmar que otro coordinador no pueda ver la carga, directorio ni perfil de esa sede.
6. Consultar Reporte General, Tendencias y Explorador.
7. Crear, editar y eliminar un egresado manual sin mediciones.
8. Descargar el directorio como Excel y una gráfica como PNG.
9. Publicar una gráfica y verificar su audiencia con un usuario de consulta autorizado y otro no autorizado.
10. Abrir Analítica y alertas y comprobar que la respuesta no contiene textos fuente.
11. Comprobar `health/live`, `health/ready`, respaldo y restauración en una base aislada.

## 14. Documentos relacionados

- [Comandos de desarrollo](00-comandos-desarrollo.md)
- [Configuración local](01-configuracion-local.md)
- [Estrategia de pruebas](03-estrategia-pruebas.md)
- [Seguridad y privacidad](04-seguridad-privacidad.md)
- [Runbook de despliegue y rollback](06-runbook-despliegue.md)
- [Backlog activo](../BACKLOG.md)
- [Matriz de trazabilidad](../requirements/matriz-trazabilidad.md)
