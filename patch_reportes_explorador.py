path = r"C:\Users\USUARIO\Documents\U\OE UPB\OEUPB-Backend\presentation\reportes_router.py"
with open(path, "r", encoding="utf-8") as f:
    content = f.read()

new_endpoints = """
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
"""

content = content + "\n" + new_endpoints

with open(path, "w", encoding="utf-8") as f:
    f.write(content)
print("Endpoints /explorador agregados a reportes_router.")
