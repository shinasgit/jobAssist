from pydantic import BaseModel, ConfigDict
from typing import List, Optional

class SettingBase(BaseModel):
    keywords: List[str] = ["Junior AI Developer"]
    locations: List[str] = ["Bangalore"]
    experience: Optional[str] = "Fresher"
    remote_type: Optional[str] = "any"
    employment_types: List[str] = ["Full-time"]
    enabled_sources: List[str] = ["himalayas", "remotive", "arbeitnow"]

class SettingUpdate(BaseModel):
    keywords: Optional[List[str]] = None
    locations: Optional[List[str]] = None
    experience: Optional[str] = None
    remote_type: Optional[str] = None
    employment_types: Optional[List[str]] = None
    enabled_sources: Optional[List[str]] = None

class SettingResponse(SettingBase):
    id: int
    model_config = ConfigDict(from_attributes=True)
