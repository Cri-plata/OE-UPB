# Changelog

## [Unreleased] - 2026-08-30
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
