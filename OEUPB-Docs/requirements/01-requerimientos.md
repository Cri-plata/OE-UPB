# Requerimientos Clasificados

> **Estado:** requisitos objetivo. Un requisito documentado no implica que esté implementado. Consultar [`matriz-trazabilidad.md`](matriz-trazabilidad.md) para el estado verificado.

**Convención:** `Requerimiento Ligado` identifica dependencias funcionales directas; no sustituye la cobertura HU/CU/RN de la matriz de trazabilidad.

| Número de requisito | RF-01 |
|---|---|
| Nombre de requisito | El sistema debe permitir subir... |
| Tipo | ☑ Requisito | ☐ Restricción |
| Prioridad del requisito | ☑ Alta/Esencial | ☐ Media/Deseado | ☐ Baja/Opcional |
| Requerimiento Ligado | - |
| Descripción del requerimiento | El sistema debe permitir subir archivos de Excel con las encuestas del ministerio. |

| Número de requisito | RF-02 |
|---|---|
| Nombre de requisito | El sistema debe leer la... |
| Tipo | ☑ Requisito | ☐ Restricción |
| Prioridad del requisito | ☑ Alta/Esencial | ☐ Media/Deseado | ☐ Baja/Opcional |
| Requerimiento Ligado | RF-01 |
| Descripción del requerimiento | El sistema debe leer la información de las encuestas del momento de grado (Momento 0). |

| Número de requisito | RF-03 |
|---|---|
| Nombre de requisito | El sistema debe leer la... |
| Tipo | ☑ Requisito | ☐ Restricción |
| Prioridad del requisito | ☑ Alta/Esencial | ☐ Media/Deseado | ☐ Baja/Opcional |
| Requerimiento Ligado | RF-02 |
| Descripción del requerimiento | El sistema debe leer la información de las encuestas de seguimiento (Momento 1 y 5). |

| Número de requisito | RF-04 |
|---|---|
| Nombre de requisito | El sistema debe limpiar y... |
| Tipo | ☑ Requisito | ☐ Restricción |
| Prioridad del requisito | ☑ Alta/Esencial | ☐ Media/Deseado | ☐ Baja/Opcional |
| Requerimiento Ligado | RF-01 |
| Descripción del requerimiento | El sistema debe limpiar y organizar los datos al cargar el archivo. |

| Número de requisito | RF-05 |
|---|---|
| Nombre de requisito | El sistema debe guardar toda... |
| Tipo | ☑ Requisito | ☐ Restricción |
| Prioridad del requisito | ☑ Alta/Esencial | ☐ Media/Deseado | ☐ Baja/Opcional |
| Requerimiento Ligado | RF-04 |
| Descripción del requerimiento | El sistema debe guardar toda la información en una base de datos central. |

| Número de requisito | RF-06 |
|---|---|
| Nombre de requisito | El sistema debe evitar guardar... |
| Tipo | ☑ Requisito | ☐ Restricción |
| Prioridad del requisito | ☑ Alta/Esencial | ☐ Media/Deseado | ☐ Baja/Opcional |
| Requerimiento Ligado | RF-04, RF-05 |
| Descripción del requerimiento | El sistema debe evitar guardar registros duplicados de un mismo egresado. |

| Número de requisito | RF-07 |
|---|---|
| Nombre de requisito | El sistema debe registrar la... |
| Tipo | ☑ Requisito | ☐ Restricción |
| Prioridad del requisito | ☑ Alta/Esencial | ☐ Media/Deseado | ☐ Baja/Opcional |
| Requerimiento Ligado | RF-01 |
| Descripción del requerimiento | El sistema debe registrar cada archivo como una carga auditable con identificador, fecha y hora, actor, sede, momento, año de grado, nombre o huella del archivo, estado, versión, resultado y mediciones afectadas. |

| Número de requisito | RF-08 |
|---|---|
| Nombre de requisito | El sistema debe permitir cargar... |
| Tipo | ☑ Requisito | ☐ Restricción |
| Prioridad del requisito | ☑ Alta/Esencial | ☐ Media/Deseado | ☐ Baja/Opcional |
| Requerimiento Ligado | RF-07 |
| Descripción del requerimiento | El sistema debe permitir cargar información histórica desde bases de datos antiguas |

| Número de requisito | RF-09 |
|---|---|
| Nombre de requisito | El sistema debe confirmar con... |
| Tipo | ☑ Requisito | ☐ Restricción |
| Prioridad del requisito | ☑ Alta/Esencial | ☐ Media/Deseado | ☐ Baja/Opcional |
| Requerimiento Ligado | RF-08 |
| Descripción del requerimiento | El sistema debe confirmar si la carga fue exitosa o detallar los errores. Una recarga de la misma sede, momento y año de grado debe reemplazar la versión vigente dentro de una sola transacción; ante cualquier fallo debe conservarse intacta la versión anterior. |

