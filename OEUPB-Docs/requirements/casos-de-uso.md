# Casos de uso de OE UPB

**Estado:** baseline objetivo actualizado con la política RBAC aprobada el 2026-09-23 y conciliado con la auditoría 05

**Fecha de revisión:** 2026-09-25

## CU-01 — Iniciar sesión

- **Actor:** usuario institucional.
- **Precondición:** cuenta existente y activa.
- **Flujo:** ingresar correo/contraseña → validar hash → emitir JWT → si la credencial es temporal, exigir cambio bloqueante → emitir nuevo JWT → redirigir según rol.
- **Resultado:** sesión con rol y sede; ninguna función distinta del cambio de contraseña queda disponible mientras la credencial sea temporal.
- **Implementación:** existente en `/api/auth/login` y `/login`.

## CU-02 — Gestionar cuentas

- **Actor:** Admin CTIC para coordinadores; Coordinador de Sede para usuarios de consulta de su sede.
- **Flujo:** listar dentro del alcance → validar correo `@upb.edu.co`, tipo de cuenta y sede → para `Usuario_Consulta`, seleccionar manualmente etiqueta informativa, permisos del catálogo y programas observados en cargas visibles de la sede → generar la credencial temporal (cédula en desarrollo, aleatoria en producción) y almacenar únicamente su hash → crear, modificar, desactivar, reactivar, reemitir credencial o borrar físicamente una cuenta ya desactivada.
- **Resultado:** cuenta administrada sin escalada de privilegios.
- **Implementación:** implementada en `/api/usuarios` con pruebas RBAC. El borrado físico lo ejecuta el mismo administrador del alcance, exige cuenta desactivada y motivo, queda en `auditoria_cuentas` y responde 409 si la cuenta conserva relaciones.

## CU-03 — Cargar encuesta

- **Actor:** Coordinador de sede.
- **Flujo:** seleccionar momento/año de grado/archivo → validar → limpiar → aceptar ausencias opcionales y mediciones anónimas permitidas → ante cualquier error obligatorio revertir el archivo completo → resolver duplicados → crear carga auditable → reemplazar transaccionalmente la versión vigente de igual sede/momento/cohorte → informar resultado.
- **Resultado:** carga identificable y mediciones asociadas a la sede del token; un fallo conserva la versión anterior.
- **Implementación:** existente; SEC-02, SEC-05 y SEC-06 cerradas. Incluye bloqueo por sede, rechazo de archivo idéntico (409), rango de año 1900-2200 y protección de correcciones manuales.

## CU-04 — Consultar historial y eliminar carga

- **Actor:** Coordinador autorizado.
- **Flujo:** listar archivos cargados → seleccionar por `carga_id` → confirmar eliminación → registrar un evento inmutable de auditoría → borrar físicamente, en una transacción, las mediciones de esa carga y la carga correspondiente dentro de la sede autorizada.
- **Implementación:** existente y restringida a `Coordinador_Sede` con sede; solo se elimina la versión vigente (409 en otro caso) y se conservan los egresados del directorio manual.

## CU-05 — Consultar reporte general

- **Actor:** Coordinador de Sede. El Usuario de Consulta solo ve las instantáneas publicadas de este origen (RN-24).
- **Flujo:** solicitar KPIs → derivar la sede privada del JWT sin selector de sede → calcular indicadores → presentar gráficas. Las publicaciones de otras sedes se consultan en una vista separada.
- **Implementación:** parcial; existen KPIs privados; faltan filtros de programa y cohorte, tasa formal/informal y rango salarial (ANA-01).

## CU-06 — Consultar tendencias

- **Actor:** Coordinador de Sede. El Usuario de Consulta solo ve las instantáneas publicadas de este origen (RN-24).
- **Flujo:** elegir indicador → agregar por año/momento → presentar línea o barras.
- **Implementación:** parcial; existe un endpoint por indicador (`empleabilidad`, `salario`, `satisfaccion`) para los cinco programas con más datos; el contrato no representa todavía la comparación de dos momentos ni la cohorte común (ANA-01).

## CU-07 — Explorar variables

- **Actor:** Coordinador de Sede. El Usuario de Consulta solo ve las instantáneas publicadas de este origen (RN-24).
- **Flujo:** obtener variables permitidas → seleccionar cruce → agregar respuestas en backend → graficar sin exponer respuestas individuales.
- **Implementación:** parcial; el catálogo RN-31 se aplica en backend desde el 2026-09-25 (init, consulta y publicación, con pruebas). Falta permitir varias gráficas simultáneas (EXP-03).

## CU-08 — Buscar egresado

- **Actor:** Coordinador de la sede propietaria.
- **Flujo:** filtrar por texto/programa → paginar → abrir ficha → consultar mediciones visibles.
- **Implementación:** existente y aislada por sede; incluye altas manuales auditadas. Un documento ya registrado responde 409 sin devolver datos y un egresado vinculado a otra sede no se edita (ADR-014).

## CU-09 — Exportar resultados

- **Actor:** Coordinador de Sede. El catálogo aprobado de permisos de consulta no incluye exportación, por lo que la vista de publicaciones no ofrece descarga.
- **Resultado esperado:** tabla Excel o gráfica como imagen.
- **Implementación:** directorio filtrado en Excel y gráficas privadas como PNG.

## CU-10 — Ejecutar análisis de IA

- **Actor:** Coordinador de Sede.
- **Flujo implementado:** seleccionar los datos de la sede → anonimizar respuestas abiertas localmente → clasificar competencias → mostrar conteos y alertas descriptivas.
- **Implementación:** clasificación y alertas verificadas; predicción continúa en pausa conforme a ADR-009.

La capacidad predictiva de RF-71/HU-10 está en pausa por decisión de producto. La clasificación NLP no usa servicios externos ni devuelve los textos fuente.

## CU-11 — Configurar usuario de consulta

- **Actor:** Coordinador de Sede.
- **Precondición:** el coordinador tiene una sede válida en su identidad autenticada.
- **Flujo:** crear cuenta `Usuario_Consulta` → asignar sede propia → elegir una etiqueta informativa sin privilegios implícitos → seleccionar manualmente permisos y programas observados en cargas visibles de la sede → guardar.
- **Resultado:** el backend puede calcular automáticamente qué gráficas puede ver la cuenta.
- **Restricción:** solo se incluyen instantáneas publicadas; una cuenta de consulta no accede a gráficas privadas de su sede.
- **Implementación:** implementada mediante permisos/programas persistidos y catálogo de publicaciones filtrado en backend.

## CU-12 — Publicar o retirar una gráfica

- **Actor:** Coordinador propietario de los datos.
- **Precondición:** coordinador activo con sede.
- **Flujo:** abrir gráfica → pulsar `Publicar` y confirmar la revisión de privacidad → el backend valida la variable (RN-31), recalcula métricas y programas con los datos de la sede del JWT, aplica el umbral k = 5 y versiona → la audiencia se calcula al consultar. `Retirar publicación` valida la propiedad o el propietario inactivo o reasignado.
- **Resultado:** los usuarios autorizados ven la gráfica y sus métricas agregadas; no obtienen filas, respuestas individuales ni datos personales.
- **Implementación:** backend implementado en `/api/publicaciones` con recálculo y umbral (ADR-015); la interfaz aún presenta los problemas de estado de PUB-01 y PUB-02, por lo que RF-35 sigue parcial.
