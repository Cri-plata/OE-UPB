import datetime
path = r"C:\Users\USUARIO\Documents\U\OE UPB\CHANGELOG.md"
with open(path, "r", encoding="utf-8") as f:
    content = f.read()

today = datetime.datetime.now().strftime("%Y-%m-%d")

new_changelog = f"""### Añadido ({today})
- **Explorador de Datos**: Nuevo módulo de Business Intelligence (Generador de Reportes Dinámico) que permite cruzar cualquiera de las 53 preguntas del instrumento SNIES y visualizar los resultados en Barras, Dona, Pie o Líneas.
- **Tendencias**: Rediseño completo de la gráfica histórica implementando paletas vibrantes, áreas bajo la curva (Fill) y suavizado de líneas para una apariencia más profesional.
- **Backend (Tendencias)**: El endpoint de tendencias fue reconstruido para soportar y calcular matemáticamente la Empleabilidad, el Promedio Salarial y el Promedio de Satisfacción General de forma dinámica.

### Arreglado ({today})
- **Seguridad (Historial de Cargas)**: Se parchó una fuga de datos en la tabla del historial donde los Coordinadores podían ver archivos subidos por otras sedes. 
- **Seguridad (Carga de Datos)**: Se corrigió la regla de validación de duplicidad (HTTP 409 Conflict) para que esté aislada por Sedes (Multitenancy).
- **Reporte General**: Se reparó un Error Interno del Servidor (HTTP 500) causado por una variable no inicializada (`query_med`) durante la reestructuración de la base de datos.
- **Autenticación**: Se programó un manejador de excepciones (HTTP 401 Unauthorized) en el `jwt.interceptor.ts` del Frontend para que, al caducar el token JWT, el sistema limpie el caché de forma segura y redirija automáticamente a la pantalla de Login sin romper la interfaz gráfica.

"""

content = content.replace("## [Unreleased] - 2026-08-30\n", "## [Unreleased] - 2026-08-30\n" + new_changelog)

with open(path, "w", encoding="utf-8") as f:
    f.write(content)
print("CHANGELOG.md actualizado.")