| Número de requisito | RF-10 |
|---|---|
| Nombre de requisito | El sistema debe permitir registrar... |
| Tipo | ☑ Requisito | ☐ Restricción |
| Prioridad del requisito | ☑ Alta/Esencial | ☐ Media/Deseado | ☐ Baja/Opcional |
| Requerimiento Ligado | RF-09 |
| Descripción del requerimiento | El sistema debe permitir registrar nuevos egresados de forma manual. |

| Número de requisito | RF-11 |
|---|---|
| Nombre de requisito | El sistema debe permitir editar... |
| Tipo | ☑ Requisito | ☐ Restricción |
| Prioridad del requisito | ☑ Alta/Esencial | ☐ Media/Deseado | ☐ Baja/Opcional |
| Requerimiento Ligado | RF-10 |
| Descripción del requerimiento | El sistema debe permitir editar o corregir la información de un egresado. |

| Número de requisito | RF-12 |
|---|---|
| Nombre de requisito | El sistema debe permitir borrar... |
| Tipo | ☑ Requisito | ☐ Restricción |
| Prioridad del requisito | ☑ Alta/Esencial | ☐ Media/Deseado | ☐ Baja/Opcional |
| Requerimiento Ligado | RF-11 |
| Descripción del requerimiento | El sistema debe permitir borrar registros si es necesario. |

| Número de requisito | RF-13 |
|---|---|
| Nombre de requisito | El sistema debe permitir organizar... |
| Tipo | ☑ Requisito | ☐ Restricción |
| Prioridad del requisito | ☑ Alta/Esencial | ☐ Media/Deseado | ☐ Baja/Opcional |
| Requerimiento Ligado | RF-04 |
| Descripción del requerimiento | El sistema debe permitir organizar a los egresados según su ceremonia de grado |

| Número de requisito | RF-14 |
|---|---|
| Nombre de requisito | El sistema debe permitir buscar... |
| Tipo | ☑ Requisito | ☐ Restricción |
| Prioridad del requisito | ☑ Alta/Esencial | ☐ Media/Deseado | ☐ Baja/Opcional |
| Requerimiento Ligado | RF-13 |
| Descripción del requerimiento | El sistema debe permitir buscar a un egresado por su nombre. |

| Número de requisito | RF-15 |
|---|---|
| Nombre de requisito | El sistema debe permitir buscar... |
| Tipo | ☑ Requisito | ☐ Restricción |
| Prioridad del requisito | ☑ Alta/Esencial | ☐ Media/Deseado | ☐ Baja/Opcional |
| Requerimiento Ligado | RF-14 |
| Descripción del requerimiento | El sistema debe permitir buscar a un egresado por su número de identificación. |

| Número de requisito | RF-16 |
|---|---|
| Nombre de requisito | El sistema debe permitir agrupar... |
| Tipo | ☑ Requisito | ☐ Restricción |
| Prioridad del requisito | ☑ Alta/Esencial | ☐ Media/Deseado | ☐ Baja/Opcional |
| Requerimiento Ligado | RF-04 |
| Descripción del requerimiento | El sistema debe permitir agrupar a los egresados según el programa que estudiaron. |

| Número de requisito | RF-17 |
|---|---|
| Nombre de requisito | El sistema debe permitir actualizar... |
| Tipo | ☑ Requisito | ☐ Restricción |
| Prioridad del requisito | ☑ Alta/Esencial | ☐ Media/Deseado | ☐ Baja/Opcional |
| Requerimiento Ligado | RF-04 |
| Descripción del requerimiento | El sistema debe permitir actualizar el estado principal del egresado usando el catálogo: empleado, independiente, estudiante o sin empleo. Cuando aplique, la formalidad del empleo se registra como un atributo separado. |

| Número de requisito | RF-18 |
|---|---|
| Nombre de requisito | El sistema debe tener un... |
| Tipo | ☑ Requisito | ☐ Restricción |
| Prioridad del requisito | ☑ Alta/Esencial | ☐ Media/Deseado | ☐ Baja/Opcional |
| Requerimiento Ligado | RF-05 |
| Descripción del requerimiento | El sistema debe tener un panel visual interactivo (dashboard). |

| Número de requisito | RF-19 |
|---|---|
| Nombre de requisito | El panel debe mostrar gráficos... |
| Tipo | ☑ Requisito | ☐ Restricción |
| Prioridad del requisito | ☑ Alta/Esencial | ☐ Media/Deseado | ☐ Baja/Opcional |
| Requerimiento Ligado | RF-18 |
| Descripción del requerimiento | El panel debe mostrar gráficos sobre la situación laboral actual de los egresados. |

| Número de requisito | RF-20 |
|---|---|
| Nombre de requisito | El panel debe mostrar gráficos... |
| Tipo | ☑ Requisito | ☐ Restricción |
| Prioridad del requisito | ☑ Alta/Esencial | ☐ Media/Deseado | ☐ Baja/Opcional |
| Requerimiento Ligado | RF-19 |
| Descripción del requerimiento | El panel debe mostrar gráficos sobre los estudios adicionales que realizan los egresados. El estado laboral se presenta por separado conforme al catálogo definido en RF-17. |

