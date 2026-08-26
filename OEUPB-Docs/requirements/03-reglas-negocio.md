# Reglas de Negocio (OE UPB)

Las reglas de negocio dictan las lógicas restrictivas que el Backend (Python) debe validar estrictamente antes de guardar cualquier dato.

1. **RN-01 Unicidad del Egresado:** El `documento_identidad` (Cédula) es el identificador único universal. El sistema **jamás** debe permitir la creación de dos egresados con el mismo documento. Si en un Excel viene un documento que ya existe, se deben actualizar sus datos, no duplicarlos.
2. **RN-02 Integridad de Momentos:** El sistema solo aceptará encuestas catalogadas estrictamente bajo los Momentos definidos por la universidad: `Momento 0` (Grado), `Momento 1` (Al año), y `Momento 5` (A los cinco años). Cualquier otro valor será rechazado.
3. **RN-03 Permisos de Solo Lectura:** Los usuarios con rol "Personal Directivo" tienen prohibido el acceso a los endpoints (API) de carga de archivos Excel o eliminación de registros (CRUD).
4. **RN-04 Anonimización (Privacidad):** Antes de enviar cualquier paquete de texto a la API de Inteligencia Artificial externa (Ej. OpenAI), el backend debe limpiar la cadena de texto asegurándose de que no viajen números de cédula, nombres propios ni correos electrónicos, cumpliendo la ley de protección de datos (Habeas Data).
5. **RN-05 Formato de Carga:** El único formato permitido para la subida masiva de datos en el Módulo de Administración es `.xlsx`. Documentos `.csv` o `.pdf` deben arrojar un error de validación en el frontend (Angular) antes de enviarse al servidor.
6. **RN-06 Aislamiento de Datos por Sede (Silos):** Toda consulta a la base de datos que involucre egresados o encuestas DEBE filtrar obligatoriamente por el `sede_id` del usuario autenticado. Ningún usuario, sin importar su rol, puede consultar información de una sede ajena.
7. **RN-07 Separación de Privilegios:** Solo los usuarios con el rol `Admin_CTIC` pueden crear o modificar cuentas en la tabla de usuarios. Un `Coordinador_Sede` o `Directivo` no tiene autorización para acceder al módulo de gestión de cuentas.
