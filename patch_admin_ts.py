path = r"C:\Users\USUARIO\Documents\U\OE UPB\OEUPB-Frontend\src\app\presentation\features\admin\admin-usuarios\admin-usuarios.ts"
with open(path, "r", encoding="utf-8") as f:
    content = f.read()

content = content.replace("sede: ['', Validators.required],", "sede: [''],")
content = content.replace("sede: ['', Validators.required]", "sede: [''],\n      rol: ['Coordinador_Sede', Validators.required]")
content = content.replace("eliminar este coordinador", "eliminar este usuario")

with open(path, "w", encoding="utf-8") as f:
    f.write(content)
print("TS actualizado para sede opcional.")
