from fastapi import FastAPI
from routes.materia import router as materias_router
from routes.eje import router as ejes_router
from routes.programa import router as programas_router
from routes.etapa import router as etapas_router
from routes.tipo_actividad import router as tipos_router
from routes.actividad import router as actividades_router
from routes.ejercicio import router as ejercicios_router

app = FastAPI(
    title="Kora API",
    description="API para gestión de materias y programas",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Incluir todos los routers
app.include_router(materias_router)
app.include_router(ejes_router)
app.include_router(programas_router)
app.include_router(etapas_router)
app.include_router(tipos_router)
app.include_router(actividades_router)
app.include_router(ejercicios_router)

@app.get("/")
def read_root():
    return {
        "message": "Bienvenido a Kora API",
        "endpoints": {
            "materias": "/materias",
            "ejes": "/ejes",
            "programas": "/programas",
            "etapas": "/etapas",
            "tipos_actividades": "/tipos-actividades",
            "actividades": "/actividades",
            "ejercicios": "/ejercicios",
            "docs": "/docs"
        }
    }

@app.get("/health")
def health_check():
    return {"status": "healthy"}


