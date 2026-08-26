# Backlog de Desarrollo Kanban (OE UPB - PI3)

Este documento es nuestra "Hoja de Ruta" técnica. Aquí dividiremos las Historias de Usuario en tareas de programación específicas para que el equipo de desarrollo sepa exactamente qué hacer.

---

## 📌 TODO (Por Hacer)

### Diseño y Prototipado
- [ ] **Diseño UI:** Crear el mockup faltante para el formulario de "Nuevo Usuario" (Admin CTIC).

### Backend (Python & MySQL)
- [ ] **DB-01:** Crear el script de migración SQL para las tablas `usuarios`, `egresados` y `encuestas` (Modelo Relacional y JSON).
- [ ] **API-01 (Auth):** Programar el endpoint de Login (`POST /api/auth/login`) y la generación del Token JWT con el `sede_id`.
- [ ] **API-02 (Usuarios):** Programar el CRUD de usuarios para el Admin CTIC.
- [ ] **API-03 (Carga):** Programar la lógica con `Pandas` para recibir el Excel, limpiar columnas, validar cédulas duplicadas y guardar en base de datos.
- [ ] **API-04 (IA Base):** Crear un endpoint básico que simule la predicción de empleabilidad.

### Frontend (Angular)
- [ ] **UI-00 (Setup):** Generar los contratos de TypeScript en la carpeta `APIcontractfront`.
- [ ] **UI-01 (Auth):** Maquetar y conectar la pantalla de Login a la API de Python.
- [ ] **UI-02 (Admin):** Maquetar la pantalla de Gestión de Usuarios y el modal de "Nuevo Usuario".
- [ ] **UI-03 (Data):** Conectar la funcionalidad "Drag & Drop" de Excel con la API de Carga y diseñar el manejo del Modal de Errores.
- [ ] **UI-04 (Dashboard):** Implementar la vista del Reporte General y conectar los filtros desplegables.

---

## 🚧 IN PROGRESS (En Progreso)
- [ ] **DOC-01:** Redacción de contratos de comunicación (API Contracts) entre Frontend y Backend.

---

## ✅ DONE (Terminado)
- [x] **REQ-01:** Documentación Arquitectónica (Proyecto, Stack, Bases de Datos).
- [x] **REQ-02:** Análisis de Actas y traducción a 73 Requerimientos Formales.
- [x] **REQ-03:** Redacción de Historias de Usuario robustas (Gherkin).
- [x] **UX-01:** Validación de Mockups (Figma) en Modo Claro.
