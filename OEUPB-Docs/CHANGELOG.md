# Historial de Cambios (Changelog)

Este documento rastrea todas las modificaciones arquitectÃ³nicas, creaciones de archivos y refactorizaciones realizadas en el proyecto OE UPB.

## [2026-08-26] - ConsolidaciÃ³n del Monorepo y Arquitectura Limpia
* **Estructura:** Se consolidÃ³ el repositorio en un esquema "Monorepo" (Docs, Frontend, Backend, Contracts).
* **Arquitectura:** Se definiÃ³ oficialmente el uso de **Clean Architecture** para Frontend y Backend.
* **Contratos:** Se crearon los primeros contratos de API para el mÃ³dulo de AutenticaciÃ³n.
* **DocumentaciÃ³n:** Se creÃ³ este archivo CHANGELOG.md para cumplir con la regla de documentar cualquier cambio realizado por la IA o el equipo.

## [2026-08-26] - ActualizaciÃ³n de CLAUDE.md (ContextualizaciÃ³n)
* **AI Context:** Se actualizÃ³ CLAUDE.md por peticiÃ³n del equipo para exigir la lectura estricta de TODOS los archivos de requerimientos, arquitectura y planes al iniciar un nuevo chat, previniendo la pÃ©rdida de reglas de negocio crÃ­ticas.

## [2026-08-26] - Contratos de Usuarios y Carga de Excel
* **Contratos API:** Se crearon los contratos usuarios.contract.ts / usuarios_schema.py para el CRUD de usuarios del CTIC.
* **Contratos API:** Se crearon los contratos carga.contract.ts / carga_schema.py que definen la estructura de respuesta del motor Pandas al subir el Excel, incluyendo la lista de errores para el frontend.

## [2026-08-26] - Contratos de Dashboard e Inteligencia Artificial
* **Contratos API:** Se crearon los contratos dashboard.contract.ts / dashboard_schema.py para abstraer los KPIs de empleabilidad y las series de tiempo (M1 vs M5).
* **Contratos API:** Se crearon los contratos ia.contract.ts / ia_schema.py para mapear los resultados predictivos (Scikit-learn) y el anÃ¡lisis de texto libre (NLP). Todos los contratos del proyecto estÃ¡n completos al 100%.

## [2026-08-26] - RefactorizaciÃ³n Frontend a Clean Architecture
* **Angular:** Se reestructurÃ³ la carpeta src/app dividiendo el cÃ³digo en domain (Modelos y Casos de Uso), data (Repositorios e Interceptores) y presentation (Componentes Visuales).
* **Routing:** Se actualizaron las referencias en pp.routes.ts apuntando a la nueva ruta presentation/features/....

## [2026-08-26] - Capa de Datos (Data) e InversiÃ³n de Dependencias
* **Data Layer:** Se implementÃ³ AuthImplementationRepository usando HttpClient de Angular para consumir la API.
* **Seguridad:** Se creÃ³ el jwtInterceptor para inyectar automÃ¡ticamente el token (Bearer) en las peticiones HTTP.
* **InyecciÃ³n de Dependencias:** Se configurÃ³ el contenedor de Angular (pp.config.ts) para que cuando el Dominio exija AuthRepository, Angular entregue la implementaciÃ³n real (AuthImplementationRepository).

## [2026-08-26] - Capa de PresentaciÃ³n (UI Login)
* **Login Component:** Se maquetÃ³ login.html y login.scss respetando estrictamente el Mockup (Modo Claro, campos oscuros, botÃ³n rojo corporativo).
* **Formularios Reactivos:** Se implementÃ³ ReactiveFormsModule en login.ts para validaciÃ³n de datos (email y longitud mÃ­nima de contraseÃ±a).
* **Clean Architecture:** El componente visual (LoginComponent) inyecta directamente el LoginUseCase del Dominio, aislando la lÃ³gica de negocio de la vista.

