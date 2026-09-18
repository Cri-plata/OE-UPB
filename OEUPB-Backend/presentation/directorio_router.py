from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import or_, and_, text
from domain.models import Egresado, Medicion
from infrastructure.database import get_db
from application.auth_service import get_current_user
from typing import Optional

router = APIRouter(prefix="/api/directorio", tags=["Directorio"])

@router.get("/tabla")
def obtener_directorio(
    q: Optional[str] = None,
    programa: Optional[str] = None,
    page: int = Query(1, ge=1),
    limit: int = Query(50, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    query = db.query(Egresado)
    if current_user.get('rol') == 'Coordinador_Sede':
        query = query.join(Medicion).filter(Medicion.sede_id == current_user.get('sede_id'))


    # Filtrar por texto libre (Nombre, Apellido o Cdula)
    if q:
        termino = f"%{q}%"
        query = query.filter(
            or_(
                Egresado.numero_documento.like(termino),
                Egresado.primer_nombre.like(termino),
                Egresado.primer_apellido.like(termino)
            )
        )
        
    # Filtrar por programa
    if programa:
        query = query.filter(Egresado.programa == programa)

    total_registros = query.count()
    
    # Paginacin
    offset = (page - 1) * limit
    egresados = query.offset(offset).limit(limit).all()

    # Formatear la salida
    resultados = []
    for e in egresados:
        # Buscar en qu momentos ha participado
        momentos = db.query(Medicion.momento, Medicion.anio).filter(Medicion.egresado_documento == e.numero_documento).all()
        
        historial = [f"M{m.momento} ({m.anio if m.anio else 'N/A'})" for m in momentos]
        
        resultados.append({
            "documento": e.numero_documento,
            "nombre_completo": f"{e.primer_nombre} {e.primer_apellido}".strip(),
            "programa": e.programa,
            "fecha_grado": e.fecha_grado.strftime("%Y-%m-%d") if e.fecha_grado else "N/A",
            "encuestas": ", ".join(historial) if historial else "Ninguna"
        })

    return {
        "total": total_registros,
        "page": page,
        "limit": limit,
        "data": resultados
    }

@router.get("/programas")
def obtener_programas_unicos(db: Session = Depends(get_db), current_user: dict = Depends(get_current_user)):
    query = db.query(Egresado.programa).filter(Egresado.programa != None)
    if current_user.get('rol') == 'Coordinador_Sede':
        query = query.join(Medicion).filter(Medicion.sede_id == current_user.get('sede_id'))
    programas = query.distinct().all()

    return [p[0] for p in programas if p[0]]

@router.get("/perfil/{documento}")
def obtener_perfil_egresado(documento: str, db: Session = Depends(get_db), current_user: dict = Depends(get_current_user)):
    egresado = db.query(Egresado).filter(Egresado.numero_documento == documento).first()
    if not egresado:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="Egresado no encontrado")
        
    med_query = db.query(Medicion).filter(Medicion.egresado_documento == documento)
    if current_user.get('rol') == 'Coordinador_Sede':
        med_query = med_query.filter(Medicion.sede_id == current_user.get('sede_id'))
    mediciones = med_query.order_by(Medicion.momento).all()
    
    if not mediciones and current_user.get('rol') == 'Coordinador_Sede':
        raise HTTPException(status_code=403, detail="No tiene permisos para ver este egresado")

    
    encuestas = []
    for m in mediciones:
        # Extraer variables clave del JSON para la vista rpida
        salario = m.respuestas.get("Cul es su ingreso mensual actual (salario ms comisiones) en Salarios Mnimos Mensuales Legales Vigentes (SMMLV)?") or m.respuestas.get("Ingreso_Mensual") or "No informa"
        empleabilidad = m.respuestas.get("En la actualidad, realiza alguna actividad remunerada?") or m.respuestas.get("Situacion_Actual") or "No informa"
        
        encuestas.append({
            "momento": m.momento,
            "anio": m.anio,
            "empleabilidad": empleabilidad,
            "salario": salario,
            "respuestas_completas": m.respuestas
        })
        
    return {
        "documento": egresado.numero_documento,
        "nombre_completo": f"{egresado.primer_nombre} {egresado.primer_apellido}".strip(),
        "programa": egresado.programa,
        "fecha_grado": egresado.fecha_grado.strftime("%Y-%m-%d") if egresado.fecha_grado else "N/A",
        "encuestas": encuestas
    }
