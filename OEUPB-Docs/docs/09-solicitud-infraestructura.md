# Solicitud de infraestructura para el despliegue

**Estado:** borrador para enviar a la dependencia de infraestructura de la UPB
**Fecha:** 2026-10-06
**Base técnica:** `docker-compose.yml`, `deploy/nginx.conf`, [runbook](06-runbook-despliegue.md) y mediciones de la [auditoría 08](../audits/08-auditoria-funcional-despliegue.md)

Los campos entre corchetes `[...]` debe completarlos el equipo antes de enviar el correo.

## 1. Información general

| Campo | Valor |
|---|---|
| Nombre del proyecto | OE UPB — Observatorio de Egresados de la Universidad Pontificia Bolivariana |
| Descripción | Aplicación web que centraliza las encuestas de egresados del OLE (momentos 0, 1 y 5), con directorio, indicadores de empleabilidad por sede, publicación controlada de gráficas entre sedes y análisis de texto local |
| Dependencia a la que va dirigido | [Dependencia usuaria, p. ej. Oficina de Egresados / coordinaciones de sede] |
| Responsables técnicos | [Nombres y correos institucionales del equipo] |
| Usuarios esperados | Administrador CTIC, coordinadores de sede y usuarios de consulta (decenas de usuarios concurrentes, no masivo) |

## 2. Requerimientos de hardware

Una sola máquina virtual con toda la solución en contenedores.

| Recurso | Mínimo | Recomendado | Justificación |
|---|---|---|---|
| Memoria RAM | 4 GB | **8 GB** | Medido en la auditoría 08: backend 1,05 GB (2 workers con el modelo de lenguaje spaCy cargado), MySQL 0,53 GB y nginx unos 20 MB. El entrenamiento del modelo de análisis, la compilación del frontend (2 GB) y el sistema operativo requieren margen. |
| CPU | 2 vCPU | **4 vCPU** | Dos procesos del backend atienden peticiones en paralelo; el entrenamiento del modelo y el análisis de texto son intensivos en CPU (carga de 30.000 filas: 69 s; primer análisis de IA: unos 40 s). |
| Almacenamiento | 40 GB | **80 GB SSD** | Imágenes de contenedores y caché de construcción (unos 8-10 GB), base de datos (unos 2-3 GB por año con 50.000 encuestas por sede y 5 sedes), respaldos lógicos y logs. |

## 3. Requerimientos de software y entorno

| Elemento | Solicitud |
|---|---|
| Sistema operativo | **Ubuntu Server 24.04 LTS** (64 bits). Alternativa: otra distribución Linux de 64 bits con soporte de Docker. |
| Motor de base de datos | **MySQL 8.4**, incluido en el despliegue como contenedor con volumen persistente. Si la UPB prefiere un MySQL institucional administrado, se requiere una base dedicada (UTF-8 `utf8mb4`) y un usuario con privilegios sobre ella. |
| Instalaciones | **Docker Engine** y **Docker Compose** (plugin v2), y **Git**. El resto (Python 3.13, Node 24, nginx) viaja dentro de los contenedores. |
| Dominio y certificado | Un nombre DNS institucional (p. ej. `[egresados.upb.edu.co]`) y su certificado TLS (`fullchain.pem` y `privkey.pem`), o autorización para emitirlo con Let's Encrypt. |
| Sincronización de hora | Servicio NTP activo: las sesiones usan tokens con vencimiento y un desfase de reloj las invalida. |
| Salida a internet (solo construcción) | HTTPS saliente hacia Docker Hub, PyPI, npm y GitHub para construir las imágenes y descargar el modelo de lenguaje en español. Si no se permite, el equipo puede entregar las imágenes ya construidas. |
| Respaldos | Espacio o ruta para respaldos lógicos de la base y, si existe, inclusión en la política de respaldos institucional. |

## 4. Requerimientos de red y acceso

### Puertos de entrada

| Puerto | Protocolo | Origen | Uso |
|---|---|---|---|
| **443** | TCP | Usuarios (red institucional o internet, según la política de la UPB) | Aplicación web por HTTPS |
| **80** | TCP | Igual que el 443 | Redirección automática a HTTPS (y validación del certificado si se usa Let's Encrypt) |
| **22** | TCP | **Solo IP del equipo o VPN institucional** | Acceso SSH para el despliegue y el mantenimiento |

**No se deben abrir** hacia fuera la base de datos (3306), el backend (8000) ni el contenedor del frontend (8080): se comunican solo en la red interna de Docker.

### Tráfico de salida

| Puerto | Destino | Uso |
|---|---|---|
| 443/TCP | `registry-1.docker.io`, `pypi.org`, `files.pythonhosted.org`, `registry.npmjs.org`, `github.com` | Construcción de imágenes y descarga de dependencias |
| 53 | DNS institucional | Resolución de nombres |
| 123/UDP | Servidor NTP | Sincronización de hora |

### Acceso remoto para el despliegue

- Una cuenta de usuario en la máquina para el equipo, con `sudo` o al menos pertenencia al grupo `docker`.
- Autenticación SSH **por llave pública**: el equipo envía sus llaves públicas y no se comparten contraseñas por correo.
- Conexión desde las IP del equipo `[IP públicas]` o mediante la VPN institucional (indicar cómo solicitarla).
- Ventana de despliegue propuesta: `[fecha y hora]`.

## 5. Correo sugerido

> **Asunto:** Solicitud de máquina virtual y apertura de puertos para el despliegue del proyecto OE UPB
>
> Cordial saludo.
>
> Desde el equipo del proyecto **OE UPB — Observatorio de Egresados**, dirigido a `[dependencia]`, solicitamos el aprovisionamiento de una máquina virtual para su despliegue. La aplicación centraliza las encuestas de egresados (momentos 0, 1 y 5), con indicadores de empleabilidad por sede y aislamiento de los datos de cada sede.
>
> **Hardware:**
>
> - 8 GB de RAM (mínimo 4 GB).
> - 4 vCPU (mínimo 2).
> - 80 GB de almacenamiento SSD (mínimo 40 GB).
>
> **Software y entorno:**
>
> - Ubuntu Server 24.04 LTS de 64 bits, con Docker Engine, Docker Compose v2 y Git.
> - Motor de base de datos: MySQL 8.4, que desplegamos en un contenedor con volumen persistente. Si prefieren un MySQL institucional, requerimos una base dedicada y su usuario.
> - Un nombre DNS institucional (`[nombre propuesto]`) con su certificado TLS.
> - Sincronización de hora (NTP).
> - Salida HTTPS hacia Docker Hub, PyPI, npm y GitHub durante la instalación.
>
> **Red:**
>
> - Puertos de entrada 443/TCP (HTTPS) y 80/TCP (redirección a HTTPS), accesibles para `[la red institucional / internet]`.
> - Puerto 22/TCP (SSH) restringido a las IP del equipo o a la VPN institucional.
> - La base de datos y los servicios internos no requieren puertos expuestos.
>
> **Acceso remoto:** solicitamos una cuenta con permisos de administración (`sudo`) o pertenencia al grupo `docker`, con acceso SSH por llave pública. Les enviaremos las llaves de `[integrantes]`. Si el acceso debe hacerse por VPN, les agradecemos indicarnos el procedimiento.
>
> Quedamos atentos a cualquier requisito adicional de seguridad o a la información que necesiten para la solicitud.
>
> Atentamente,
> `[Nombre, cargo/rol, correo institucional y teléfono]`
