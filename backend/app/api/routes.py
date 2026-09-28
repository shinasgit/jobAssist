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



# --- APPLICATIONS HANDLED BY APP.API.APPLICATIONS ---
