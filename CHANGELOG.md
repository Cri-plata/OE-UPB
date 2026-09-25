# Changelog

Este es el historial global del producto y el código del monorepo. Los cambios exclusivos de documentación se registran en [`OEUPB-Docs/CHANGELOG.md`](OEUPB-Docs/CHANGELOG.md).

## [Unreleased] - 2026-08-30
### Añadido (2026-09-24)
- **Higiene del repositorio:** se retiraron 73 scripts históricos ad hoc, se organizó un generador Excel reproducible y se cerraron la trazabilidad RF y las decisiones documentales pendientes.
- **Autenticación endurecida:** secreto obligatorio y robusto fuera de desarrollo, credenciales temporales con expiración, recuperación RBAC auditada y modo inicial aleatorio obligatorio en producción.
- **Directorio manual:** CRUD por sede con auditoría, motivo obligatorio, control de conflictos y exportación Excel.
- **Exportación visual:** Reporte General, Tendencias y Explorador descargan sus gráficas como PNG.
- **Analítica NLP:** clasificación local de competencias sobre texto anonimizado y alertas descriptivas de empleabilidad por programa.
- **Preparación productiva:** contenedores, proxy HTTPS, CORS por entorno, health checks, observabilidad, backup, restauración y runbook de rollback.
- **Arquitectura Angular:** El acceso HTTP se movió a clientes tipados de Data y las rutas ahora aplican guards de sesión y rol.
- **Design system:** Se consolidaron tokens CSS globales y una paleta única para Chart.js, con validación automática en CI.
- **Operación reproducible:** Dependencias Python fijadas, `.env.example`, migraciones, lockfile y procedimiento de inicialización desde cero.
- **Publicación de gráficas:** Los coordinadores pueden publicar o retirar instantáneas agregadas desde Reporte General, Tendencias y Explorador; coordinadores y usuarios de consulta disponen de una vista separada filtrada por audiencia.
- **Privacidad de publicaciones:** Las instantáneas son inmutables y versionadas, requieren aprobación explícita y contienen únicamente etiquetas y métricas numéricas, nunca datos fuente.
- **Contratos API:** OpenAPI genera los modelos TypeScript consumidos por Angular y una validación automática evita divergencias entre rutas, respuestas y clientes.
- **Datos:** Se añadió el catálogo persistente de sedes, relaciones obligatorias y soporte explícito de intentos de medición con política de selección por indicador.
- **Auditoría de cargas:** La eliminación física exige motivo, conserva un evento inmutable y evita reutilizar números de versión borrados.
- **Calidad:** Se consolidaron 19 pruebas de backend y 11 de frontend, más validaciones de contratos, documentación y compilación en CI.

### Añadido (2026-09-23)
- **RBAC:** Se implementaron `Admin_CTIC`, `Coordinador_Sede` y `Usuario_Consulta` con administración jerárquica y denegaciones 403.
- **Permisos:** Los usuarios de consulta almacenan etiqueta informativa, cuatro permisos y programas validados contra cargas visibles de su sede.
- **Cuentas:** Se añadieron desactivación/reactivación, borrado físico excepcional auditado y revocación inmediata mediante versión de autorización.
- **Aislamiento:** Directorio, perfiles, reportes, explorador y cargas restringen los datos privados al coordinador y a su sede.

### Añadido (2026-09-12)
- **Explorador de Datos**: Nuevo módulo de Business Intelligence (Generador de Reportes Dinámico) que permite cruzar cualquiera de las 53 preguntas del instrumento SNIES y visualizar los resultados en Barras, Dona, Pie o Líneas.
- **Tendencias**: Rediseño completo de la gráfica histórica implementando paletas vibrantes, áreas bajo la curva (Fill) y suavizado de líneas para una apariencia más profesional.
- **Backend (Tendencias)**: El endpoint de tendencias fue reconstruido para soportar y calcular matemáticamente la Empleabilidad, el Promedio Salarial y el Promedio de Satisfacción General de forma dinámica.

### Arreglado (2026-09-12)
- **Seguridad (Historial de Cargas)**: Se parchó una fuga de datos en la tabla del historial donde los Coordinadores podían ver archivos subidos por otras sedes. 
- **Seguridad (Carga de Datos)**: Se corrigió la regla de validación de duplicidad (HTTP 409 Conflict) para que esté aislada por Sedes (Multitenancy).
- **Reporte General**: Se reparó un Error Interno del Servidor (HTTP 500) causado por una variable no inicializada (`query_med`) durante la reestructuración de la base de datos.
- **Autenticación**: Se programó un manejador de excepciones (HTTP 401 Unauthorized) en el `jwt.interceptor.ts` del Frontend para que, al caducar el token JWT, el sistema limpie el caché de forma segura y redirija automáticamente a la pantalla de Login sin romper la interfaz gráfica.

