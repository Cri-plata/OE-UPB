from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.orm import Session
from sqlalchemy import func
from domain.models import AuditoriaEgresado, Carga, Egresado, EgresadoSede, EventoEliminacionCarga, Medicion, Sede, Usuario
from infrastructure.database import get_db
from application.auth_service import get_current_user
from presentation.errores import RESPUESTAS_PROTEGIDAS, errores
from application.documentos import MENSAJE_INVALIDO, es_documento_valido, normalizar_documento
from application.programas import limpiar_nombre_programa
import pandas as pd
import io
import hashlib
from pydantic import BaseModel, Field
from typing import List, Optional

router = APIRouter(prefix="/api/carga", tags=["Carga de Datos"], responses=RESPUESTAS_PROTEGIDAS)

MOMENTOS_PERMITIDOS = {0, 1, 5}
ANIO_MINIMO = 1900
ANIO_MAXIMO = 2200
TAMANO_MAXIMO_BYTES = 25 * 1024 * 1024
FILAS_MAXIMAS = 50_000


def validar_coordinador_con_sede(current_user: dict) -> int:
    if current_user.get("rol") != "Coordinador_Sede":
        raise HTTPException(
            status_code=403,
            detail="Solo un Coordinador de Sede puede administrar cargas",
        )

    sede_id = current_user.get("sede_id")
    if sede_id is None:
        raise HTTPException(
            status_code=403,
            detail="El Coordinador de Sede no tiene una sede válida asignada",
        )
    return sede_id


def validar_momento(momento: int) -> None:
    if momento not in MOMENTOS_PERMITIDOS:
        raise HTTPException(
            status_code=422,
            detail="El momento debe ser 0, 1 o 5",
        )


def validar_anio(anio: int) -> None:
    if not ANIO_MINIMO <= anio <= ANIO_MAXIMO:
        raise HTTPException(
            status_code=422,
            detail=f"El año de grado debe estar entre {ANIO_MINIMO} y {ANIO_MAXIMO}",
        )


def bloquear_sede(db: Session, sede_id: int) -> None:
    """Serializa las operaciones de carga de una sede (SELECT ... FOR UPDATE en MySQL)."""
    db.query(Sede).filter(Sede.id == sede_id).with_for_update().one()

class ErrorFila(BaseModel):
    fila: int
    columna: str
    error: str

class DetalleCargaRechazada(BaseModel):
    mensaje: str
    errores: List[ErrorFila]


class CargaRechazadaResponse(BaseModel):
    """Cuerpo de un 422 de carga: el archivo completo se rechaza (RN-20)."""
    detail: DetalleCargaRechazada


def rechazar_carga(mensaje: str, errores: List[ErrorFila]) -> HTTPException:
    return HTTPException(
        status_code=422,
        detail={"mensaje": mensaje, "errores": [error.model_dump() for error in errores]},
    )


class CargaResponse(BaseModel):
    mensaje: str
    errores: List[ErrorFila] = []
    carga_id: Optional[int] = None
    version: Optional[int] = None
    estado: Optional[str] = None
    registros: Optional[int] = None


class HistorialCargaItem(BaseModel):
    id: int
    momento: int
    anio: int
    nombre: str
    nombre_archivo: str
    fecha_carga: str
    version: int
    registros: int
    estado: str


class MensajeResponse(BaseModel):
    mensaje: str


class EliminarCargaRequest(BaseModel):
    motivo: str = Field(min_length=10, max_length=500)