| Número de requisito | RF-21 |
|---|---|
| Nombre de requisito | El panel debe tener un... |
| Tipo | ☑ Requisito | ☐ Restricción |
| Prioridad del requisito | ☑ Alta/Esencial | ☐ Media/Deseado | ☐ Baja/Opcional |
| Requerimiento Ligado | RF-18 |
| Descripción del requerimiento | El panel debe tener un filtro para ver solo los datos de un programa académico específico |

| Número de requisito | RF-22 |
|---|---|
| Nombre de requisito | El panel debe tener un... |
| Tipo | ☑ Requisito | ☐ Restricción |
| Prioridad del requisito | ☑ Alta/Esencial | ☐ Media/Deseado | ☐ Baja/Opcional |
| Requerimiento Ligado | RF-18 |
| Descripción del requerimiento | El panel debe tener un filtro para ver los datos según el año de grado o cohorte. El año informado durante la carga representa siempre este año de grado. |

| Número de requisito | RF-23 |
|---|---|
| Nombre de requisito | El panel debe tener un... |
| Tipo | ☑ Requisito | ☐ Restricción |
| Prioridad del requisito | ☑ Alta/Esencial | ☐ Media/Deseado | ☐ Baja/Opcional |
| Requerimiento Ligado | RF-18 |
| Descripción del requerimiento | El panel debe permitir agrupar por situación laboral: empleado, independiente, estudiante o sin empleo. |

| Número de requisito | RF-24 |
|---|---|
| Nombre de requisito | El panel debe mostrar líneas... |
| Tipo | ☑ Requisito | ☐ Restricción |
| Prioridad del requisito | ☑ Alta/Esencial | ☐ Media/Deseado | ☐ Baja/Opcional |
| Requerimiento Ligado | RF-18 |
| Descripción del requerimiento | El panel debe mostrar líneas de tiempo para ver tendencias de empleo. |

| Número de requisito | RF-25 |
|---|---|
| Nombre de requisito | El sistema debe calcular y... |
| Tipo | ☑ Requisito | ☐ Restricción |
| Prioridad del requisito | ☑ Alta/Esencial | ☐ Media/Deseado | ☐ Baja/Opcional |
| Requerimiento Ligado | RF-24 |
| Descripción del requerimiento | El sistema debe calcular y mostrar el porcentaje de egresados con trabajo formal. |

| Número de requisito | RF-26 |
|---|---|
| Nombre de requisito | El sistema debe mostrar el... |
| Tipo | ☑ Requisito | ☐ Restricción |
| Prioridad del requisito | ☑ Alta/Esencial | ☐ Media/Deseado | ☐ Baja/Opcional |
| Requerimiento Ligado | RF-25 |
| Descripción del requerimiento | El sistema debe mostrar el rango de salario promedio reportado. |

| Número de requisito | RF-27 |
|---|---|
| Nombre de requisito | El panel debe mostrar un... |
| Tipo | ☑ Requisito | ☐ Restricción |
| Prioridad del requisito | ☑ Alta/Esencial | ☐ Media/Deseado | ☐ Baja/Opcional |
| Requerimiento Ligado | RF-26 |
| Descripción del requerimiento | El panel debe mostrar un gráfico con los sectores económicos donde trabajan los egresados. |

| Número de requisito | RF-28 |
|---|---|
| Nombre de requisito | El panel debe mostrar de... |
| Tipo | ☑ Requisito | ☐ Restricción |
| Prioridad del requisito | ☑ Alta/Esencial | ☐ Media/Deseado | ☐ Baja/Opcional |
| Requerimiento Ligado | RF-27 |
| Descripción del requerimiento | El panel debe mostrar de forma visual cómo se distribuyen los datos (dispersión). |

| Número de requisito | RF-29 |
|---|---|
| Nombre de requisito | El panel debe mostrar un... |
| Tipo | ☑ Requisito | ☐ Restricción |
| Prioridad del requisito | ☑ Alta/Esencial | ☐ Media/Deseado | ☐ Baja/Opcional |
| Requerimiento Ligado | RF-28 |
| Descripción del requerimiento | El panel debe mostrar un mapa o gráfico con las ciudades donde viven los egresados. |

| Número de requisito | RF-30 |
|---|---|
| Nombre de requisito | El sistema debe crear gráficas... |
| Tipo | ☑ Requisito | ☐ Restricción |
| Prioridad del requisito | ☑ Alta/Esencial | ☐ Media/Deseado | ☐ Baja/Opcional |
| Requerimiento Ligado | RF-18 |
| Descripción del requerimiento | El sistema debe crear gráficas sobre la satisfacción del egresado con la universidad. |

| Número de requisito | RNF-01 |
|---|---|
| Nombre de requisito | El panel debe ser fácil... |
| Tipo | ☐ Requisito | ☑ Restricción |
| Prioridad del requisito | ☑ Alta/Esencial | ☐ Media/Deseado | ☐ Baja/Opcional |
| Requerimiento Ligado | RF-18 |
| Descripción del requerimiento | El panel debe ser fácil de entender para ayudar a la universidad a tomar decisiones. |

