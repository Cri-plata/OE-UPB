import datetime

path = r"C:\Users\USUARIO\Documents\U\OE UPB\CHANGELOG.md"
with open(path, "r", encoding="utf-8") as f:
    content = f.read()

new_log = """
### Añadido (2026-09-09)
- **Perfil de Usuario**: Nueva pestaña interactiva que muestra los datos de sesión, el rol, la sede asignada y los privilegios de seguridad del usuario autenticado.
- **Sedes**: Se añadió soporte oficial para la Seccional Bogotá (Sede 5) en los diccionarios internos de la aplicación.
- **Seguridad (Multitenancy)**: El sistema ahora cuenta con arquitectura multitenante. Todos los endpoints (Reportes, Directorio, Perfil, Carga) extraen la Sede del token JWT y limitan los datos mostrados exclusivamente a los de la jurisdicción del Coordinador que inicia sesión.
"""

if "## [Unreleased]" in content:
    content = content.replace("## [Unreleased] - 2026-08-30", "## [Unreleased] - 2026-08-30" + new_log)
else:
    content = content + new_log

with open(path, "w", encoding="utf-8") as f:
    f.write(content)
print("CHANGELOG actualizado para el perfil de usuario.")
