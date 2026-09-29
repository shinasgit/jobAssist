from pydantic import BaseModel, ConfigDict
from typing import List
from app.schemas.job import JobResponse
from app.schemas.saved_job import SavedJobResponse
from app.schemas.application import ApplicationResponse

class DashboardResponse(BaseModel):
    total_jobs: int
    new_jobs: int
    mnc_jobs: int = 0
    startup_jobs: int = 0
    it_tech_jobs: int = 0
    remote_jobs: int = 0
    saved_jobs: int
    applications: int
    recent_jobs: List[JobResponse] = []
    recent_saved_jobs: List[SavedJobResponse] = []
    recent_applications: List[ApplicationResponse] = []


    model_config = ConfigDict(from_attributes=True)
