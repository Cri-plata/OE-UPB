# Estudio del proyecto OE UPB

**Fecha:** 2026-10-06
**Base:** rama `dev-cristian` (incluye el commit `46921d7`), código, contrato OpenAPI, matriz de trazabilidad, auditorías 07 y 08.

## 1. Resumen ejecutivo

OE UPB es el Observatorio de Egresados de la Universidad Pontificia Bolivariana. Reemplaza las hojas de cálculo dispersas de las encuestas del OLE (momentos 0, 1 y 5) por una plataforma web con aislamiento estricto por sede, analítica, publicación controlada de gráficas entre sedes e inteligencia artificial local.

El producto está **listo para la exposición**. El stack de producción (Docker Compose con MySQL, FastAPI, Angular y nginx con HTTPS) se desplegó desde cero y superó un recorrido funcional de 54 comprobaciones con los tres roles (auditoría 08). Las suites automáticas pasan: 82 pruebas de backend y 107 de frontend. De los 73 requisitos funcionales, 36 están implementados, 30 parcialmente y 7 sin implementar. Las brechas restantes son analíticas curadas de baja o media prioridad, no funciones del núcleo.

| Indicador | Valor |
|---|---|
| Periodo de desarrollo | 2026-08-26 a 2026-10-05 (6 semanas) |
| Commits / integrantes | 51 / 3 (Cri-plata 22, GiosueAcosta 21, Atalpe 8) |
| Requisitos funcionales | 73: 36 implementados, 30 parciales, 7 sin implementar |
| API | 46 operaciones en 42 rutas; 70 esquemas |
| Pantallas | 14 rutas Angular; 15 mockups |
| Modelo de datos | 11 tablas; 12 migraciones Alembic |
| Pruebas automáticas | 82 backend (15 archivos) y 107 frontend (21 archivos) |
| Decisiones documentadas | 20 ADR |
| Pendientes activos | 11 ítems en el backlog |

## 2. Problema y alcance

- **Problema:** las encuestas de egresados llegan como archivos Excel del Ministerio por sede, momento y cohorte. Consolidarlas, evitar duplicados, seguir a la misma persona entre momentos y compartir resultados sin exponer datos personales era manual.
- **Usuarios:** `Admin_CTIC` administra coordinadores. `Coordinador_Sede` carga datos y analiza su sede, gestiona usuarios de consulta y publica gráficas. `Usuario_Consulta` (rector, profesor o administrativo) solo ve las gráficas publicadas que le corresponden por permisos y programas.
- **Fuera del alcance:** encuestas manuales, custodia institucional de identidades (ADR-014) y verificación en dos pasos (diferida a Proyecto de Grado).

## 3. Arquitectura

```text
Navegador ──HTTPS──> nginx (proxy, TLS, 26 MB, 180 s)
                       ├── /      -> Angular 22 (nginx estático, índice no-cache)
                       └── /api/  -> FastAPI + Uvicorn (2 workers, Python 3.13)
                                        └── SQLAlchemy + Alembic -> MySQL 8.4
```

- **Frontend** (Angular 22.1 standalone, zoneless, TypeScript 6, Chart.js): capas `domain/`, `data/` y `presentation/`. Los clientes HTTP viven en `data/api` con tipos generados desde OpenAPI. Los guards controlan la navegación, pero la autorización la decide el backend.
- **Backend** (FastAPI, Pandas, scikit-learn, spaCy): capas `domain/`, `application/`, `infrastructure/` y `presentation/`. Los routers todavía concentran parte de la lógica de negocio (deuda reconocida).
- **Datos:** la identidad (`egresados`) está separada de las respuestas longitudinales (`mediciones`, JSON con intentos). Hay cargas versionadas, publicaciones inmutables y auditorías de cuentas, egresados y cargas eliminadas.
- **Contrato:** `specs/api/openapi.json` es la fuente canónica. `tools/validate_contracts.py` verifica tipos, esquemas y, desde la auditoría 08, que cada ruta de los clientes exista tal cual en el contrato.

### Tamaño del código