| Número de requisito | RF-31 |
|---|---|
| Nombre de requisito | El sistema debe sugerir tendencias... |
| Tipo | ☑ Requisito | ☐ Restricción |
| Prioridad del requisito | ☑ Alta/Esencial | ☐ Media/Deseado | ☐ Baja/Opcional |
| Requerimiento Ligado | RF-18, RF-67 |
| Descripción del requerimiento | El sistema debe sugerir tendencias de cursos o programas nuevos basados en los datos |

| Número de requisito | RNF-02 |
|---|---|
| Nombre de requisito | El sistema debe poder usarse... |
| Tipo | ☐ Requisito | ☑ Restricción |
| Prioridad del requisito | ☑ Alta/Esencial | ☐ Media/Deseado | ☐ Baja/Opcional |
| Requerimiento Ligado | RF-04 |
| Descripción del requerimiento | El sistema debe poder usarse desde los navegadores de internet definidos como compatibles en la estrategia de pruebas (versión web). |

| Número de requisito | RNF-03 |
|---|---|
| Nombre de requisito | El sistema debe verse y... |
| Tipo | ☐ Requisito | ☑ Restricción |
| Prioridad del requisito | ☑ Alta/Esencial | ☐ Media/Deseado | ☐ Baja/Opcional |
| Requerimiento Ligado | RF-04 |
| Descripción del requerimiento | El sistema debe verse y funcionar correctamente en teléfonos celulares (versión móvil). |

| Número de requisito | RF-32 |
|---|---|
| Nombre de requisito | El sistema debe pedir un... |
| Tipo | ☑ Requisito | ☐ Restricción |
| Prioridad del requisito | ☑ Alta/Esencial | ☐ Media/Deseado | ☐ Baja/Opcional |
| Requerimiento Ligado | - |
| Descripción del requerimiento | El sistema debe pedir un usuario y contraseña para poder entrar. |

| Número de requisito | RF-33 |
|---|---|
| Nombre de requisito | Alcance operativo del coordinador de sede |
| Tipo | ☑ Requisito | ☐ Restricción |
| Prioridad del requisito | ☑ Alta/Esencial | ☐ Media/Deseado | ☐ Baja/Opcional |
| Requerimiento Ligado | RF-32 |
| Descripción del requerimiento | El coordinador de sede debe administrar las encuestas de su propia sede, gestionar sus usuarios de consulta y publicar o retirar gráficas agregadas. No puede crear otros coordinadores ni acceder a datos fuente de otra sede. |

| Número de requisito | RNF-04 |
|---|---|
| Nombre de requisito | El sistema debe tener menús... |
| Tipo | ☐ Requisito | ☑ Restricción |
| Prioridad del requisito | ☑ Alta/Esencial | ☐ Media/Deseado | ☐ Baja/Opcional |
| Requerimiento Ligado | RF-01 |
| Descripción del requerimiento | El sistema debe tener menús sencillos y botones claros. |

| Número de requisito | RNF-05 |
|---|---|
| Nombre de requisito | El sistema debe estar diseñado... |
| Tipo | ☐ Requisito | ☑ Restricción |
| Prioridad del requisito | ☑ Alta/Esencial | ☐ Media/Deseado | ☐ Baja/Opcional |
| Requerimiento Ligado | RF-01 |
| Descripción del requerimiento | El sistema debe estar diseñado para poder crecer y usarse en otras sedes de la universidad. |

| Número de requisito | RF-34 |
|---|---|
| Nombre de requisito | Aislamiento de datos fuente por sede |
| Tipo | ☑ Requisito | ☐ Restricción |
| Prioridad del requisito | ☑ Alta/Esencial | ☐ Media/Deseado | ☐ Baja/Opcional |
| Requerimiento Ligado | RF-33 |
| Descripción del requerimiento | El sistema debe identificar la sede propietaria de cada encuesta y aplicar ese alcance en consultas, gráficas y permisos. Los datos fuente no pueden cruzar sedes. |

| Número de requisito | RNF-06 |
|---|---|
| Nombre de requisito | El sistema debe soportar el... |
| Tipo | ☐ Requisito | ☑ Restricción |
| Prioridad del requisito | ☑ Alta/Esencial | ☐ Media/Deseado | ☐ Baja/Opcional |
| Requerimiento Ligado | RF-33 |
| Descripción del requerimiento | El sistema debe soportar el almacenamiento de miles de encuestas nuevas cada año sin ponerse lento. |

| Número de requisito | RF-35 |
|---|---|
| Nombre de requisito | Consulta de gráficas publicadas por otras sedes |
| Tipo | ☑ Requisito | ☐ Restricción |
| Prioridad del requisito | ☑ Alta/Esencial | ☐ Media/Deseado | ☐ Baja/Opcional |
| Requerimiento Ligado | RF-33, RF-34 |
| Descripción del requerimiento | El sistema debe permitir consultar en una vista común las gráficas y métricas agregadas que los coordinadores de otras sedes hayan publicado. La vista no debe unir ni exponer datos fuente o respuestas individuales. |

