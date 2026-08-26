# Historial de Cambios (Changelog)

Este documento rastrea todas las modificaciones arquitectónicas, creaciones de archivos y refactorizaciones realizadas en el proyecto OE UPB.

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
