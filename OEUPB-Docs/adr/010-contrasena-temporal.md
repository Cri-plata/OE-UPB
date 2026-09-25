# ADR-010 — Contraseña temporal con cambio obligatorio

**Estado:** Reemplazado por ADR-013

**Fecha de registro:** 2026-09-23

## Contexto

El proyecto aún no dispone de permisos para enviar invitaciones mediante Outlook, Microsoft 365/Graph o SMTP institucional. La contraseña compartida fija `upb123` es insegura y no permite distinguir credenciales iniciales.

## Decisión

1. El backend genera una contraseña temporal aleatoria y distinta para cada cuenta.
2. La contraseña temporal solo se devuelve una vez, en la respuesta de creación, para que el administrador o coordinador la entregue por un canal seguro.
3. La base de datos conserva únicamente su hash bcrypt.
4. El primer login emite una sesión restringida. Todos los endpoints protegidos, excepto el cambio de contraseña, responden 403 mientras `debe_cambiar_contrasena` sea verdadero.
5. El frontend presenta un modal bloqueante para definir y confirmar una contraseña nueva.
6. La contraseña nueva debe tener al menos 10 caracteres, una mayúscula, una minúscula y un número.
7. Después del cambio, la contraseña temporal queda revocada y se emite un JWT sin la restricción.
8. Al aplicar la migración, todas las cuentas existentes quedan marcadas para cambio obligatorio en su siguiente inicio, eliminando la continuidad de contraseñas iniciales conocidas como `admin123` o `upb123`.

## Consecuencias

- No se necesita integración de correo en esta etapa.
- La persona que crea la cuenta es responsable de entregar la credencial temporal por un canal seguro y no conservarla.
- Se requiere un mecanismo administrativo separado para regenerar una credencial temporal perdida; queda pendiente en el backlog.
- Una integración futura de correo podrá sustituir la entrega manual sin cambiar la obligación de establecer una contraseña personal.

Esta decisión documenta el mecanismo inicial aleatorio. El ciclo de vida vigente, incluida la credencial basada en documento para desarrollo y la alternativa aleatoria obligatoria en producción, está en [ADR-013](013-ciclo-vida-credenciales-temporales.md).
