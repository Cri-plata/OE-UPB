path = r"C:\Users\USUARIO\Documents\U\OE UPB\OEUPB-Frontend\src\app\presentation\features\admin\admin-usuarios\admin-usuarios.html"
with open(path, "r", encoding="utf-8") as f:
    content = f.read()

content = content.replace(
    "<h1>Administración de Usuarios (CTIC)</h1>",
    "<h1>Gestión de Accesos y Usuarios</h1>"
)

with open(path, "w", encoding="utf-8") as f:
    f.write(content)
print("Título del HTML actualizado.")
