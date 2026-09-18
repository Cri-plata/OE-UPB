path = r"C:\Users\USUARIO\Documents\U\OE UPB\OEUPB-Frontend\src\app\presentation\features\admin\admin-usuarios\admin-usuarios.ts"
with open(path, "r", encoding="utf-8") as f:
    content = f.read()

# Quitar el filtro estricto del frontend, dejar que el backend decida quién ve a quién
content = content.replace(
    "this.usuarios = data.filter(u => u.rol !== 'Admin_CTIC');",
    "this.usuarios = data;"
)
content = content.replace(
    "// Filtrar para no mostrar al super administrador si queremos, o mostrarlos todos\n        ",
    ""
)

with open(path, "w", encoding="utf-8") as f:
    f.write(content)
print("Filtro frontend eliminado. El backend ahora maneja la visibilidad.")
