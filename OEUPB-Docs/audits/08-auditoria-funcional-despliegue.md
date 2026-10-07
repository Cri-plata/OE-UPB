# Auditoría funcional del despliegue 08

**Estado:** Cerrada el 2026-10-04; todos los defectos encontrados están corregidos y verificados.
**Fecha:** 2026-10-03 a 2026-10-04
**Alcance:** la aplicación completa tal como se despliega (`docker-compose.yml`, imágenes de backend y frontend, proxy `deploy/nginx.conf`), antes de la exposición.

## Método

Se levantó el stack de producción con Docker Compose en un proyecto aislado (`oeupb-audit`): MySQL 8.4 propio, `APP_ENV=production`, credenciales aleatorias, certificado autofirmado y puertos alternativos. No se tocó ninguna base de datos existente. Las migraciones se aplicaron desde cero y se creó el administrador con `seed_db.py`.

Los datos fueron 100 % sintéticos: encuestas M0 2023, M1 2023, M0 2019 y M5 2019 (unos 900 egresados, con mediciones anónimas y un texto libre con un correo y un nombre ficticios) y un archivo de 30.000 filas (1,5 MB).

La verificación tuvo tres partes:

1. Un recorrido de 54 comprobaciones contra la API desplegada, con los tres roles: activación de cuentas, carga, reportes, comparación, explorador, publicación, audiencia, IA, curaduría entre workers, directorio, exportaciones y revocación de sesión.
2. Un recorrido por la interfaz de producción en el navegador, revisando consola y red.
3. Las suites completas de pruebas dentro de la imagen de Python 3.13.

## Defectos encontrados y corregidos

| # | Severidad | Defecto | Corrección |
|---|---|---|---|
| D-01 | Bloqueante | El backend no arrancaba en la imagen: `ia_service.py` usaba `Any` en anotaciones sin importarlo. En Python 3.14 (entorno local) las anotaciones se evalúan de forma diferida y no fallaba; la imagen usa Python 3.13 y el proceso moría al importar. | Import agregado. La suite completa pasa dentro de la imagen de 3.13. |
| D-02 | Alta | "Administrar Usuarios" no listaba ni creaba usuarios tras el proxy. El cliente llamaba a `/api/usuarios` sin la barra final y FastAPI respondía 307 hacia `http://localhost/api/usuarios/` (esquema http, sin puerto), que el navegador no puede seguir desde HTTPS. En desarrollo no se notaba porque el host coincide. | `usuarios.api.ts` usa `/api/usuarios/`. Uvicorn confía en las cabeceras del proxy interno (`--forwarded-allow-ips`) para generar URL https. `tools/validate_contracts.py` ahora exige que cada ruta de los clientes exista tal cual en el OpenAPI. |
| D-03 | Alta | El proxy rechazaba con 413 cualquier Excel de más de 1 MB (valor por defecto de nginx), aunque el backend admite 25 MB. | `client_max_body_size 26m` y tiempos de espera de 180 s para `/api/` en `deploy/nginx.conf`. Una carga de 30.000 filas tardó 69 s. |
| D-04 | Alta | Revertir una curaduría no la quitaba de la taxonomía en memoria hasta reiniciar el proceso, y con 2 workers cada uno tenía su propia copia y caché. | La taxonomía se reconstruye desde la base fija más las curadurías de la BD cuando cambia su firma, y la firma forma parte de la clave de caché. Pruebas de reversión y de alineación entre procesos. |
| D-05 | Alta | La exportación de habilidades a Excel respondía 500: pasaba las transacciones como primer argumento posicional, que la función interpreta como textos. Además, agrupaba a todos los anónimos en una sola canasta. | Argumento por nombre y canastas solo para egresados identificados. Prueba nueva. |
| D-06 | Media | La imagen no incluía el modelo de spaCy `es_core_news_md`. La IA seguía funcionando sin lematización y sin avisar, así que los resultados del despliegue diferían de los de desarrollo. | El modelo se instala desde `requirements.txt` (rueda fijada 3.8.0). |
| D-07 | Media | "Mi Perfil" mostraba "Sin Sede Asignada" a coordinadores y usuarios de consulta: el nombre llegaba de forma asíncrona sin signal (detección de cambios zoneless, como en PUB-01). | `sedeNombre` es un signal. Prueba nueva. |
| D-08 | Media | El filtro de año de Habilidades ofrecía 2022 a 2026 fijos; las cohortes anteriores no se podían elegir. | Las cohortes se cargan desde `/api/reportes/filtros`. |
| D-09 | Media | Los errores de curaduría (409 término de otro autor, 403 reversión ajena) solo iban a la consola: el botón no hacía nada. | Se muestra el motivo del backend con el mismo aviso que usa Administrar Usuarios. |
| D-10 | Media | El índice del frontend se servía sin `Cache-Control`: tras un redespliegue el navegador podía seguir usando la versión anterior. | `no-cache` para `index.csr.html` en `OEUPB-Frontend/nginx.conf`. |

