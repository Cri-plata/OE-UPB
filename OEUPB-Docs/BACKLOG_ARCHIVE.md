# Archivo histórico del backlog de OE UPB

Este archivo conserva tareas completadas, reemplazadas o descartadas. No debe usarse para priorizar trabajo activo.

## Verificado y archivado el 2026-09-22

Los siguientes ítems figuraban como pendientes en el backlog de 2026-08-26, pero el código actual demuestra que existe una implementación al menos funcional. Que estén archivados no significa que carezcan de deuda técnica; los pendientes reales relacionados están en `BACKLOG.md`.

- [x] **DOC-01 original — Contratos iniciales:** existen DTO TypeScript y Pydantic en `OEUPB-Contracts/`. Reemplazado por API-01 para resolver su divergencia.
- [x] **UI-00 — Setup de contratos TypeScript:** existen contratos en `OEUPB-Contracts/APIcontractfront/`.
- [x] **UI-01 — Login:** existe pantalla, repositorio de autenticación, interceptor JWT y endpoint real.
- [x] **UI-02 — Gestión de usuarios:** existe formulario y tabla conectados a `/api/usuarios`.
- [x] **UI-03 — Carga Excel:** existe pantalla conectada a `/api/carga/excel`, historial y eliminación por momento/año.
- [x] **UI-04 — Dashboard:** existen reporte general, tendencias y explorador conectados al backend.
- [x] **API-01 — Login/JWT:** implementado en `/api/auth/login`, con `rol` y `sede_id` en el token.
- [x] **API-02 — Usuarios:** existen listado, creación y eliminación.
- [x] **API-03 — Carga:** existe ETL con Pandas y persistencia de mediciones JSON.
- [x] **Diseño UI — Nuevo usuario:** el formulario fue implementado, aunque no existiera un mockup separado.
- [x] **REQ-01, REQ-02, REQ-03 y UX-01:** documentación inicial, requisitos, historias y revisión de mockups existentes.

## Elementos reemplazados

- **API-04 — IA simulada:** se retira como criterio suficiente. El backlog activo exige implementación verificable, anonimización y pruebas.
- **DB-01 original — Script SQL puntual:** se reemplaza por migraciones formales y esquema canónico versionado.

## Completado el 2026-09-23

- [x] **SEC-02 — Eliminar fallbacks inseguros de sede:** carga, historial y eliminación rechazan coordinadores sin sede y ya no asignan sede 1 por defecto.
- [x] **SEC-05 — Validar momentos:** backend y pruebas aceptan únicamente 0, 1 y 5.
- [x] **SEC-06 — Resolver formato permitido:** frontend y backend aceptan exclusivamente `.xlsx` y el backend valida que Pandas pueda leer el contenido.
- [x] **DB-01 — Incorporar migraciones formales:** Alembic contiene un baseline para bases nuevas y una migración verificada de `cargas`; la adopción de bases existentes está documentada.
- [x] **LOAD-01 — Carga auditable:** cada archivo tiene ID, huella, actor, sede, momento, cohorte, estado y versión; la recarga sustituye transaccionalmente la versión vigente y la eliminación opera por `carga_id`.
- [x] **SEC-07 — Evitar contraseña fija:** cada cuenta recibe una contraseña temporal aleatoria, mostrada una sola vez, y el backend exige reemplazarla antes de permitir otras operaciones.

## Completado el 2026-09-23 (P0 de permisos)

- [x] **SEC-01 — Aplicar la matriz RBAC aprobada:** backend restringe datos privados a coordinadores, separa administración CTIC/coordinador y cubre denegaciones y escalada con pruebas 403.
- [x] **SEC-04 — Corregir aislamiento del directorio:** tabla, perfil, programas e historial de mediciones vuelven a aplicar el `sede_id` autenticado.
- [x] **SHARE-01 — Modelar usuarios de consulta:** roles heredados migran a `Usuario_Consulta`; se persisten etiqueta informativa, cuatro permisos y programas validados contra los observados en la sede.
- [x] **SHARE-02 — Separar administración y ciclo de vida de cuentas:** se incorporaron desactivación/reactivación, borrado físico excepcional auditado, versión de autorización y revocación inmediata de sesiones.

## Completado el 2026-09-24 — Contratos, datos y calidad

