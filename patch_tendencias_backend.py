import re

path = r"C:\Users\USUARIO\Documents\U\OE UPB\OEUPB-Backend\presentation\reportes_router.py"
with open(path, "r", encoding="utf-8") as f:
    content = f.read()

new_tendencias = """@router.get("/tendencias")
def get_tendencias(indicador: str = "empleabilidad", db: Session = Depends(get_db), current_user: dict = Depends(get_current_user)):
    query = db.query(Medicion, Egresado.programa).join(Egresado, Medicion.egresado_documento == Egresado.numero_documento)
    if current_user.get('rol') == 'Coordinador_Sede':
        query = query.filter(Medicion.sede_id == current_user.get('sede_id'))
    mediciones = query.all()
    
    data_store = {}
    
    for m, programa in mediciones:
        if programa not in data_store:
            # Para empleabilidad: emp, total
            # Para salario: suma, count
            # Para satisfaccion: suma, count
            data_store[programa] = {
                0: {"emp": 0, "total": 0, "suma_salario": 0, "count_salario": 0, "suma_sat": 0, "count_sat": 0}, 
                1: {"emp": 0, "total": 0, "suma_salario": 0, "count_salario": 0, "suma_sat": 0, "count_sat": 0}, 
                5: {"emp": 0, "total": 0, "suma_salario": 0, "count_salario": 0, "suma_sat": 0, "count_sat": 0}
            }
            
        momento = m.momento if m.momento in [0, 1, 5] else 1
        resp = m.respuestas if m.respuestas else {}
        
        # 1. Empleabilidad
        key_empleo = next((k for k in resp.keys() if "realiza alguna actividad remunerada?" in k.lower()), None)
        if key_empleo:
            val = str(resp[key_empleo]).strip().upper()
            if val in ["SI", "SÍ", "NO"]:
                data_store[programa][momento]["total"] += 1
                if val in ["SI", "SÍ"]:
                    data_store[programa][momento]["emp"] += 1
                    
        # 2. Salario
        key_salario = next((k for k in resp.keys() if "ingreso mensual" in k.lower() and "smlv" in k.lower()), None)
        if key_salario and resp[key_salario]:
            val_sal = extraer_salario(str(resp[key_salario]))
            if val_sal is not None:
                data_store[programa][momento]["suma_salario"] += val_sal
                data_store[programa][momento]["count_salario"] += 1
                
        # 3. Satisfacción Institucional (Pregunta 1 general o promedio de todo)
        sat_sum = 0
        sat_count = 0
        for key, val in resp.items():
            if "nivel de satisfacci" in key.lower() and val is not None:
                try:
                    sat_sum += float(val)
                    sat_count += 1
                except:
                    pass
        if sat_count > 0:
            data_store[programa][momento]["suma_sat"] += (sat_sum / sat_count)
            data_store[programa][momento]["count_sat"] += 1

    labels = ["Momento 0 (Grado)", "Momento 1 (1 año)", "Momento 5 (5 años)"]
    datasets = []
    
    # Elegir el criterio de ordenamiento basado en el indicador y filtrar top 5
    if indicador == "salario":
        programas_ordenados = sorted(data_store.keys(), key=lambda p: sum(data_store[p][m]["count_salario"] for m in [0,1,5]), reverse=True)[:5]
    elif indicador == "satisfaccion":
        programas_ordenados = sorted(data_store.keys(), key=lambda p: sum(data_store[p][m]["count_sat"] for m in [0,1,5]), reverse=True)[:5]
    else:
        programas_ordenados = sorted(data_store.keys(), key=lambda p: sum(data_store[p][m]["total"] for m in [0,1,5]), reverse=True)[:5]
    
    # Paleta de colores más vibrante
    colores = [
        {"border": "#E63946", "bg": "rgba(230, 57, 70, 0.2)"},
        {"border": "#1D3557", "bg": "rgba(29, 53, 87, 0.2)"},
        {"border": "#2A9D8F", "bg": "rgba(42, 157, 143, 0.2)"},
        {"border": "#F4A261", "bg": "rgba(244, 162, 97, 0.2)"},
        {"border": "#9B5DE5", "bg": "rgba(155, 93, 229, 0.2)"}
    ]
    
    for idx, prog in enumerate(programas_ordenados):
        valores_por_momento = []
        for m in [0, 1, 5]:
            valor = None
            if indicador == "salario":
                count = data_store[prog][m]["count_salario"]
                suma = data_store[prog][m]["suma_salario"]
                valor = round(suma / count, 2) if count > 0 else None
            elif indicador == "satisfaccion":
                count = data_store[prog][m]["count_sat"]
                suma = data_store[prog][m]["suma_sat"]
                valor = round(suma / count, 2) if count > 0 else None
            else: # empleabilidad
                total = data_store[prog][m]["total"]
                emp = data_store[prog][m]["emp"]
                valor = round((emp / total) * 100, 1) if total > 0 else None
                
            valores_por_momento.append(valor)
            
        color = colores[idx % len(colores)]
        datasets.append({
            "label": prog,
            "data": valores_por_momento,
            "borderColor": color["border"],
            "backgroundColor": color["bg"],
            "borderWidth": 3,
            "pointBackgroundColor": "#ffffff",
            "pointBorderColor": color["border"],
            "pointBorderWidth": 2,
            "pointRadius": 5,
            "pointHoverRadius": 7,
            "fill": True,
            "tension": 0.4,
            "spanGaps": True # Conecta los puntos incluso si el momento 1 falta
        })

    return {
        "labels": labels,
        "datasets": datasets
    }
"""

content = re.sub(
    r'@router\.get\("/tendencias"\)\s*def get_tendencias\(db: Session = Depends\(get_db\), current_user: dict = Depends\(get_current_user\)\):.*?(?=\Z|\n\n)',
    new_tendencias,
    content,
    flags=re.DOTALL
)

with open(path, "w", encoding="utf-8") as f:
    f.write(content)
print("reportes_router parcheado para tendencias dinámicas.")
