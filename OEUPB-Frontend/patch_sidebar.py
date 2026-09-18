path = r"C:\Users\USUARIO\Documents\U\OE UPB\OEUPB-Frontend\src\app\presentation\shared\components\sidebar\sidebar.html"
with open(path, "r", encoding="utf-8") as f:
    content = f.read()

import re
content = re.sub(
    r'<div class="bottom-menu">.*?<button class="logout-btn"',
    '<div class="bottom-menu">\n    <a routerLink="/mi-perfil" routerLinkActive="active" class="nav-item">Mi Perfil</a>\n    <button class="logout-btn"',
    content,
    flags=re.DOTALL
)

with open(path, "w", encoding="utf-8") as f:
    f.write(content)
print("Sidebar parcheado con Python.")
