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
5. Si el cambio agrega un campo a una respuesta, probarlo sobre el endpoint HTTP y no solo sobre el servicio: el `response_model` de FastAPI descarta los campos no declarados (caso `estrategia_balanceo`, 2026-10-06).

## Versión de Python

La CI y la imagen Docker usan Python 3.13. En Python 3.14 las anotaciones se evalúan de forma diferida, así que un nombre sin importar en una anotación no falla localmente pero detiene el backend en producción (auditoría 08). Las pruebas del backend se ejecutan con el entorno `OEUPB-Backend/.venv` creado con `py -3.13 -m venv .venv`:

```powershell
cd OEUPB-Backend
.\.venv\Scripts\Activate.ps1
python -m unittest discover -s tests
```

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
- La IA solo es accesible para coordinadores y solo con datos de su sede; `Admin_CTIC` y `Usuario_Consulta` reciben 403.
- El texto libre se anonimiza antes del análisis de habilidades: correos, números largos, nombre y documento no aparecen en los resultados.
- Una curaduría solo la modifica (409 para otros) o revierte (403) su autor, y revertirla la retira de la taxonomía en todos los workers.
- El título de una publicación con correo, enlace o documento se rechaza (422).
- En el frontend zoneless, las pruebas de vista deben esperar `fixture.whenStable()` sin llamar `detectChanges()` a mano, para detectar estado que no está en signals.

## Estado actual

- Backend: 87 pruebas bajo `OEUPB-Backend/tests/` cubren el alcance y la anonimización de la IA, la curaduría entre workers, la exportación de habilidades, el modelo de análisis de empleabilidad (entrenamiento, robustez, datos insuficientes, balanceo y respuesta del endpoint), la validación del título de publicaciones, autenticación, secreto productivo, expiración y reemisión auditada de credenciales, RBAC, sede, CRUD manual, exportación, NLP, cargas (concurrencia, idempotencia, precedencia manual y limpieza de huérfanos), reportes, catálogo analítico, umbral de publicación, ciclo publicar → consultar → retirar, catálogo del coordinador (propias aparte y las de los demás coordinadores), preguntas largas del cuestionario y su orden natural, ID del estudiante (carga, búsqueda y perfil), filas sin documento con pandas 3, enmascaramiento de logs, taxonomía laboral, filtros, comparación de momentos, normalización del documento, límites y rechazo de cargas, programas por clave normalizada, criterios de alertas, contrato de errores (401/403 en toda ruta protegida) y OpenAPI.
- Frontend: 107 pruebas Vitest cubren la redirección del usuario de consulta, la sede en Mi Perfil, las cohortes y los errores de curaduría en Co-relaciones, la ruta exacta del cliente de usuarios, aplicación, login, interceptor, guards, visibilidad por rol, carga, directorio, cliente de publicaciones, estado de publicación (éxito, error HTTP, error de red, duplicados y retiro) la vista de publicaciones (datos, vacío, error y reintento; secciones del coordinador y retiro de las propias), la búsqueda del directorio y el ID en la ficha del egresado, filtros analíticos, Reporte General con filtros, comparación de Tendencias, varias gráficas en el Explorador, el rechazo de cargas con detalle por fila y los programas sin datos actuales en la administración de cuentas.
- Aislamiento: las pruebas de `OEUPB-Backend/tests/` usan SQLite en memoria con `app.dependency_overrides[get_db]`; nunca deben abrir `SessionLocal` ni ejecutar `create_all` sobre la base configurada en `.env`.
- Contrato: el OpenAPI guardado se compara con FastAPI, y los tipos TypeScript generados se verifican con `tools/validate_contracts.py`. Ese validador también exige que cada ruta que construyen los clientes de `data/api` exista tal cual en el contrato, incluida la barra final.
- Diagnósticos manuales: `OEUPB-Backend/scripts/dev/diagnostico_ia/` imprime el resultado del pipeline NLP sobre textos de ejemplo. No son pruebas y no se ejecutan en la suite.
- Despliegue: la auditoría 08 recorrió el stack Docker de producción con 54 comprobaciones funcionales y datos sintéticos.
- CI: `.github/workflows/quality.yml` ejecuta pruebas, build y validadores de contratos, documentación y arquitectura frontend.
