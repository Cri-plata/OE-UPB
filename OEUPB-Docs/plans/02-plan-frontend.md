# Plan de Desarrollo Frontend (Angular)

> **Estado:** histórico. Describe la planificación inicial; el estado vigente está en `../BACKLOG.md` y `../architecture/01-frontend.md`.

## 1. Fase Inicial: Arquitectura del Proyecto
* **Estructura Standalone:** Inicializar Angular 17+ usando componentes *Standalone*.
* **Routing:** Configurar pp.routes.ts con protección de rutas (Guards) para que solo usuarios logueados accedan al sistema.
* **Estilos:** Configurar variables CSS globales en styles.scss (Colores corporativos UPB: blanco, rojo, dorado).

## 2. Fase de Servicios y Estado
* **AuthService:** Manejar el guardado del token JWT en localStorage o sessionStorage.
* **DataService:** Centralizar las peticiones HTTP (GET, POST) al backend de Python mediante HttpClient.
* **Interceptors:** Crear un interceptor que inyecte automáticamente el token Bearer en los Headers de todas las peticiones salientes.

## 3. Fase de UI: Autenticación y Gestión
* **Login:** Maquetar la pantalla de inicio de sesión.
* **Gestión de Usuarios (Admin CTIC):** Crear la tabla de usuarios y el modal reactivo (ReactiveFormsModule) para agregar nuevos cuentas asignando el rol y la sede.

## 4. Fase de UI: Módulo de Carga y Limpieza
* **Drag & Drop:** Implementar un componente visual para arrastrar archivos Excel.
* **Filtros Previos:** Añadir los selectores obligatorios (Momento y Sede) antes de enviar el archivo.
* **Modal de Feedback:** Leer la respuesta HTTP del backend y mostrar el resumen de filas exitosas y errores (con opción a descargar el reporte).

## 5. Fase de UI: Dashboard Analítico
* **Librería de Gráficos:** Integrar librerías como Chart.js, Ng2-Charts o ECharts para la visualización.
* **Componentización:** Crear componentes aislados para:
  * Tarjetas de resumen (KPIs).
  * Gráficas de tendencias M1 vs M5.
  * Gráficos de Inteligencia Artificial (Word clouds, barras predictivas).
* **Filtros Dinámicos:** Conectar los menús desplegables (Programa, Cohorte) para que al cambiar, actualicen el estado de las gráficas.
