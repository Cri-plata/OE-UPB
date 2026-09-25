import logging
import os
import time
import uuid

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from sqlalchemy import text

from infrastructure.database import SessionLocal
from presentation.analitica_router import router as analitica_router
from presentation.auth_router import router as auth_router
from presentation.carga_router import router as carga_router
from presentation.directorio_router import router as directorio_router
from presentation.publicaciones_router import router as publicaciones_router
from presentation.reportes_router import router as reportes_router
from presentation.sedes_router import router as sedes_router
from presentation.usuarios_router import router as usuarios_router

app = FastAPI(title="OE UPB - Observatorio de Egresados", description="API RESTful para el procesamiento de egresados UPB.", version="1.0.0")
logging.basicConfig(level=os.getenv("LOG_LEVEL", "INFO"), format="%(asctime)s %(levelname)s %(name)s %(message)s")
logger = logging.getLogger("oeupb.http")
allowed_origins = [origin.strip() for origin in os.getenv("CORS_ALLOWED_ORIGINS", "http://localhost:4200").split(",") if origin.strip()]
app.add_middleware(CORSMiddleware, allow_origins=allowed_origins, allow_credentials=True, allow_methods=["*"], allow_headers=["*"])

for router in (auth_router, usuarios_router, carga_router, reportes_router, directorio_router, sedes_router, publicaciones_router, analitica_router):
    app.include_router(router)


class HealthResponse(BaseModel):
    status: str


@app.middleware("http")
async def request_observability(request: Request, call_next):
    request_id = request.headers.get("X-Request-ID", str(uuid.uuid4()))[:100]
    inicio = time.perf_counter()
    response = await call_next(request)
    response.headers["X-Request-ID"] = request_id
    logger.info("request_id=%s method=%s path=%s status=%s duration_ms=%.2f", request_id, request.method, request.url.path, response.status_code, (time.perf_counter() - inicio) * 1000)
    return response


@app.get("/api/health/live", response_model=HealthResponse, tags=["Operación"])
def liveness():
    return {"status": "ok"}


@app.get("/api/health/ready", response_model=HealthResponse, tags=["Operación"])
def readiness():
    try:
        with SessionLocal() as db:
            db.execute(text("SELECT 1"))
    except Exception as exc:
        logger.error("readiness_failed type=%s", type(exc).__name__)
        raise HTTPException(status_code=503, detail="Base de datos no disponible") from exc
    return {"status": "ok"}


@app.get("/")
def root():
    return {"mensaje": "El Backend de OE UPB está funcionando correctamente."}
