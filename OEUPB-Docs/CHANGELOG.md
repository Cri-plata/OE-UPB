# Historial de Cambios (Changelog)

Este documento rastrea todas las modificaciones arquitectónicas, creaciones de archivos y refactorizaciones realizadas en el proyecto OE UPB.

## [2026-08-26] - Consolidación del Monorepo y Arquitectura Limpia
* **Estructura:** Se consolidó el repositorio en un esquema "Monorepo" (Docs, Frontend, Backend, Contracts).
* **Arquitectura:** Se definió oficialmente el uso de **Clean Architecture** para Frontend y Backend.
* **Contratos:** Se crearon los primeros contratos de API para el módulo de Autenticación.
* **Documentación:** Se creó este archivo CHANGELOG.md para cumplir con la regla de documentar cualquier cambio realizado por la IA o el equipo.

## [2026-08-26] - Actualización de CLAUDE.md (Contextualización)
* **AI Context:** Se actualizó CLAUDE.md por petición del equipo para exigir la lectura estricta de TODOS los archivos de requerimientos, arquitectura y planes al iniciar un nuevo chat, previniendo la pérdida de reglas de negocio críticas.

## [2026-08-26] - Contratos de Usuarios y Carga de Excel
* **Contratos API:** Se crearon los contratos usuarios.contract.ts / usuarios_schema.py para el CRUD de usuarios del CTIC.
* **Contratos API:** Se crearon los contratos carga.contract.ts / carga_schema.py que definen la estructura de respuesta del motor Pandas al subir el Excel, incluyendo la lista de errores para el frontend.

## [2026-08-26] - Contratos de Dashboard e Inteligencia Artificial
* **Contratos API:** Se crearon los contratos dashboard.contract.ts / dashboard_schema.py para abstraer los KPIs de empleabilidad y las series de tiempo (M1 vs M5).
* **Contratos API:** Se crearon los contratos ia.contract.ts / ia_schema.py para mapear los resultados predictivos (Scikit-learn) y el análisis de texto libre (NLP). Todos los contratos del proyecto están completos al 100%.

## [2026-08-26] - Refactorización Frontend a Clean Architecture
* **Angular:** Se reestructuró la carpeta src/app dividiendo el código en domain (Modelos y Casos de Uso), data (Repositorios e Interceptores) y presentation (Componentes Visuales).
* **Routing:** Se actualizaron las referencias en app.routes.ts apuntando a la nueva ruta presentation/features/....

## [2026-08-26] - Capa de Datos (Data) e Inversión de Dependencias
* **Data Layer:** Se implementó AuthImplementationRepository usando HttpClient de Angular para consumir la API.
* **Seguridad:** Se creó el jwtInterceptor para inyectar automáticamente el token (Bearer) en las peticiones HTTP.
* **Inyección de Dependencias:** Se configuró el contenedor de Angular (app.config.ts) para que cuando el Dominio exija AuthRepository, Angular entregue la implementación real (AuthImplementationRepository).

## [2026-08-26] - Capa de Presentación (UI Login)
* **Login Component:** Se maquetó login.html y login.scss respetando estrictamente el Mockup (Modo Claro, campos oscuros, botón rojo corporativo).
* **Formularios Reactivos:** Se implementó ReactiveFormsModule en login.ts para validación de datos (email y longitud mínima de contraseña).
* **Clean Architecture:** El componente visual (LoginComponent) inyecta directamente el LoginUseCase del Dominio, aislando la lógica de negocio de la vista.

## [2026-08-26] - Capa de Presentación (Dashboard)
* **Sidebar Component:** Se creó la barra lateral de navegación con estilos oscuros y los enlaces de ruteo principales.
* **Reporte General Component:** Se diseñó el layout principal del Dashboard. Se incluyó una cuadrícula de KPIs (Total Egresados, Demora, Satisfacción, Empleabilidad) con simulación de carga asíncrona, y un "placeholder" de barras CSS como preparación para Chart.js.

## [2026-08-26] - Capa de Presentación (Carga de Datos Excel)
* **Carga Datos Component:** Se maquetó la pantalla de administración de datos con formularios reactivos para elegir Sede y Momento.
* **Drag & Drop UI:** Se implementó una zona interactiva para arrastrar y soltar el archivo .xlsx o .xls.
* **Mock del Motor ETL:** Se simuló el caso de uso del procesador de Pandas, mostrando una tabla visual de errores extraída directamente del DTO UploadExcelResponseDto cuando se detectan fallos como 'Doble titulación'.

## [2026-08-26] - Inicialización del Backend (FastAPI)
* **Arquitectura:** Se inicializó el directorio OEUPB-Backend con las capas de domain, application, infrastructure y presentation.
* **Configuración Base:** Se creó el requirements.txt con las librerías necesarias, el archivo oculto .env para las variables de entorno (MySQL) y el main.py con configuración CORS habilitada para conectar con el puerto 4200 de Angular.

## [2026-08-27] - Panel de Administración y Conexión Real
* **Backend Autenticación:** Se reemplazó el mock por una conexión real a MySQL usando SQLAlchemy y JWT. Se configuró exitosamente la contraseña con el algoritmo bcrypt puro solucionando problemas de compatibilidad en Python 3.14.
* **Frontend Admin-Usuarios:** Se creó la vista protegida para el rol Admin_CTIC. Incluye un formulario reactivo con reglas de negocio (ej. el campo Sede solo es obligatorio si se elige el rol Coordinador) y una tabla de visualización de usuarios.
* **Ruteo Dinámico:** El LoginUseCase ahora redirige automáticamente a /admin-usuarios o /reporte dependiendo del rol JWT detectado en la respuesta de la API.

## [2026-08-27] - Refinamientos de Seguridad y UI para CTIC
* **Frontend:** Se eliminaron los emojis del Sidebar y se agregó un borde blanco al botón de Cerrar Sesión para un aspecto más sobrio y corporativo.
* **Angular Zone.js Fix:** Se implementó ChangeDetectorRef en el Login y en Admin Usuarios para solucionar problemas de renderizado fantasma tras la resolución de peticiones HTTP asíncronas.
* **Seguridad de Negocio (Full-Stack):** Se implementó una validación estricta para que el sistema solo acepte correos institucionales @upb.edu.co. En el Frontend mediante un Custom Validator reactivo, y en el Backend mediante un rechazo HTTP 400.
* **Gestión de Coordinadores:** 
  - Se agregó el endpoint DELETE /api/usuarios/{id} con protección para no poder borrar al Administrador Principal.
  - Se actualizó la vista para ocultar al Admin_CTIC de la lista y se agregó el botón para eliminar Coordinadores dinámicamente de la interfaz y la base de datos.

## [1.2.0] - 2026-08-27
### Agregado
- Rediseño corporativo de la pestaña "Cargar Datos".
- Algoritmo en Pandas (Backend) para leer y procesar las dobles titulaciones de los archivos Excel del Ministerio.
- Conexión de Pandas con MySQL (Modelos Egresado y Medicion) para guardar dinámicamente las encuestas con formato JSON.
- Generador automático de archivos Excel de prueba con datos falsos (50, 120 y 500 filas).
- Dashboards interactivos con Chart.js para "Reporte General" y "Tendencias" con indicadores KPI y gráficas (Datos simulados para presentación).
- Logo oficial de la UPB integrado en las vistas del Coordinador.
