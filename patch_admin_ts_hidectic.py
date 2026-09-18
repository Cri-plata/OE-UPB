path = r"C:\Users\USUARIO\Documents\U\OE UPB\OEUPB-Frontend\src\app\presentation\features\admin\admin-usuarios\admin-usuarios.ts"
with open(path, "r", encoding="utf-8") as f:
    content = f.read()

# Restore the filter to hide Admin_CTIC from the table
content = content.replace(
    "this.usuarios = data;",
    "this.usuarios = data.filter(u => u.rol !== 'Admin_CTIC');"
)

# If we want Admin_CTIC to auto-select "Coordinador_Sede" since it's their only option
old_init = "this.cargarUsuarios();"
new_init = """if (this.usuarioActual.rol === 'Admin_CTIC') {
      this.userForm.patchValue({ rol: 'Coordinador_Sede' });
    }
    this.cargarUsuarios();"""
content = content.replace(old_init, new_init)

with open(path, "w", encoding="utf-8") as f:
    f.write(content)
print("TS actualizado para ocultar Admin_CTIC y autoseleccionar rol.")
