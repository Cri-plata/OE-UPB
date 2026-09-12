from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from infrastructure.database import get_db
from application.auth_service import get_current_user
from domain.models import Egresado, Medicion
from pydantic import BaseModel
import re

router = APIRouter(prefix="/api/reportes", tags=["Reportes"])

class KpisResponse(BaseModel):
    total_egresados: int
    tasa_empleabilidad: float
    promedio_salarial: float
    distribucion_programas: dict
    nivel_satisfaccion: dict

def extraer_salario(texto):
    if not texto or not isinstance(texto, str):
        return None
    texto = texto.lower()
    
    # Extraer el patrón "entre X y Y smlv"
    if "entre" in texto and "smlv" in texto:
        match = re.search(r"entre ([\d,]+) y ([\d,]+)", texto)
        if match:
            v1 = float(match.group(1).replace(",", "."))
            v2 = float(match.group(2).replace(",", "."))
            return (v1 + v2) / 2.0
    if "menos de 1" in texto:
        return 0.8
    if "más de 10" in texto or "mas de 10" in texto:
        return 12.0
    if "1 smlv" in texto:
        return 1.0
        
    # Extraer primer número si es distinto
    numeros = re.findall(r"([\d,]+)", texto.split("(")[0])
    if numeros:
        return float(numeros[0].replace(",", "."))
    return None

@router.get("/general", response_model=KpisResponse)
def get_reporte_general(db: Session = Depends(get_db), current_user: dict = Depends(get_current_user)):
    
    query_med = db.query(Medicion)
    query_egresados = db.query(Egresado)
    
    if current_user.get('rol') == 'Coordinador_Sede':
        query_med = query_med.filter(Medicion.sede_id == current_user.get('sede_id'))
        query_egresados = query_egresados.filter(Egresado.numero_documento.in_(db.query(Medicion.egresado_documento).filter(Medicion.sede_id == current_user.get('sede_id'))))

    total = query_egresados.count()
    programas = query_egresados.with_entities(Egresado.programa).all()

    dist = {}
    for p in programas:
        prog = p[0]
        if prog in dist:
            dist[prog] += 1
        else:
            dist[prog] = 1
            
    mediciones = query_med.all()
    
    empleados_count = 0
    respuestas_validas = 0
    
    suma_salarios = 0
    salarios_validos = 0
    
    satisfaccion = {
        "Aplicación Conocimientos": {"suma": 0, "count": 0},
        "Retos Intelectuales": {"suma": 0, "count": 0},
        "Estabilidad": {"suma": 0, "count": 0},
        "Ascenso": {"suma": 0, "count": 0}
    }
    
    for m in mediciones:
        resp = m.respuestas if m.respuestas else {}
        
        # 1. Empleabilidad (Pregunta 22)
        key_empleo = next((k for k in resp.keys() if "realiza alguna actividad remunerada?" in k.lower()), None)
        if key_empleo:
            val = str(resp[key_empleo]).strip().upper()
            if val in ["SI", "SÍ", "NO"]:
                respuestas_validas += 1
                if val in ["SI", "SÍ"]:
                    empleados_count += 1
                    
        # 2. Salario (Pregunta 55)
        key_salario = next((k for k in resp.keys() if "ingreso mensual" in k.lower() and "smlv" in k.lower() and "realiza" in k.lower()), None)
        if key_salario and resp[key_salario]:
            val_sal = extraer_salario(str(resp[key_salario]))
            if val_sal is not None:
                suma_salarios += val_sal
                salarios_validos += 1
                
        # 3. Satisfacción (Pregunta 54)
        for key, val in resp.items():
            if "califique su nivel de satisfacci" in key.lower() and val is not None:
                try:
                    num_val = float(val)
                    if "aplicaci" in key.lower() and "conocimientos" in key.lower():
                        satisfaccion["Aplicación Conocimientos"]["suma"] += num_val
                        satisfaccion["Aplicación Conocimientos"]["count"] += 1
                    elif "retos y desaf" in key.lower():
                        satisfaccion["Retos Intelectuales"]["suma"] += num_val
                        satisfaccion["Retos Intelectuales"]["count"] += 1
                    elif "estabilidad" in key.lower():
                        satisfaccion["Estabilidad"]["suma"] += num_val
                        satisfaccion["Estabilidad"]["count"] += 1
                    elif "ascenso" in key.lower():
                        satisfaccion["Ascenso"]["suma"] += num_val
                        satisfaccion["Ascenso"]["count"] += 1
                except:
                    pass

    tasa_empleabilidad = round((empleados_count / respuestas_validas) * 100, 1) if respuestas_validas > 0 else 0
    promedio_salarial = round(suma_salarios / salarios_validos, 1) if salarios_validos > 0 else 0
    
    resultado_satisfaccion = {}
    for k, v in satisfaccion.items():
        resultado_satisfaccion[k] = round(v["suma"] / v["count"], 1) if v["count"] > 0 else 0

    return {
        "total_egresados": total,
        "tasa_empleabilidad": tasa_empleabilidad,
        "promedio_salarial": promedio_salarial,
        "distribucion_programas": dist,
        "nivel_satisfaccion": resultado_satisfaccion
    }

