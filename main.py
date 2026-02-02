from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routes.subject import router as subjects_router
from routes.axis import router as axes_router
from routes.program import router as programs_router
from routes.stage import router as stages_router
from routes.activity_type import router as activity_types_router
from routes.activity import router as activities_router
from routes.exercise import router as exercises_router
from routes.user_activities import router as user_activities_router
from routes import auth

app = FastAPI(
    title="Kora API",
    description="API para gestión de materias y programas",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include all routers
app.include_router(subjects_router)
app.include_router(axes_router)
app.include_router(programs_router)
app.include_router(stages_router)
app.include_router(activity_types_router)
app.include_router(activities_router)
app.include_router(exercises_router)
app.include_router(user_activities_router)
app.include_router(auth.router)

@app.get("/")
def read_root():
    return {
        "message": "Welcome to Kora API",
        "endpoints": {
            "subjects": "/subjects",
            "axes": "/axes",
            "programs": "/programs",
            "stages": "/stages",
            "activity_types": "/activity-types",
            "activities": "/activities",
            "exercises": "/exercises",
            "user_activities": "/users/me/activities",
            "docs": "/docs"
        }
    }

@app.get("/health")
def health_check():
    return {"status": "healthy"}


