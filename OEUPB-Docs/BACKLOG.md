# Backlog activo de OE UPB

**Última verificación contra el código:** 2026-09-25

**Última decisión de producto incorporada:** 2026-09-25 (ADR-014 y ADR-015)
**Regla:** este archivo contiene solo trabajo pendiente. Al completar o descartar un ítem, moverlo a [`BACKLOG_ARCHIVE.md`](BACKLOG_ARCHIVE.md) con evidencia.

## P1 — Flujo de publicación

- [ ] **PUB-01 — Cerrar correctamente el estado de publicación.** La acción `Publicar gráfica` debe finalizar en éxito/error, impedir duplicados, actualizar inmediatamente el estado visible y permitir reintento controlado. Desde ADR-015 el backend puede rechazar con 422 por datos insuficientes; la interfaz debe mostrar ese motivo sin quedar cargando.
  - **Implementado el 2026-09-25, pendiente de validación manual.** Causa: la aplicación es zoneless y el estado se guardaba en campos simples, así que la vista no se refrescaba hasta otra interacción. `presentation/shared/publicacion-control.ts` concentra el estado en signals, bloquea duplicados, muestra errores HTTP y de red en la gráfica con reintento, y reconcilia el 409 del retiro. Pruebas: `publicacion-control.spec.ts`.
- [ ] **PUB-02 — Corregir la carga del catálogo publicado.** La vista debe resolver listas con datos, vacías y errores; debe reflejar el ciclo publicar → consultar → retirar sin perder las restricciones de audiencia.
  - **Implementado el 2026-09-25, pendiente de validación manual.** La misma causa zoneless. `/publicaciones` usa signals, muestra los estados de datos, vacío y error con `Reintentar`, y tiene un botón `Actualizar`. Pruebas: `publicaciones.spec.ts`, más la prueba de backend `test_ciclo_publicar_consultar_retirar_para_consulta`.
  - **Para cerrar ambos:** validar el flujo en el entorno local (ver la lista de `docs/07-estado-funcional-actual.md`, sección 8) y archivarlos con la evidencia.

## P2 — Analítica y contratos

- [ ] **EXP-03 — Permitir varias gráficas simultáneas.** Añadir `Crear otra gráfica` y mantener configuraciones, estados y acciones independientes para comparar varias visualizaciones en la misma pantalla.
- [ ] **ANA-01 — Filtros e indicadores del dashboard privado.** Multiselección de programa y cohorte en Reporte General y Tendencias (HU-09), comparación de dos momentos con cohorte común (HU-08), tasa formal/informal y rango salarial (HU-07 CA1). Definir la fórmula de la tasa de empleo sobre la taxonomía de RN-16 y el tratamiento de respuestas vacías o no mapeables. Cierra RF-21, RF-22 y RF-26 (auditoría 05: C-12, B-17).
- [ ] **DB-03 — Invariante de sede por rol en la base.** Añadir una migración con `CHECK (rol = 'Admin_CTIC' OR sede_id IS NOT NULL)`, previa verificación de los datos existentes, y reflejarla en `oeupb-schema.sql` (auditoría 05: C-10).
- [ ] **ETL-01 — Normalizar el documento de identidad y los límites de carga.** Definir la normalización (puntos, espacios, ceros a la izquierda, documentos alfanuméricos), unificar la validación entre egresado (3-50 caracteres) y usuario (6-20 dígitos), fijar el tamaño y el número de filas máximos, y responder a una carga inválida con error HTTP y detalle por fila en lugar de 200 con `errores` (auditoría 05: B-13, B-14). Requiere migrar los documentos existentes con pruebas de equivalencia.

## P3 — Calidad de contrato y documentación

- [ ] **API-02 — Completar el contrato de errores.** Declarar el esquema `{detail}` y los códigos 401/403/404/409 por endpoint, añadir el patrón `@upb.edu.co` al correo y marcar `DELETE /api/usuarios/{id}` como alias obsoleto de `POST /{id}/desactivar` (auditoría 05: C-11, C-18).
- [ ] **PRG-01 — Catálogo normalizado de programas.** La visibilidad entre sedes depende de que los nombres de programa coincidan como texto. Definir la normalización o una tabla de equivalencias, y el tratamiento de programas asignados que dejan de observarse (auditoría 05: B-07, B-08).
- [ ] **ANA-02 — Criterios de alertas.** Enumerar la severidad y fijar umbrales y muestra mínima de las alertas descriptivas de `/api/analitica/resumen` (auditoría 05: B-18).
- [ ] **DOC-03 — Completar el modelo y el catálogo de requisitos.** Añadir al diagrama ER `auditoria_cuentas`, `auditoria_egresados`, los atributos de `eventos_eliminacion_carga` y las columnas faltantes de `publicaciones_graficas`. Priorizar los RF/RNF, corregir los `Requerimiento Ligado` sin dependencia funcional y dar métricas verificables a los RNF-01 a RNF-06 (auditoría 05: C-17, C-19, B-20).

## P2 — Decisión de producto en pausa

- [ ] **IA-01 — Modelo predictivo (en pausa).** No iniciar implementación hasta que producto apruebe objetivo, métricas, población, horizonte y criterios de aceptación conforme a ADR-009.
