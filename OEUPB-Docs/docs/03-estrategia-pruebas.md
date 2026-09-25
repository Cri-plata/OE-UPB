# Estrategia de pruebas

**Estado:** implementado como baseline automatizado

## Pirámide

| Nivel | Alcance prioritario |
|---|---|
| Unitarias | reglas de momento, doble titulación, normalización, RBAC, cálculos KPI |
| Integración | routers FastAPI + base temporal, aislamiento por sede, JWT, carga Excel |
| Contrato | OpenAPI válido y consumidores compatibles |
| Frontend | servicios, interceptor, formularios, estados de error y permisos visibles |
| E2E | login → carga → reporte; login → directorio → ficha; gestión de usuarios |

## Regla para nueva lógica

1. Agregar una prueba que falle por el comportamiento esperado.
2. Implementar el mínimo cambio.
3. Ejecutar pruebas relacionadas y build.
4. Refactorizar manteniendo la suite verde.

## Casos críticos de seguridad

- Coordinador A no puede leer ni eliminar datos de sede B.
- `Usuario_Consulta` no puede cargar, borrar, publicar ni administrar usuarios.
- Token ausente, vencido o manipulado devuelve 401.
- Rol no autorizado devuelve 403.
- Usuario sin sede no cae silenciosamente en sede 1.
- Reintentos de carga no duplican información.
- CTIC puede administrar coordinadores, pero no datos ni gráficas.
- Un coordinador solo administra usuarios de consulta de su propia sede.
- Una gráfica no publicada no es visible desde otra sede.
- Una gráfica publicada expone métricas agregadas, nunca datos fuente.
- Un usuario con alcance profesor solo ve gráficas asociadas a sus programas.
- Retirar una publicación revoca la vista externa sin borrar la gráfica privada.
- Las métricas publicadas se recalculan en backend: los valores y programas enviados por el cliente se ignoran.
- Ninguna celda publicada representa menos de 5 observaciones, y las variables personales o administrativas se rechazan (RN-31).
- Eliminar una carga conserva los egresados del directorio manual.
- En el frontend zoneless, las pruebas de vista deben esperar `fixture.whenStable()` sin llamar `detectChanges()` a mano, para detectar estado que no está en signals.

## Estado actual

- Backend: 59 pruebas bajo `OEUPB-Backend/tests/` cubren autenticación, secreto productivo, expiración y reemisión auditada de credenciales, RBAC, sede, CRUD manual, exportación, NLP, cargas (concurrencia, idempotencia, precedencia manual y limpieza de huérfanos), reportes, catálogo analítico, umbral de publicación, ciclo publicar → consultar → retirar, enmascaramiento de logs, taxonomía laboral, filtros, comparación de momentos, normalización del documento, límites y rechazo de cargas, programas por clave normalizada, criterios de alertas, contrato de errores (401/403 en toda ruta protegida) y OpenAPI.
- Frontend: 31 pruebas Vitest cubren aplicación, login, interceptor, guards, visibilidad por rol, carga, directorio, cliente de publicaciones, estado de publicación (éxito, error HTTP, error de red, duplicados y retiro) la vista de publicaciones (datos, vacío, error y reintento), filtros analíticos, Reporte General con filtros, comparación de Tendencias, varias gráficas en el Explorador, el rechazo de cargas con detalle por fila y los programas sin datos actuales en la administración de cuentas.
- Contrato: el OpenAPI guardado se compara con FastAPI y los tipos TypeScript generados se verifican con `tools/validate_contracts.py`.
- CI: `.github/workflows/quality.yml` ejecuta pruebas, build y validadores de contratos, documentación y arquitectura frontend.
