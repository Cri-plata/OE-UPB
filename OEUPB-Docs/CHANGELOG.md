# Historial de Cambios (Changelog)

Este documento registra únicamente cambios de la documentación canónica. Los cambios funcionales del monorepo se registran en `../CHANGELOG.md`.

## [2026-09-25] - P2 Analítica y contratos

* **ADR-016:** mapeo de los cuestionarios OLE a la taxonomía laboral, la formalidad, el salario y la comparación de momentos.
* **ADR-017:** normalización del documento de identidad, límites de carga y rechazo con detalle por fila.
* **Requisitos:** RF-21, RF-22, RF-23, RF-25, RF-26 y RF-61 pasan a Implementado. RN-01, RN-16, RN-26 y RN-31, HU-07 y CU-05 a CU-07 se actualizaron.
* **Backlog:** EXP-03, ANA-01, DB-03 y ETL-01 se archivaron; se agregó ANA-03 y se amplió ANA-02.

## [2026-09-25] - Actualización de verificación

* **Pruebas:** la estrategia y el estado funcional reflejan 38 pruebas de backend y 23 de frontend, los casos de privacidad de publicación y la convención de pruebas zoneless.
* **Estado:** se actualizaron CU-12, la fecha de corte funcional y las fechas de verificación del modelo de datos y del despliegue.

## [2026-09-25] - Corrección del flujo de publicación

* **PUB-01/PUB-02:** se documentó la causa (detección de cambios zoneless con estado fuera de signals), la corrección, las pruebas y la lista de validación manual. RF-35 sigue Parcial hasta esa validación.
* **Arquitectura frontend:** se registró la convención de usar signals para el estado asíncrono.

## [2026-09-25] - Auditoría de requerimientos 05

* **Auditoría:** se ejecutó `audits/auditoria_requerimientos.md` (20 contradicciones y 21 casos de borde) y se verificó cada hallazgo contra código y ADR en `audits/05-auditoria-requerimientos.md`.
* **Decisiones:** ADR-014 saca del alcance la custodia institucional y las encuestas manuales y fija la precedencia de cargas. ADR-015 exige recálculo en backend, umbral k = 5 y autoaprobación explícita de las publicaciones.
* **Requisitos:** se alinearon RN-01, 07, 09, 12-15, 18, 22-24, 26, 28 y 31, HU-01, 05-09 y 11-13, y CU-02 a CU-12 con RN-24, ADR-013, ADR-014 y ADR-015. RF-21, RF-22 y RF-26 pasan a Parcial.
* **Arquitectura y operación:** se completaron inventarios de routers y rutas, frontera de publicación, invariantes del modelo y enmascaramiento de logs.
* **Backlog:** EXP-02 archivado; nuevos ítems ANA-01, DB-03, ETL-01, API-02, PRG-01, ANA-02 y DOC-03.

## [2026-09-25] - Hallazgos de Explorador y publicaciones

* **Privacidad:** se documentó la exclusión obligatoria de PII y metadatos del catálogo graficable mediante RN-31 y EXP-02.
* **Experiencia:** se registró la necesidad de comparar varias gráficas simultáneas como EXP-03.
* **Publicación:** PUB-01 y PUB-02 registran los estados de carga permanentes al publicar y consultar el catálogo, con criterios de aceptación y pruebas mínimas.
* **Trazabilidad:** RF-35 cambia de implementado a parcial hasta verificar el flujo completo.

## [2026-09-24] - Higiene y cierre de trazabilidad

* **Requisitos:** RF-01 a RF-73 quedaron auditados individualmente y con evidencia.
* **Gobierno:** se cerraron las ocho decisiones del plan y se corrigieron referencias obsoletas sobre migraciones y formato Excel.
* **Scripts:** se documentó la retirada de residuos y el generador sintético parametrizable que los reemplaza.

## [2026-09-24] - Endurecimiento de autenticación

* **ADR-013:** se documentó el ciclo de vida de credenciales temporales, su expiración, recuperación y modo productivo aleatorio.
* **Seguridad:** el secreto JWT robusto y la configuración aleatoria son requisitos de arranque fuera de desarrollo.
* **Backlog:** SEC-03, SEC-08 y SEC-09 pasaron al histórico con pruebas de expiración, revocación y auditoría.

