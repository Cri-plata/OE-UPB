from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from presentation.auth_router import router as auth_router
from presentation.usuarios_router import router as usuarios_router
from presentation.carga_router import router as carga_router
from presentation.reportes_router import router as reportes_router

app = FastAPI(
    title="OE UPB - Observatorio de Egresados",
    description="API RESTful aplicando Clean Architecture para el procesamiento de egresados UPB.",
    version="1.0.0"
)

# Configuración de CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:4200"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Registrar rutas
app.include_router(auth_router)
app.include_router(usuarios_router)
app.include_router(carga_router)
app.include_router(reportes_router)

@app.get("/")
def root():
    return {"mensaje": "El Backend de OE UPB está funcionando correctamente."}




