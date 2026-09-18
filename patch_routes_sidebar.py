path = r"C:\Users\USUARIO\Documents\U\OE UPB\OEUPB-Frontend\src\app\app.routes.ts"
with open(path, "r", encoding="utf-8") as f:
    content = f.read()

# Make sure to import ExploradorComponent
import re
if "ExploradorComponent" not in content:
    content = re.sub(
        r"(import .*?;\n)(?=\s*export const routes)",
        r"\1import { ExploradorComponent } from './presentation/features/dashboard/explorador/explorador';\n",
        content,
        count=1
    )

if "path: 'explorador'" not in content:
    content = re.sub(
        r"(path: 'tendencias', component: TendenciasComponent \},)",
        r"\1\n  { path: 'explorador', component: ExploradorComponent },",
        content
    )

with open(path, "w", encoding="utf-8") as f:
    f.write(content)

path_sidebar = r"C:\Users\USUARIO\Documents\U\OE UPB\OEUPB-Frontend\src\app\presentation\shared\components\sidebar\sidebar.html"
with open(path_sidebar, "r", encoding="utf-8") as f:
    content_sidebar = f.read()

if "/explorador" not in content_sidebar:
    content_sidebar = content_sidebar.replace(
        """<a routerLink="/tendencias" routerLinkActive="active" class="menu-item">Tendencias</a>""",
        """<a routerLink="/tendencias" routerLinkActive="active" class="menu-item">Tendencias</a>
        <a routerLink="/explorador" routerLinkActive="active" class="menu-item">Generador de Reportes</a>"""
    )
with open(path_sidebar, "w", encoding="utf-8") as f:
    f.write(content_sidebar)

print("Rutas y Sidebar actualizados.")
