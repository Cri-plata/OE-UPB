path = r"C:\Users\USUARIO\Documents\U\OE UPB\OEUPB-Frontend\src\app\presentation\features\admin\admin-usuarios\admin-usuarios.html"
with open(path, "r", encoding="utf-8") as f:
    content = f.read()

import re

# Find the form-group for Sede and wrap it or add ngIf
# We'll use string replace for simplicity
content = content.replace(
    '<div class="form-group">\n            <label>Sede Asignada * (Dejar vacío si es Nacional)</label>',
    '<div class="form-group" *ngIf="usuarioActual?.rol === \'Admin_CTIC\'">\n            <label>Sede Asignada * (Dejar vacío si es Nacional)</label>'
)

with open(path, "w", encoding="utf-8") as f:
    f.write(content)
print("HTML actualizado para ocultar la casilla de sede a los coordinadores.")