- [x] **API-01 — Sincronizar consumidores con OpenAPI:** Angular consume tipos generados; un validador comprueba tipos, rutas, respuestas y ausencia de URLs duplicadas.
- [x] **API-02 — Decidir versionado de rutas:** ADR-011 mantiene `/api/*` con evolución compatible.
- [x] **DB-02 — Aprobar modelo objetivo:** ADR-012 conserva `Egresado`–`Medicion` y formaliza intentos.
- [x] **DB-03 — Crear catálogo de sedes:** `sedes` y `/api/sedes` reemplazan mapas repetidos y agregan FK.
- [x] **DB-04 — Completar invariantes heredadas:** mediciones completas, carga, actor, sede, momento, cohorte, respuestas e intento son obligatorios; cargas legacy usan actor técnico desactivado.
- [x] **DB-05 — Auditar eliminación física de cargas:** el evento inmutable se registra con actor, alcance, versión, cantidad, archivo y motivo en la misma transacción.
- [x] **DB-06 — Modelar múltiples intentos:** se persisten intento/fecha y los indicadores declaran selección del último intento identificado.
- [x] **QA-01 — Organizar y ampliar pruebas backend:** 19 pruebas cubren autenticación, RBAC, sedes, carga, reportes, intentos y contratos.
- [x] **QA-02 — Ampliar pruebas frontend:** 11 pruebas cubren login, interceptor, permisos, carga y directorio.
- [x] **QA-03 — Añadir pruebas de contrato e integración:** OpenAPI se compara con FastAPI y los tipos/consumidores se validan en CI.

## Completado el 2026-09-24 — Publicación de gráficas

- [x] **SHARE-03 — Modelar publicación de gráficas:** `PublicacionGrafica` conserva una instantánea agregada e inmutable con propietario, sede, programas, permiso, definición, métricas, aprobación, versión, estado y trazabilidad temporal.
- [x] **SHARE-04 — Implementar publicación y audiencia automática:** Reporte General, Tendencias y Explorador permiten publicar/retirar; el catálogo separado filtra en backend por rol, permisos y programas, sin exponer datos fuente.

## Completado el 2026-09-24 — Arquitectura frontend y operación

- [x] **FE-01 — Centralizar configuración de API:** la URL base vive en `environment.ts`/`api.config.ts` y un validador impide URLs duplicadas.
- [x] **FE-02 — Completar separación de capas:** Presentation dejó de importar `HttpClient`; los clientes tipados se concentran en `data/api/`.
- [x] **FE-03 — Proteger rutas por sesión y rol:** guards funcionales cubren sesión, invitado, cambio inicial pendiente y matriz de roles.
- [x] **FE-04 — Normalizar el design system:** tokens CSS globales y paleta de gráficas sustituyen colores repetidos; la arquitectura se valida automáticamente.
- [x] **OPS-01 — Configuración reproducible:** `.env.example`, dependencias fijadas, lockfile, migraciones y procedimiento desde cero están documentados y verificados.
- [x] **OPS-02 — Configurar CI:** GitHub Actions ejecuta pruebas, build, OpenAPI/tipos, enlaces/documentación y arquitectura frontend.

## Completado el 2026-09-24 — Funcionalidad objetivo P2

- [x] **DATA-01 — CRUD manual de egresados:** coordinadores crean, corrigen y eliminan registros manuales de su sede; cada operación exige motivo, conserva auditoría y bloquea conflictos intersede o borrado con mediciones.
- [x] **EXP-01 — Exportación:** el directorio filtrado se descarga como `.xlsx` y Reporte General, Tendencias y Explorador exportan sus lienzos como PNG.
- [x] **IA-02 — Clasificación NLP anonimizada:** el backend extrae únicamente respuestas abiertas, elimina correos, números y datos conocidos del egresado, y clasifica competencias localmente sin enviar texto a terceros.
- [x] **IA-03 — Alertas de patrones negativos:** la vista de analítica presenta reglas descriptivas por programa para baja empleabilidad y recurrencia negativa, con muestra y severidad; no se presenta como predicción.
- [x] **DEPLOY-01 — Preparación productiva en repositorio:** Dockerfiles, Compose, proxy HTTPS, CORS por entorno, health checks, logs de solicitud sin cuerpos, backup, restauración protegida por confirmación y runbook de rollback están versionados. La instalación real de Docker, certificados y simulacro institucional corresponde al ambiente.

## Completado el 2026-09-24 — Endurecimiento de autenticación P2

- [x] **SEC-03 — Endurecer secretos JWT:** fuera de desarrollo/test el proceso falla si `SECRET_KEY` falta, es conocida o tiene menos de 32 caracteres; producción exige además credenciales iniciales aleatorias.
- [x] **SEC-08 — Regenerar credencial temporal:** CTIC recupera coordinadores y cada coordinador sus usuarios de consulta; la operación exige motivo, reemplaza la credencial, revoca sesiones y conserva auditoría.
- [x] **SEC-09 — Ciclo de vida de credencial inicial:** el alta solicita documento y guarda solo su hash; la credencial vence, mantiene el cambio inicial bloqueante y usa modo aleatorio en producción. La recuperación emite una alternativa aleatoria de corta duración.