### Añadido (2026-09-09)
- **Administración de Usuarios**: Se reestructuró la pestaña de Gestión de Accesos habilitándola también para los Coordinadores de Sede con un sistema de separación de deberes (Separation of Duties).
- **Seguridad (Creación de Usuarios)**: El rol CTIC ahora está estrictamente limitado a crear exclusivamente cuentas de `Coordinador_Sede`. Los Coordinadores, a su vez, son los únicos autorizados para crear `Directivos` y `Profesores` para su propia jurisdicción.
- **Seguridad (Invisibilidad CTIC)**: Las cuentas de nivel CTIC fueron removidas completamente de la tabla de visualización global (invisibles para todos, incluyendo para otros CTIC) para evitar manipulaciones operativas.
- **UX/UI (Formularios Dinámicos)**: El formulario de creación de usuarios ahora es reactivo a la sesión; autocompleta el rol para los CTIC y esconde la casilla de asignación de Sede para los Coordinadores, inyectándola por debajo para agilizar el registro.

- **Perfil de Usuario**: Nueva pestaña interactiva que muestra los datos de sesión, el rol, la sede asignada y los privilegios de seguridad del usuario autenticado.
- **Sedes**: Se añadió soporte oficial para la Seccional Bogotá (Sede 5) en los diccionarios internos de la aplicación.
- **Seguridad (Multitenancy)**: El sistema ahora cuenta con arquitectura multitenante. Todos los endpoints (Reportes, Directorio, Perfil, Carga) extraen la Sede del token JWT y limitan los datos mostrados exclusivamente a los de la jurisdicción del Coordinador que inicia sesión.

### Añadido (2026-09-04)
- **Directorio de Egresados**: Nuevo módulo de búsqueda, paginación y filtro de programas para inspeccionar la tabla de egresados.
- **Ficha del Egresado**: Nueva vista de perfil individual que muestra los detalles del estudiante y una línea de tiempo (Timeline) con su historial de encuestas y salarios en cada momento.
- **Carga de Datos**: La tabla del Historial de Cargas ahora se actualiza en tiempo real inmediatamente después de subir un archivo de Excel.

### Cambiado
- **Carga de Datos**: El algoritmo de extracción de Pandas fue flexibilizado para tolerar encuestas anónimas (estudiantes que no proveen documento) registrándolos en las métricas pero sin crear perfiles vacíos en el Directorio.
- **Carga de Datos**: El algoritmo ahora filtra e ignora automáticamente las filas basura o de "sumatorias/totales" ubicadas al final de los archivos Excel oficiales.
- **Enrutamiento**: Se migró de `RenderMode.Prerender` a `RenderMode.Client` en el servidor de Angular para prevenir errores de compilación con rutas paramétricas como `/perfil/:cedula`.


### Añadido
- **Reporte General**: Paleta de colores predeterminada dinámica (15 colores) para la gráfica de distribución por programa.
- **Reporte General**: El gráfico de *Nivel de Satisfacción* ahora permite personalizar el color de cada barra independientemente haciendo clic sobre ellas.
- **Tendencias**: Nuevo Panel de Control que permite cambiar el indicador a graficar (Empleabilidad, Salario, Satisfacción) y el tipo de gráfico (Líneas/Barras).
- **Tendencias**: Backend conectado para agrupar matemáticamente los resultados por Cohorte (Momento 0, 1 y 5).
- **Carga de Datos**: Tabla interactiva de *Historial de Cargas*, que muestra el número de egresados procesados por archivo.
- **Carga de Datos**: Nuevo selector obligatorio de **Año de Aplicación**, el cual se autogenera dinámicamente hasta el año actual, e incluye una opción para ingresar años antiguos manualmente.
- **Base de Datos**: Modificada la tabla `mediciones` para incluir la columna nativa `anio`.

### Cambiado
- **Reporte General**: El gráfico de radar fue sustituido por un gráfico de pastel para el *Nivel de Satisfacción*.
- **Carga de Datos**: El texto de las opciones de Momento de Medición fue simplificado visualmente (Ej. "Momento 0" en lugar de "Momento 0 (Grado)").

### Arreglado
- **Carga de Datos**: Prevención del error 500 al realizar consultas globales en la base de datos para el Historial.
- **Carga de Datos**: Botón de eliminación ahora desvincula los datos de forma exacta combinando el `momento` y el `anio`.
