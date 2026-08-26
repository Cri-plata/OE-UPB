# Instrucciones del Sistema (AI Context)

Este archivo sirve como el "cerebro" o memoria principal para cualquier asistente de Inteligencia Artificial o desarrollador nuevo que ingrese al proyecto. 

> **INSTRUCCIÓN CRÍTICA PARA NUEVOS CHATS (IA):**
> Si acabas de iniciar una nueva sesión de chat, **DEBES** leer todos los archivos listados en la Sección 1 usando tus herramientas (ej. iew_file o cat) antes de sugerir o escribir cualquier código. El contexto de este proyecto es estricto y saltarse documentos romperá reglas de negocio críticas (como el aislamiento de sedes o la regla de doble titulación).

## 1. Orden de Lectura Estricto (Para Contextualización Total)

Para entender el proyecto OE UPB a profundidad, debes consumir la documentación en este orden exacto:

### A. Contexto Base y Reglas
1. CLAUDE.md (Este archivo - Reglas del proyecto y Arquitectura Limpia).
2. OEUPB-Docs/CHANGELOG.md (Qué se ha modificado históricamente).
3. BACKLOG.md (En qué tarea vamos actualmente).

### B. Arquitectura Core
4. OEUPB-Docs/architecture/00-proyecto.md (Visión global y roles).
5. OEUPB-Docs/architecture/04-modelo-datos.md (Estructura de la base de datos relacional).

### C. Requerimientos y Reglas de Negocio
6. OEUPB-Docs/requirements/01-requerimientos.md (Listado de los 73 RFs).
7. OEUPB-Docs/requirements/02-historias-usuario.md (Historias robustas con Criterios de Aceptación).
8. OEUPB-Docs/requirements/03-reglas-negocio.md (Reglas inflexibles, ej. Habeas Data y Doble Titulación).
9. OEUPB-Docs/requirements/04-hallazgos-figma.md (Correspondencia con la Interfaz Visual UI).

### D. Planes de Ejecución
10. OEUPB-Docs/plans/01-plan-backend.md
11. OEUPB-Docs/plans/02-plan-frontend.md
12. OEUPB-Docs/plans/03-plan-despliegue.md

## 2. Reglas de Arquitectura: Clean Architecture
El proyecto ESTRICTAMENTE utiliza **Arquitectura Limpia (Clean Architecture)**:
* **Frontend (Angular):** Separado en capas: Domain (Modelos), Data (Servicios HTTP), y Presentation (Componentes UI).
* **Backend (Python):** Separado en Domain (Modelos), Application (Casos de uso), Infrastructure (BD/Rutas) y Presentation.
* **Contratos (OEUPB-Contracts):** Actúan como los DTOs en la frontera para comunicar Back y Front.

## 3. Stack Tecnológico
* **Frontend:** Angular 17+ (Standalone Components), SCSS.
* **Backend:** Python (FastAPI/Flask), Pandas, Scikit-Learn.
* **Base de Datos:** MySQL.
