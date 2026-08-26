# Plan de Desarrollo Backend (Python)

## 1. Fase Inicial: Setup y Conexión
* **Entorno:** Configurar un entorno virtual en Python (env) y definir las dependencias en 
equirements.txt (FastAPI/Flask, Pandas, SQLAlchemy, PyJWT, scikit-learn).
* **Base de Datos:** Crear los modelos ORM (Object-Relational Mapping) usando SQLAlchemy para mapear las tablas usuarios, egresados y encuestas.
* **Migraciones:** Configurar Alembic o equivalente para gestionar los cambios en la base de datos MySQL.

## 2. Fase de Autenticación y Seguridad
* **Login:** Crear el endpoint /api/auth/login.
* **JWT:** Implementar la lógica para generar tokens JWT que incluyan el rol y el sede_id del usuario.
* **Middleware:** Crear un decorador o middleware que intercepte todas las peticiones a la API para verificar la validez del token y extraer la sede para aislar los datos.

## 3. Fase Core: Procesamiento de Excel (Pandas)
* **Endpoint de Carga:** Crear /api/datos/upload que reciba el archivo binario .xlsx.
* **ETL (Extract, Transform, Load):**
  1. Usar pandas.read_excel para parsear la data.
  2. Limpiar nombres de columnas, espacios y valores nulos.
  3. Ejecutar la lógica de **Upsert**: Si la cédula existe, actualizar; si no, insertar.
  4. Agrupar las respuestas dinámicas de la encuesta y guardarlas en el campo JSON.
* **Manejo de Errores:** Devolver un reporte estructurado si hay cédulas vacías o formatos inválidos.

## 4. Fase Analítica (Endpoints para el Dashboard)
* Crear endpoints de solo lectura (GET) protegidos por sede_id:
  * /api/dashboard/kpis (Totales, empleabilidad general).
  * /api/dashboard/tendencias (Cruce M1 vs M5).
* Los filtros (facultad, programa) se recibirán como Query Parameters.

## 5. Fase IA y Predicción
* **Modelo Scikit-Learn:** Entrenar un modelo de clasificación simple para riesgo de desempleo usando datos históricos anonimizados.
* **Endpoint Predictivo:** Exponer una ruta que evalúe a una cohorte pasándole sus variables de entrada al modelo pre-entrenado.
