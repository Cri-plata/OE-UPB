# Formulario de decisiones para cerrar la auditoría

**Objetivo:** resolver únicamente las decisiones de producto o datos que no deben inferirse desde el código.  
**Cómo responder:** escribe la letra elegida en cada línea `Respuesta`. Puedes devolver solo una secuencia como `1A, 2B, 3A...` y añadir observaciones cuando sea necesario.

## 1. Unidad de carga e historial

¿Qué debe representar una fila del historial?

- **A — Un archivo individual (recomendada):** cada subida tiene ID, fecha, actor, sede, estado y registros; se puede eliminar o revertir por ID.
- **B — Un lote sede/momento/año:** varias subidas se consolidan y se eliminan juntas.
- **C — Ambas:** se auditan archivos individuales, pero también existe una operación masiva explícita.

**Respuesta:** A — una fila representa un archivo individual.

## 2. Recarga del mismo momento y año

Si ya existen datos para la misma sede, momento y año, ¿qué debe ocurrir?

- **A — Reemplazo transaccional (recomendada):** la carga nueva sustituye la anterior solo si termina completa y correctamente.
- **B — Rechazo:** debe eliminarse manualmente la carga anterior antes de subir otra.
- **C — Versionado:** se conservan ambas versiones y una se marca como vigente.

**Respuesta:** A — reemplazo transaccional.

## 3. Credencial inicial de una cuenta

¿Cómo obtiene su contraseña un coordinador o usuario de consulta nuevo?

- **A — Invitación para definir contraseña (recomendada):** enlace de un solo uso y expiración.
- **B — Contraseña temporal aleatoria:** se entrega por canal institucional y obliga a cambiarla.
- **C — Contraseña ingresada por quien crea la cuenta:** el administrador/coordinador la define en el formulario.

**Respuesta sustituida por la decisión 16:** se mantiene el cambio bloqueante del primer ingreso, pero la credencial temporal objetivo deja de ser aleatoria y pasa a ser la cédula suministrada durante el alta. Solo se almacena su hash. La implementación se difiere hasta completar permisos y el flujo funcional principal.

### 3A. Servicio de envío disponible

- **A — Microsoft 365/Graph (recomendada si UPB usa Microsoft 365):** autenticación de aplicación y envío desde una cuenta institucional autorizada.
- **B — SMTP institucional:** host, puerto y credenciales de una cuenta de servicio proporcionados por UPB.
- **C — Aún no hay servicio:** implementar tokens y activación, pero mantener el envío deshabilitado hasta recibir infraestructura.

**Respuesta:** C — no hay permisos de correo por ahora; el flujo no depende de Outlook ni SMTP.

## 4. Datos personales de un egresado presente en varias sedes

¿Quién puede modificar el registro global del egresado?

- **A — Custodio institucional (recomendada):** una función central corrige identidad; las sedes solo administran sus mediciones.
- **B — Cualquier sede vinculada:** la última edición válida actualiza el registro global.
- **C — Datos separados por sede:** cada sede mantiene su propia versión del egresado.

**Respuesta confirmada:** A, con ajuste: existe custodia institucional para resolver conflictos globales, pero el coordinador puede registrar encuestas manuales y corregir datos de egresados visibles de su sede. Toda modificación manual debe quedar auditada y protegida frente a sobrescritura automática.

## 5. Significado del año

¿Cómo se deben modelar los años usados por carga y filtros?

- **A — Dos campos (recomendada):** `anio_encuesta` en la medición y `anio_grado` derivado de `fecha_grado` para cohorte.
- **B — Solo año de encuesta:** “cohorte” se interpreta también como año de encuesta.
- **C — Solo año de grado:** el año de la carga siempre representa la cohorte.

**Respuesta:** C — el año capturado representa el año de grado/cohorte.

## 6. Precedencia de datos

Si una carga posterior contradice una corrección manual, ¿qué prevalece?

- **A — Corrección manual protegida (recomendada):** la carga reporta el conflicto y no la sobrescribe sin confirmación.
- **B — Última escritura:** la carga más reciente sobrescribe siempre.
- **C — Fuente prioritaria por campo:** se define una matriz de precedencia para identidad, programa, grado y respuestas.

**Respuesta:** A — la corrección manual queda protegida.

## 7. Mediciones anónimas

