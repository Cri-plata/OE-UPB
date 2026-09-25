# ADR-015 — Recálculo en backend y umbral mínimo de las publicaciones

**Estado:** Aceptado

**Fecha:** 2026-09-25

**Modifica:** ADR-008 (consecuencias) y ADR-009, punto 8.

## Contexto

La auditoría 05 detectó que `POST /api/publicaciones` aceptaba del cliente las métricas, las etiquetas y los programas de audiencia (C-02). El backend no podía demostrar que la instantánea provenía de datos de la sede, el cliente podía declarar programas para ampliar la audiencia y no existía un umbral que impidiera reidentificar personas en celdas pequeñas (B-04). Además, la "aprobación manual de privacidad" no identificaba al aprobador (C-06).

## Decisión

1. **Recálculo obligatorio.** El cliente envía solo `grafica_key`, `titulo`, `definicion` y la confirmación de privacidad. El backend recalcula las métricas a partir de `definicion` y de la sede del JWT, con las mismas funciones que usa el dashboard privado (`application/indicadores.py`). Cualquier campo `metricas` o `programas` enviado por el cliente se ignora.
2. **Audiencia derivada.** Los programas de la publicación son los que aportan datos a las celdas publicadas: el filtro `definicion.programa` si existe o, si no, los programas observados en el cálculo. En la distribución por programa, un programa suprimido sin agrupar no forma parte de la audiencia.
3. **Umbral k = 5.** Ninguna celda publicada puede representar menos de 5 observaciones:
   - en los conteos por categoría (distribución por programa y Explorador), las categorías menores se agrupan en `Otros (agrupados por privacidad)` si en conjunto alcanzan 5; si no, se omiten;
   - en los promedios y tasas (satisfacción y tendencias), el valor se publica como `null` si su denominador es menor que 5.
   Si no queda ninguna celda publicable, la publicación se rechaza con 422.
4. **Catálogo analítico (RN-31).** El Explorador y la publicación solo aceptan variables clasificadas como analíticas por el backend. Las familias excluidas se detectan sobre el nombre normalizado de la columna.
5. **Autoaprobación explícita.** La aprobación de privacidad es la confirmación explícita del coordinador propietario en la misma acción de publicar (`aprobada_privacidad: true`). No existe un segundo aprobador ni un estado pendiente.
6. **Reporte general.** Su definición exige `indicador` con valor `distribucion_programas` o `satisfaccion`.

## Consecuencias

- El umbral aplica solo a las publicaciones. El dashboard privado del coordinador conserva los valores exactos de su sede.
- Las publicaciones usan la paleta del sistema; los colores personalizados en el dashboard privado no se transfieren.
- RN-14, RN-26 y RN-31, HU-13 y CU-12 se actualizan con esta política.
- Cambiar el umbral requiere un ADR nuevo y actualizar `UMBRAL_MINIMO_PUBLICACION` y sus pruebas.
