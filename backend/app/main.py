from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.api.routes import router as api_router
from app.api.jobs import router as jobs_router
from app.database.database import engine
from app.database import models

# Create database tables
models.Base.metadata.create_all(bind=engine)

app = FastAPI(
    title=settings.PROJECT_NAME,
    description="Personal Job Finder API",
    version="0.1.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.FRONTEND_URL],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/api/health")
def health_check():
    return {"status": "ok", "project": settings.PROJECT_NAME}

from app.api.saved_jobs import router as saved_jobs_router
from app.api.applications import router as applications_router
from app.api.dashboard import router as dashboard_router
from app.api.settings import router as settings_router

app.include_router(api_router, prefix="/api")
app.include_router(jobs_router, prefix="/api/jobs", tags=["jobs"])
app.include_router(saved_jobs_router, prefix="/api/saved-jobs", tags=["saved_jobs"])
app.include_router(applications_router, prefix="/api/applications", tags=["applications"])
app.include_router(dashboard_router, prefix="/api/dashboard", tags=["dashboard"])
app.include_router(settings_router, prefix="/api/settings", tags=["settings"])