¿Dónde deben participar?

- **A — Solo agregados (recomendada):** cuentan en KPIs si cumplen calidad, pero nunca en directorio, perfil ni comparación individual M0/M1/M5.
- **B — Excluirlas de toda analítica:** se almacenan solo para auditoría.
- **C — Incluirlas en agregados y tendencias:** sin intentar enlazarlas longitudinalmente.

**Respuesta:** A — participan únicamente en agregados y nunca en perfiles o cruces longitudinales.

## 8. Taxonomía laboral

¿Cuál será el catálogo base?

- **A — Exclusivo y detallado (recomendada):** empleado formal, empleado informal, independiente/emprendedor, estudiante, desempleado e inactivo; una persona ocupa una categoría principal.
- **B — Simplificado:** empleado, independiente, estudiante y sin empleo.
- **C — Multiselección:** una persona puede estar simultáneamente empleada, emprendiendo y estudiando.

**Respuesta:** B — empleado, independiente, estudiante y sin empleo. La formalidad se conserva como atributo separado cuando aplique.

## 9. Objetivo del modelo predictivo

¿Qué debe predecir RF-71/HU-10?

- **A — Probabilidad de empleo formal a cinco años (recomendada):** conserva el objetivo explícito de RF-71.
- **B — Riesgo de desempleo a cinco años:** se reescribe RF-71 para alinearlo con HU-10.
- **C — Ambos modelos:** salidas separadas, sin tratarlas como complementarias.

**Respuesta confirmada:** En pausa. La capacidad usará un modelo de IA, pero no se implementará ni cerrará el objetivo predictivo hasta definir métricas, alcance y criterios de aceptación.

## 10. Comportamiento de una gráfica publicada

¿Debe cambiar cuando llegan nuevas cargas?

- **A — Instantánea versionada (recomendada):** conserva exactamente las métricas revisadas al publicar; una actualización crea versión nueva.
- **B — Vista en vivo:** se recalcula automáticamente con los datos vigentes.
- **C — Configurable por publicación:** el coordinador elige instantánea o en vivo.

**Respuesta:** A — instantánea versionada.

## 11. Umbral de privacidad para agregados

¿Qué ocurre si un filtro representa muy pocas personas?

- **A — Suprimir grupos menores de 5 (recomendada):** no se publica la cifra ni se permite inferirla por totales.
- **B — Suprimir grupos menores de 10:** protección más conservadora.
- **C — Sin umbral fijo:** cada publicación requiere aprobación manual.

**Respuesta:** C — sin umbral fijo; cada publicación requiere aprobación manual de privacidad.

## 12. Alcance de esta remediación

¿Hasta dónde deseas llegar en la siguiente fase?

- **A — Seguridad y carga primero (recomendada):** migraciones, RBAC, entidad de carga, contratos y pruebas; analítica/IA después.
- **B — Toda la auditoría:** incluir CRUD, publicación, analítica, exportaciones e IA en una intervención amplia.
- **C — Solo documentación:** cerrar decisiones y planes sin implementar nuevas capacidades.

**Respuesta confirmada:** A, con orden interno: completar primero RBAC, permisos por usuario y el flujo funcional. Después se atienden publicación y demás capacidades operativas. El endurecimiento del inicio de sesión y del mecanismo de entrega/cambio de contraseña queda para la última fase, sin eliminar el cambio obligatorio ya existente.

---

## Decisiones pendientes de la auditoría actualizada

Las preguntas 1 a 12 ya están resueltas y no deben contestarse de nuevo. Para continuar, responde con una secuencia como `13A, 14A, 15A...`; puedes añadir una observación después de cualquier respuesta.

## 13. Eliminación de cuentas

¿Qué debe significar la acción “eliminar” para una cuenta?

- **A — Desactivación reversible (recomendada):** impide iniciar sesión, conserva relaciones y auditoría, y permite reactivación controlada.
- **B — Borrado físico:** elimina la fila cuando no existan relaciones que lo impidan.
- **C — Ambos:** la operación ordinaria desactiva; un proceso excepcional y auditado permite borrado físico.

**Respuesta confirmada:** C — la operación ordinaria desactiva la cuenta y conserva su auditoría. Un proceso excepcional, restringido y auditado puede ejecutar borrado físico cuando las relaciones de integridad lo permitan.

