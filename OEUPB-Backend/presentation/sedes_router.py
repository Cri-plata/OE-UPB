from typing import List

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session

from application.auth_service import get_current_user
from domain.models import Sede
from infrastructure.database import get_db
from presentation.errores import RESPUESTAS_PROTEGIDAS

router = APIRouter(prefix="/api/sedes", tags=["Sedes"], responses=RESPUESTAS_PROTEGIDAS)


class SedeResponse(BaseModel):
    id: int
    codigo: str
    nombre: str

    class Config:
        from_attributes = True


@router.get("/", response_model=List[SedeResponse])
def listar_sedes(
    db: Session = Depends(get_db),
    _current_user: dict = Depends(get_current_user),
):
    return db.query(Sede).filter(Sede.activa.is_(True)).order_by(Sede.id).all()