## Comprobado sin defectos

- **Migraciones:** aplican desde cero hasta `k8a26e3b5c74` y el catálogo de sedes queda poblado.
- **Credenciales:** la credencial inicial aleatoria aparece una sola vez en un modal. El token temporal no permite otras operaciones y el cambio obligatorio funciona.
- **Aislamiento:** historial, directorio y ficha de otra sede responden vacío o 404. CTIC no accede a reportes ni a IA. El usuario de consulta solo ve `/publicaciones` y "Mi Perfil", y no puede forzar rutas privadas.
- **Publicación:** recálculo en backend con k = 5. Otra sede ve las publicaciones y el usuario de consulta solo las de su permiso y programa.
- **Carga:** un archivo idéntico responde 409 y una extensión distinta, 400. Las mediciones anónimas se aceptan.
- **Indicadores:** comparación M0→M1 con mínimo de 5 pares (rechaza el mismo momento) y Explorador sin columnas personales.
- **IA:** el texto libre se anonimiza (el correo y el nombre sintéticos no aparecen en los resultados). La robustez del modelo solo evalúa la sede propia.
- **Directorio y cuentas:** alta, edición y eliminación manual. Desactivar un usuario revoca su sesión al instante.
- **Tiempos con unas 31.000 mediciones en una sede:** reportes de 1,3 a 2 s; IA y analítica de 2 a 7 s en caliente.

## Lista de preparación para la exposición

1. Construir las imágenes desde este código y ejecutar `alembic upgrade head` y `seed_db.py` según el [runbook](../docs/06-runbook-despliegue.md).
2. Instalar los certificados reales en `deploy/tls/` y sustituir `egresados.example.edu.co` en `deploy/nginx.conf` y `PUBLIC_ORIGIN` por el dominio real.
3. Comprobar que el reloj del servidor esté sincronizado. En la prueba, un salto de reloj de Docker Desktop tras una suspensión hizo caducar los tokens de 120 minutos.
4. **Calentar la IA antes de presentar.** La primera consulta de cada worker tras un reinicio carga spaCy y procesa todas las respuestas abiertas (unos 40 s con 31.000 respuestas). Abrir Analítica y Co-relaciones dos o tres veces antes de la exposición; los resultados quedan en caché 5 minutos y el procesamiento por texto se reutiliza.
5. Una carga grande tarda en la pantalla de Carga: 69 s para 30.000 filas. Para la demostración conviene un archivo de pocos miles de filas.
6. Tener a mano cuentas de las tres demostraciones (CTIC, coordinador y consulta) ya activadas, para no depender del cambio obligatorio de contraseña en vivo.

## Riesgos aceptados para la exposición

- La etiqueta del filtro de Habilidades sigue diciendo "Año de Encuesta", aunque el filtro es por cohorte. Cambiar el texto requiere actualizar antes el mockup (regla de interfaz 2).
- Los presupuestos de estilo de Analítica y Habilidades superan el aviso de 10 kB; la build compila.
- Quedan los pendientes de la auditoría 07 en el backlog (PUB-03, PUB-04, PUB-05, CAR-01 y AUT-01).