## [2026-09-24] - Estado funcional consolidado

* **Documento de entrega:** se añadió una descripción integral de las capacidades actuales, comportamiento esperado por rol, verificaciones, limitaciones y lista de comprobación funcional.
* **Operación:** la revisión esperada de Alembic se actualizó a `f3b91d7c6a20`.

## [2026-09-24] - Cierre de funcionalidad objetivo P2

* **Trazabilidad:** RF-10 a RF-12 y RF-69, RF-70, RF-72 y RF-73 enlazan ahora a implementación y pruebas verificables; RF-71 conserva su pausa de ADR-009.
* **Operación:** la arquitectura de despliegue refleja contenedores, proxy, configuración por entorno, observabilidad y continuidad.
* **Runbook:** se documentó despliegue, health checks, respaldo, restauración y rollback.
* **Backlog:** DATA-01, EXP-01, IA-02, IA-03 y DEPLOY-01 pasaron al histórico; IA-01 permanece activo y en pausa.

## [2026-09-24] - Cierre de arquitectura frontend y operación

* **Frontend:** se documentaron clientes HTTP en Data, guards por sesión/rol y tokens visuales globales.
* **Operación:** dependencias fijadas, inicialización con Alembic y verificaciones locales/CI quedaron consolidadas en la guía de comandos.
* **Calidad:** un nuevo validador impide HTTP directo desde Presentation, guards ausentes y colores repetidos fuera del design system.
* **Backlog:** FE-01 a FE-04 y OPS-01/OPS-02 pasaron al archivo histórico.

## [2026-09-24] - Publicación de gráficas agregadas

* **Modelo:** se documentó `PublicacionGrafica` como instantánea versionada e inmutable con propiedad, programas, permiso, aprobación y trazabilidad de retiro.
* **Seguridad:** el contrato limita el contenido a etiquetas y valores numéricos; la audiencia se calcula en backend por rol, permisos y programas.
* **Interfaz:** Reporte General, Tendencias y Explorador incorporan publicación/retiro, y una ruta separada muestra el catálogo autorizado.
* **Backlog:** SHARE-03 y SHARE-04 pasaron al archivo histórico con pruebas y migración aplicadas.

## [2026-09-24] - Cierre del P1 de contratos, datos y calidad

* **Contratos:** OpenAPI queda como fuente canónica; sus tipos TypeScript se generan y CI detecta consumidores o especificaciones desactualizados.
* **API:** ADR-011 mantiene las rutas compatibles bajo `/api/*` hasta que exista un cambio incompatible; ADR-012 conserva la separación entre identidad y mediciones.
* **Datos:** El esquema y la arquitectura reflejan catálogo de sedes, claves foráneas y nulabilidad obligatorias, múltiples intentos y auditoría inmutable de eliminación de cargas.
* **Calidad:** La estrategia documenta 19 pruebas de backend, 11 de frontend y verificaciones automáticas de contratos, documentación y compilación.
* **Backlog:** API-01, API-02, DB-02 a DB-06 y QA-01 a QA-03 pasaron al archivo histórico con su evidencia.

## [2026-09-23] - Implementación del P0 de permisos y flujo funcional

* **Backlog:** SEC-01, SEC-04, SHARE-01 y SHARE-02 pasaron al archivo histórico con evidencia de implementación y pruebas.
* **Contratos:** OpenAPI y DTO de administración reflejan permisos, programas, estado, versión y operaciones de ciclo de vida.
* **Datos:** El esquema documenta el alcance del usuario y la auditoría de borrado físico.
* **Trazabilidad:** La matriz distingue el RBAC ya implementado de la publicación de gráficas que continúa en P1.

## [2026-09-23] - Priorización de permisos y cierre de decisiones de auditoría

