import re
from typing import Optional

TECH_KEYWORDS = [
    # AI / ML / Data
    "ai", "artificial intelligence", "generative ai", "genai", "machine learning",
    "deep learning", "data science", "data scientist", "data engineer", "mlops", "llm",
    "prompt engineer", "ai engineer", "ai developer", "generative ai developer",
    "nlp", "computer vision", "ml engineer", "data analyst", "bi developer",
    
    # Software & Development
    "software engineer", "software developer", "application developer", "full stack",
    "fullstack", "frontend", "front-end", "backend", "back-end", "web developer",
    "react", "angular", "vue", "node", "nodejs", "node.js", "java", "python", "c#",
    ".net", "spring boot", "mern", "mobile developer", "android", "ios",
    "react native", "flutter", "golang", "rust", "typescript", "javascript",
    
    # Cloud / DevOps / Infra / Security / QA
    "devops", "cloud engineer", "aws", "azure", "gcp", "platform engineer",
    "site reliability engineer", "sre", "cybersecurity", "security engineer",
    "security analyst", "application security", "qa", "qa engineer", "test engineer",
    "automation tester", "sdet", "database", "database engineer", "sql developer",
    
    # Technical Product & Support
    "technical product manager", "technical program manager", "solutions engineer",
    "sales engineer", "developer relations", "devrel", "technical support engineer",
    "solutions architect", "system architect", "scrum master"
]

NON_TECH_EXCLUSIONS = [
    "hr recruiter", "talent acquisition", "human resources", "hr manager", "hr generalist",
    "sales executive", "sales representative", "account executive", "business development",
    "bde", "bdr", "marketing manager", "content writer", "copywriter", "graphic designer",
    "graphic artist", "accountant", "accounting", "finance analyst", "legal counsel",
    "receptionist", "office admin", "customer service representative", "customer support agent",
    "call center", "telecaller", "store manager", "facility manager"
]

def is_tech_job(title: Optional[str], description: Optional[str] = "") -> bool:
    """
    Determines if a job listing is IT/technology/software/AI related.
    Returns False if the job matches an explicit non-tech role (HR, Sales, Accountant, etc.)
    unless it contains strong technical evidence.
    """
    if not title:
        return False

    title_lower = title.lower().strip()
    desc_lower = (description or "").lower().strip()

    # Check non-tech exclusions first
    for exclusion in NON_TECH_EXCLUSIONS:
        if exclusion in title_lower:
            # Check if it's explicitly technical (e.g. "Technical Sales Engineer" or "Recruiter - Tech Tech")
            if not any(tech in title_lower for tech in ["technical", "engineering", "developer", "software"]):
                return False

    # Check for tech keywords in title
    for kw in TECH_KEYWORDS:
        if re.search(r'\b' + re.escape(kw) + r'\b', title_lower):
            return True

    # Fallback to description check if title has vague terms like "Engineer", "Developer", "Consultant"
    if any(term in title_lower for term in ["engineer", "developer", "architect", "consultant", "analyst", "trainee", "intern"]):
        if any(kw in desc_lower for kw in TECH_KEYWORDS[:20]):
            return True

    return False