@router.get("/tendencias")
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


    
    # Estructura para almacenar data real: programa -> momento -> valores
    data_empleo = {}
    
    for m, programa in mediciones:
        if programa not in data_empleo:
            data_empleo[programa] = {0: {"emp": 0, "total": 0}, 1: {"emp": 0, "total": 0}, 5: {"emp": 0, "total": 0}}
            
        momento = m.momento if m.momento in [0, 1, 5] else 1 # Fallback seguro
        resp = m.respuestas if m.respuestas else {}
        
        # Empleabilidad NLP
        key_empleo = next((k for k in resp.keys() if "realiza alguna actividad remunerada?" in k.lower()), None)
        if key_empleo:
            val = str(resp[key_empleo]).strip().upper()
            if val in ["SI", "SÍ", "NO"]:
                data_empleo[programa][momento]["total"] += 1
                if val in ["SI", "SÍ"]:
                    data_empleo[programa][momento]["emp"] += 1
    
    # Formatear para Chart.js
    labels = ["Momento 0 (Grado)", "Momento 1 (1 año)", "Momento 5 (5 años)"]
    datasets = []
    
    # Para no saturar la gráfica de tendencias, tomamos los top 5 programas con más datos
    programas_ordenados = sorted(data_empleo.keys(), key=lambda p: sum(data_empleo[p][m]["total"] for m in [0,1,5]), reverse=True)[:5]
    
    for prog in programas_ordenados:
        valores_por_momento = []
        for m in [0, 1, 5]:
            total = data_empleo[prog][m]["total"]
            emp = data_empleo[prog][m]["emp"]
            tasa = round((emp / total) * 100, 1) if total > 0 else None
            valores_por_momento.append(tasa)
            
        # Si algún momento está vacío (ej. no han subido Momento 5), interpolamos visualmente o dejamos null
        # Para la demo, si es None, le ponemos un valor estético si los otros existen
        
        datasets.append({
            "label": prog,
            "data": valores_por_momento,
            "tension": 0.4
        })

    return {
        "labels": labels,
        "datasets": datasets
    }



@router.get("/explorador/init")
def explorador_init(db: Session = Depends(get_db), current_user: dict = Depends(get_current_user)):
    query = db.query(Medicion, Egresado.programa).join(Egresado, Medicion.egresado_documento == Egresado.numero_documento)
    if current_user.get('rol') == 'Coordinador_Sede':
        query = query.filter(Medicion.sede_id == current_user.get('sede_id'))
    
    mediciones = query.all()
    
    # Extraer preguntas únicas, programas y años
    preguntas_set = set()
    programas_set = set()
    anios_set = set()
    
    for m, prog in mediciones:
        programas_set.add(prog)
        if m.anio:
            anios_set.add(m.anio)
        if m.respuestas:
            for k in m.respuestas.keys():
                preguntas_set.add(k)
                
    return {
        "preguntas": sorted(list(preguntas_set)),
        "programas": sorted(list(programas_set)),
        "anios": sorted(list(anios_set))
    }

@router.get("/explorador")
def explorador_data(
    pregunta: str,
    momento: str = None,
    programa: str = None,
    anio: str = None,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    query = db.query(Medicion, Egresado).join(Egresado, Medicion.egresado_documento == Egresado.numero_documento)
    
    if current_user.get('rol') == 'Coordinador_Sede':
        query = query.filter(Medicion.sede_id == current_user.get('sede_id'))
        
    if momento and momento != '':
        query = query.filter(Medicion.momento == int(momento))
    if programa and programa != '':
        query = query.filter(Egresado.programa == programa)
    if anio and anio != '':
        query = query.filter(Medicion.anio == int(anio))
        
    resultados = query.all()
    
    # Agrupar las respuestas a la pregunta seleccionada
    conteo_respuestas = {}
    
    for m, e in resultados:
        if m.respuestas and pregunta in m.respuestas:
            valor = str(m.respuestas[pregunta]).strip()
            # Limpiar algunos datos si son None o "nan"
            if valor.lower() in ["nan", "none", ""]:
                valor = "Sin respuesta"
            
            if valor in conteo_respuestas:
                conteo_respuestas[valor] += 1
            else:
                conteo_respuestas[valor] = 1
                
    # Ordenar resultados por conteo descendente
    sorted_items = sorted(conteo_respuestas.items(), key=lambda x: x[1], reverse=True)
    
    labels = [item[0][:50] + ('...' if len(item[0]) > 50 else '') for item in sorted_items]
    valores = [item[1] for item in sorted_items]
    
    return {
        "labels": labels,
        "valores": valores
    }
