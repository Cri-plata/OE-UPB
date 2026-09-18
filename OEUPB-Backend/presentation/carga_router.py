from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.orm import Session
from domain.models import Egresado, Medicion
from infrastructure.database import get_db
from application.auth_service import get_current_user
import pandas as pd
import io
from pydantic import BaseModel
from typing import List

router = APIRouter(prefix="/api/carga", tags=["Carga de Datos"])

class ErrorFila(BaseModel):
    fila: int
    columna: str
    error: str

class CargaResponse(BaseModel):
    mensaje: str
    errores: List[ErrorFila] = []

@router.post("/excel", response_model=CargaResponse)
async def procesar_excel(
    momento: int = Form(...),
    anio: int = Form(...),
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    if not file.filename.endswith(('.xlsx', '.xls')):
        raise HTTPException(status_code=400, detail="El archivo debe ser un Excel (.xlsx o .xls)")

        # REGLA DE NEGOCIO: Evitar duplicidad de cargas por sede
    sede_coordinador_actual = current_user.get('sede_id') or 1
    carga_existente = db.query(Medicion).filter(
        Medicion.momento == momento, 
        Medicion.anio == anio,
        Medicion.sede_id == sede_coordinador_actual
    ).first()
    
    if carga_existente:
        raise HTTPException(
            status_code=409, 
            detail=f"Tu sede ya tiene registros cargados para el Momento {momento} del año {anio}. Por favor, elimínelos desde el Historial antes de volver a cargarlos."
        )

    # Leer el archivo a la memoria
    contents = await file.read()
    
    try:
        # Usar Pandas para leer el Excel
        df = pd.read_excel(io.BytesIO(contents))
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"No se pudo leer el archivo Excel: {str(e)}")

    errores = []
    
    # Columnas esperadas básicas (podemos agregar más según necesidad)
    columnas_esperadas = ["NUMERO_DOCUMENTO", "PRIMER NOMBRE", "PROGRAMA", "FECHA_GRADO"]
    for col in columnas_esperadas:
        if col not in df.columns:
            errores.append(ErrorFila(fila=0, columna=col, error="Falta columna obligatoria"))

    # Si faltan columnas estructurales, paramos el análisis
    if errores:
        return CargaResponse(mensaje="El archivo no tiene el formato correcto", errores=errores)

    # Limpiar datos: Quitar espacios en blanco
    df.columns = df.columns.str.strip()

    # REGLA DE LIMPIEZA: Eliminar filas basura del final del Excel
    # Reemplazar celdas con solo espacios por NaN
    import numpy as np
    df.replace(r'^\s*$', np.nan, regex=True, inplace=True)
    
    # Si la fila no tiene ni Cdula ni Programa, es casi seguro una fila de totales o basura
    df.dropna(subset=['NUMERO_DOCUMENTO', 'PROGRAMA'], how='all', inplace=True)


    

    total_inicial = len(df)

    # REGLA DE NEGOCIO: DOBLE TITULACIÓN
    # 1. Convertir FECHA_GRADO a tipo Fecha (DateTime) para poder comparar
    df['FECHA_GRADO'] = pd.to_datetime(df['FECHA_GRADO'], errors='coerce')
    
    # 2. Ordenar por Cédula y luego por Fecha de Grado (de la más antigua a la más reciente)

    # 2. Separar anonimos de identificados para no borrar anonimos por error
    df_con_cedula = df.dropna(subset=['NUMERO_DOCUMENTO'])
    df_anonimos = df[df['NUMERO_DOCUMENTO'].isna()]

    # 3. Ordenar y eliminar duplicados SOLO en los que tienen cedula
    df_con_cedula = df_con_cedula.sort_values(by=['NUMERO_DOCUMENTO', 'FECHA_GRADO'])
    df_con_cedula = df_con_cedula.drop_duplicates(subset=['NUMERO_DOCUMENTO'], keep='last')
    
    # 4. Volver a unir
    df = pd.concat([df_con_cedula, df_anonimos], ignore_index=True)
    total_final = len(df)
    casos_resueltos = total_inicial - total_final

    # Guardar en Base de Datos MySQL
    
    import numpy as np

    # Limpiar NaN de Pandas para que sean compatibles con JSON/SQLAlchemy
    df = df.replace({np.nan: None})

    # Extraemos la sede del token JWT
    sede_coordinador = current_user.get('sede_id') or 1

    for index, row in df.iterrows():
        # Manejo de Cdulas vacas (Annimos)
        is_empty_doc = pd.isna(row.get('NUMERO_DOCUMENTO')) or str(row.get('NUMERO_DOCUMENTO')).strip() == ''
        
        doc = None
        if not is_empty_doc:
            doc = str(row.get('NUMERO_DOCUMENTO'))
            if doc.endswith('.0'):
                doc = doc[:-2]
                
        # 1. Crear o Actualizar al Egresado SOLO si hay cdula
        if doc:
            egresado = db.query(Egresado).filter(Egresado.numero_documento == doc).first()
            if not egresado:
                
                # Manejo de Nombres vacos o sin segundo nombre
                p_nombre = str(row.get('PRIMER NOMBRE', '')) if not pd.isna(row.get('PRIMER NOMBRE')) else "Sin Nombre"
                p_apellido = str(row.get('PRIMER_APELLIDO', '')) if not pd.isna(row.get('PRIMER_APELLIDO')) else ""
                prog = str(row.get('PROGRAMA', '')) if not pd.isna(row.get('PROGRAMA')) else "Sin Programa"
                
                egresado = Egresado(
                    numero_documento=doc,
                    primer_nombre=p_nombre,
                    primer_apellido=p_apellido,
                    programa=prog,
                    fecha_grado=row.get('FECHA_GRADO') if pd.notnull(row.get('FECHA_GRADO')) else None
                )
                db.add(egresado)
            else:
                # Actualizamos fecha de grado si es mas reciente
                if row.get('FECHA_GRADO') and pd.notnull(row.get('FECHA_GRADO')):
                    if not egresado.fecha_grado or row.get('FECHA_GRADO') > egresado.fecha_grado:
                        egresado.fecha_grado = row.get('FECHA_GRADO')
                        
            db.commit() # Aseguramos que el egresado exista para la llave foranea

        
        # 2. Guardar la medición con todas sus respuestas en JSON
        # Convertimos las fechas a string para el JSON
        respuestas_dict = row.to_dict()
        if isinstance(respuestas_dict.get('FECHA_GRADO'), pd.Timestamp):
            respuestas_dict['FECHA_GRADO'] = respuestas_dict['FECHA_GRADO'].strftime('%Y-%m-%d %H:%M:%S')

        medicion = Medicion(
            egresado_documento=doc,
            momento=momento,
            anio=anio,
            sede_id=sede_coordinador,
            respuestas=respuestas_dict
        )
        db.add(medicion)
        
    db.commit()

    mensaje_exito = f"Archivo procesado exitosamente. Se guardaron {total_final} egresados."
    if casos_resueltos > 0:
        mensaje_exito += f" Se detectaron y resolvieron automáticamente {casos_resueltos} casos de Doble Titulación (se dejó la fecha más reciente)."

    return CargaResponse(mensaje=mensaje_exito, errores=[])







