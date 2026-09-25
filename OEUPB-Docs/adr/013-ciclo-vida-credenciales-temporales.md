# ADR-013 — Ciclo de vida endurecido de credenciales temporales

**Estado:** Aceptado

**Fecha:** 2026-09-24

## Contexto

La política funcional aprobó usar el número de documento suministrado durante el alta como credencial inicial, sin conservar otra copia para autenticación. El documento es predecible y no resulta apropiado para producción. También faltaban expiración y recuperación auditada.

## Decisión

1. El alta exige `numero_documento`, lo usa como credencial inicial cuando `INITIAL_CREDENTIAL_MODE=documento` y almacena únicamente su hash bcrypt.
2. La credencial inicial vence después de `TEMPORARY_CREDENTIAL_EXPIRE_HOURS`, 24 horas por defecto.
3. Fuera de `development` y `test`, el servicio solo inicia con `INITIAL_CREDENTIAL_MODE=random`; por tanto, producción utiliza una credencial criptográficamente aleatoria mostrada una sola vez.
4. Fuera de desarrollo, `SECRET_KEY` es obligatorio, debe tener al menos 32 caracteres y no puede usar valores de ejemplo conocidos.
5. Admin CTIC puede recuperar el acceso de coordinadores y cada coordinador el de usuarios de consulta de su sede. La reemisión usa siempre una credencial aleatoria y vence después de `RECOVERY_CREDENTIAL_EXPIRE_MINUTES`, 60 minutos por defecto.
6. Reemitir reemplaza el hash anterior, marca de nuevo el cambio obligatorio, incrementa la versión de autorización y registra actor, objetivo, sede, motivo y fecha en `auditoria_cuentas`.
7. Una credencial vencida no inicia sesión. Al establecer la contraseña personal se elimina la fecha de expiración y se revoca la credencial temporal.

## Consecuencias

- La cédula no se persiste como atributo de la cuenta ni se devuelve en listados.
- Toda recuperación requiere intervención de un administrador autorizado y entrega por un canal externo seguro.
- Los tokens anteriores quedan revocados después de una reemisión.
- Una futura invitación institucional podrá reemplazar la entrega manual sin cambiar el estado de primer ingreso.
