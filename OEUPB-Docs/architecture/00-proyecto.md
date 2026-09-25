# Arquitectura general de OE UPB

**Estado:** Vigente

**Verificado contra el código:** 2026-09-23

**Política objetivo actualizada:** 2026-09-23

## Propósito

OE UPB centraliza información de egresados y encuestas de seguimiento para reemplazar hojas de cálculo dispersas por una fuente institucional consultable y analítica.

## Módulos del monorepo

```text
OEUPB-Frontend (Angular :4200)
        │ HTTP + JWT
        ▼
OEUPB-Backend (FastAPI :8000)
        │ SQLAlchemy + PyMySQL
        ▼
MySQL

OEUPB-Contracts
  DTO heredados; en transición hacia OpenAPI canónico
```

| Módulo | Responsabilidad actual |
|---|---|
| Frontend | Login, gestión de usuarios, carga, reportes, tendencias, explorador, directorio y perfiles |
| Backend | JWT, usuarios, ETL de Excel, consultas de reportes y directorio |
| Base de datos | Usuarios, egresados y mediciones con respuestas JSON |
| Contratos | Tipos manuales que deben sincronizarse con OpenAPI |

## Roles observados

| Rol | Estado actual verificado | Estado normativo |
|---|---|---|
| `Admin_CTIC` | Crea coordinadores; no tiene sede en el modelo actual | Administra solo coordinadores y no accede a datos ni gráficas |
| `Coordinador_Sede` | Opera datos de su sede y crea roles inferiores | Administra datos propios y usuarios de consulta; publica gráficas agregadas; ve todas las publicadas |
| `Usuario_Consulta` | Implementado con etiqueta, permisos, programas, sede, estado y catálogo de publicaciones autorizado | Rol único de solo lectura; no accede a datos privados |

La política normativa está definida en RN-03 y RN-06 a RN-11. RBAC, cuentas, aislamiento y publicación de gráficas agregadas están implementados.

## Flujos principales

1. **Autenticación:** credenciales institucionales → JWT con rol y sede → almacenamiento local en frontend.
2. **Carga:** Excel + momento + año → validación y limpieza con Pandas → egresados y mediciones JSON.
3. **Consulta:** frontend solicita indicadores/directorio → backend filtra según identidad JWT → MySQL responde.
4. **Análisis:** endpoints agregan campos conocidos y respuestas JSON para gráficas.
5. **Publicación:** coordinador publica una gráfica propia → backend guarda definición agregada, sede y programas → usuarios autorizados la consultan sin acceso a datos fuente.

## Principios vigentes

- La autorización pertenece al backend.
- El aislamiento de datos fuente por sede es una frontera de seguridad.
- Compartir entre sedes significa publicar gráficas y métricas agregadas; nunca habilitar consultas a filas o respuestas de otra sede.
- La audiencia de una gráfica se calcula en backend a partir de permisos y programas asignados manualmente al usuario. Las etiquetas rector, profesor o administrativo no amplían el alcance.
- El código real y la documentación deben distinguirse del diseño objetivo.
- OpenAPI es la fuente canónica de contratos HTTP.
- Los cambios estructurales de datos deben pasar por migraciones formales.
- La arquitectura por capas es objetivo y convención; su cumplimiento actual es parcial y debe verificarse por cambio.

## Documentos relacionados

- [Frontend](01-frontend.md)
- [Backend](02-backend.md)
- [Contratos](03-contratos.md)
- [Modelo de datos](04-modelo-datos.md)
- [Despliegue](05-despliegue.md)
- [ADRs](../adr/INDEX.md)
