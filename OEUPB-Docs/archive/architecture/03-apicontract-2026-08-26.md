# Contratos de API (API Contracts)

> **Estado: Archivado.** Sus rutas no coincidían con el backend implementado. Reemplazado el 2026-09-22 por `architecture/03-contratos.md` y `specs/api/openapi.json`.

## ¿Qué es este documento?
Este archivo define el "contrato de comunicación" entre el Frontend (Angular) y el Backend (Python). Establece exactamente cómo Angular debe pedir la información y cómo Python promete responder. Esto permite que el equipo de frontend y el de backend trabajen en paralelo sin equivocarse.

**Convenciones Generales:**
* Todas las rutas inician con `/api/v1/`.
* Todas las respuestas viajan en formato `JSON`.
* Los endpoints protegidos requieren enviar un token en las cabeceras: `Authorization: Bearer <token>`.

---

## 1. Módulo de Autenticación (Login)
*Permite al Coordinador ingresar al sistema.*

* **Ruta:** `/api/v1/auth/login`
* **Método:** `POST`
* **Cuerpo de la Petición (Request - Lo que envía Angular):**
  ```json
  {
    "email": "coordinador@universidad.edu.co",
    "password": "mypassword123"
  }
  ```
* **Respuesta Exitosa (Response - Lo que devuelve Python - 200 OK):**
  ```json
  {
    "token": "eyJhbGciOiJIUzI1NiIsIn...",
    "rol": "Coordinador",
    "nombre": "Diego Barrera"
  }
  ```

---

## 2. Módulo de Carga de Datos (Excel OLE)
*Permite subir los archivos de encuestas al servidor.*

* **Ruta:** `/api/v1/data/upload`
* **Método:** `POST`
* **Cabeceras:** `Content-Type: multipart/form-data` (Requerido para enviar archivos físicos).
* **Cuerpo de la Petición (Form Data):**
  * `file`: (El archivo .xlsx seleccionado)
  * `momento`: `0` (Momento de grado)
* **Respuesta Exitosa (Response - 200 OK):**
  ```json
  {
    "status": "success",
    "message": "Archivo procesado correctamente",
    "registros_nuevos": 120,
    "duplicados_omitidos": 5
  }
  ```

---

## 3. Módulo de Inteligencia de Negocios (Dashboard)
*Permite a Angular obtener la información resumida para dibujar las gráficas.*

* **Ruta:** `/api/v1/dashboard/stats`
* **Método:** `GET`
* **Parámetros de Búsqueda (Filtros en la URL):**
  `?programa=Sistemas&cohorte=2023&sede=Principal` (Angular envía los filtros que seleccione el usuario).
* **Respuesta Exitosa (Response - 200 OK):**
  ```json
  {
    "total_egresados": 450,
    "situacion_laboral": [
      {"estado": "Empleado", "cantidad": 300},
      {"estado": "Desempleado", "cantidad": 50},
      {"estado": "Independiente", "cantidad": 100}
    ],
    "salario_promedio": 2500000
  }
  ```
