# ADR-018 — Catálogo de publicaciones del coordinador

**Estado:** Aceptado

**Fecha:** 2026-09-30

## Contexto

ADR-008 (punto 5) y RN-10 limitaban al coordinador a ver las publicaciones de otras sedes. Sus propias publicaciones y las de los demás coordinadores de su sede no aparecían en ninguna lista: solo se veían como "Publicada vN" en el dashboard de origen. Un coordinador que acababa de publicar encontraba vacía la vista "Gráficas publicadas" y lo interpretaba como un fallo. El retiro solo era posible desde la gráfica privada, con los mismos filtros con que se publicó.

## Decisión

1. Para `Coordinador_Sede`, la vista "Gráficas publicadas" tiene dos secciones:
   - **Mis publicaciones:** sus publicaciones vigentes (`GET /api/publicaciones/mias`), cada una con la acción `Retirar publicación`.
   - **Publicadas por otros coordinadores:** `GET /api/publicaciones/` devuelve las publicaciones vigentes de todos los demás coordinadores, de su sede y de las demás. Se excluyen solo las propias, que ya están en la primera sección.
2. Las reglas de retiro no cambian: solo el propietario, u otro coordinador de la sede propietaria si el propietario está inactivo o fue reasignado.
3. `Usuario_Consulta` no cambia (RN-24): una sola lista según permisos y programas.

## Consecuencias

- La regla de privacidad se mantiene: solo se comparten instantáneas agregadas con el umbral k = 5 (ADR-015). Ver las publicaciones de otro coordinador de la misma sede no da acceso a nada que el coordinador no pudiera consultar ya en su dashboard privado.
- El contrato HTTP no cambia de forma; cambia el conjunto de filas que `GET /api/publicaciones/` devuelve a un coordinador.
- ADR-008 punto 5 y RN-10 quedan modificados en el alcance del coordinador.