* **Prioridad:** RBAC, permisos por usuario y flujo funcional pasan a P0; el endurecimiento adicional del inicio de sesión y la entrega de credenciales se difiere hasta completar ese flujo.
* **Credencial inicial:** La política objetivo usa la cédula suministrada durante el alta como contraseña temporal, conserva únicamente su hash y mantiene el cambio bloqueante mediante modal en el primer ingreso. Su implementación se difiere hasta completar RBAC.
* **Correo institucional:** Se documenta como regla canónica el dominio `@upb.edu.co`, ya validado por frontend y backend.
* **Publicación:** Las gráficas publicadas quedan definidas como instantáneas versionadas e inmutables; una actualización requiere versión y aprobación nuevas.
* **Contratos:** Se documentaron HTTP Bearer, la respuesta tipada de login, metadatos de carga y año obligatorio en historial.
* **Auditoría:** Las decisiones 1 a 25 quedaron consolidadas en `audits/03-formulario-decisiones.md`.
* **Cuentas:** La eliminación ordinaria será desactivación reversible; el borrado físico queda como operación excepcional auditada. Los cambios de permisos deben invalidar el acceso inmediatamente.
* **Carga:** Se aprobó atomicidad todo-o-nada para errores obligatorios y borrado físico transaccional con evento de auditoría separado. Las ausencias opcionales y mediciones anónimas permitidas no se consideran errores.
* **Mediciones:** Se permiten múltiples intentos válidos para el mismo documento, sede, momento y cohorte; cada indicador debe definir su regla de selección o agregación y su propio umbral de suficiencia.
* **Consulta:** `Usuario_Consulta` solo ve instantáneas publicadas. El dashboard privado deriva la sede del JWT y las publicaciones de otras sedes se muestran en una vista separada.
* **Permisos:** El catálogo inicial queda limitado a `ver_reporte_general`, `ver_tendencias`, `ver_explorador` y `ver_publicaciones`. Los programas provienen de cargas visibles de la sede y rector/profesor/administrativo son etiquetas informativas sin privilegios automáticos.

## [2026-09-23] - Política de permisos y publicación de gráficas

* **RBAC:** Se aprobaron tres roles técnicos: `Admin_CTIC`, `Coordinador_Sede` y `Usuario_Consulta`. CTIC administra coordinadores y cada coordinador administra usuarios de consulta de su propia sede.
* **Permisos:** Rector, profesor y personal administrativo pasan a ser alcances configurables del rol `Usuario_Consulta`; los permisos y programas se asignan al crear la cuenta.
* **Publicación:** El coordinador publica o retira cada gráfica desde la visualización. La audiencia se calcula automáticamente; no se seleccionan personas manualmente ni se comparte desde la pantalla de carga.
* **Privacidad:** Entre sedes solo se comparten gráficas y métricas agregadas. Datos fuente, respuestas individuales, archivos, directorios y perfiles permanecen aislados por sede.
* **Trazabilidad:** Se corrigieron referencias RF incorrectas en historias de usuario, errores de nombres y requisitos contradictorios de acceso multisede.
* **Arquitectura:** Se añadió ADR-008 y se actualizaron ADR-004, arquitectura, seguridad, casos de uso, matriz y backlog. La implementación continúa pendiente en `SEC-01` y `SHARE-01` a `SHARE-04`.

## [2026-09-22] - Auditoría y plan de organización documental
* **Auditoría:** Se creó `audits/01-auditoria-organizacion-documental.md` con los faltantes, contradicciones y problemas de organización verificados frente a la estructura y el código actuales.
* **Plan:** Se creó `plans/04-plan-reorganizacion-documental.md` con la estructura objetivo, fases, criterios de salida y decisiones que requieren aprobación del equipo.
* **Gobierno:** `OEUPB-Docs/CLAUDE.md` quedó como contexto canónico; el archivo de la raíz ahora es un puntero sin reglas duplicadas.
* **Navegación:** Se añadieron `README.md` y `SUMMARY.md`.
* **Backlog:** Se verificó el backlog contra el código; las tareas activas quedaron en `BACKLOG.md` y lo implementado pasó a `BACKLOG_ARCHIVE.md`.
* **Arquitectura:** Se documentaron frontend, backend, contratos, modelo de datos y despliegue según el estado real. Los documentos contradictorios se preservaron en `archive/architecture/`.
* **Especificaciones:** Se generó OpenAPI desde FastAPI y se añadió un esquema SQL de referencia.
* **Trazabilidad:** Se crearon casos de uso y una matriz inicial de requisitos, implementación y evidencia.
* **Decisiones:** Se registraron siete ADR y un design system inicial.
* **Operación:** Se documentaron comandos, configuración, datos de prueba, estrategia de pruebas, seguridad e inventario de scripts.
* **Alcance:** No se cambió lógica funcional ni se eliminaron scripts históricos.

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
