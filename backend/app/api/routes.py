from fastapi import APIRouter
import uuid
from datetime import datetime

from app.schemas.models import Profile, Job, Application

router = APIRouter()

# --- PROFILE ---
@router.get("/profile")
def read_profile():
    return {"success": True, "data": Profile().model_dump()}

@router.put("/profile")
def write_profile(profile: Profile):
    return {"success": True, "data": profile.model_dump()}



# --- APPLICATIONS (MOCK UNTIL PHASE 2 SQLITE) ---
@router.get("/applications")
def read_applications(status: str | None = None):
    return {"success": True, "data": []}

@router.post("/applications")
def add_application(job_id: str):
    new_app = Application(
        id=str(uuid.uuid4()),
        jobId=job_id,
        jobTitle="Unknown",
        companyName="Unknown",
        status="SAVED",
        createdAt=datetime.now().isoformat(),
        updatedAt=datetime.now().isoformat()
    )
    return {"success": True, "data": new_app.model_dump()}
