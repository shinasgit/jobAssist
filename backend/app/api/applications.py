from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from typing import List, Optional
from datetime import datetime, timezone

from app.database.database import get_db
from app.database import models
from app.schemas.application import ApplicationCreate, ApplicationUpdate, ApplicationResponse

router = APIRouter()

@router.get("", response_model=List[ApplicationResponse])
def get_applications(db: Session = Depends(get_db)):
    applications = db.query(models.Application).order_by(models.Application.updated_at.desc()).all()
    for app in applications:
        if app.job:
            app.job.isSaved = len(app.job.saved_entries) > 0
            app.job.isApplied = True
    return applications

@router.get("/{job_id}", response_model=ApplicationResponse)
def get_application_by_job(job_id: int, db: Session = Depends(get_db)):
    app = db.query(models.Application).filter(models.Application.job_id == job_id).first()
    if not app:
        # Check if ID passed was Application.id
        app = db.query(models.Application).filter(models.Application.id == job_id).first()

    if not app:
        raise HTTPException(status_code=404, detail="Application not found")

    if app.job:
        app.job.isSaved = len(app.job.saved_entries) > 0
        app.job.isApplied = True
    return app

@router.post("/{job_id}", response_model=ApplicationResponse)
def create_application(job_id: int, body: Optional[ApplicationCreate] = None, db: Session = Depends(get_db)):
    # Check if job exists
    job = db.query(models.Job).filter(models.Job.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    # Check if application already exists
    existing = db.query(models.Application).filter(models.Application.job_id == job_id).first()
    if existing:
        raise HTTPException(
            status_code=409,
            detail="Application record already exists for this job"
        )

    now = datetime.now(timezone.utc)
    notes = body.notes if body else None

    app_record = models.Application(
        job_id=job_id,
        status="APPLIED",
        notes=notes,
        applied_at=now,
        updated_at=now
    )
    db.add(app_record)
    try:
        db.commit()
        db.refresh(app_record)
        if app_record.job:
            app_record.job.isSaved = len(app_record.job.saved_entries) > 0
            app_record.job.isApplied = True
        return app_record
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=409,
            detail="Application record already exists for this job"
        )

@router.patch("/{job_id}", response_model=ApplicationResponse)
def update_application(job_id: int, body: ApplicationUpdate, db: Session = Depends(get_db)):
    app = db.query(models.Application).filter(models.Application.job_id == job_id).first()
    if not app:
        app = db.query(models.Application).filter(models.Application.id == job_id).first()

    if not app:
        raise HTTPException(status_code=404, detail="Application not found")

    if body.status is not None:
        app.status = body.status
    if body.notes is not None:
        app.notes = body.notes

    app.updated_at = datetime.now(timezone.utc)
    db.commit()
    db.refresh(app)
    if app.job:
        app.job.isSaved = len(app.job.saved_entries) > 0
        app.job.isApplied = True
    return app

@router.delete("/{job_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_application(job_id: int, db: Session = Depends(get_db)):
    app = db.query(models.Application).filter(models.Application.job_id == job_id).first()
    if not app:
        app = db.query(models.Application).filter(models.Application.id == job_id).first()

    if not app:
        raise HTTPException(status_code=404, detail="Application not found")

    db.delete(app)
    db.commit()
