from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.orm import Session
from infrastructure.database import get_db
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

    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    if not file.filename.endswith(('.xlsx', '.xls')):
        raise HTTPException(status_code=400, detail="El archivo debe ser un Excel (.xlsx o .xls)")

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

    # Validar fila por fila (Simulación de reglas de negocio)
    for index, row in df.iterrows():
        fila_real = index + 2 # +2 por el encabezado y porque empieza en 0
        
        # Validación de cédula vacía
        if pd.isna(row.get('NUMERO_DOCUMENTO')):
            errores.append(ErrorFila(fila=fila_real, columna="NUMERO_DOCUMENTO", error="La cédula no puede estar vacía"))

        # Validación de nombre vacío
        if pd.isna(row.get('PRIMER NOMBRE')):
            errores.append(ErrorFila(fila=fila_real, columna="PRIMER NOMBRE", error="El nombre no puede estar vacío"))

    if errores:
        return CargaResponse(mensaje="Se encontraron errores estructurales (vacíos o formato)", errores=errores)

    total_inicial = len(df)

    # REGLA DE NEGOCIO: DOBLE TITULACIÓN
    # 1. Convertir FECHA_GRADO a tipo Fecha (DateTime) para poder comparar
    df['FECHA_GRADO'] = pd.to_datetime(df['FECHA_GRADO'], errors='coerce')
    
    # 2. Ordenar por Cédula y luego por Fecha de Grado (de la más antigua a la más reciente)
    df = df.sort_values(by=['NUMERO_DOCUMENTO', 'FECHA_GRADO'])
    
    # 3. Eliminar duplicados manteniendo solo la ÚLTIMA fila (la fecha más reciente)
    df = df.drop_duplicates(subset=['NUMERO_DOCUMENTO'], keep='last')
    
    total_final = len(df)
    casos_resueltos = total_inicial - total_final

    # Guardar en Base de Datos MySQL
    from domain.models import Egresado, Medicion
    import numpy as np

    # Limpiar NaN de Pandas para que sean compatibles con JSON/SQLAlchemy
    df = df.replace({np.nan: None})

    # Extraemos la sede (hardcodeada a 1 por ahora, luego vendrá del token JWT)
    sede_coordinador = 1

    for index, row in df.iterrows():
        doc = str(row.get('NUMERO_DOCUMENTO'))
        
        # 1. Crear o Actualizar al Egresado
        egresado = db.query(Egresado).filter(Egresado.numero_documento == doc).first()
        if not egresado:
            egresado = Egresado(
                numero_documento=doc,
                primer_nombre=str(row.get('PRIMER NOMBRE', '')),
                primer_apellido=str(row.get('PRIMER_APELLIDO', '')),
                programa=str(row.get('PROGRAMA', '')),
                fecha_grado=row.get('FECHA_GRADO') if pd.notnull(row.get('FECHA_GRADO')) else None
            )
            db.add(egresado)
        else:
            # Actualizamos fecha de grado si es más reciente
            if row.get('FECHA_GRADO') and pd.notnull(row.get('FECHA_GRADO')):
                if not egresado.fecha_grado or row.get('FECHA_GRADO') > egresado.fecha_grado:
                    egresado.fecha_grado = row.get('FECHA_GRADO')
                    egresado.programa = str(row.get('PROGRAMA', ''))

        db.commit() # Aseguramos que el egresado exista para la llave foránea
        
        # 2. Guardar la medición con todas sus respuestas en JSON
        # Convertimos las fechas a string para el JSON
        respuestas_dict = row.to_dict()
        if isinstance(respuestas_dict.get('FECHA_GRADO'), pd.Timestamp):
            respuestas_dict['FECHA_GRADO'] = respuestas_dict['FECHA_GRADO'].strftime('%Y-%m-%d %H:%M:%S')

        medicion = Medicion(
            egresado_documento=doc,
            momento=momento,
            sede_id=sede_coordinador,
            respuestas=respuestas_dict
        )
        db.add(medicion)
        
    db.commit()

    mensaje_exito = f"Archivo procesado exitosamente. Se guardaron {total_final} egresados."
    if casos_resueltos > 0:
        mensaje_exito += f" Se detectaron y resolvieron automáticamente {casos_resueltos} casos de Doble Titulación (se dejó la fecha más reciente)."

    return CargaResponse(mensaje=mensaje_exito, errores=[])