## [2026-08-26] - Capa de PresentaciÃ³n (Dashboard)
* **Sidebar Component:** Se creÃ³ la barra lateral de navegaciÃ³n con estilos oscuros y los enlaces de ruteo principales.
* **Reporte General Component:** Se diseÃ±Ã³ el layout principal del Dashboard. Se incluyÃ³ una cuadrÃ­cula de KPIs (Total Egresados, Demora, SatisfacciÃ³n, Empleabilidad) con simulaciÃ³n de carga asÃ­ncrona, y un "placeholder" de barras CSS como preparaciÃ³n para Chart.js.

## [2026-08-26] - Capa de PresentaciÃ³n (Carga de Datos Excel)
* **Carga Datos Component:** Se maquetÃ³ la pantalla de administraciÃ³n de datos con formularios reactivos para elegir Sede y Momento.
* **Drag & Drop UI:** Se implementÃ³ una zona interactiva para arrastrar y soltar el archivo .xlsx o .xls.
* **Mock del Motor ETL:** Se simulÃ³ el caso de uso del procesador de Pandas, mostrando una tabla visual de errores extraÃ­da directamente del DTO UploadExcelResponseDto cuando se detectan fallos como 'Doble titulaciÃ³n'.

## [2026-08-26] - InicializaciÃ³n del Backend (FastAPI)
* **Arquitectura:** Se inicializÃ³ el directorio OEUPB-Backend con las capas de domain, pplication, infrastructure y presentation.
* **ConfiguraciÃ³n Base:** Se creÃ³ el equirements.txt con las librerÃ­as necesarias, el archivo oculto .env para las variables de entorno (MySQL) y el main.py con configuraciÃ³n CORS habilitada para conectar con el puerto 4200 de Angular.

## [2026-08-27] - Panel de AdministraciÃ³n y ConexiÃ³n Real
* **Backend AutenticaciÃ³n:** Se reemplazÃ³ el mock por una conexiÃ³n real a MySQL usando SQLAlchemy y JWT. Se configurÃ³ exitosamente la contraseÃ±a con el algoritmo crypt puro solucionando problemas de compatibilidad en Python 3.14.
* **Frontend Admin-Usuarios:** Se creÃ³ la vista protegida para el rol Admin_CTIC. Incluye un formulario reactivo con reglas de negocio (ej. el campo Sede solo es obligatorio si se elige el rol Coordinador) y una tabla de visualizaciÃ³n de usuarios.
* **Ruteo DinÃ¡mico:** El LoginUseCase ahora redirige automÃ¡ticamente a /admin-usuarios o /reporte dependiendo del rol JWT detectado en la respuesta de la API.

## [2026-08-27] - Refinamientos de Seguridad y UI para CTIC
* **Frontend:** Se eliminaron los emojis del Sidebar y se agregÃ³ un borde blanco al botÃ³n de Cerrar SesiÃ³n para un aspecto mÃ¡s sobrio y corporativo.
* **Angular Zone.js Fix:** Se implementÃ³ ChangeDetectorRef en el Login y en Admin Usuarios para solucionar problemas de renderizado fantasma tras la resoluciÃ³n de peticiones HTTP asÃ­ncronas.
* **Seguridad de Negocio (Full-Stack):** Se implementÃ³ una validaciÃ³n estricta para que el sistema solo acepte correos institucionales @upb.edu.co. En el Frontend mediante un Custom Validator reactivo, y en el Backend mediante un rechazo HTTP 400.
* **GestiÃ³n de Coordinadores:** 
  - Se agregÃ³ el endpoint DELETE /api/usuarios/{id} con protecciÃ³n para no poder borrar al Administrador Principal.
  - Se actualizÃ³ la vista para ocultar al Admin_CTIC de la lista y se agregÃ³ el botÃ³n para eliminar Coordinadores dinÃ¡micamente de la interfaz y la base de datos.

