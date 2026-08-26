# Plan de Despliegue y Seguridad (Cloud UPB)

## 1. Entorno de Servidores
Dado que el proyecto exige confidencialidad (Habeas Data), no se utilizarán nubes públicas genéricas para la base de datos principal, sino los servidores institucionales de la universidad.

## 2. Configuración de Base de Datos (MySQL)
* Instalar y configurar MySQL Server en una máquina virtual de la UPB.
* Crear roles y usuarios de base de datos restringidos exclusivamente a la aplicación de Python (Principio de Menor Privilegio).

## 3. Despliegue del Backend (Python)
* Contenerizar la aplicación usando Docker y Dockerfile.
* Servir la API mediante un servidor de grado de producción como Gunicorn o Uvicorn en combinación con Nginx como proxy inverso.
* Habilitar HTTPS / SSL para cifrar la comunicación entre cliente y servidor.

## 4. Despliegue del Frontend (Angular)
* Ejecutar el build de producción 
g build --configuration production para minimizar, ofuscar y optimizar los archivos estáticos (JS, CSS, HTML).
* Servir los archivos estáticos desde un servidor web ligero (ej. Nginx o un bucket interno si la infraestructura lo permite).

## 5. Pruebas de Carga y Seguridad
* **CORS:** Restringir los orígenes permitidos en Python para que solo acepte peticiones HTTP desde el dominio oficial del Frontend.
* **Validación de Token:** Probar exhaustivamente que la manipulación manual de tokens JWT (ataque de escalada de privilegios) sea rechazada por el middleware de Python.
