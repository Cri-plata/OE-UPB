# Historias de Usuario (OE UPB)

> **Estado:** intención de producto normalizada el 2026-09-23. La política de cuentas, permisos y publicación de gráficas está implementada; la matriz de trazabilidad conserva las capacidades aún parciales.

Formato: **Como** [rol], **quiero** [acción], **para** [beneficio]. Incluye criterios de aceptación (CA) vinculados a los requerimientos formales (RF).

---

## Épica 1: Autenticación y Accesos

### HU-01 — Gestión de Coordinadores y Sedes
**Como** Administrador CTIC, **quiero** un panel de administración de cuentas, **para** crear y gestionar exclusivamente coordinadores asignándoles su respectiva sede.

- CA1: El formulario de creación de coordinador exige nombre, correo terminado en `@upb.edu.co` y sede. El rol asignado es `Coordinador_Sede`. *(RF-36, RN-07, RN-19)*
- CA2: El formulario solicita la cédula del usuario y la usa como contraseña temporal inicial. El backend guarda únicamente su hash bcrypt y no conserva una copia adicional de la cédula con fines de autenticación. En el primer ingreso, el usuario debe reemplazarla antes de acceder a cualquier otra función. *(RN-18)*
- CA3: Un coordinador o usuario de consulta no puede crear, modificar ni eliminar cuentas CTIC o de coordinadores. *(RN-07)*
- CA4: El Administrador CTIC administra únicamente cuentas de coordinadores y no tiene acceso al dashboard ni a los datos de egresados.
- CA5: Quien solicita o crea la cuenta comunica al usuario que su cédula es la credencial temporal. El primer ingreso abre un modal bloqueante para reemplazarla. El endurecimiento de este mecanismo se ejecutará después de completar RBAC, permisos y el flujo funcional principal.

### HU-02 — Inicio de Sesión
**Como** usuario del sistema (CTIC, Coordinador o Usuario de Consulta), **quiero** iniciar sesión con mi correo institucional y contraseña, **para** acceder a mi espacio de trabajo.

- CA1: Con credenciales incorrectas, el sistema muestra "Correo o contraseña incorrectos" sin especificar cuál falló (seguridad).
- CA2: Tras un inicio exitoso, el sistema devuelve un token JWT que incluye el rol y el `sede_id` del usuario; los permisos y programas efectivos se obtienen y validan en backend contra su estado vigente. *(RN-08, RN-11, RN-22)*
- CA3: El sistema redirige al usuario a su pantalla inicial según su rol (CTIC → Gestión de Coordinadores; Coordinador/Usuario de Consulta → Dashboard).

### HU-03 — Aislamiento de Datos Fuente por Sede
**Como** Coordinador de Sede, **quiero** que el sistema filtre automáticamente los datos fuente, **para** gestionar únicamente los egresados y encuestas de mi sede sin exponerlos a otras sedes.

- CA1: Toda petición a datos fuente extrae el `sede_id` del JWT validado. *(RN-06)*
- CA2: Las consultas de egresados, mediciones, respuestas individuales, cargas e historiales filtran nuevamente por la sede autorizada. *(RN-06)*
- CA3: La publicación de una gráfica no concede acceso al directorio, perfil, archivo ni respuestas usados para calcularla. *(RN-09, RF-35)*

---

## Épica 2: Carga y Gestión de Datos

### HU-04 — Subida Masiva de Excel
**Como** Coordinador de Sede, **quiero** poder cargar un archivo Excel (.xlsx) proveniente del OLE, **para** integrar los resultados de las encuestas (Momento 0, 1 o 5) a la base de datos central.

- CA1: El frontend debe rechazar archivos que no tengan extensión .xlsx antes de enviarlos al servidor, mostrando un mensaje de error claro. *(RN-05, RF-01)*
- CA2: El sistema debe permitir seleccionar el Momento (0, 1, o 5) al cual corresponden las encuestas que se están subiendo. Si se elige un momento inválido, se bloquea la carga. *(RN-02, RF-02, RF-03)*
- CA3: Muestra una barra de progreso o un indicador de "Procesando" mientras Python limpia los datos, y luego arroja un modal de "Carga Exitosa" con el resumen de registros. *(RF-09)*
- CA4: El año seleccionado representa el año de grado o cohorte. Cada archivo recibe un identificador auditable. Una recarga de la misma sede, momento y cohorte reemplaza la versión vigente de forma transaccional. *(RF-07, RF-09, RN-12)*
- CA5: La carga es atómica: si una fila incumple una validación obligatoria, no se persiste ninguna fila del archivo. Un documento ausente y otros campos opcionales expresamente permitidos no cuentan como error y pueden producir una medición anónima válida. *(RN-15, RN-20)*