| Número de requisito | RF-36 |
|---|---|
| Nombre de requisito | Administración jerárquica de cuentas |
| Tipo | ☑ Requisito | ☐ Restricción |
| Prioridad del requisito | ☑ Alta/Esencial | ☐ Media/Deseado | ☐ Baja/Opcional |
| Requerimiento Ligado | RF-33 |
| Descripción del requerimiento | El Admin CTIC debe crear las cuentas de Coordinador de Sede. Cada coordinador debe crear y administrar únicamente usuarios de consulta de su propia sede. |

| Número de requisito | RF-37 |
|---|---|
| Nombre de requisito | Permitir asignar permisos y programas... |
| Tipo | ☑ Requisito | ☐ Restricción |
| Prioridad del requisito | ☑ Alta/Esencial | ☐ Media/Deseado | ☐ Baja/Opcional |
| Requerimiento Ligado | RF-36 |
| Descripción del requerimiento | Al crear un usuario de consulta, el coordinador debe asignarle manualmente programas y permisos de visualización. Las etiquetas rector, profesor y administrativo son informativas y no conceden privilegios implícitos. El backend debe mostrar únicamente las gráficas publicadas compatibles con los permisos y programas asignados. Los coordinadores, por su rol técnico, pueden ver todas las publicadas. |

| Número de requisito | RF-38 |
|---|---|
| Nombre de requisito | El sistema debe guardar el... |
| Tipo | ☑ Requisito | ☐ Restricción |
| Prioridad del requisito | ☑ Alta/Esencial | ☐ Media/Deseado | ☐ Baja/Opcional |
| Requerimiento Ligado | RF-04, RF-05 |
| Descripción del requerimiento | El sistema debe guardar el nivel de satisfacción del estudiante con sus profesores. |

| Número de requisito | RF-39 |
|---|---|
| Nombre de requisito | El sistema debe registrar si... |
| Tipo | ☑ Requisito | ☐ Restricción |
| Prioridad del requisito | ☑ Alta/Esencial | ☐ Media/Deseado | ☐ Baja/Opcional |
| Requerimiento Ligado | RF-04 |
| Descripción del requerimiento | El sistema debe registrar si el egresado tuvo que trabajar mientras estudiaba. |

| Número de requisito | RF-40 |
|---|---|
| Nombre de requisito | El sistema debe guardar la... |
| Tipo | ☑ Requisito | ☐ Restricción |
| Prioridad del requisito | ☑ Alta/Esencial | ☐ Media/Deseado | ☐ Baja/Opcional |
| Requerimiento Ligado | RF-04, RF-05 |
| Descripción del requerimiento | El sistema debe guardar la opinión del estudiante sobre las instalaciones (salones, biblioteca). |

| Número de requisito | RF-41 |
|---|---|
| Nombre de requisito | El sistema debe registrar las... |
| Tipo | ☑ Requisito | ☐ Restricción |
| Prioridad del requisito | ☑ Alta/Esencial | ☐ Media/Deseado | ☐ Baja/Opcional |
| Requerimiento Ligado | RF-04 |
| Descripción del requerimiento | El sistema debe registrar las habilidades que el estudiante siente que mejoró |

| Número de requisito | RF-42 |
|---|---|
| Nombre de requisito | El sistema debe guardar los... |
| Tipo | ☑ Requisito | ☐ Restricción |
| Prioridad del requisito | ☑ Alta/Esencial | ☐ Media/Deseado | ☐ Baja/Opcional |
| Requerimiento Ligado | RF-04, RF-05 |
| Descripción del requerimiento | El sistema debe guardar los planes que tenía el estudiante justo al graduarse. |

| Número de requisito | RF-43 |
|---|---|
| Nombre de requisito | El sistema debe registrar si... |
| Tipo | ☑ Requisito | ☐ Restricción |
| Prioridad del requisito | ☑ Alta/Esencial | ☐ Media/Deseado | ☐ Baja/Opcional |
| Requerimiento Ligado | RF-42 |
| Descripción del requerimiento | El sistema debe registrar si el egresado vive en una ciudad diferente a donde estudió. |

| Número de requisito | RF-44 |
|---|---|
| Nombre de requisito | El sistema debe guardar el... |
| Tipo | ☑ Requisito | ☐ Restricción |
| Prioridad del requisito | ☑ Alta/Esencial | ☐ Media/Deseado | ☐ Baja/Opcional |
| Requerimiento Ligado | RF-04, RF-05 |
| Descripción del requerimiento | El sistema debe guardar el motivo principal por el cual un egresado cambió de ciudad. |

| Número de requisito | RF-45 |
|---|---|
| Nombre de requisito | El sistema debe registrar el... |
| Tipo | ☑ Requisito | ☐ Restricción |
| Prioridad del requisito | ☑ Alta/Esencial | ☐ Media/Deseado | ☐ Baja/Opcional |
| Requerimiento Ligado | RF-44 |
| Descripción del requerimiento | El sistema debe registrar el tiempo (en meses) que tardó en conseguir su primer empleo. |

