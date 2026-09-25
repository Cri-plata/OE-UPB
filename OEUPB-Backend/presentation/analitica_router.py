from collections import defaultdict
from typing import List

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session

from application.auth_service import require_roles
from application.medicion_policy import seleccionar_intentos
from application.nlp_service import clasificar, extraer_textos
from domain.models import Egresado, Medicion
from infrastructure.database import get_db

router = APIRouter(prefix="/api/analitica", tags=["Analítica"])


class CompetenciaResponse(BaseModel):
    categoria: str
    frecuencia: int


class AlertaResponse(BaseModel):
    tipo: str
    programa: str
    severidad: str
    mensaje: str
    valor: float
    muestra: int


class AnaliticaResponse(BaseModel):
    textos_analizados: int
    competencias: List[CompetenciaResponse]
    alertas: List[AlertaResponse]


def _respuesta_empleo(respuestas: dict):
    for clave, valor in (respuestas or {}).items():
        if "actividad remunerada" in clave.lower() or "situacion_actual" in clave.lower():
            normal = str(valor).strip().upper()
            if normal in {"SI", "SÍ", "NO"}:
                return normal in {"SI", "SÍ"}
    return None


@router.get("/resumen", response_model=AnaliticaResponse)
def resumen(db: Session = Depends(get_db), current_user: dict = Depends(require_roles("Coordinador_Sede"))):
    filas = db.query(Medicion, Egresado).join(Egresado, Medicion.egresado_documento == Egresado.numero_documento).filter(Medicion.sede_id == current_user["sede_id"]).all()
    competencias = defaultdict(int)
    estadisticas = defaultdict(lambda: {"empleados": 0, "validos": 0, "negativos": 0, "textos": 0})
    total_textos = 0
    for medicion, egresado in seleccionar_intentos(filas):
        datos = [egresado.numero_documento, egresado.primer_nombre, egresado.primer_apellido or ""]
        textos = extraer_textos(medicion.respuestas or {}, datos)
        conteo, negativos = clasificar(textos)
        total_textos += len(textos)
        for categoria, frecuencia in conteo.items():
            competencias[categoria] += frecuencia
        programa = egresado.programa or "Sin programa"
        empleo = _respuesta_empleo(medicion.respuestas or {})
        if empleo is not None:
            estadisticas[programa]["validos"] += 1
            estadisticas[programa]["empleados"] += int(empleo)
        estadisticas[programa]["negativos"] += negativos
        estadisticas[programa]["textos"] += len(textos)
    alertas = []
    for programa, valores in estadisticas.items():
        if valores["validos"] >= 3:
            tasa = round(valores["empleados"] * 100 / valores["validos"], 1)
            if tasa < 70:
                alertas.append({"tipo": "empleabilidad", "programa": programa, "severidad": "alta" if tasa < 50 else "media", "mensaje": "Tasa descriptiva de empleabilidad inferior al 70 %.", "valor": tasa, "muestra": valores["validos"]})
        if valores["negativos"] >= 3:
            alertas.append({"tipo": "texto_abierto", "programa": programa, "severidad": "media", "mensaje": "Se repite un patrón negativo de inserción laboral en textos anonimizados.", "valor": float(valores["negativos"]), "muestra": valores["textos"]})
    return {"textos_analizados": total_textos, "competencias": [{"categoria": k, "frecuencia": v} for k, v in sorted(competencias.items(), key=lambda item: (-item[1], item[0]))], "alertas": alertas}
