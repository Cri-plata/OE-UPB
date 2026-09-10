path = r"C:\Users\USUARIO\Documents\U\OE UPB\OEUPB-Frontend\src\app\presentation\features\admin\admin-usuarios\admin-usuarios.ts"
with open(path, "r", encoding="utf-8") as f:
    content = f.read()

content = content.replace(
    "      const formValue = this.userForm.value;\n      const nuevoUsuario: UsuarioCreateDto = {",
    "      const nuevoUsuario: UsuarioCreateDto = {"
)

with open(path, "w", encoding="utf-8") as f:
    f.write(content)
print("Variable formValue duplicada eliminada.")
