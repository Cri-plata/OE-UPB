path = r"C:\Users\USUARIO\Documents\U\OE UPB\OEUPB-Frontend\src\app\presentation\features\data-admin\carga-datos\carga-datos.ts"
with open(path, "r", encoding="utf-8") as f:
    content = f.read()

old_next = """          this.isSubmitting = false;
          this.mensajeValidacion = response.mensaje;
          this.erroresTabla = response.errores || [];
          this.cdr.detectChanges();"""

new_next = """          this.isSubmitting = false;
          this.mensajeValidacion = response.mensaje;
          this.erroresTabla = response.errores || [];
          this.cargarHistorial(); // Actualizar tabla automáticamente
          this.cdr.detectChanges();"""

content = content.replace(old_next, new_next)

with open(path, "w", encoding="utf-8") as f:
    f.write(content)
print("Se añadió cargarHistorial al final del onSubmit.")
