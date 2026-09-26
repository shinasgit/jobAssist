from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime

class Profile(BaseModel):
    name: str = ""
    email: str = ""
    phone: str = ""
    location: str = ""
    linkedin_url: str = ""
    github_url: str = ""
    portfolio_url: str = ""
    
    current_role: str = ""
    target_roles: List[str] = []
    experience_level: str = ""
    preferred_locations: List[str] = []
    remote_preference: str = ""
    expected_salary: str = ""
    notice_period: str = ""
    
    skills_programming: List[str] = []
    skills_frameworks: List[str] = []
    skills_ai_ml: List[str] = []
    skills_databases: List[str] = []
    skills_cloud: List[str] = []
    skills_tools: List[str] = []
    skills_other: List[str] = []
    
    education: List[Dict[str, str]] = []
    projects: List[Dict[str, str]] = []

class Job(BaseModel):
    id: str
    title: str
    companyName: str
    location: Optional[str] = None
    remoteType: Optional[str] = None
    description: str
    requirements: List[str] = []
    responsibilities: List[str] = []
    skills: List[str] = []
    salaryMin: Optional[int] = None
    salaryMax: Optional[int] = None
    salaryCurrency: Optional[str] = "$"
    employmentType: Optional[str] = None
    source: str
    sourceUrl: str
    postedAt: Optional[str] = None
    discoveredAt: str
    isSaved: bool = False
    
class Application(BaseModel):
    id: str
    jobId: str
    jobTitle: str
    companyName: str
    resumeId: Optional[str] = None
    coverLetter: Optional[str] = None
    applicationUrl: Optional[str] = None
    status: str = "SAVED"  # SAVED, PREPARING, READY_TO_APPLY, USER_REVIEW, APPLIED, INTERVIEW, OFFER, REJECTED, WITHDRAWN
    notes: Optional[str] = ""
    createdAt: str
    updatedAt: str