## Completado el 2026-09-24 — Higiene del repositorio P2

- [x] **REPO-01 — Clasificar scripts temporales:** se revisaron y retiraron 73 scripts históricos de parches, diagnósticos y datos; las utilidades vigentes quedaron en `tools/` o `OEUPB-Backend/scripts/`, y Git conserva lo retirado.
- [x] **DOC-01 — Auditar RF-01 a RF-73:** la matriz registra evidencia y estado individual para los 73 requisitos (32 implementados, 33 parciales, 7 no implementados y 1 en pausa).
- [x] **DOC-02 — Resolver decisiones abiertas:** las ocho preguntas del plan fueron resueltas por ADR vigentes o delimitadas formalmente en `audits/03-cierre-decisiones-abiertas.md`.

## Completado el 2026-09-25 — Auditoría de requerimientos 05

- [x] **EXP-02 — Restringir variables graficables:** `application/indicadores.py` clasifica las columnas por nombre normalizado y excluye documentos, nombres, correos, teléfonos, fechas, identificadores, códigos, IES, nivel académico y país. Se aplica en `/api/reportes/explorador/init`, `/api/reportes/explorador` (422) y la publicación. Pruebas en `test_indicadores.py` y `test_publicaciones.py`.
- [x] **PUB-03 — Recálculo de publicaciones en backend (ADR-015):** el cliente ya no envía métricas ni programas; el backend los recalcula con la sede del JWT, agrupa u omite las celdas con menos de 5 observaciones y rechaza con 422 las gráficas sin datos suficientes.
- [x] **PUB-04 — Retiro por coordinador de la sede:** si el propietario está inactivo o fue reasignado, otro coordinador de la sede propietaria puede retirar la publicación.
- [x] **ETL-02 — Egresados manuales al eliminar cargas:** la limpieza posterior a la eliminación ya no borra egresados con vínculo `egresados_sedes`. Antes eliminaba registros manuales de todas las sedes y, en MySQL, fallaba por la FK. Hay prueba de regresión.
- [x] **ETL-03 — Precedencia y concurrencia de cargas (ADR-014):** la carga no modifica los datos personales de egresados con corrección manual auditada, serializa por sede con `SELECT ... FOR UPDATE`, rechaza con 409 un archivo idéntico a la versión vigente y valida el año de grado entre 1900 y 2200.
- [x] **SEC-11 — Documento fuera de los logs:** el middleware enmascara el documento en las rutas del directorio y la imagen Docker desactiva el access log de Uvicorn.
- [x] **DOC-04 — Conciliación documental:** requisitos, casos de uso, matriz, arquitectura y seguridad quedaron alineados con ADR-013, ADR-014 y ADR-015; la resolución de cada hallazgo está en `audits/05-auditoria-requerimientos.md`.

## Completado el 2026-09-25 — P2 Analítica y contratos

- [x] **EXP-03 — Varias gráficas simultáneas:** el Explorador renderiza bloques `ExploradorGraficaComponent` independientes (variable, filtros, tipo, carga, error y publicación propios) con `Crear otra gráfica` y `Quitar gráfica`. Pruebas: `explorador.spec.ts`.
- [x] **ANA-01 — Filtros e indicadores del dashboard privado:** taxonomía RN-16 y formalidad según ADR-016, rango salarial, corrección del ingreso en SMMLV, filtros de selección múltiple de programa y cohorte (y momento en el Reporte General) con `/api/reportes/filtros`, comparación de momentos con cohorte común y mínimo de 5 pares en `/api/reportes/comparacion`, gráfica publicable de estado laboral y publicaciones que conservan los filtros. Pruebas: `test_reportes_analiticos.py`, `reporte-general.spec.ts`, `tendencias.spec.ts` y `filtros-analiticos.spec.ts`.
- [x] **DB-03 — Sede obligatoria para roles no CTIC:** `CHECK ck_usuarios_sede_por_rol` en el modelo, el esquema y la migración `h5d93b0e2f41`, que se detiene con un mensaje claro si existen cuentas que la incumplen. La base local cumplía la restricción (0 cuentas afectadas).
- [x] **ETL-01 — Documento normalizado y límites de carga (ADR-017):** normalización única en `application/documentos.py` aplicada a cargas, directorio y cuentas; límites de 25 MB y 50.000 filas; rechazo con 422 y detalle por fila; migración `i6e04c1f3a52`, que en la simulación de solo lectura sobre la base local no cambiaba ningún documento ni generaba colisiones.
- [x] **FIX — Proveedor faltante en Tendencias:** `TendenciasComponent` inyectaba `PublicacionControl` sin declararlo en `providers` (introducido en el commit `0d87af9`); ahora `tendencias.spec.ts` crea el componente.