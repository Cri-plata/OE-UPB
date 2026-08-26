# Historias de Usuario (OE UPB)

Formato: **Como** [rol], **quiero** [acción], **para** [beneficio]. Incluye criterios de aceptación (CA) vinculados a los requerimientos formales (RF).

---

## Épica 1: Autenticación y Accesos

### HU-01 — Gestión de Usuarios y Sedes
**Como** Administrador CTIC, **quiero** un panel de administración de cuentas, **para** crear y gestionar el acceso de los coordinadores y directivos asignándoles su respectiva sede.

- CA1: El formulario de creación de usuario exige obligatoriamente un nombre, correo institucional, rol y sede_id. *(RF-70)*
- CA2: El sistema encripta la contraseña antes de guardarla en la base de datos (bcrypt/argon2).
- CA3: Un Coordinador de Sede o Directivo NO puede ver ni acceder a este panel de administración por falta de privilegios. *(RF-07, RN-07)*
- CA4: El Administrador CTIC solo puede crear/bloquear cuentas, pero no tiene acceso al dashboard ni a los datos de egresados.

### HU-02 — Inicio de Sesión
**Como** usuario del sistema (CTIC, Coordinador o Directivo), **quiero** iniciar sesión con mi correo institucional y contraseña, **para** acceder a mi espacio de trabajo.

- CA1: Con credenciales incorrectas, el sistema muestra "Correo o contraseña incorrectos" sin especificar cuál falló (seguridad).
- CA2: Tras un inicio exitoso, el sistema devuelve un Token JWT que incluye el 
ol y el sede_id del usuario. *(RF-72)*
- CA3: El sistema redirige al usuario a su pantalla inicial según su rol (CTIC -> Gestión Usuarios; Coordinador/Directivo -> Dashboard).

### HU-03 — Silos de Datos por Sede (Aislamiento)
**Como** Coordinador o Directivo, **quiero** que el sistema filtre automáticamente toda la información, **para** visualizar única y exclusivamente los datos de los egresados pertenecientes a mi sede.

- CA1: Toda petición HTTP al backend (visualizar dashboard, buscar egresado) extrae el sede_id del Token JWT del usuario que realiza la petición. *(RN-06)*
- CA2: Las sentencias SQL del backend agregan automáticamente un WHERE sede_id = ? para evitar filtraciones de datos cruzados. *(RN-06)*

---

## Épica 2: Carga y Gestión de Datos

### HU-04 — Subida Masiva de Excel
**Como** Coordinador de Sede, **quiero** poder cargar un archivo Excel (.xlsx) proveniente del OLE, **para** integrar los resultados de las encuestas (Momento 0, 1 o 5) a la base de datos central.

- CA1: El frontend debe rechazar archivos que no tengan extensión .xlsx antes de enviarlos al servidor, mostrando un mensaje de error claro. *(RN-05, RF-01)*
- CA2: El sistema debe permitir seleccionar el Momento (0, 1, o 5) al cual corresponden las encuestas que se están subiendo. Si se elige un momento inválido, se bloquea la carga. *(RN-02, RF-08)*
- CA3: Muestra una barra de progreso o un indicador de "Procesando" mientras Python limpia los datos, y luego arroja un modal de "Carga Exitosa" con el resumen de registros. *(RF-09)*

### HU-05 — Limpieza y Unicidad de Datos (Pandas)
**Como** Sistema (Backend), **quiero** procesar y limpiar el archivo Excel cargado, **para** asegurar que no existan duplicados ni datos corruptos en la base de datos.

- CA1: El backend normaliza los nombres de las columnas, elimina filas completamente vacías y unifica formatos de texto (minúsculas, sin espacios extra). *(RF-04)*
- CA2: El sistema usa la Cédula (documento_identidad) como llave primaria. Si el Excel contiene una cédula que ya existe en la base de datos, el sistema **actualiza** sus datos (UPSERT) en lugar de crear un duplicado. *(RN-01, RF-06)*
- CA3: Las respuestas dinámicas a las encuestas se serializan en un formato JSON y se almacenan en la columna 
espuestas_completas para evitar migraciones costosas de esquema en el futuro. *(Modelo de Datos)*

### HU-06 — Búsqueda y Edición Manual
**Como** Coordinador de Sede, **quiero** un módulo de gestión individual, **para** buscar un egresado por su cédula y modificar o agregar su información manualmente en caso de omisiones en el Excel.