### HU-05 — Limpieza y Unicidad de Datos (Pandas)
**Como** Sistema (Backend), **quiero** procesar y limpiar el archivo Excel cargado, **para** asegurar que no existan duplicados ni datos corruptos en la base de datos.

- CA1: El backend normaliza los nombres de las columnas, elimina filas completamente vacías y unifica formatos de texto (minúsculas, sin espacios extra). *(RF-04)*
- CA2: El sistema usa la cédula (`numero_documento`) como llave primaria. Si el Excel contiene una cédula que ya existe en la base de datos, el sistema **actualiza** sus datos (UPSERT) en lugar de crear un duplicado. *(RN-01, RF-06)*
- CA3: Las respuestas dinámicas a las encuestas se serializan en JSON y se almacenan en `mediciones.respuestas`. *(Modelo de Datos)*
- CA4: Una carga no sobrescribe correcciones manuales protegidas sin confirmación explícita y registro del conflicto. *(RN-13)*

### HU-06 — Búsqueda y Edición Manual
**Como** Coordinador de Sede, **quiero** un módulo de gestión individual, **para** buscar un egresado por su cédula y modificar o agregar su información manualmente en caso de omisiones en el Excel.

- CA1: El módulo incluye una barra de búsqueda que acepta cédula o nombre. *(RF-14, RF-15)*
- CA2: Al encontrar al egresado, se despliega una "Ficha Individual" con su información personal y su historial de encuestas visibles para la sede. *(RF-14, RF-15, RF-52, RN-06)*
- CA3: Si el egresado no existe, el coordinador puede crear un registro desde cero ingresando manualmente los datos básicos. *(RF-10)*
- CA4: Todo cambio manual queda reflejado instantáneamente en los Dashboards de la sede.
- CA5: El coordinador puede registrar encuestas manuales y corregir egresados visibles para su sede. El sistema registra actor, fecha, procedencia y campos modificados; los conflictos multisede los resuelve la custodia institucional. *(RN-13)*

---
## Épica 3: Dashboard Analítico (Visualización de Datos)

### HU-07 — Resumen General de Empleabilidad (Dashboard Principal)
**Como** Coordinador o Usuario de Consulta autorizado, **quiero** ver un panel de métricas, **para** entender la situación laboral dentro del alcance que me fue asignado.

- CA1: El dashboard muestra tarjetas con el número total de encuestados, tasa de empleo formal e informal y salario promedio. *(RF-25, RF-26, RF-61)*
- CA2: Incluye una gráfica comparativa rápida del estado laboral actual frente al año anterior.
- CA3: Los datos propios están limitados por sede; las gráficas de otras sedes solo aparecen si fueron publicadas y el usuario tiene permiso para verlas. *(RN-06, RN-09, RN-10)*

### HU-08 — Tendencias por Momento de Seguimiento (M1 vs M5)
**Como** Usuario de Consulta autorizado, **quiero** poder comparar visualmente los resultados del Momento 1 contra el Momento 5, **para** evaluar la evolución profesional y salarial de una misma cohorte a lo largo del tiempo.

- CA1: La pantalla incluye selectores independientes para "Momento Inicial" y "Momento a Comparar". *(RF-24, RF-52)*
- CA2: El sistema genera una gráfica de líneas o barras agrupadas cruzando la tasa de empleo y el salario promedio entre ambos momentos. *(RF-24, RF-25, RF-26, RF-52)*
- CA3: Si no hay datos suficientes para un cruce, se muestra un mensaje "Datos insuficientes para la comparación seleccionada".

### HU-09 — Filtros Dinámicos (Cohorte y Programa)
**Como** Usuario de Consulta autorizado, **quiero** aplicar filtros de cohorte y programa dentro de mi alcance, **para** analizar un programa académico específico.

- CA1: Debe existir un menú desplegable multi-selección de "Programa Académico" y "Cohorte (Año de Grado)". *(RF-21, RF-22)*
- CA2: Al aplicar los filtros, el frontend solicita al backend un nuevo agregado autorizado. El backend valida nuevamente sede, programas y permisos antes de calcularlo. El frontend solo puede reorganizar o volver a renderizar métricas agregadas ya autorizadas; no recibe ni filtra filas o respuestas individuales para recalcular gráficas.
- CA3: Existe un botón de "Limpiar Filtros" para volver a la vista general de la sede.

---

## Épica 4: Inteligencia Artificial (Módulo Predictivo)

### HU-10 — Predicción de Riesgo de Desempleo
> **Estado:** en pausa hasta aprobar objetivo, métricas, población, horizonte y criterios de aceptación. Los criterios siguientes se conservan como antecedente y no autorizan implementación.

