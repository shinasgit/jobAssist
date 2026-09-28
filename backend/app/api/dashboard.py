from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from datetime import datetime, timezone, timedelta
from typing import List

from app.database.database import get_db
from app.database import models
from app.schemas.dashboard import DashboardResponse

router = APIRouter()

@router.get("", response_model=DashboardResponse)
def get_dashboard_summary(db: Session = Depends(get_db)):
    total_jobs = db.query(models.Job).count()
    
    seven_days_ago = datetime.now(timezone.utc) - timedelta(days=7)
    new_jobs = db.query(models.Job).filter(models.Job.discovered_at >= seven_days_ago).count()
    
    saved_jobs_count = db.query(models.SavedJob).count()
    applications_count = db.query(models.Application).count()

    # Recent 5 jobs
    recent_jobs = db.query(models.Job).order_by(models.Job.discovered_at.desc()).limit(5).all()
    for job in recent_jobs:
        job.isSaved = len(job.saved_entries) > 0
        job.isApplied = len(job.applications) > 0

    # Recent 5 saved jobs
    recent_saved = db.query(models.SavedJob).order_by(models.SavedJob.saved_at.desc()).limit(5).all()
    for sj in recent_saved:
        if sj.job:
            sj.job.isSaved = True
            sj.job.isApplied = len(sj.job.applications) > 0

    # Recent 5 applications
    recent_apps = db.query(models.Application).order_by(models.Application.updated_at.desc()).limit(5).all()
    for app in recent_apps:
        if app.job:
            app.job.isSaved = len(app.job.saved_entries) > 0
            app.job.isApplied = True

    return DashboardResponse(
        total_jobs=total_jobs,
        new_jobs=new_jobs,
        saved_jobs=saved_jobs_count,
        applications=applications_count,
        recent_jobs=recent_jobs,
        recent_saved_jobs=recent_saved,
        recent_applications=recent_apps
    )
