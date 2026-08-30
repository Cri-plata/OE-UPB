from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from infrastructure.database import get_db
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
def get_reporte_general(db: Session = Depends(get_db)):
    total = db.query(Egresado).count()
    
    programas = db.query(Egresado.programa).all()
    dist = {}
    for p in programas:
        prog = p[0]
        if prog in dist:
            dist[prog] += 1
        else:
            dist[prog] = 1
            
    mediciones = db.query(Medicion).all()
    
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
def get_tendencias(db: Session = Depends(get_db)):
    # Obtenemos todas las mediciones con sus egresados asociados
    mediciones = db.query(Medicion, Egresado.programa).join(Egresado, Medicion.egresado_documento == Egresado.numero_documento).all()
    
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

