# Matriz de trazabilidad funcional

**Verificada:** 2026-09-25  
**Alcance:** auditoría individual de RF-01 a RF-73 contra código, contrato y pruebas vigentes.

Estados: **Implementado** (flujo verificable), **Parcial** (solo parte o capacidad genérica), **No implementado** (sin comportamiento correspondiente) y **En pausa** (decisión explícita).

| RF | Capacidad | Evidencia principal | Estado |
|---|---|---|---|
| RF-01 | Subir Excel ministerial | `carga_router.py`, Carga de datos y pruebas | Implementado; solo `.xlsx` |
| RF-02 | Leer Momento 0 | validación de momento y `Medicion` | Implementado |
| RF-03 | Leer Momentos 1 y 5 | validación de momento y `Medicion` | Implementado |
| RF-04 | Limpiar/organizar carga | normalización Pandas | Implementado |
| RF-05 | Persistir en base central | `Egresado`, `Carga`, `Medicion` | Implementado |
| RF-06 | Evitar egresados duplicados | documento único, precedencia ADR-014 y doble titulación | Implementado |
| RF-07 | Carga auditable | actor, sede, huella, versión y resultado | Implementado |
| RF-08 | Importar históricos | ETL `.xlsx` admite cohortes anteriores; las bases antiguas deben exportarse a `.xlsx` (RN-05) | Parcial |
| RF-09 | Resultado y recarga atómica | respuesta, rollback y versión vigente | Implementado |
| RF-10 | Crear egresado manual | `POST /api/directorio/egresados` | Implementado |
| RF-11 | Editar/corregir egresado | `PATCH /api/directorio/egresados/{documento}` | Implementado |
| RF-12 | Borrar egresado | `DELETE`, motivo, auditoría y protecciones | Implementado |
| RF-13 | Organizar por ceremonia | hay fecha/cohorte, no ceremonia ni filtro | Parcial |
| RF-14 | Buscar por nombre | parámetro `q` del Directorio | Implementado |
| RF-15 | Buscar por identificación | `q` y perfil por documento | Implementado |
| RF-16 | Agrupar por programa | catálogo y filtro `programa` | Implementado |
| RF-17 | Actualizar situación laboral catalogada | respuesta JSON; CRUD no edita el catálogo | Parcial |
| RF-18 | Dashboard interactivo | Reporte, Tendencias, Explorador y Chart.js | Implementado |
| RF-19 | Situación laboral | KPI de empleabilidad y Tendencias | Implementado |
| RF-20 | Estudios adicionales | pregunta genérica, sin indicador curado | Parcial |
| RF-21 | Filtro por programa | selección múltiple en Reporte General y Tendencias; filtro por bloque en el Explorador | Implementado |
| RF-22 | Filtro por cohorte | selección múltiple de cohortes en Reporte General y Tendencias; filtro por bloque en el Explorador | Implementado |
| RF-23 | Cuatro situaciones laborales | `estado_laboral` (ADR-016) y gráfica de estado laboral | Implementado |
| RF-24 | Tendencias de empleo | `/api/reportes/tendencias`, momentos 0/1/5 | Implementado |
| RF-25 | Trabajo formal | tasa formal/informal por tipo de contrato en M1/M5 (ADR-016) | Implementado |
| RF-26 | Salario promedio/rango | promedio y rango (mínimo, mediana, máximo) con SMLV/SMMLV | Implementado |
| RF-27 | Sectores económicos | pregunta genérica, sin gráfica curada | Parcial |
| RF-28 | Dispersión de datos | sin cálculo ni visualización de dispersión | No implementado |
| RF-29 | Ciudades de residencia | pregunta genérica, sin mapa | Parcial |
| RF-30 | Satisfacción con universidad | promedios y gráfica de satisfacción | Implementado |
| RF-31 | Sugerir cursos/programas | sin motor de recomendación aprobado | No implementado |
| RF-32 | Usuario y contraseña | JWT, hash, expiración, cambio; ADR-013 | Implementado |
| RF-33 | Alcance Coordinador | RBAC, sede, usuarios y publicación | Implementado |
| RF-34 | Aislamiento por sede | filtros backend y pruebas negativas | Implementado |
| RF-35 | Gráficas agregadas publicadas | `/api/publicaciones` con recálculo, k = 5 y RN-31 (ADR-015); estados de interfaz corregidos con pruebas (PUB-01/PUB-02), pendientes de validación manual | Parcial |
| RF-36 | Administración jerárquica | CTIC/coordinador según RBAC | Implementado |
| RF-37 | Permisos/programas/audiencia | audiencia calculada en backend | Implementado |
| RF-38 | Satisfacción con profesores | preservada en `mediciones.respuestas` | Parcial |
| RF-39 | Trabajo mientras estudiaba | preservada en `mediciones.respuestas` | Parcial |
| RF-40 | Opinión de instalaciones | preservada en `mediciones.respuestas` | Parcial |
| RF-41 | Habilidades desarrolladas | preservada en `mediciones.respuestas` | Parcial |
| RF-42 | Planes al graduarse | preservada en `mediciones.respuestas` | Parcial |
| RF-43 | Cambio de ciudad | preservada en `mediciones.respuestas` | Parcial |
| RF-44 | Motivo de cambio de ciudad | preservada en `mediciones.respuestas` | Parcial |
| RF-45 | Meses hasta primer empleo | preservada en `mediciones.respuestas` | Parcial |
| RF-46 | Tipo de contrato | preservada en `mediciones.respuestas` | Parcial |
| RF-47 | Utilidad de lo aprendido | preservada en `mediciones.respuestas` | Parcial |
| RF-48 | Empresas creadas | preservada en `mediciones.respuestas` | Parcial |
| RF-49 | Dificultad para buscar trabajo | preservada en `mediciones.respuestas` | Parcial |
| RF-50 | Viaje académico exterior | preservada en `mediciones.respuestas` | Parcial |
| RF-51 | Canal para conseguir empleo | preservada en `mediciones.respuestas` | Parcial |
| RF-52 | Unir momentos por documento | FK, intentos y `medicion_policy.py` | Implementado |
| RF-53 | Movilidad entre etapas | sin cruce temporal de ubicaciones | No implementado |
| RF-54 | Formación vs. exigencia laboral | sin cruce específico | No implementado |
| RF-55 | Financiación vs. empleo | sin cruce específico | No implementado |
| RF-56 | Conteo por programa y año | distribución y filtro anual separados | Parcial |
| RF-57 | Promedio hasta primer empleo | sin tabla/cálculo específico | No implementado |
| RF-58 | Sectores y tamaños de empresa | exploración univariada genérica | Parcial |
| RF-59 | Áreas por mejorar | pregunta genérica, sin resumen curado | Parcial |
| RF-60 | Satisfacción laboral | algunos promedios, no todos los ejes | Parcial |
| RF-61 | Comparar cuatro estados | gráfica de estado laboral con filtros, publicable | Implementado |
| RF-62 | Dispersión salarial por programa | sin percentiles/desviación/gráfico | No implementado |
| RF-63 | Efectividad de canales | pregunta graficable, sin efectividad | Parcial |
| RF-64 | Utilidad de conocimientos | promedio de aplicación en Reporte | Implementado |
| RF-65 | Razones para recomendar | pregunta graficable en Explorador | Parcial |
| RF-66 | Herramientas de emprendimiento | pregunta graficable en Explorador | Parcial |
| RF-67 | Tendencias de nuevos estudios | pregunta graficable, sin detector dedicado | Parcial |
| RF-68 | Destinos de movilidad | pregunta graficable, sin mapa/flujo | Parcial |
| RF-69 | Descargar tablas en Excel | exporta Directorio, no toda analítica | Parcial |
| RF-70 | Exportar gráficas | PNG en Reporte, Tendencias y Explorador | Implementado |
| RF-71 | Modelo predictivo | ADR-009 e IA-01 | En pausa |
| RF-72 | Clasificar texto abierto | `nlp_service.py`, Analítica y pruebas | Implementado, NLP local anonimizado |
| RF-73 | Alertas de patrones negativos | endpoint y vista Analítica | Implementado, descriptivo |

## Resultado

| Estado | Cantidad |
|---|---:|
| Implementado | 34 |
| Parcial | 31 |
| No implementado | 7 |
| En pausa | 1 |
| **Total** | **73** |

Los RF-38 a RF-51 preservan cualquier columna dinámica, pero no tienen validación semántica individual. Los estados Parcial y No implementado describen brechas del alcance objetivo; producto debe priorizarlas antes de convertirlas en backlog comprometido. RF-71 permanece en pausa. Las brechas priorizadas por producto están en `BACKLOG.md`.

## Autorización verificada

| Operación | Admin CTIC | Coordinador | Consulta |
|---|---:|---:|---:|
| Administrar coordinadores | Sí | No | No |
| Administrar consulta | No | Propia sede | No |
| Datos fuente/directorio | No | Propia sede | No |
| Carga y eliminación | No | Propia sede | No |
| Publicar/retirar | No | Gráfica propia (retiro también si el propietario está inactivo o reasignado) | No |
| Ver publicadas | No | Todas las de otras sedes | Según permisos/programas, cualquier sede |
| Reportes, tendencias, explorador, analítica | No | Propia sede | No |

La autoridad se aplica en backend; los guards del frontend solo controlan navegación.
