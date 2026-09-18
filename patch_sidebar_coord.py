path = r"C:\Users\USUARIO\Documents\U\OE UPB\OEUPB-Frontend\src\app\presentation\shared\components\sidebar\sidebar.html"
with open(path, "r", encoding="utf-8") as f:
    content = f.read()

content = content.replace(
    "<ng-container *ngIf=\"userRole === 'Admin_CTIC'\">",
    "<ng-container *ngIf=\"userRole === 'Admin_CTIC' || userRole === 'Coordinador_Sede'\">"
)

with open(path, "w", encoding="utf-8") as f:
    f.write(content)
print("Sidebar actualizado para permitir a los coordinadores administrar usuarios.")