## 14. Eliminación de una carga vigente

¿Qué debe ocurrir con la carga y sus mediciones?

- **A — Retiro lógico (recomendada):** la carga y sus mediciones dejan de participar en consultas, pero se conservan la traza y la cadena de versiones.
- **B — Borrado físico auditado:** se eliminan carga y mediciones y se conserva un evento mínimo en una tabla de auditoría separada.
- **C — Restauración automática:** se retira la carga vigente y la versión reemplazada más reciente vuelve a quedar vigente.

**Respuesta confirmada:** B — se eliminan físicamente la carga y sus mediciones dentro de una transacción, pero antes se conserva un evento mínimo e inmutable en una tabla de auditoría separada.

## 15. Archivo parcialmente válido

Si un Excel contiene filas válidas y filas con errores, ¿qué política se aplica?

- **A — Todo o nada (recomendada):** cualquier error revierte el archivo completo y se entrega el detalle para corregirlo.
- **B — Aceptación parcial:** se guardan las filas válidas y la carga queda marcada como parcial con las filas rechazadas.
- **C — Configurable:** el coordinador elige la política antes de cada carga.

**Respuesta confirmada:** A — todo o nada. Una validación obligatoria fallida revierte el archivo completo. Las mediciones anónimas y los campos opcionales vacíos expresamente permitidos no se consideran errores de fila ni convierten la operación en aceptación parcial.

## 16. Política de contraseña personal

¿Qué regla mínima debe validar el cambio de contraseña?

- **A — Frase de 12 caracteres (recomendada):** mínimo 12, permite espacios, bloquea contraseñas comprometidas y evita reglas rígidas de composición.
- **B — Complejidad clásica:** mínimo 8 con mayúscula, minúscula, número y símbolo.
- **C — Política institucional externa:** el sistema adopta literalmente una política de UPB que debe adjuntarse o referenciarse.

**Respuesta confirmada:** La cédula suministrada al crear la cuenta se usa como contraseña temporal inicial. El backend almacena únicamente su hash y no conserva una copia adicional de la cédula para autenticación. En el primer ingreso, el modal bloqueante obliga a establecer una contraseña personal. El endurecimiento posterior de este mecanismo continúa diferido.

## 17. Correo institucional permitido

¿Qué correos pueden registrarse?

- **A — Solo dominio UPB (recomendada):** se debe indicar el dominio o lista exacta de dominios institucionales aceptados.
- **B — Cualquier correo válido:** el carácter institucional se controla fuera del sistema.
- **C — Lista configurable:** una tabla/configuración mantiene dominios permitidos sin desplegar código.

**Respuesta confirmada:** A — solo se aceptan cuentas terminadas en `@upb.edu.co`, con validación en frontend y backend.

## 18. Cambio de permisos con sesión activa

¿Cuándo pierde acceso un usuario bloqueado o con permisos reducidos?

- **A — Inmediatamente (recomendada):** cada operación valida estado/permisos vigentes y los tokens se revocan o versionan.
- **B — Al vencer el JWT:** el cambio surte efecto cuando expira la sesión existente.
- **C — Cierre forzado administrativo:** el cambio revoca sesiones solo si el administrador activa expresamente esa opción.

**Respuesta confirmada:** A — el cambio tiene efecto inmediato. Cada operación protegida valida el estado y los permisos vigentes; los tokens se revocan o invalidan mediante una versión de sesión/autorización.

## 19. Usuario de consulta y gráficas privadas

¿Puede un `Usuario_Consulta` ver gráficas de su propia sede que no se han publicado?

- **A — No (recomendada):** solo ve instantáneas publicadas compatibles con sus permisos y programas.
- **B — Sí:** puede ver gráficas privadas de su sede según permisos/programas, aunque no hayan pasado aprobación de publicación.
- **C — Permiso separado:** existe un permiso explícito para resultados privados de la sede, distinto del catálogo publicado.

**Respuesta confirmada:** A — `Usuario_Consulta` solo puede ver instantáneas publicadas compatibles con sus permisos y programas. No accede a gráficas privadas, aunque pertenezcan a su sede.

## 20. Medición repetida de la misma persona

Si existen dos respuestas para igual documento, sede, momento y cohorte, ¿cuál es válida?

