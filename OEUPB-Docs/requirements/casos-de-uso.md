# Casos de uso de OE UPB

**Estado:** baseline objetivo actualizado con la política RBAC aprobada el 2026-09-23

**Fecha de revisión:** 2026-09-23

## CU-01 — Iniciar sesión

- **Actor:** usuario institucional.
- **Precondición:** cuenta existente y activa.
- **Flujo:** ingresar correo/contraseña → validar hash → emitir JWT → si la credencial es temporal, exigir cambio bloqueante → emitir nuevo JWT → redirigir según rol.
- **Resultado:** sesión con rol y sede; ninguna función distinta del cambio de contraseña queda disponible mientras la credencial sea temporal.
- **Implementación:** existente en `/api/auth/login` y `/login`.

## CU-02 — Gestionar cuentas

- **Actor:** Admin CTIC para coordinadores; Coordinador de Sede para usuarios de consulta de su sede.
- **Flujo:** listar dentro del alcance → validar correo `@upb.edu.co`, tipo de cuenta y sede → para `Usuario_Consulta`, seleccionar manualmente etiqueta informativa, permisos del catálogo y programas observados en cargas visibles de la sede → recibir la cédula y almacenar únicamente su hash como contraseña temporal → crear, bloquear, modificar, desactivar o solicitar borrado excepcional.
- **Resultado:** cuenta administrada sin escalada de privilegios.
- **Implementación:** parcial; endpoints básicos existen, pero faltan bloqueo, permisos, programas y enforcement integral de la matriz aprobada.

## CU-03 — Cargar encuesta

- **Actor:** Coordinador de sede.
- **Flujo:** seleccionar momento/año de grado/archivo → validar → limpiar → aceptar ausencias opcionales y mediciones anónimas permitidas → ante cualquier error obligatorio revertir el archivo completo → resolver duplicados → crear carga auditable → reemplazar transaccionalmente la versión vigente de igual sede/momento/cohorte → informar resultado.
- **Resultado:** carga identificable y mediciones asociadas a la sede del token; un fallo conserva la versión anterior.
- **Implementación:** existente con brechas SEC-02, SEC-05 y SEC-06.

## CU-04 — Consultar historial y eliminar carga

- **Actor:** Coordinador autorizado.
- **Flujo:** listar archivos cargados → seleccionar por `carga_id` → confirmar eliminación → registrar un evento inmutable de auditoría → borrar físicamente, en una transacción, las mediciones de esa carga y la carga correspondiente dentro de la sede autorizada.
- **Implementación:** existente; autorización por rol debe endurecerse.

## CU-05 — Consultar reporte general

- **Actor:** Coordinador o Usuario de Consulta autorizado.
- **Flujo:** solicitar KPIs → derivar la sede privada del JWT sin selector de sede → aplicar permisos y programas → calcular indicadores → presentar gráficas. Las publicaciones de otras sedes se consultan en una vista separada.
- **Implementación:** parcial; existen KPIs privados y un catálogo separado de publicaciones autorizado para `Usuario_Consulta`; faltan filtros analíticos y cobertura RF individual.

## CU-06 — Consultar tendencias

- **Actor:** Coordinador o Usuario de Consulta autorizado.
- **Flujo:** elegir indicador → agregar por año/momento → presentar línea o barras.
- **Implementación:** parcial; existe un endpoint base, pero el contrato no representa todavía la comparación de dos momentos, la cohorte común ni los permisos objetivo.

## CU-07 — Explorar variables

- **Actor:** Coordinador o Usuario de Consulta autorizado.
- **Flujo:** obtener variables permitidas → seleccionar cruce → agregar respuestas en backend → graficar sin exponer respuestas individuales.
- **Implementación:** parcial; el explorador base funciona, pero la validación manual del 2026-09-25 confirmó que ofrece datos personales y metadatos no analíticos. Falta aplicar RN-31 en backend y permitir varias gráficas simultáneas.

## CU-08 — Buscar egresado

- **Actor:** Coordinador de la sede propietaria.
- **Flujo:** filtrar por texto/programa → paginar → abrir ficha → consultar mediciones visibles.
- **Implementación:** existente y aislada por sede; incluye altas manuales auditadas.

## CU-09 — Exportar resultados

- **Actor:** Coordinador de Sede. El catálogo aprobado de permisos de consulta no incluye exportación.
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
- **Precondición:** la gráfica se calculó exclusivamente con datos fuente de su sede.
- **Flujo:** abrir gráfica → pulsar `Publicar` o `Retirar publicación` → validar propiedad → guardar estado, programas y definición agregada → recalcular audiencia por permisos.
- **Resultado:** los usuarios autorizados ven la gráfica y sus métricas agregadas; no obtienen filas, respuestas individuales ni datos personales.
- **Implementación:** implementada en `/api/publicaciones` y en las acciones de Reporte General, Tendencias y Explorador.
