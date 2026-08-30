import os

changelog_path = r"C:\Users\USUARIO\Documents\U\OE UPB\CHANGELOG.md"
new_entry = """
## [Unreleased] - 2026-08-30

### Añadido
- **Reporte General**: Paleta de colores predeterminada dinámica (15 colores) para la gráfica de distribución por programa.
- **Reporte General**: El gráfico de *Nivel de Satisfacción* ahora permite personalizar el color de cada barra independientemente haciendo clic sobre ellas.
- **Tendencias**: Nuevo Panel de Control que permite cambiar el indicador a graficar (Empleabilidad, Salario, Satisfacción) y el tipo de gráfico (Líneas/Barras).
- **Tendencias**: Backend conectado para agrupar matemáticamente los resultados por Cohorte (Momento 0, 1 y 5).
- **Carga de Datos**: Tabla interactiva de *Historial de Cargas*, que muestra el número de egresados procesados por archivo.
- **Carga de Datos**: Nuevo selector obligatorio de **Año de Aplicación**, el cual se autogenera dinámicamente hasta el año actual, e incluye una opción para ingresar años antiguos manualmente.
- **Base de Datos**: Modificada la tabla `mediciones` para incluir la columna nativa `anio`.

### Cambiado
- **Reporte General**: El gráfico de radar fue sustituido por un gráfico de pastel para el *Nivel de Satisfacción*.
- **Carga de Datos**: El texto de las opciones de Momento de Medición fue simplificado visualmente (Ej. "Momento 0" en lugar de "Momento 0 (Grado)").

### Arreglado
- **Carga de Datos**: Prevención del error 500 al realizar consultas globales en la base de datos para el Historial.
- **Carga de Datos**: Botón de eliminación ahora desvincula los datos de forma exacta combinando el `momento` y el `anio`.
"""

if os.path.exists(changelog_path):
    with open(changelog_path, "r", encoding="utf-8") as f:
        content = f.read()
    
    # Insertar justo después de la etiqueta de título si existe
    if "# Changelog" in content:
        content = content.replace("# Changelog", "# Changelog\n" + new_entry)
    else:
        content = new_entry + "\n" + content
        
    with open(changelog_path, "w", encoding="utf-8") as f:
        f.write(content)
    print("CHANGELOG.md actualizado.")
else:
    with open(changelog_path, "w", encoding="utf-8") as f:
        f.write("# Changelog\n" + new_entry)
    print("CHANGELOG.md creado.")