@router.post(
    "/excel",
    response_model=CargaResponse,
    responses={
        **errores(
            400, 409, 413, 500,
            d400="El archivo no es .xlsx o su contenido no puede leerse",
            d409="El archivo es idéntico a la versión vigente del mismo alcance",
            d413="El archivo supera 25 MB",
        ),
        422: {"model": CargaRechazadaResponse, "description": "Parámetros inválidos o archivo rechazado; incluye el detalle por fila"},
    },
)
async def procesar_excel(
    momento: int = Form(..., description="Momento 0, 1 o 5"),
    anio: int = Form(..., description="Año de grado o cohorte (1900-2200)"),
    file: UploadFile = File(..., description="Archivo Excel en formato .xlsx"),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    sede_coordinador_actual = validar_coordinador_con_sede(current_user)
    validar_momento(momento)
    validar_anio(anio)

    nombre_archivo = (file.filename or "").lower()
    if not nombre_archivo.endswith(".xlsx"):
        raise HTTPException(status_code=400, detail="El único formato permitido es .xlsx")

    # Leer el archivo a la memoria
    contents = await file.read()
    if len(contents) > TAMANO_MAXIMO_BYTES:
        raise HTTPException(status_code=413, detail="El archivo supera el máximo de 25 MB")
    hash_archivo = hashlib.sha256(contents).hexdigest()
    
    try:
        # Usar Pandas para leer el Excel
        # El documento se lee como texto para no perder ceros ni letras.
        df = pd.read_excel(io.BytesIO(contents), dtype={"NUMERO_DOCUMENTO": str})
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
        raise rechazar_carga("El archivo no tiene el formato correcto", errores)

    # Limpiar datos: Quitar espacios en blanco
    df.columns = df.columns.str.strip()

    # REGLA DE LIMPIEZA: Eliminar filas basura del final del Excel
    # Reemplazar celdas con solo espacios por NaN
    import numpy as np
    df.replace(r'^\s*$', np.nan, regex=True, inplace=True)
    
    # Si la fila no tiene ni Cdula ni Programa, es casi seguro una fila de totales o basura
    df.dropna(subset=['NUMERO_DOCUMENTO', 'PROGRAMA'], how='all', inplace=True)

    if len(df) > FILAS_MAXIMAS:
        raise rechazar_carga(
            f"El archivo supera el máximo de {FILAS_MAXIMAS} filas",
            [ErrorFila(fila=0, columna="*", error=f"{len(df)} filas con datos")],
        )

    # ETL-01: normalización única del documento; un documento inválido rechaza el archivo.
    df['NUMERO_DOCUMENTO'] = df['NUMERO_DOCUMENTO'].map(normalizar_documento)
    for indice, documento in df['NUMERO_DOCUMENTO'].items():
        if documento is not None and not es_documento_valido(documento):
            # +2: encabezado en la fila 1 de Excel e índice basado en cero.
            errores.append(ErrorFila(fila=int(indice) + 2, columna="NUMERO_DOCUMENTO", error=MENSAJE_INVALIDO))
    if errores:
        raise rechazar_carga(f"El archivo contiene {len(errores)} documentos inválidos; no se guardó ninguna fila", errores[:200])


    

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

    try:
        actor = db.query(Usuario).filter(
            Usuario.correo == current_user.get("correo")
        ).first()
        if actor is None:
            raise HTTPException(status_code=403, detail="El usuario autenticado no existe")

        bloquear_sede(db, sede_coordinador_actual)
        consulta_alcance = db.query(Carga).filter(
            Carga.sede_id == sede_coordinador_actual,
            Carga.momento == momento,
            Carga.anio_grado == anio,
        )
        ultima_carga = consulta_alcance.order_by(Carga.version.desc()).first()
        carga_anterior = (
            consulta_alcance.filter(Carga.estado == "vigente")
            .order_by(Carga.version.desc())
            .first()
        )
        ultima_version_eliminada = db.query(func.max(EventoEliminacionCarga.version)).filter(
            EventoEliminacionCarga.sede_id == sede_coordinador_actual,
            EventoEliminacionCarga.momento == momento,
            EventoEliminacionCarga.anio_grado == anio,
        ).scalar() or 0
        if carga_anterior and carga_anterior.hash_archivo == hash_archivo:
            raise HTTPException(
                status_code=409,
                detail="El archivo es idéntico a la versión vigente; no se creó una nueva versión",
            )
        documentos_protegidos = {
            documento for (documento,) in db.query(AuditoriaEgresado.egresado_documento).distinct().all()
        }
        registros_protegidos = 0
        version = max(ultima_carga.version if ultima_carga else 0, ultima_version_eliminada) + 1

        nueva_carga = Carga(
            nombre_archivo=file.filename or "carga.xlsx",
            hash_archivo=hash_archivo,
            usuario_id=actor.id,
            sede_id=sede_coordinador_actual,
            momento=momento,
            anio_grado=anio,
            estado="procesando",
            version=version,
            registros=0,
            reemplaza_carga_id=carga_anterior.id if carga_anterior else None,
        )
        db.add(nueva_carga)
        db.flush()

        if carga_anterior:
            db.query(Medicion).filter(
                Medicion.carga_id == carga_anterior.id
            ).delete(synchronize_session=False)
            carga_anterior.estado = "reemplazada"

        for _, row in df.iterrows():
            is_empty_doc = (
                pd.isna(row.get("NUMERO_DOCUMENTO"))
                or str(row.get("NUMERO_DOCUMENTO")).strip() == ""
            )

            doc = None if is_empty_doc else row.get("NUMERO_DOCUMENTO")

            if doc:
                egresado = db.query(Egresado).filter(
                    Egresado.numero_documento == doc
                ).first()
                if not egresado:
                    p_nombre = (
                        str(row.get("PRIMER NOMBRE", ""))
                        if not pd.isna(row.get("PRIMER NOMBRE"))
                        else "Sin Nombre"
                    )
                    p_apellido = (
                        str(row.get("PRIMER_APELLIDO", ""))
                        if not pd.isna(row.get("PRIMER_APELLIDO"))
                        else ""
                    )
                    programa = (
                        limpiar_nombre_programa(row.get("PROGRAMA"))
                        if not pd.isna(row.get("PROGRAMA"))
                        else None
                    ) or "Sin Programa"
                    egresado = Egresado(
                        numero_documento=doc,
                        primer_nombre=p_nombre,
                        primer_apellido=p_apellido,
                        programa=programa,
                        fecha_grado=(
                            row.get("FECHA_GRADO")
                            if pd.notnull(row.get("FECHA_GRADO"))
                            else None
                        ),
                    )
                    db.add(egresado)
                elif doc in documentos_protegidos:
                    # RN-13: una corrección manual auditada prevalece sobre cargas posteriores.
                    registros_protegidos += 1
                elif pd.notnull(row.get("FECHA_GRADO")):
                    if (
                        not egresado.fecha_grado
                        or row.get("FECHA_GRADO") > egresado.fecha_grado
                    ):
                        egresado.fecha_grado = row.get("FECHA_GRADO")

            respuestas_dict = row.to_dict()
            if isinstance(respuestas_dict.get("FECHA_GRADO"), pd.Timestamp):
                respuestas_dict["FECHA_GRADO"] = respuestas_dict[
                    "FECHA_GRADO"
                ].strftime("%Y-%m-%d %H:%M:%S")

            db.add(
                Medicion(
                    carga_id=nueva_carga.id,
                    egresado_documento=doc,
                    momento=momento,
                    anio=anio,
                    sede_id=sede_coordinador_actual,
                    intento=1,
                    respuestas=respuestas_dict,
                )
            )

        nueva_carga.estado = "vigente"
        nueva_carga.registros = total_final
        db.commit()
    except HTTPException:
        db.rollback()
        raise
    except Exception as exc:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail="La carga no pudo persistirse; la versión anterior se conservó",
        ) from exc

    mensaje_exito = f"Archivo procesado exitosamente. Se guardaron {total_final} egresados."
    if casos_resueltos > 0:
        mensaje_exito += f" Se detectaron y resolvieron automáticamente {casos_resueltos} casos de Doble Titulación (se dejó la fecha más reciente)."
    if registros_protegidos > 0:
        mensaje_exito += f" {registros_protegidos} egresados con corrección manual conservaron sus datos personales."

    return CargaResponse(
        mensaje=mensaje_exito,
        errores=[],
        carga_id=nueva_carga.id,
        version=nueva_carga.version,
        estado=nueva_carga.estado,
        registros=nueva_carga.registros,
    )







