path = r"C:\Users\USUARIO\Documents\U\OE UPB\OEUPB-Frontend\src\app\presentation\shared\components\sidebar\sidebar.html"
with open(path, "r", encoding="utf-8") as f:
    content = f.read()

import re

# Remove Mi Perfil from bottom-menu
content = re.sub(
    r'<div class="bottom-menu">\s*<a routerLink="/mi-perfil"[^>]+>.*?</a>',
    '<div class="bottom-menu">',
    content,
    flags=re.DOTALL
)

# Insert Mi Perfil at the end of nav-menu
if '<a routerLink="/mi-perfil"' not in content:
    content = content.replace(
        '</nav>',
        '  <!-- Perfil General -->\n    <a routerLink="/mi-perfil" routerLinkActive="active" class="nav-item">Mi Perfil</a>\n  </nav>'
    )

with open(path, "w", encoding="utf-8") as f:
    f.write(content)
print("Sidebar HTML corregido.")
