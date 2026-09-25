# Arquitectura del frontend

**Estado:** descripción del código actual

**Verificado:** 2026-09-24

## Stack

- Angular 22.1 con componentes standalone.
- TypeScript 6.0.
- SCSS global y por componente.
- Chart.js 4 + ng2-charts 10.
- SSR configurado mediante `@angular/ssr`, con rutas servidas en modo cliente.
- Pruebas mediante el builder unitario de Angular y Vitest instalado.

## Estructura

```text
src/app/
├── domain/
│   ├── models/
│   ├── repositories/
│   └── usecases/
├── data/
│   ├── api/
│   ├── interceptors/
│   └── repositories/
└── presentation/
    ├── features/
    └── shared/
```

La URL base está centralizada en `environments/environment.ts` y `data/api/api.config.ts`. Los tipos HTTP compartidos se generan desde el OpenAPI canónico en `data/api/generated-api.models.ts`. Todo acceso HTTP vive en `data/api/` o repositorios; Presentation consume esas abstracciones y no construye URLs.

## Rutas actuales

| Ruta | Función |
|---|---|
| `/login` | Inicio de sesión |
| `/admin-usuarios` | Gestión de accesos |
| `/reporte` | Reporte general |
| `/tendencias` | Tendencias históricas |
| `/explorador` | Cruce dinámico de variables |
| `/publicaciones` | Catálogo de instantáneas agregadas autorizadas |
| `/carga` | Carga e historial de Excel |
| `/directorio` | Directorio de egresados |
| `/perfil/:cedula` | Ficha individual |
| `/mi-perfil` | Perfil del usuario autenticado |

`authGuard`, `rolesGuard` y `guestGuard` protegen sesión, cambio inicial pendiente y navegación por rol. El interceptor limpia sesión y redirige ante HTTP 401. Estas restricciones mejoran la navegación, pero la autorización definitiva continúa en backend.

## Estado y autenticación

- JWT y usuario se guardan en `localStorage` bajo `jwt_token` y `user_data`.
- El interceptor añade `Authorization: Bearer`.
- La URL del backend se toma de la configuración de entorno y los clientes de Data construyen las rutas.
- Los componentes no importan `HttpClient`; los clientes tipados de `data/api/` construyen rutas y parámetros.
- Si el login indica `debeCambiarContrasena`, la pantalla mantiene un modal bloqueante y renueva token y datos locales únicamente después de completar el cambio.

## Reglas para cambios

1. Servicios HTTP y repositorios pertenecen a Data; los componentes no deben crear URLs.
2. Modelos y reglas puras pertenecen a Domain.
3. Presentation solo coordina vista y casos de uso.
4. Todo estilo nuevo debe usar los tokens y componentes de [`../design/design.md`](../design/design.md).
5. Los permisos visibles mejoran UX, pero el backend sigue siendo la autoridad.
6. Ninguna pantalla o modificación visual se implementa sin un mockup previo o actualizado en [`../mockups/`](../mockups/) y su entrada correspondiente en [`../mockups/screen-map.md`](../mockups/screen-map.md).
7. No se utilizan emojis en la interfaz. Los iconos proceden de la librería estándar definida en el sistema de diseño y conservan etiquetas accesibles cuando representan acciones.

## Objetivo aprobado: permisos y publicación

- `Admin_CTIC` mantiene una vista para administrar coordinadores.
- `Coordinador_Sede` administra usuarios de consulta, su etiqueta informativa, los cuatro permisos del catálogo inicial y los programas observados en cargas visibles de la sede propia desde la vista de accesos.
- Las gráficas publicables muestran una acción `Publicar`/`Retirar publicación` únicamente al coordinador propietario.
- La pantalla de carga no selecciona una sede para ampliar alcance y no contiene la acción de compartir encuestas.
- `Usuario_Consulta` recibe un dashboard de solo lectura; el frontend muestra las gráficas autorizadas por la respuesta del backend y no intenta reconstruir permisos localmente.
- El dashboard privado no ofrece selector de sede: usa exclusivamente la sede derivada de la sesión. Una vista separada presenta las instantáneas publicadas por otras sedes.
- `Usuario_Consulta` nunca recibe gráficas privadas, ni siquiera las de su propia sede; solo instantáneas publicadas compatibles con sus permisos y programas.
- Rector, profesor y administrativo son etiquetas informativas: la interfaz no precarga ni bloquea privilegios por etiqueta. Permisos y programas se seleccionan manualmente.

La administración de usuarios, el menú y los guards reflejan RBAC. Cada gráfica de Reporte General, Tendencias y Explorador ofrece publicación/retiro con aprobación explícita; `/publicaciones` renderiza únicamente el catálogo filtrado por el backend.