**Como** Coordinador de Sede, **quiero** que el sistema corra un modelo predictivo sobre los egresados recién graduados, **para** identificar qué porcentaje tiene un alto riesgo de quedar desempleado a los 5 años.

- CA1: El backend cuenta con un endpoint que recibe las características sociodemográficas y de desempeño académico de una cohorte. *(RF-71)*
- CA2: Un modelo entrenado en scikit-learn evalúa los datos y devuelve una probabilidad de empleabilidad (0 a 100%).
- CA3: En la interfaz, si el riesgo de desempleo de una cohorte supera el 30%, se despliega una alerta visual (color rojo/naranja) recomendando acciones a la decanatura. *(RF-73)*

### HU-11 — Clasificación de Habilidades (NLP / OpenAI)
**Como** Usuario de Consulta autorizado, **quiero** que la inteligencia artificial analice las respuestas de "texto libre" de las encuestas, **para** extraer las habilidades blandas y técnicas más demandadas sin tener que leer manualmente cientos de opiniones.

- CA1: El backend debe tomar la columna JSON de respuestas abiertas y limpiarla, removiendo nombres propios o cédulas (Anonimización). *(RN-04)*
- CA2: El texto anonimizado se procesa (ej. vía API de OpenAI o NLP local) para agrupar términos similares (Ej. "Trabajo en equipo", "Liderazgo", "Python"). *(RF-72)*
- CA3: El resultado se visualiza en el frontend mediante un gráfico tipo "Nube de Palabras" (Word Cloud) o gráfico de barras horizontales con las 10 competencias principales.

---

## Épica 5: Permisos y Publicación de Gráficas

### HU-12 — Gestión de Usuarios de Consulta
**Como** Coordinador de Sede, **quiero** crear usuarios de consulta de mi sede y asignarles programas y permisos, **para** que rectores, profesores y personal administrativo vean únicamente las gráficas que les corresponden.

- CA1: El coordinador solo puede crear, modificar, bloquear o eliminar cuentas `Usuario_Consulta` de su propia sede. *(RF-36, RN-07)*
- CA2: El formulario exige nombre, correo terminado en `@upb.edu.co`, etiqueta informativa de perfil, sede, permisos de visualización y programas. El catálogo inicial de permisos contiene `ver_reporte_general`, `ver_tendencias`, `ver_explorador` y `ver_publicaciones`; no incluye exportación. *(RF-37, RN-08, RN-19, RN-28)*
- CA3: Las etiquetas rector, profesor y administrativo no conceden permisos predeterminados. El coordinador selecciona manualmente todos los permisos y programas, y el backend aplica únicamente esa asignación explícita. *(RN-10, RN-30)*
- CA3A: La lista de programas se obtiene de los nombres distintos observados en las cargas visibles de la sede del coordinador; no se aceptan programas de otra sede ni valores arbitrarios enviados por el cliente. *(RN-29)*
- CA4: El usuario de consulta no puede cargar, eliminar, publicar ni administrar cuentas. *(RN-03)*
- CA5: La cuenta nueva usa la cédula suministrada como contraseña temporal y queda restringida hasta que el usuario establezca una contraseña personal. Solo se almacena el hash de la credencial temporal. *(RN-18)*
- CA6: Un bloqueo o reducción de permisos tiene efecto inmediato en sesiones existentes; cada operación protegida valida el estado y la versión de autorización vigentes. *(RN-22)*

### HU-13 — Publicar Gráfica Agregada
**Como** Coordinador de Sede, **quiero** publicar o retirar una gráfica desde la propia visualización, **para** compartir resultados agregados con usuarios autorizados sin exponer los datos fuente.

- CA1: Cada gráfica publicable ofrece una acción `Publicar`; la pantalla de carga no contiene una acción para compartir encuestas. *(RF-35, RN-09)*
- CA2: La publicación conserva la sede propietaria, los programas relacionados, la definición de filtros y una copia inmutable de las métricas agregadas aprobadas. La definición se usa para renderizar y auditar la instantánea, no para recalcularla automáticamente con datos posteriores. *(RN-09, RN-11, RN-14)*
- CA3: El backend calcula la audiencia automáticamente; el coordinador no selecciona personas manualmente por gráfica. *(RF-37, RN-08, RN-11)*
- CA4: Otra sede nunca recibe filas, documentos, nombres, correos, respuestas individuales ni archivos fuente. *(RN-04, RN-06, RN-09)*
- CA5: Al retirar una publicación, deja de estar disponible para usuarios de otras sedes sin afectar la gráfica privada de la sede propietaria.
- CA6: La publicación crea una instantánea versionada y requiere aprobación manual de privacidad antes de hacerse visible. Una actualización produce una versión nueva. *(RN-14)*
