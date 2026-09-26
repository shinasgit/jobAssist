from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from typing import List

from app.database.database import get_db
from app.database import models
from app.schemas.job import JobCreate, JobResponse

router = APIRouter()

@router.get("", response_model=List[JobResponse])
def get_jobs(db: Session = Depends(get_db)):
    jobs = db.query(models.Job).all()
    return jobs

@router.get("/{job_id}", response_model=JobResponse)
def get_job(job_id: int, db: Session = Depends(get_db)):
    job = db.query(models.Job).filter(models.Job.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    return job

@router.post("", response_model=JobResponse, status_code=status.HTTP_201_CREATED)
def create_job(job: JobCreate, db: Session = Depends(get_db)):
    db_job = models.Job(**job.model_dump())
    db.add(db_job)
    try:
        db.commit()
        db.refresh(db_job)
        return db_job
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=409, 
            detail="Duplicate job (source + source_url combination already exists)"
        )

@router.delete("/{job_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_job(job_id: int, db: Session = Depends(get_db)):
    job = db.query(models.Job).filter(models.Job.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    db.delete(job)
    db.commit()

from pydantic import BaseModel
from typing import Optional

class JobSearchRequest(BaseModel):
    keyword: str
    location: Optional[str] = None
    experience: Optional[str] = None
    remote_type: Optional[str] = None

@router.post("/search")
def search_jobs(params: JobSearchRequest):
    return {
        "message": "Search parameters received successfully. Scraping will be added in Phase 5.",
        "params": params.model_dump()
    }
