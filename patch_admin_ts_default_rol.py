path = r"C:\Users\USUARIO\Documents\U\OE UPB\OEUPB-Frontend\src\app\presentation\features\admin\admin-usuarios\admin-usuarios.ts"
with open(path, "r", encoding="utf-8") as f:
    content = f.read()

# Change the form init
content = content.replace(
    "rol: ['Coordinador_Sede', Validators.required]",
    "rol: ['', Validators.required]"
)

with open(path, "w", encoding="utf-8") as f:
    f.write(content)
print("Formulario reseteado para no seleccionar Coordinador por defecto.")
