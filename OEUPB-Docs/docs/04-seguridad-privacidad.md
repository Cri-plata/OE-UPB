# Seguridad y privacidad

## Datos protegidos

OE UPB trata documentos de identidad, información académica, situación laboral, salarios y respuestas abiertas. Deben considerarse datos personales y, según el contenido, potencialmente sensibles.

## Controles obligatorios

- Autorización por rol y sede en backend.
- Contraseñas almacenadas únicamente mediante hash bcrypt y cambio bloqueante en el primer ingreso.
- JWT con secreto robusto, expiración y validación de algoritmo.
- HTTPS en entornos compartidos o productivos.
- Archivos de carga limitados por tipo, tamaño y estructura.
- Consultas parametrizadas mediante ORM o parámetros SQL.
- Anonimización antes de cualquier servicio externo de IA y también en el análisis local de texto libre (habilidades, emergentes, reglas, exportación y curaduría). Se reemplazan correos, números de 8 o más caracteres, y documento, nombre y apellido del egresado (RN-04, RN-32).
- Logs sin tokens, documentos, correos ni respuestas completas. El middleware HTTP registra `/api/directorio/perfil/{documento}` y `/api/directorio/egresados/{documento}` con el documento enmascarado, y la imagen Docker desactiva el access log de Uvicorn.
- Backups cifrados y acceso por mínimo privilegio.

## Aislamiento por sede

El `sede_id` se obtiene del JWT validado. Nunca debe aceptarse un `sede_id` del cliente para ampliar alcance. Todas las consultas a datos fuente —incluidos conteos, historiales, perfiles y subconsultas— deben filtrar por la sede autorizada.

Un cambio de estado, rol, permisos o programas tiene efecto inmediato. Los endpoints protegidos deben contrastar la identidad del token con el estado y la versión de autorización vigentes; no basta con confiar en atributos incluidos en un JWT emitido antes del cambio.

## Credencial inicial y recuperación

El alta solicita la cédula y, en desarrollo, puede usarla como credencial temporal inicial. Solo se almacena el hash; no se conserva otra copia de la cédula para autenticación. La credencial vence en 24 horas por defecto y el primer ingreso obliga a establecer una contraseña personal.

En producción, `INITIAL_CREDENTIAL_MODE=random` es obligatorio: el backend no inicia si se intenta usar la cédula. La recuperación administrativa genera una credencial aleatoria de una hora, revoca la anterior y cualquier sesión vigente, y conserva un evento auditado con motivo. La entrega sigue requiriendo un canal externo seguro hasta disponer de invitaciones institucionales.

Fuera de desarrollo el backend tampoco inicia sin un `SECRET_KEY` no trivial de al menos 32 caracteres.

## Inteligencia artificial

- El módulo de IA es exclusivo de `Coordinador_Sede` y solo procesa datos de la sede del JWT. Ningún endpoint de IA devuelve métricas de otras sedes (ADR-020).
- El modelo de análisis de empleabilidad no usa documento, nombres ni correo como variables, y solo publica agregados por programa (ADR-019).
- La taxonomía curada es institucional y contiene términos, no datos fuente. Como los términos emergentes salen de respuestas individuales, la anonimización previa es obligatoria.
- El detalle de cada modelo y sus límites está en [`architecture/06-modelos-analiticos.md`](../architecture/06-modelos-analiticos.md).

## Despliegue

- El proxy termina TLS con HSTS y reenvía `X-Forwarded-*`. Uvicorn solo confía en ellos porque el backend no publica puertos fuera de la red interna de Compose.
- El proxy limita los cuerpos a 26 MB y el backend valida tipo, tamaño (25 MB) y filas (50.000) de cada carga.

## Gráficas compartidas entre sedes

- Solo el coordinador propietario puede publicar una gráfica. Puede retirarla el propietario o, si este está inactivo o fue reasignado, otro coordinador de la sede.
- El backend recalcula la publicación con datos de la sede del JWT; el cliente no aporta métricas ni programas.
- Ninguna celda publicada representa menos de 5 observaciones (ADR-015), y solo se publican variables del catálogo analítico RN-31.
- El título es el único texto libre del cliente: se rechaza si contiene correos, enlaces o secuencias de 5 o más dígitos (ADR-020).
- Riesgo residual aceptado: publicar la misma métrica con filtros solapados permite deducir por diferencia una celda suprimida (ADR-020).
- No se comparten filas, documentos, nombres, correos, respuestas individuales, archivos de carga, directorios ni perfiles.
- La audiencia se determina en backend con los permisos y programas asignados a la cuenta; el coordinador no selecciona destinatarios manualmente.
- Un permiso para ver gráficas compartidas nunca concede acceso a endpoints de datos fuente de otra sede.
- Debe registrarse quién publicó o retiró la gráfica y cuándo lo hizo.

Estas reglas están implementadas en `application/indicadores.py`, `PublicacionGrafica` y `/api/publicaciones`: el payload solo admite la definición, exige confirmación explícita y el catálogo aplica permiso de módulo y coincidencia de programas en backend. Hay pruebas para el recálculo, la supresión, las variables prohibidas y el retiro.

## Respuesta ante contradicciones

Si una regla documental permite algo que el código niega, o viceversa, no se amplían permisos por conveniencia. Se crea una decisión de producto/RBAC, una prueba de seguridad y luego se cambia implementación y documentación juntas.
