path_sidebar = r"C:\Users\USUARIO\Documents\U\OE UPB\OEUPB-Frontend\src\app\presentation\shared\components\sidebar\sidebar.html"
with open(path_sidebar, "r", encoding="utf-8") as f:
    content_sidebar = f.read()

content_sidebar = content_sidebar.replace(
    """<a routerLink="/tendencias" routerLinkActive="active" class="nav-item">Tendencias</a>""",
    """<a routerLink="/tendencias" routerLinkActive="active" class="nav-item">Tendencias</a>
      <a routerLink="/explorador" routerLinkActive="active" class="nav-item">Explorador de Datos</a>"""
)
with open(path_sidebar, "w", encoding="utf-8") as f:
    f.write(content_sidebar)

print("Sidebar parcheado correctamente.")