| Número de requisito | RF-46 |
|---|---|
| Nombre de requisito | El sistema debe almacenar el... |
| Tipo | ☑ Requisito | ☐ Restricción |
| Prioridad del requisito | ☑ Alta/Esencial | ☐ Media/Deseado | ☐ Baja/Opcional |
| Requerimiento Ligado | RF-45 |
| Descripción del requerimiento | El sistema debe almacenar el tipo de contrato que tiene el egresado en su trabajo. |

| Número de requisito | RF-47 |
|---|---|
| Nombre de requisito | El sistema debe registrar en... |
| Tipo | ☑ Requisito | ☐ Restricción |
| Prioridad del requisito | ☑ Alta/Esencial | ☐ Media/Deseado | ☐ Baja/Opcional |
| Requerimiento Ligado | RF-46 |
| Descripción del requerimiento | El sistema debe registrar en qué medida le sirvió lo aprendido en la universidad para su trabajo. |

| Número de requisito | RF-48 |
|---|---|
| Nombre de requisito | El sistema debe guardar información... |
| Tipo | ☑ Requisito | ☐ Restricción |
| Prioridad del requisito | ☑ Alta/Esencial | ☐ Media/Deseado | ☐ Baja/Opcional |
| Requerimiento Ligado | RF-04, RF-05 |
| Descripción del requerimiento | El sistema debe guardar información sobre negocios o empresas creadas por el egresado. |

| Número de requisito | RF-49 |
|---|---|
| Nombre de requisito | El sistema debe registrar la... |
| Tipo | ☑ Requisito | ☐ Restricción |
| Prioridad del requisito | ☑ Alta/Esencial | ☐ Media/Deseado | ☐ Baja/Opcional |
| Requerimiento Ligado | RF-48 |
| Descripción del requerimiento | El sistema debe registrar la principal dificultad del egresado al buscar trabajo. |

| Número de requisito | RF-50 |
|---|---|
| Nombre de requisito | El sistema debe registrar si... |
| Tipo | ☑ Requisito | ☐ Restricción |
| Prioridad del requisito | ☑ Alta/Esencial | ☐ Media/Deseado | ☐ Baja/Opcional |
| Requerimiento Ligado | RF-04 |
| Descripción del requerimiento | El sistema debe registrar si el egresado ha viajado al exterior por motivos académicos. |

| Número de requisito | RF-51 |
|---|---|
| Nombre de requisito | El sistema debe guardar el... |
| Tipo | ☑ Requisito | ☐ Restricción |
| Prioridad del requisito | ☑ Alta/Esencial | ☐ Media/Deseado | ☐ Baja/Opcional |
| Requerimiento Ligado | RF-04, RF-05 |
| Descripción del requerimiento | El sistema debe guardar el medio o canal por el cual el egresado consiguió su empleo |

| Número de requisito | RF-52 |
|---|---|
| Nombre de requisito | El sistema debe unir las... |
| Tipo | ☑ Requisito | ☐ Restricción |
| Prioridad del requisito | ☑ Alta/Esencial | ☐ Media/Deseado | ☐ Baja/Opcional |
| Requerimiento Ligado | RF-02 |
| Descripción del requerimiento | El sistema debe unir las respuestas del grado (Momento 0) con las respuestas posteriores (Momento 1 y 5) usando el documento de identidad. |

| Número de requisito | RF-53 |
|---|---|
| Nombre de requisito | El sistema debe analizar los... |
| Tipo | ☑ Requisito | ☐ Restricción |
| Prioridad del requisito | ☑ Alta/Esencial | ☐ Media/Deseado | ☐ Baja/Opcional |
| Requerimiento Ligado | RF-02 |
| Descripción del requerimiento | El sistema debe analizar los cambios de ciudad o país entre el momento de estudio, el primer empleo y la residencia actual. |

| Número de requisito | RF-54 |
|---|---|
| Nombre de requisito | El sistema debe comparar el... |
| Tipo | ☑ Requisito | ☐ Restricción |
| Prioridad del requisito | ☑ Alta/Esencial | ☐ Media/Deseado | ☐ Baja/Opcional |
| Requerimiento Ligado | RF-53 |
| Descripción del requerimiento | El sistema debe comparar el nivel de formación del egresado con el nivel de estudio que realmente le exige su trabajo actual. |

| Número de requisito | RF-55 |
|---|---|
| Nombre de requisito | El sistema debe relacionar las... |
| Tipo | ☑ Requisito | ☐ Restricción |
| Prioridad del requisito | ☑ Alta/Esencial | ☐ Media/Deseado | ☐ Baja/Opcional |
| Requerimiento Ligado | RF-04 |
| Descripción del requerimiento | El sistema debe relacionar las fuentes de financiación de la carrera con la situación laboral actual. |

