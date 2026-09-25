# Arquitectura Técnica del Sistema: OE UPB

> **Estado: Archivado.** Reemplazado el 2026-09-22 por `architecture/01-frontend.md`, `architecture/02-backend.md` y los ADR vigentes.

## 1. Modelo Arquitectónico
El proyecto **OE UPB (Observatorio de Egresados UPB)** utiliza una arquitectura **Cliente-Servidor (N-Capas)** totalmente conectada. La información reside de manera centralizada en los servidores de la universidad, garantizando que todos los roles (Coordinador y Directivos) accedan a los datos reales en todo momento.

Las responsabilidades se dividen en tres capas principales:
1. **Capa de Presentación (Frontend):** Interfaz gráfica interactiva y validaciones básicas.
2. **Capa de Lógica de Negocio (Backend):** Procesamiento de datos, limpieza de Excel, seguridad e integración con IA.
3. **Capa de Datos (Base de Datos):** Almacenamiento persistente, estructurado y relacional.

## 2. Stack Tecnológico (PI3)

| Capa | Tecnología | Justificación |
|---|---|---|
| **Frontend** | **Angular** | Framework robusto basado en componentes, ideal para construir Dashboards interactivos e interfaces ricas. |
| **Backend** | **Python (FastAPI / Flask)** | Python es el estándar de la industria para manipulación de datos. Usando librerías como `Pandas` se facilita enormemente la lectura y limpieza de los Excel del OLE. |
| **Base de Datos** | **MySQL** | Motor relacional maduro que garantiza la integridad de los datos de egresados, soportando consultas complejas para las analíticas. |
| **Inteligencia Artificial** | **Híbrida (Scikit-Learn + API Externa)** | Se usará `Scikit-learn` en Python para la predicción estadística de empleabilidad, y una API Externa (ej. OpenAI) de forma desacoplada para el análisis de texto abierto. |

## 3. Flujo Principal de Trabajo (Carga de Datos)
El flujo crítico del sistema se ejecuta de la siguiente manera:

1. **Selección:** El *Coordinador de Egresados* accede a la aplicación (Angular) y selecciona el archivo Excel (Momento 0, 1 o 5).
2. **Transferencia:** Angular envía el archivo mediante una petición HTTP (POST) hacia el servidor Backend.
3. **Procesamiento:** Python recibe el archivo temporal. Utilizando `Pandas`, extrae las filas, limpia datos vacíos o inconsistentes, y detecta posibles duplicados mediante el documento de identidad.
4. **Almacenamiento:** Una vez normalizados los datos, Python ejecuta las consultas SQL para insertar/actualizar la información en **MySQL**.
5. **Confirmación:** El servidor responde al Frontend con el resultado de la carga, y Angular notifica al Coordinador.

## 4. Decisiones Arquitectónicas Relevantes
* **Desacoplamiento Frontend/Backend:** Permite que en el futuro (Proyecto de Grado) se pueda conectar una Aplicación Móvil nativa utilizando la misma API de Python, sin tener que reescribir la lógica de negocio.
* **Por qué NO "Local-First":** Al estar los datos alojados en la nube institucional, la arquitectura conectada (Online) garantiza que no haya conflictos de datos y asegura que los Decanos y el Rector vean siempre estadísticas actualizadas al segundo.
