path = r"C:\Users\USUARIO\Documents\U\OE UPB\OEUPB-Frontend\src\app\presentation\features\admin\admin-usuarios\admin-usuarios.ts"
with open(path, "r", encoding="utf-8") as f:
    content = f.read()

# Add a custom validator or just handle it in onSubmit
content = content.replace(
    "if (this.userForm.valid) {",
    "if (this.userForm.valid) {\n      const formValue = this.userForm.value;\n      if (formValue.rol === 'Coordinador_Sede' && !formValue.sede) {\n        alert('Los Coordinadores de Sede deben tener una sede asignada obligatoriamente.');\n        return;\n      }"
)

# Clean up duplicated const formValue declaration since I just added one above
content = content.replace(
    "const formValue = this.userForm.value;\n      const formValue = this.userForm.value;",
    "const formValue = this.userForm.value;"
)

with open(path, "w", encoding="utf-8") as f:
    f.write(content)
print("Validación de sede obligatoria añadida para coordinadores.")