- **A — Una vigente y versiones históricas (recomendada):** la nueva reemplaza transaccionalmente a la vigente sin borrar el historial.
- **B — La primera:** se rechazan respuestas posteriores como duplicadas.
- **C — Múltiples válidas:** se conservan todas como intentos distintos y los indicadores definen cómo agregarlas.

**Respuesta confirmada:** C — pueden existir múltiples respuestas válidas para igual documento, sede, momento y cohorte. Cada indicador debe declarar cómo selecciona, ordena o agrega los intentos para evitar doble conteo accidental.

## 21. Tamaño mínimo para “datos suficientes”

¿Qué umbral se usa para comparaciones M1/M5 y otros indicadores?

- **A — Cinco pares válidos (recomendada inicial):** requiere al menos cinco egresados enlazados con datos en ambos momentos; es independiente de la aprobación manual de privacidad para publicar.
- **B — Diez pares válidos:** aplica un umbral estadístico más conservador.
- **C — Sin umbral fijo:** cada indicador define su mínimo en el diccionario de métricas.

**Respuesta confirmada:** C — no existe un umbral global. El diccionario de métricas define el mínimo requerido por indicador, de forma independiente a la aprobación manual de privacidad para publicar.

## 22. Filtro de sede en el dashboard

¿Cómo debe comportarse el filtro histórico de sede?

- **A — Retirarlo de datos propios (recomendada):** el dashboard privado usa la sede del JWT; otra vista separada permite explorar publicaciones agregadas.
- **B — Mantenerlo solo para publicaciones:** la sede propia queda fija y el selector filtra exclusivamente el catálogo publicado.
- **C — Unificar ambas vistas:** el filtro alterna entre datos privados propios y publicaciones, con señalización visual explícita.

**Respuesta confirmada:** A — el dashboard privado no muestra selector de sede y siempre usa la sede del JWT. Las publicaciones agregadas de otras sedes se consultan en una vista separada.

---

## Decisiones de implementación de permisos

Estas decisiones son necesarias para implementar `SHARE-01` y `SHARE-02` sin inventar el modelo RBAC.

## 23. Granularidad del catálogo de permisos

¿Qué representa un permiso asignable a `Usuario_Consulta`?

- **A — Módulos funcionales (recomendada):** permisos estables como `ver_reporte_general`, `ver_tendencias`, `ver_explorador`, `ver_publicaciones` y `exportar_resultados`.
- **B — Cada gráfica o indicador:** se asigna acceso individual a elementos como empleabilidad, salarios o satisfacción.
- **C — Híbrido:** permisos por módulo y restricciones adicionales por indicadores; ofrece más control, pero aumenta complejidad de administración y pruebas.

**Respuesta confirmada:** A, con ajuste — el catálogo inicial contiene `ver_reporte_general`, `ver_tendencias`, `ver_explorador` y `ver_publicaciones`. `exportar_resultados` no forma parte del catálogo.

## 24. Fuente de programas asignables

¿De dónde obtiene el coordinador la lista de programas para un usuario de consulta?

- **A — Catálogo interno estable (recomendada):** una tabla de programas con identificador propio, alimentada y normalizada desde los datos institucionales.
- **B — Programas observados en las cargas:** se usan directamente los nombres distintos existentes en `egresados.programa`.
- **C — Catálogo institucional externo:** se integra una fuente oficial que todavía debe identificarse.

**Respuesta confirmada:** B — los programas asignables se obtienen de los nombres distintos observados en las cargas visibles de la sede del coordinador.

## 25. Alcances rector, profesor y administrativo

¿Cómo se traducen estos perfiles al único rol técnico `Usuario_Consulta`?

- **A — Plantillas editables (recomendada):** rector inicia con acceso a todas las publicaciones; profesor con publicaciones de sus programas; administrativo con módulos/programas seleccionados. El coordinador puede reducir, pero no ampliar, el límite de cada plantilla.
- **B — Configuración totalmente manual:** los nombres son informativos y todos los permisos/programas se seleccionan uno por uno.
- **C — Plantillas rígidas:** cada perfil tiene permisos fijos que el coordinador no puede modificar.

**Respuesta confirmada:** B — rector, profesor y administrativo son etiquetas informativas. Todos los permisos y programas se seleccionan manualmente, sin privilegios implícitos por etiqueta.
