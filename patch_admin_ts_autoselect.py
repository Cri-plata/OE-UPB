path = r"C:\Users\USUARIO\Documents\U\OE UPB\OEUPB-Frontend\src\app\presentation\features\admin\admin-usuarios\admin-usuarios.ts"
with open(path, "r", encoding="utf-8") as f:
    content = f.read()

# Auto select sede if there is only 1 option
old_init = "this.cargarUsuarios();"
new_init = """if (this.sedesDisponibles.length === 1) {
      this.userForm.patchValue({ sede: this.sedesDisponibles[0] });
    }
    this.cargarUsuarios();"""

content = content.replace(old_init, new_init)

with open(path, "w", encoding="utf-8") as f:
    f.write(content)
print("TS actualizado para autoseleccionar sede.")