| Componente | Líneas |
|---|---:|
| Backend (aplicación) | 6.551 Python |
| Backend (migraciones) | 927 Python |
| Backend (pruebas en `tests/`) | 1.898 Python |
| Frontend | 3.757 TS + 2.690 HTML + 5.430 SCSS |
| Frontend (pruebas) | 2.317 TS |

Los módulos más grandes son `ia_service.py` (1.071), `prediccion_service.py` (955), `ia_router.py` (821), `indicadores.py` (540) y `carga_router.py` (504).

## 4. Funcionalidad por módulo

| Módulo | Capacidad | Estado |
|---|---|---|
| Autenticación | Correo institucional, JWT con versión de autorización, credencial temporal aleatoria con cambio obligatorio y revocación inmediata | Completo |
| Cuentas | CTIC → coordinadores; coordinador → usuarios de consulta con etiqueta, permisos y programas observados | Completo |
| Carga | `.xlsx` hasta 25 MB y 50.000 filas, todo-o-nada, versionado por sede, momento y cohorte, rechazo de archivos idénticos, doble titulación, mediciones anónimas y bloqueo por sede | Completo |
| Directorio | Búsqueda por nombre, cédula o ID, ficha longitudinal, altas y correcciones manuales auditadas, exportación Excel | Completo |
| Reporte general | KPI de empleabilidad, formalidad, salario y satisfacción, con filtros de programa, cohorte y momento | Completo |
| Tendencias | Indicadores por momento y comparación de los mismos egresados entre momentos (mínimo 5 pares) | Completo |
| Explorador | Cruces de variables con catálogo analítico que excluye datos personales (RN-31) | Completo |
| Publicaciones | Recálculo en backend, umbral k = 5, versiones, retiro y audiencia derivada de permisos y programas | Completo (retiro por sucesor sin interfaz: PUB-03) |
| Analítica | Competencias en texto libre (NLP local) y alertas descriptivas por programa | Completo |
| IA | Habilidades demandadas, reglas de asociación, comparativa M0/M1/M5, curaduría institucional, modelo de análisis de empleabilidad (Gradient Boosting con ponderación de clases), exportaciones | Completo |

**Brechas de requisitos (30 parciales y 7 sin implementar):** sobre todo indicadores curados de preguntas específicas (RF-38 a RF-51 se conservan en el JSON sin validación semántica), cruces avanzados (RF-53 a RF-55), dispersión (RF-28, RF-62), mapas de movilidad, exportación Excel de todas las tablas analíticas (RF-69) y recomendación de programas (RF-31). Producto debe priorizarlas (PRD-01).

## 5. Seguridad y privacidad

- **Aislamiento por sede en el backend:** la sede sale del JWT y no hay selector de sede en las vistas privadas. Las pruebas cubren el acceso entre sedes.
- **Única vía entre sedes:** las publicaciones. Cada una se recalcula en el backend, ninguna celda representa menos de 5 observaciones y el título se valida contra correos, enlaces y números de documento (ADR-015, ADR-020).
- **IA local y anonimizada:** el texto libre se anonimiza antes de analizarlo (correos, números largos, documento y nombre) y no sale a servicios externos. El modelo de análisis de empleabilidad no usa identificadores como variables.
- **Credenciales y sesiones:** solo se guardan hashes bcrypt, la credencial aleatoria se muestra una vez y vence, y desactivar una cuenta revoca su sesión al instante.
- **Operación:** logs sin documentos (se enmascaran rutas y el access log de Uvicorn está desactivado), HTTPS con HSTS, CORS por entorno y secreto JWT obligatorio de 32 caracteres o más en producción.
- **Riesgos aceptados:** revelación por diferencia entre publicaciones con filtros solapados, y métricas de otros programas visibles para un usuario con al menos un programa en común (ADR-020).

## 6. Calidad y proceso

- **Pruebas:** backend con `unittest` sobre SQLite en memoria (RBAC, aislamiento, carga transaccional, publicaciones, IA, contrato OpenAPI). Frontend con Vitest y el builder de Angular. La suite del backend también se verificó dentro de la imagen de Python 3.13.
- **Validadores:** contrato y consumidores, documentación (enlaces y OpenAPI) y arquitectura del frontend (capas, guards y tokens).
- **Auditorías:** ocho auditorías documentadas. La 07 (requisitos) dejó 41 hallazgos con veredicto y la 08 (despliegue) corrigió 10 defectos que solo aparecían en producción.
- **Gobierno:** 20 ADR, backlog vivo, matriz de trazabilidad verificada, mockups y mapa de pantallas obligatorios antes de cualquier cambio visual.

