import datetime

path = r"C:\Users\USUARIO\Documents\U\OE UPB\CHANGELOG.md"
with open(path, "r", encoding="utf-8") as f:
    content = f.read()

new_log = """
- **Administración de Usuarios**: Se reestructuró la pestaña de Gestión de Accesos habilitándola también para los Coordinadores de Sede con un sistema de separación de deberes (Separation of Duties).
- **Seguridad (Creación de Usuarios)**: El rol CTIC ahora está estrictamente limitado a crear exclusivamente cuentas de `Coordinador_Sede`. Los Coordinadores, a su vez, son los únicos autorizados para crear `Directivos` y `Profesores` para su propia jurisdicción.
- **Seguridad (Invisibilidad CTIC)**: Las cuentas de nivel CTIC fueron removidas completamente de la tabla de visualización global (invisibles para todos, incluyendo para otros CTIC) para evitar manipulaciones operativas.
- **UX/UI (Formularios Dinámicos)**: El formulario de creación de usuarios ahora es reactivo a la sesión; autocompleta el rol para los CTIC y esconde la casilla de asignación de Sede para los Coordinadores, inyectándola por debajo para agilizar el registro.
"""

if "### Añadido (2026-09-09)" in content:
    content = content.replace("### Añadido (2026-09-09)", "### Añadido (2026-09-09)" + new_log)
else:
    # Fallback if section doesn't exist exactly like that
    if "## [Unreleased]" in content:
        content = content.replace("## [Unreleased] - 2026-08-30", "## [Unreleased] - 2026-08-30\n### Añadido (2026-09-09)" + new_log)
    else:
        content = content + new_log

with open(path, "w", encoding="utf-8") as f:
    f.write(content)
print("CHANGELOG actualizado con las reglas de administración de usuarios.")
