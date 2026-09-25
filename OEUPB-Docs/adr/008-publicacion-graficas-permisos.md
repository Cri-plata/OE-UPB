# ADR-008 — Publicación de gráficas y permisos de consulta

**Estado:** Aceptado

**Fecha de decisión:** 2026-09-23

## Contexto

Los coordinadores necesitan compartir resultados entre sedes y dar acceso de lectura a rectores, profesores y personal administrativo. Compartir encuestas o seleccionar destinatarios manualmente por cada publicación aumentaría el alcance de datos personales y la complejidad operativa.

## Decisión

1. Existirá un único rol técnico de solo lectura: `Usuario_Consulta`.
2. Al crear la cuenta, el coordinador de la sede asignará permisos de visualización y programas. Rector, profesor y personal administrativo son alcances de permisos, no roles técnicos independientes.
3. Cada gráfica publicable tendrá una acción `Publicar`/`Retirar publicación` visible al coordinador propietario.
4. El coordinador no elegirá personas manualmente por gráfica. El backend calculará la audiencia a partir del estado de publicación, sede propietaria, programas de la gráfica y permisos/programas del usuario.
5. Los coordinadores podrán ver todas las gráficas publicadas por otras sedes. Todo `Usuario_Consulta` verá exclusivamente publicaciones compatibles con sus permisos y programas; rector, profesor y administrativo son etiquetas informativas sin privilegios implícitos.
6. La publicación compartirá únicamente la gráfica y sus métricas agregadas. Nunca incluirá filas, documentos, nombres, correos, respuestas individuales, archivos fuente, directorio o perfiles de otra sede.
7. La acción de compartir pertenece a la gráfica, no a la pantalla de carga.

## Consecuencias

- Se mantiene el aislamiento de datos fuente definido por ADR-004.
- El modelo necesita permisos, asociaciones usuario–programa y una entidad de publicación de gráfica.
- El backend debe ser la autoridad de audiencia; ocultar elementos en el frontend no es suficiente.
- Una gráfica retirada deja de ser visible fuera de su sede sin eliminar la gráfica privada ni sus datos fuente.
- Deben existir pruebas negativas para acceso a datos fuente ajenos y pruebas de alcance por programa.

## Alternativa descartada

Seleccionar manualmente usuarios o sedes al publicar cada gráfica. Se descarta porque duplica reglas de acceso, incrementa la administración por publicación y facilita configuraciones inconsistentes.
