from collections import defaultdict
from typing import List, Literal, Optional

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session

from application.auth_service import require_roles
from presentation.errores import RESPUESTAS_PROTEGIDAS
from application.indicadores import estado_laboral
from application.medicion_policy import seleccionar_intentos
from application.nlp_service import clasificar, extraer_textos
from domain.models import Egresado, Medicion
from infrastructure.database import get_db

router = APIRouter(prefix="/api/analitica", tags=["Analítica"], responses=RESPUESTAS_PROTEGIDAS)


class CompetenciaResponse(BaseModel):
    categoria: str
    frecuencia: int


class AlertaResponse(BaseModel):
    tipo: Literal["empleabilidad", "texto_abierto"]
    programa: str
    momento: Optional[int] = None
    severidad: Literal["media", "alta"]
    mensaje: str
    valor: float
    muestra: int


# ANA-02: criterios de alerta. Solo momentos de seguimiento: en M0 los graduandos
# que aún estudian no representan un problema de inserción laboral.
MOMENTOS_SEGUIMIENTO = (1, 5)
MUESTRA_MINIMA_ALERTA = 5
UMBRAL_EMPLEABILIDAD_MEDIA = 70.0
UMBRAL_EMPLEABILIDAD_ALTA = 50.0
MINIMO_TEXTOS_NEGATIVOS = 3


def alertas_de_programas(empleo: dict, textos: dict) -> list[dict]:
    """Aplica los criterios de ANA-02 a los conteos por programa (y momento)."""
    alertas = []
    for (programa, momento), valores in sorted(empleo.items()):
        if valores["clasificados"] < MUESTRA_MINIMA_ALERTA:
            continue
        tasa = round(valores["ocupados"] * 100 / valores["clasificados"], 1)
        if tasa < UMBRAL_EMPLEABILIDAD_MEDIA:
            alertas.append({
                "tipo": "empleabilidad", "programa": programa, "momento": momento,
                "severidad": "alta" if tasa < UMBRAL_EMPLEABILIDAD_ALTA else "media",
                "mensaje": f"Empleabilidad del {tasa} % en el momento {momento}, inferior al {UMBRAL_EMPLEABILIDAD_MEDIA:g} %.",
                "valor": tasa, "muestra": valores["clasificados"],
            })
    for programa, valores in sorted(textos.items()):
        if valores["textos"] >= MUESTRA_MINIMA_ALERTA and valores["negativos"] >= MINIMO_TEXTOS_NEGATIVOS:
            alertas.append({
                "tipo": "texto_abierto", "programa": programa, "momento": None, "severidad": "media",
                "mensaje": "Se repite un patrón negativo de inserción laboral en textos anonimizados.",
                "valor": float(valores["negativos"]), "muestra": valores["textos"],
            })
    return alertas


class AnaliticaResponse(BaseModel):
    textos_analizados: int
    competencias: List[CompetenciaResponse]
    alertas: List[AlertaResponse]


@router.get("/resumen", response_model=AnaliticaResponse)
def resumen(db: Session = Depends(get_db), current_user: dict = Depends(require_roles("Coordinador_Sede"))):
    filas = db.query(Medicion, Egresado).join(Egresado, Medicion.egresado_documento == Egresado.numero_documento).filter(Medicion.sede_id == current_user["sede_id"]).all()
    competencias = defaultdict(int)
    empleo = defaultdict(lambda: {"ocupados": 0, "clasificados": 0})
    textos_por_programa = defaultdict(lambda: {"negativos": 0, "textos": 0})
    total_textos = 0
    for medicion, egresado in seleccionar_intentos(filas):
        datos = [egresado.numero_documento, egresado.primer_nombre, egresado.primer_apellido or ""]
        textos = extraer_textos(medicion.respuestas or {}, datos)
        conteo, negativos = clasificar(textos)
        total_textos += len(textos)
        for categoria, frecuencia in conteo.items():
            competencias[categoria] += frecuencia
        programa = egresado.programa or "Sin programa"
        estado = estado_laboral(medicion.respuestas)
        if estado is not None and medicion.momento in MOMENTOS_SEGUIMIENTO:
            empleo[(programa, medicion.momento)]["clasificados"] += 1
            empleo[(programa, medicion.momento)]["ocupados"] += estado in ("empleado", "independiente")
        textos_por_programa[programa]["negativos"] += negativos
        textos_por_programa[programa]["textos"] += len(textos)
    alertas = alertas_de_programas(empleo, textos_por_programa)
    return {"textos_analizados": total_textos, "competencias": [{"categoria": k, "frecuencia": v} for k, v in sorted(competencias.items(), key=lambda item: (-item[1], item[0]))], "alertas": alertas}
