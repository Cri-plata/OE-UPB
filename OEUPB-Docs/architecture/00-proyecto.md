# Visión General del Proyecto: OE UPB (Observatorio de Egresados UPB)

## Índice de Documentación del Proyecto
Este archivo es la puerta de entrada a la arquitectura. Aquí tienes el mapa de todos los documentos técnicos del proyecto:

| Archivo | Ubicación | Descripción |
| :--- | :--- | :--- |
| **`00-proyecto.md`** | `/architecture` | Este documento master (Visión, alcance, usuarios, pilares). |
| **`02-arquitectura-tecnica.md`** | `/architecture` | Decisiones técnicas consolidadas (Stack Angular + Python + MySQL). |
| **`03-apicontract.md`** | `/architecture` | Contratos de la API REST (Endpoints de Login, Carga y Dashboards). |
| **`04-modelo-datos.md`** | `/architecture` | Diagrama Entidad-Relación, tablas y lógica de almacenamiento JSON. |
| **`01-requerimientos.md`** | `/requirements` | Requerimientos funcionales y no funcionales originales. |
| **`02-historias-usuario.md`** | `/requirements` | Historias de usuario ágiles separadas por épica. |
| **`03-reglas-negocio.md`** | `/requirements` | Reglas estrictas de validación y privacidad (Silos de datos). |
| **`04-hallazgos-figma.md`** | `/requirements` | Análisis de la Interfaz de Usuario (UI) y pantallas de Figma. |
| **`BACKLOG.md`** | `/ (Raíz)` | Backlog Kanban para la gestión ágil de las tareas de desarrollo. |

---

## 1. ¿Qué es OE UPB?
Es una plataforma web analítica orientada al seguimiento de egresados. Su objetivo en esta fase de Proyecto Integrador 3 (PI3) es centralizar, normalizar y visualizar la información histórica y actual proveniente de encuestas institucionales (Momentos 0, 1 y 5), permitiendo pasar de un modelo de gestión manual (hojas de cálculo esparcidas) a uno automatizado, centralizado y predictivo.

## 2. Alcance Funcional para PI3 (MVP)
Para cumplir con los objetivos del séptimo semestre, el sistema garantiza la entrega de las siguientes funcionalidades clave:

| Módulo Principal | Descripción Funcional | Tecnología Base |
| :--- | :--- | :--- |
| **Carga y Limpieza** | Procesamiento masivo de archivos Excel provenientes del Observatorio Laboral para unificarlos. | Python (Pandas) |
| **Dashboard Interactivo** | Panel visual para la toma de decisiones con filtros dinámicos y métricas de empleabilidad. | Angular 17+ |
| **Modelo Predictivo (IA)** | Integración de IA para predecir empleabilidad y clasificar respuestas de texto libre de egresados. | Scikit-Learn / OpenAI |
| **Repositorio Central** | Almacenamiento seguro, estandarizado y centralizado de la "Única Fuente de Verdad". | MySQL Relacional |

## 3. Matriz de Usuarios y Privacidad Multi-Sede
El sistema opera bajo una arquitectura de **Silos de Datos Estrictos por Sede**. Ningún usuario puede vulnerar la privacidad de los egresados de otras sedes. 

| Rol del Sistema | Nivel de Acceso | Responsabilidad Principal | Regla de Aislamiento de Datos |
| :--- | :--- | :--- | :--- |
| **Administrador CTIC** | Gestión de Accesos | Creación, edición y bloqueo de cuentas institucionales. Soporte técnico. | **Sin acceso a datos.** No consumen ni visualizan dashboards de egresados. |
| **Coordinador de Sede** | Control Total (Local) | Carga de archivos Excel, edición manual de egresados, visualización del Dashboard. | **Silo local.** Solo ve la información de su sede (Ej. Solo Bucaramanga). |
| **Directivo / Decano** | Solo Lectura | Revisión de métricas, gráficas y toma de decisiones basadas en tendencias. | **Silo local.** Solo ve el dashboard filtrado de su respectiva sede asignada. |

> *Nota: El acceso de usuarios finales (los propios egresados para auto-actualizar sus datos) queda documentado como una escalabilidad futura recomendada para el Proyecto de Grado.*

## 4. Pilares del Proyecto
Más allá del código, la concepción del **OE UPB** se sostiene sobre pilares que garantizan su viabilidad y el valor aportado a la Universidad Pontificia Bolivariana:

| Pilar | Tipo | Beneficio / Justificación Institucional |
| :--- | :--- | :--- |
| **Centralización y Calidad** | Estratégico | Elimina el riesgo de datos duplicados y desactualizados al unificar múltiples archivos Excel en una base robusta. |
| **Análisis de Decisiones** | Estratégico | Transforma números estáticos en tableros gráficos interactivos para identificar falencias curriculares. |
| **Proactividad con IA** | Innovación | Permite a la universidad dejar de reaccionar al pasado y anticiparse al futuro laboral de sus próximas cohortes. |
| **Habeas Data (Silos)** | Seguridad | Garantiza el cumplimiento estricto de la ley de protección de datos al aislar la información por sedes universitarias. |
| **Desacoplamiento API** | Arquitectura | Al separar Frontend (Angular) del Backend (Python), el proyecto puede evolucionar a una app móvil sin reescribir la lógica. |
