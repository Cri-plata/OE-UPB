path = r"C:\Users\USUARIO\Documents\U\OE UPB\OEUPB-Frontend\src\app\presentation\features\admin\admin-usuarios\admin-usuarios.html"
with open(path, "r", encoding="utf-8") as f:
    content = f.read()

content = content.replace(
    '<option value="Admin_CTIC">Administrador CTIC</option>',
    '<option value="Admin_CTIC" *ngIf="usuarioActual?.rol === \'Admin_CTIC\'">Administrador CTIC</option>'
)

with open(path, "w", encoding="utf-8") as f:
    f.write(content)
print("HTML actualizado para esconder Admin_CTIC.")
