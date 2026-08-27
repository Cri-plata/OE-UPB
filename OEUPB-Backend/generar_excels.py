import pandas as pd
import random
from datetime import datetime, timedelta

def generar_excel(nombre_archivo, num_filas, doble_titulacion=False):
    datos = []
    programas = ['Ingeniería de Sistemas', 'Derecho', 'Psicología', 'Arquitectura', 'Medicina']
    
    for i in range(num_filas):
        cedula = random.randint(1000000000, 1999999999)
        fecha = datetime.now() - timedelta(days=random.randint(100, 2000))
        datos.append({
            'NUMERO_DOCUMENTO': cedula,
            'PRIMER NOMBRE': f'Egresado_{i}',
            'PRIMER_APELLIDO': f'Prueba_{i}',
            'PROGRAMA': random.choice(programas),
            'FECHA_GRADO': fecha.strftime('%Y-%m-%d %H:%M:%S')
        })
        
        # Generar doble titulación a propósito (5% de probabilidad si doble_titulacion es True)
        if doble_titulacion and random.random() < 0.05:
            datos.append({
                'NUMERO_DOCUMENTO': cedula,
                'PRIMER NOMBRE': f'Egresado_{i}',
                'PRIMER_APELLIDO': f'Prueba_{i}',
                'PROGRAMA': random.choice(programas),
                'FECHA_GRADO': (fecha - timedelta(days=365)).strftime('%Y-%m-%d %H:%M:%S') # Fecha más antigua
            })
            
    df = pd.DataFrame(datos)
    path = rf"C:\Users\USUARIO\Documents\U sexto\egresados\{nombre_archivo}.xlsx"
    df.to_excel(path, index=False)
    print(f"Archivo generado: {path} con {len(df)} filas.")

generar_excel('Prueba_Momento_0_Limpio', 50, doble_titulacion=False)
generar_excel('Prueba_Momento_5_Con_Dobles', 120, doble_titulacion=True)
generar_excel('Prueba_Archivo_Masivo', 500, doble_titulacion=True)
