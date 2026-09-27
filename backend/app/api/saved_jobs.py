from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from typing import List

from app.database.database import get_db
from app.database import models
from app.schemas.saved_job import SavedJobResponse

router = APIRouter()

@router.get("", response_model=List[SavedJobResponse])
def get_saved_jobs(db: Session = Depends(get_db)):
    saved_jobs = db.query(models.SavedJob).all()
    return saved_jobs

@router.post("/{job_id}")
def save_job(job_id: int, db: Session = Depends(get_db)):
    # Check if job exists
    job = db.query(models.Job).filter(models.Job.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
        
    # Check if already saved
    existing = db.query(models.SavedJob).filter(models.SavedJob.job_id == job_id).first()
    if existing:
        return {"success": True, "job_id": job_id, "saved": True, "message": "Already saved"}
        
    # Create saved job
    saved_job = models.SavedJob(job_id=job_id)
    db.add(saved_job)
    try:
        db.commit()
        return {"success": True, "job_id": job_id, "saved": True}
    except IntegrityError:
        db.rollback()
        return {"success": True, "job_id": job_id, "saved": True, "message": "Already saved"}

@router.delete("/{job_id}", status_code=status.HTTP_204_NO_CONTENT)
def remove_saved_job(job_id: int, db: Session = Depends(get_db)):
    saved_job = db.query(models.SavedJob).filter(models.SavedJob.job_id == job_id).first()
    if not saved_job:
        raise HTTPException(status_code=404, detail="Saved job not found")
        
    db.delete(saved_job)
    db.commit()
