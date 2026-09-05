import datetime

path = r"C:\Users\USUARIO\Documents\U\OE UPB\CHANGELOG.md"
with open(path, "r", encoding="utf-8") as f:
    content = f.read()

new_log = """
### Añadido (2026-09-04)
- **Directorio de Egresados**: Nuevo módulo de búsqueda, paginación y filtro de programas para inspeccionar la tabla de egresados.
- **Ficha del Egresado**: Nueva vista de perfil individual que muestra los detalles del estudiante y una línea de tiempo (Timeline) con su historial de encuestas y salarios en cada momento.
- **Carga de Datos**: La tabla del Historial de Cargas ahora se actualiza en tiempo real inmediatamente después de subir un archivo de Excel.

### Cambiado
- **Carga de Datos**: El algoritmo de extracción de Pandas fue flexibilizado para tolerar encuestas anónimas (estudiantes que no proveen documento) registrándolos en las métricas pero sin crear perfiles vacíos en el Directorio.
- **Carga de Datos**: El algoritmo ahora filtra e ignora automáticamente las filas basura o de "sumatorias/totales" ubicadas al final de los archivos Excel oficiales.
- **Enrutamiento**: Se migró de `RenderMode.Prerender` a `RenderMode.Client` en el servidor de Angular para prevenir errores de compilación con rutas paramétricas como `/perfil/:cedula`.
"""

# Insert right under ## [Unreleased] or at the top of the Additions
if "## [Unreleased]" in content:
    content = content.replace("## [Unreleased] - 2026-08-30", "## [Unreleased] - 2026-08-30" + new_log)
else:
    content = content + new_log

with open(path, "w", encoding="utf-8") as f:
    f.write(content)
print("CHANGELOG actualizado.")