| Número de requisito | RF-56 |
|---|---|
| Nombre de requisito | El sistema debe crear tablas... |
| Tipo | ☑ Requisito | ☐ Restricción |
| Prioridad del requisito | ☑ Alta/Esencial | ☐ Media/Deseado | ☐ Baja/Opcional |
| Requerimiento Ligado | RF-55 |
| Descripción del requerimiento | El sistema debe crear tablas que cuenten la cantidad de egresados por programa y año de grado |

| Número de requisito | RF-57 |
|---|---|
| Nombre de requisito | El sistema debe generar una... |
| Tipo | ☑ Requisito | ☐ Restricción |
| Prioridad del requisito | ☑ Alta/Esencial | ☐ Media/Deseado | ☐ Baja/Opcional |
| Requerimiento Ligado | RF-56 |
| Descripción del requerimiento | El sistema debe generar una tabla que calcule el promedio de meses que tardan los egresados en conseguir su primer empleo. |

| Número de requisito | RF-58 |
|---|---|
| Nombre de requisito | El sistema debe agrupar en... |
| Tipo | ☑ Requisito | ☐ Restricción |
| Prioridad del requisito | ☑ Alta/Esencial | ☐ Media/Deseado | ☐ Baja/Opcional |
| Requerimiento Ligado | RF-57 |
| Descripción del requerimiento | El sistema debe agrupar en una tabla los sectores económicos y tamaños de empresa donde más trabajan los egresados. |

| Número de requisito | RF-59 |
|---|---|
| Nombre de requisito | El sistema debe mostrar tablas... |
| Tipo | ☑ Requisito | ☐ Restricción |
| Prioridad del requisito | ☑ Alta/Esencial | ☐ Media/Deseado | ☐ Baja/Opcional |
| Requerimiento Ligado | RF-58 |
| Descripción del requerimiento | El sistema debe mostrar tablas resumen con las principales áreas de conocimiento que los egresados sienten que deben mejorar. |

| Número de requisito | RF-60 |
|---|---|
| Nombre de requisito | El sistema debe calcular y... |
| Tipo | ☑ Requisito | ☐ Restricción |
| Prioridad del requisito | ☑ Alta/Esencial | ☐ Media/Deseado | ☐ Baja/Opcional |
| Requerimiento Ligado | RF-59 |
| Descripción del requerimiento | El sistema debe calcular y tabular los promedios de satisfacción laboral (ingreso, horas, estabilidad, retos). |

| Número de requisito | RF-61 |
|---|---|
| Nombre de requisito | El sistema debe mostrar gráficas... |
| Tipo | ☑ Requisito | ☐ Restricción |
| Prioridad del requisito | ☑ Alta/Esencial | ☐ Media/Deseado | ☐ Baja/Opcional |
| Requerimiento Ligado | RF-18 |
| Descripción del requerimiento | El sistema debe mostrar gráficas que comparen el porcentaje de egresados empleados, independientes, estudiantes o sin empleo. |

| Número de requisito | RF-62 |
|---|---|
| Nombre de requisito | El sistema debe aplicar cálculos... |
| Tipo | ☑ Requisito | ☐ Restricción |
| Prioridad del requisito | ☑ Alta/Esencial | ☐ Media/Deseado | ☐ Baja/Opcional |
| Requerimiento Ligado | RF-04 |
| Descripción del requerimiento | El sistema debe aplicar cálculos de dispersión para graficar qué tan variados son los ingresos salariales entre egresados de un mismo programa. |

| Número de requisito | RF-63 |
|---|---|
| Nombre de requisito | El sistema debe graficar los... |
| Tipo | ☑ Requisito | ☐ Restricción |
| Prioridad del requisito | ☑ Alta/Esencial | ☐ Media/Deseado | ☐ Baja/Opcional |
| Requerimiento Ligado | RF-04 |
| Descripción del requerimiento | El sistema debe graficar los canales de búsqueda de empleo para identificar los más efectivos (redes sociales, conocidos, portales web). |

| Número de requisito | RF-64 |
|---|---|
| Nombre de requisito | El sistema debe generar gráficas... |
| Tipo | ☑ Requisito | ☐ Restricción |
| Prioridad del requisito | ☑ Alta/Esencial | ☐ Media/Deseado | ☐ Baja/Opcional |
| Requerimiento Ligado | RF-18 |
| Descripción del requerimiento | El sistema debe generar gráficas que muestren qué tan útiles resultaron los conocimientos aprendidos en la universidad para el trabajo actual. |

| Número de requisito | RF-65 |
|---|---|
| Nombre de requisito | El sistema debe mostrar en... |
| Tipo | ☑ Requisito | ☐ Restricción |
| Prioridad del requisito | ☑ Alta/Esencial | ☐ Media/Deseado | ☐ Baja/Opcional |
| Requerimiento Ligado | RF-18 |
| Descripción del requerimiento | El sistema debe mostrar en gráficas de barras las razones principales por las que los egresados recomiendan o no la universidad. |

