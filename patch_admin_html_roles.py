path = r"C:\Users\USUARIO\Documents\U\OE UPB\OEUPB-Frontend\src\app\presentation\features\admin\admin-usuarios\admin-usuarios.html"
with open(path, "r", encoding="utf-8") as f:
    content = f.read()

import re

old_select = """            <select formControlName="rol">
              <option value="">Seleccione un rol...</option>
              <option value="Coordinador_Sede" *ngIf="usuarioActual?.rol === 'Admin_CTIC'">Coordinador de Sede</option>
              <option value="Directivo">Directivo</option>
              <option value="Profesor">Profesor</option>
              <option value="Admin_CTIC" *ngIf="usuarioActual?.rol === 'Admin_CTIC'">Administrador CTIC</option>
            </select>"""

# Using regex to catch whatever the current select looks like
new_select = """            <select formControlName="rol">
              <option value="">Seleccione un rol...</option>
              <option value="Coordinador_Sede" *ngIf="usuarioActual?.rol === 'Admin_CTIC'">Coordinador de Sede</option>
              <option value="Directivo" *ngIf="usuarioActual?.rol === 'Coordinador_Sede'">Directivo</option>
              <option value="Profesor" *ngIf="usuarioActual?.rol === 'Coordinador_Sede'">Profesor</option>
            </select>"""

content = re.sub(
    r'<select formControlName="rol">.*?</select>',
    new_select,
    content,
    flags=re.DOTALL
)

with open(path, "w", encoding="utf-8") as f:
    f.write(content)
print("HTML actualizado para restringir roles según quién crea el usuario.")