### Lecciones del proceso

1. **El entorno local no reproducía producción.** Python 3.14 frente a 3.13, el modelo de spaCy instalado solo en local, sin proxy delante y con el host igual al del backend: cuatro defectos de la auditoría 08 solo se manifestaban desplegados. Conviene construir y ejecutar la imagen en cada integración.
2. **Detección de cambios zoneless.** El estado asíncrono fuera de signals dejó pantallas sin refrescar en tres ocasiones (PUB-01, PUB-02 y "Mi Perfil"). La regla del equipo es usar signals en el código nuevo.
3. **Probar la respuesta HTTP, no solo el servicio.** El campo `estrategia_balanceo` del commit `46921d7` se calculaba en el servicio, pero el `response_model` lo descartaba y el badge de la interfaz nunca aparecía. Se corrigió en este estudio, con una prueba sobre el endpoint.

## 7. Deuda técnica y riesgos

| Riesgo | Impacto | Recomendación |
|---|---|---|
| Lógica de negocio en routers grandes (`ia_router.py`, `carga_router.py`) | Mantenimiento y pruebas más costosos | Extraer casos de uso a `application/` con pruebas |
| ~~Scripts de prueba en la raíz del backend que usaban la base de `.env`~~ | Resuelto el 2026-10-06 (TST-01): la prueba del modelo de empleabilidad pasó a `tests/` sobre SQLite y los diagnósticos a `scripts/dev/diagnostico_ia/` | — |
| Pantallas con `ChangeDetectorRef` (UI-03) | Pantallas en "Cargando…" tras recargas en caliente | Migrar a signals |
| IA en frío | La primera consulta por worker tras un reinicio puede tardar unos 40 s con decenas de miles de respuestas | Calentar antes de la demo; a futuro, precálculo o caché compartida |
| Cachés en memoria por worker | Resultados de IA calculados por proceso (la taxonomía ya se alinea por firma) | Caché compartida (Redis) si se escala |
| Pendientes de interfaz con mockup (PUB-03, PUB-04, CAR-01) y decisiones de producto (PUB-05, AUT-01, PRD-01) | Flujos de excepción sin interfaz | Priorizar después de la exposición |
| Presupuesto de estilos superado en Analítica y Habilidades | Solo aviso de build | Extraer estilos compartidos |

## 8. Recomendaciones

1. **Antes de la exposición:** seguir la lista de preparación de la [auditoría 08](../audits/08-auditoria-funcional-despliegue.md): certificados y dominio reales, reloj sincronizado, calentamiento de la IA, cuentas de demostración ya activadas y un archivo de pocos miles de filas.
2. **Corto plazo:** cerrar UI-03 y añadir a la integración continua la construcción de imágenes y una prueba de humo contra el stack desplegado.
3. **Mediano plazo:** priorizar con producto las brechas analíticas (PRD-01), extraer la lógica de los routers y definir el ciclo de vida de sedes y cuentas CTIC (AUT-01).

## 9. Guion sugerido para la demostración

1. **CTIC:** crear un coordinador y mostrar la credencial temporal de un solo uso y el cambio obligatorio.
2. **Coordinador:** cargar un Excel (doble titulación y rechazo de un archivo idéntico) y recorrer el Reporte general con filtros, Tendencias con la comparación M0→M1 y el Explorador.
3. **Publicación:** publicar una gráfica, mostrar que la instantánea se recalcula con k = 5 y verla desde el coordinador de otra sede.
4. **Usuario de consulta:** entrar y comprobar que solo ve las publicaciones de su permiso y programa, sin acceso a datos fuente.
5. **IA:** competencias demandadas, reglas de asociación, curaduría de un término y modelo de análisis de empleabilidad con su confiabilidad y el balanceo de clases.
6. **Cierre:** aislamiento por sede, anonimización y trazabilidad (auditorías, ADR, matriz).