| Número de requisito | RF-66 |
|---|---|
| Nombre de requisito | El sistema debe graficar las... |
| Tipo | ☑ Requisito | ☐ Restricción |
| Prioridad del requisito | ☑ Alta/Esencial | ☐ Media/Deseado | ☐ Baja/Opcional |
| Requerimiento Ligado | RF-04 |
| Descripción del requerimiento | El sistema debe graficar las herramientas institucionales que más ayudaron a quienes decidieron crear su propia empresa. |

| Número de requisito | RF-67 |
|---|---|
| Nombre de requisito | El sistema debe resaltar en... |
| Tipo | ☑ Requisito | ☐ Restricción |
| Prioridad del requisito | ☑ Alta/Esencial | ☐ Media/Deseado | ☐ Baja/Opcional |
| Requerimiento Ligado | RF-04 |
| Descripción del requerimiento | El sistema debe resaltar en el panel visual las tendencias de los nuevos estudios o cursos que están tomando los egresados. |

| Número de requisito | RF-68 |
|---|---|
| Nombre de requisito | El sistema debe identificar y... |
| Tipo | ☑ Requisito | ☐ Restricción |
| Prioridad del requisito | ☑ Alta/Esencial | ☐ Media/Deseado | ☐ Baja/Opcional |
| Requerimiento Ligado | RF-18 |
| Descripción del requerimiento | El sistema debe identificar y mostrar gráficamente hacia qué ciudades o países se están yendo los egresados a trabajar o estudiar. |

| Número de requisito | RF-69 |
|---|---|
| Nombre de requisito | El sistema debe permitir descargar... |
| Tipo | ☑ Requisito | ☐ Restricción |
| Prioridad del requisito | ☑ Alta/Esencial | ☐ Media/Deseado | ☐ Baja/Opcional |
| Requerimiento Ligado | RF-01 |
| Descripción del requerimiento | El sistema debe permitir descargar estas tablas de análisis en formato Excel. |

| Número de requisito | RF-70 |
|---|---|
| Nombre de requisito | El sistema debe permitir exportar... |
| Tipo | ☑ Requisito | ☐ Restricción |
| Prioridad del requisito | ☑ Alta/Esencial | ☐ Media/Deseado | ☐ Baja/Opcional |
| Requerimiento Ligado | RF-18 |
| Descripción del requerimiento | El sistema debe permitir exportar las gráficas como imágenes para usarlas en informes. |

| Número de requisito | RF-71 |
|---|---|
| Nombre de requisito | El modelo de IA debe... |
| Tipo | ☑ Requisito | ☐ Restricción |
| Prioridad del requisito | ☑ Alta/Esencial | ☐ Media/Deseado | ☐ Baja/Opcional |
| Requerimiento Ligado | RF-04 |
| Descripción del requerimiento | **En pausa por decisión de producto.** No se implementará un modelo predictivo hasta aprobar la variable objetivo, las métricas, la población, el horizonte y los criterios de aceptación. |

| Número de requisito | RF-72 |
|---|---|
| Nombre de requisito | La IA debe clasificar automáticamente... |
| Tipo | ☑ Requisito | ☐ Restricción |
| Prioridad del requisito | ☑ Alta/Esencial | ☐ Media/Deseado | ☐ Baja/Opcional |
| Requerimiento Ligado | RF-04 |
| Descripción del requerimiento | La IA debe clasificar automáticamente las respuestas de texto abierto |

| Número de requisito | RF-73 |
|---|---|
| Nombre de requisito | El sistema debe generar alertas... |
| Tipo | ☑ Requisito | ☐ Restricción |
| Prioridad del requisito | ☑ Alta/Esencial | ☐ Media/Deseado | ☐ Baja/Opcional |
| Requerimiento Ligado | RF-72 |
| Descripción del requerimiento | El sistema debe generar alertas visuales para el coordinador cuando detecte patrones negativos en la empleabilidad. |

| Número de requisito | RNF-07 |
|---|---|
| Nombre de requisito | La IA debe sugerir competencias... |
| Tipo | ☐ Requisito | ☑ Restricción |
| Prioridad del requisito | ☑ Alta/Esencial | ☐ Media/Deseado | ☐ Baja/Opcional |
| Requerimiento Ligado | RF-72 |
| Descripción del requerimiento | La IA debe sugerir competencias o habilidades demandadas en el mercado a partir de los sectores y cargos actuales de los egresados.El módulo de IA debe estar desacoplado (ej. mediante una API) para que sus procesos no bloqueen ni ralenticen el dashboard principal.(NF) |

| Número de requisito | RNF-08 |
|---|---|
| Nombre de requisito | El modelo de IA debe... |
| Tipo | ☐ Requisito | ☑ Restricción |
| Prioridad del requisito | ☑ Alta/Esencial | ☐ Media/Deseado | ☐ Baja/Opcional |
| Requerimiento Ligado | RF-72 |
| Descripción del requerimiento | El modelo de IA debe entrenarse exclusivamente con datos anonimizados, sin usar nombres ni documentos de identidad.(NF) |