@router.get(
    "/historial",
    response_model=List[HistorialCargaItem],
    responses=errores(403, d403="El usuario no es coordinador o no tiene sede asignada"),
)
def get_historial(db: Session = Depends(get_db), current_user: dict = Depends(get_current_user)):
    sede_id = validar_coordinador_con_sede(current_user)
    cargas = (
        db.query(Carga)
        .filter(Carga.sede_id == sede_id)
        .order_by(Carga.fecha_carga.desc(), Carga.id.desc())
        .all()
    )

    return [
        {
            "id": carga.id,
            "momento": carga.momento,
            "anio": carga.anio_grado,
            "nombre": f"Momento {carga.momento} - Cohorte {carga.anio_grado}",
            "nombre_archivo": carga.nombre_archivo,
            "fecha_carga": carga.fecha_carga.isoformat(),
            "version": carga.version,
            "registros": carga.registros,
            "estado": carga.estado,
        }
        for carga in cargas
    ]

@router.delete(
    "/archivo/{carga_id}",
    response_model=MensajeResponse,
    responses=errores(
        404, 409, 500,
        d404="La carga no existe dentro de la sede autorizada",
        d409="La carga ya no está vigente o está referenciada por una versión posterior",
    ),
)
def eliminar_carga(
    carga_id: int,
    solicitud: EliminarCargaRequest,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    from sqlalchemy import exists

    sede_id = validar_coordinador_con_sede(current_user)
    carga = (
        db.query(Carga)
        .filter(Carga.id == carga_id, Carga.sede_id == sede_id)
        .first()
    )
    if carga is None:
        raise HTTPException(status_code=404, detail="Carga no encontrada")
    bloquear_sede(db, sede_id)
    db.refresh(carga)
    if carga.estado != "vigente":
        raise HTTPException(status_code=409, detail="La carga ya no está vigente")

    actor = db.query(Usuario).filter(
        Usuario.correo == current_user.get("correo")
    ).first()
    if actor is None:
        raise HTTPException(status_code=403, detail="El usuario autenticado no existe")
    if db.query(Carga).filter(Carga.reemplaza_carga_id == carga.id).first():
        raise HTTPException(
            status_code=409,
            detail="La carga está referenciada por una versión posterior",
        )

    try:
        db.add(EventoEliminacionCarga(
            carga_id_eliminada=carga.id,
            actor_id=actor.id,
            actor_correo=actor.correo,
            sede_id=carga.sede_id,
            momento=carga.momento,
            anio_grado=carga.anio_grado,
            version=carga.version,
            registros=carga.registros,
            nombre_archivo=carga.nombre_archivo,
            hash_archivo=carga.hash_archivo,
            motivo=solicitud.motivo.strip(),
        ))
        db.query(Medicion).filter(Medicion.carga_id == carga.id).delete(
            synchronize_session=False
        )
        db.delete(carga)

        # Solo se eliminan identidades que quedan sin mediciones ni vínculo manual
        # con alguna sede; los registros del directorio manual se conservan.
        db.query(Egresado).filter(
            ~exists().where(
                Medicion.egresado_documento == Egresado.numero_documento
            ),
            ~exists().where(
                EgresadoSede.egresado_documento == Egresado.numero_documento
            ),
        ).delete(synchronize_session=False)
        db.commit()
    except Exception as exc:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail="La carga no pudo eliminarse y no se aplicaron cambios",
        ) from exc

    return {"mensaje": f"Carga {carga_id} eliminada físicamente y evento auditado."}









