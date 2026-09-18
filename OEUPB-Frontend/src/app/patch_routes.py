path = r"C:\Users\USUARIO\Documents\U\OE UPB\OEUPB-Frontend\src\app\app.routes.ts"
with open(path, "r", encoding="utf-8") as f:
    content = f.read()

new_route = """  { 
    path: 'mi-perfil', 
    loadComponent: () => import('./presentation/features/profile/perfil-usuario/perfil-usuario').then(m => m.PerfilUsuarioComponent)
  },
  { path: '**', redirectTo: 'login' }"""

content = content.replace("  { path: '**', redirectTo: 'login' }", new_route)

with open(path, "w", encoding="utf-8") as f:
    f.write(content)
print("Ruta de mi-perfil añadida.")
