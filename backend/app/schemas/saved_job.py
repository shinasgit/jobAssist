from pydantic import BaseModel, ConfigDict
from typing import Optional
from datetime import datetime
from .job import JobResponse

class SavedJobResponse(BaseModel):
    id: int
    job_id: int
    saved_at: datetime
    job: JobResponse
    
    model_config = ConfigDict(from_attributes=True)
