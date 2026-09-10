path = r"C:\Users\USUARIO\Documents\U\OE UPB\OEUPB-Frontend\src\app\presentation\features\admin\admin-usuarios\admin-usuarios.html"
with open(path, "r", encoding="utf-8") as f:
    content = f.read()

import re

old_select = """            <select formControlName="sede">
              <option value="">Seleccione una sede...</option>
              <option value="Bucaramanga">Bucaramanga</option>
              <option value="Medelln">Medelln</option>
              <option value="Palmira">Palmira</option>
              <option value="Montera">Montera</option>
              <option value="Bogot">Bogot</option>
            </select>"""

# If the encoding got messy, let's just use regex to replace everything between <select formControlName="sede"> and </select>
new_select = """            <select formControlName="sede">
              <option value="">Seleccione una sede...</option>
              <option *ngFor="let s of sedesDisponibles" [value]="s">{{ s }}</option>
            </select>"""

content = re.sub(
    r'<select formControlName="sede">.*?</select>',
    new_select,
    content,
    flags=re.DOTALL
)

with open(path, "w", encoding="utf-8") as f:
    f.write(content)
print("HTML actualizado para usar sedesDisponibles dinámico.")
