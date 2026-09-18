path = r"C:\Users\USUARIO\Documents\U\OE UPB\OEUPB-Frontend\src\app\presentation\features\admin\admin-usuarios\admin-usuarios.html"
with open(path, "r", encoding="utf-8") as f:
    content = f.read()

content = content.replace(
    '<option value="Coordinador_Sede">Coordinador de Sede</option>',
    '<option value="Coordinador_Sede" *ngIf="usuarioActual?.rol === \'Admin_CTIC\'">Coordinador de Sede</option>'
)

with open(path, "w", encoding="utf-8") as f:
    f.write(content)
print("HTML actualizado para ocultar la opción de Coordinador de Sede.")
