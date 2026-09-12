path = r"C:\Users\USUARIO\Documents\U\OE UPB\OEUPB-Frontend\src\app\app.routes.ts"
with open(path, "r", encoding="utf-8") as f:
    content = f.read()

import re
if "path: 'explorador'" not in content:
    content = re.sub(
        r"(\{ \s*path: 'tendencias',\s*loadComponent: \(\) => import\('\./presentation/features/dashboard/tendencias/tendencias'\)\.then\(m => m\.TendenciasComponent\)\s*\},)",
        r"\1\n  { path: 'explorador', component: ExploradorComponent },",
        content
    )

with open(path, "w", encoding="utf-8") as f:
    f.write(content)
print("Rutas arregladas.")
