from pydantic import BaseModel, ConfigDict
from typing import Optional
from datetime import datetime

class JobBase(BaseModel):
    title: str
    company: Optional[str] = None
    location: Optional[str] = None
    remote_type: Optional[str] = None
    salary: Optional[str] = None
    experience: Optional[str] = None
    employment_type: Optional[str] = None
    description: Optional[str] = None
    source: Optional[str] = None
    source_category: Optional[str] = "IT_TECH"
    source_url: Optional[str] = None
    posted_date: Optional[str] = None


class JobCreate(JobBase):
    pass

class JobResponse(JobBase):
    id: int
    discovered_at: datetime
    isSaved: Optional[bool] = False
    isApplied: Optional[bool] = False
    
    model_config = ConfigDict(from_attributes=True)
