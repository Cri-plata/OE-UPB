path = r"C:\Users\USUARIO\Documents\U\OE UPB\OEUPB-Frontend\src\app\presentation\features\admin\admin-usuarios\admin-usuarios.ts"
with open(path, "r", encoding="utf-8") as f:
    content = f.read()

# Add a sedesDisponibles array
if "sedesDisponibles" not in content:
    content = content.replace(
        "usuarioActual: any = null;",
        "usuarioActual: any = null;\n  sedesDisponibles: string[] = [];"
    )
    
    # In ngOnInit, calculate the allowed sedes
    old_init = "this.cargarUsuarios();"
    new_init = """const mapaSedes: any = { 1: 'Bucaramanga', 2: 'Medellín', 3: 'Palmira', 4: 'Montería', 5: 'Bogotá' };
    if (this.usuarioActual.rol === 'Admin_CTIC') {
      this.sedesDisponibles = ['Bucaramanga', 'Medellín', 'Palmira', 'Montería', 'Bogotá'];
    } else if (this.usuarioActual.rol === 'Coordinador_Sede' && this.usuarioActual.sedeId) {
      this.sedesDisponibles = [mapaSedes[this.usuarioActual.sedeId]];
    }
    this.cargarUsuarios();"""
    content = content.replace(old_init, new_init)

with open(path, "w", encoding="utf-8") as f:
    f.write(content)
print("TS actualizado para manejar sedesDisponibles.")
