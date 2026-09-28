from pydantic import BaseModel, ConfigDict
from typing import Optional
from datetime import datetime
from app.schemas.job import JobResponse

class ApplicationCreate(BaseModel):
    notes: Optional[str] = None

class ApplicationUpdate(BaseModel):
    status: Optional[str] = None
    notes: Optional[str] = None

class ApplicationResponse(BaseModel):
    id: int
    job_id: int
    status: str
    notes: Optional[str] = None
    applied_at: Optional[datetime] = None
    updated_at: datetime
    job: Optional[JobResponse] = None

    model_config = ConfigDict(from_attributes=True)
