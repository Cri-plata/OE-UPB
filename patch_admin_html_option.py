path = r"C:\Users\USUARIO\Documents\U\OE UPB\OEUPB-Frontend\src\app\presentation\features\admin\admin-usuarios\admin-usuarios.html"
with open(path, "r", encoding="utf-8") as f:
    content = f.read()

content = content.replace(
    '<select formControlName="rol">',
    '<select formControlName="rol">\n              <option value="">Seleccione un rol...</option>'
)

with open(path, "w", encoding="utf-8") as f:
    f.write(content)
print("Option vacío añadido.")