@router.get("/historial")
def get_historial(db: Session = Depends(get_db), current_user: dict = Depends(get_current_user)):
    from sqlalchemy import func
    query = db.query(Medicion.momento, Medicion.anio, func.count(Medicion.id))
    if current_user.get('rol') == 'Coordinador_Sede':
        query = query.filter(Medicion.sede_id == current_user.get('sede_id'))
    resultados = query.group_by(Medicion.momento, Medicion.anio).all()
    
    historial = []
    for momento, anio, cantidad in resultados:
        # Para datos antiguos que no tenían año, mostramos N/A
        anio_str = anio if anio else "N/A"
        historial.append({
            "momento": momento,
            "anio": anio,
            "nombre": f"Momento {momento} - {anio_str}",
            "registros": cantidad,
            "estado": "Procesado"
        })
    return historial

@router.delete("/momento/{momento}/{anio}")
def eliminar_momento(momento: int, anio: str, db: Session = Depends(get_db), current_user: dict = Depends(get_current_user)):
    if current_user.get('rol') == 'Coordinador_Sede':
        # Validar que no borre algo de otra sede? Realmente al borrar vamos a filtrar por sede
        pass
    # Eliminar todas las encuestas de ese momento
    if anio == "null" or anio == "N/A" or anio == "None":
        (db.query(Medicion).filter(Medicion.momento == momento, Medicion.anio.is_(None))
       .filter(Medicion.sede_id == current_user.get('sede_id') if current_user.get('rol') == 'Coordinador_Sede' else True)
       .delete(synchronize_session=False))
    else:
        (db.query(Medicion).filter(Medicion.momento == momento, Medicion.anio == int(anio))
       .filter(Medicion.sede_id == current_user.get('sede_id') if current_user.get('rol') == 'Coordinador_Sede' else True)
       .delete(synchronize_session=False))
    db.commit()
    
    # Opcional: Eliminar egresados huérfanos que ya no tengan ninguna medición
    from sqlalchemy import text
    db.execute(text("DELETE FROM egresados WHERE numero_documento NOT IN (SELECT egresado_documento FROM mediciones)"))
    db.commit()
    
    return {"mensaje": f"Momento {momento} eliminado correctamente."}