- CA1: El módulo incluye una barra de búsqueda que acepta cédula o nombre. *(RF-14, RF-15)*
- CA2: Al encontrar al egresado, se despliega una "Ficha Individual" con su información personal y su historial de encuestas. *(RF-36)*
- CA3: Si el egresado no existe, el coordinador puede crear un registro desde cero ingresando manualmente los datos básicos. *(RF-10, RF-12)*
- CA4: Todo cambio manual queda reflejado instantáneamente en los Dashboards de la sede.

---
## Épica 3: Dashboard Analítico (Visualización de Datos)

### HU-07 — Resumen General de Empleabilidad (Dashboard Principal)
**Como** Directivo o Coordinador, **quiero** ver un panel de métricas generales al iniciar sesión, **para** entender rápidamente la situación laboral global de mi sede.

- CA1: El dashboard muestra "Tarjetas de Métricas" con el número total de encuestados, tasa de empleabilidad formal e informal, y salario promedio. *(RF-20, RF-31)*
- CA2: Incluye una gráfica comparativa rápida del estado laboral actual frente al año anterior.
- CA3: Los datos mostrados están limitados por el sede_id del usuario (Silos de Datos). *(RN-06)*

### HU-08 — Tendencias por Momento de Seguimiento (M1 vs M5)
**Como** Directivo Académico, **quiero** poder comparar visualmente los resultados del Momento 1 contra el Momento 5, **para** evaluar la evolución profesional y salarial de una misma cohorte a lo largo del tiempo.

- CA1: La pantalla incluye selectores independientes para "Momento Inicial" y "Momento a Comparar". *(RF-40)*
- CA2: El sistema genera una gráfica de líneas o barras agrupadas cruzando la tasa de empleo y el salario promedio entre ambos momentos. *(RF-42)*
- CA3: Si no hay datos suficientes para un cruce, se muestra un mensaje "Datos insuficientes para la comparación seleccionada".

### HU-09 — Filtros Dinámicos (Cohorte y Programa)
**Como** Decano (Directivo), **quiero** poder aplicar filtros avanzados en cualquier gráfica del dashboard, **para** aislar el rendimiento de un programa académico específico (Ej. Ingeniería de Sistemas).

- CA1: Debe existir un menú desplegable multi-selección de "Programa Académico" y "Cohorte (Año de Grado)". *(RF-15, RF-24)*
- CA2: Al aplicar los filtros, el frontend re-calcula las gráficas del dashboard instantáneamente usando los datos filtrados en memoria, o realiza una nueva petición al backend si la data es muy grande.
- CA3: Existe un botón de "Limpiar Filtros" para volver a la vista general de la sede.

---

## Épica 4: Inteligencia Artificial (Módulo Predictivo)

### HU-10 — Predicción de Riesgo de Desempleo
**Como** Coordinador de Sede, **quiero** que el sistema corra un modelo predictivo sobre los egresados recién graduados, **para** identificar qué porcentaje tiene un alto riesgo de quedar desempleado a los 5 años.

- CA1: El backend cuenta con un endpoint que recibe las características sociodemográficas y de desempeño académico de una cohorte. *(RF-60)*
- CA2: Un modelo entrenado en scikit-learn evalúa los datos y devuelve una probabilidad de empleabilidad (0 a 100%).
- CA3: En la interfaz, si el riesgo de desempleo de una cohorte supera el 30%, se despliega una alerta visual (color rojo/naranja) recomendando acciones a la decanatura. *(RF-65)*

### HU-11 — Clasificación de Habilidades (NLP / OpenAI)
**Como** Decano, **quiero** que la inteligencia artificial analice las respuestas de "texto libre" de las encuestas, **para** extraer las habilidades blandas y técnicas más demandadas sin tener que leer manualmente cientos de opiniones.

- CA1: El backend debe tomar la columna JSON de respuestas abiertas y limpiarla, removiendo nombres propios o cédulas (Anonimización). *(RN-04)*
- CA2: El texto anonimizado se procesa (ej. vía API de OpenAI o NLP local) para agrupar términos similares (Ej. "Trabajo en equipo", "Liderazgo", "Python"). *(RF-68)*
- CA3: El resultado se visualiza en el frontend mediante un gráfico tipo "Nube de Palabras" (Word Cloud) o gráfico de barras horizontales con las 10 competencias principales.
