import re
from typing import Optional, List

# List of target tech/IT keywords in job titles and descriptions
TECH_TITLE_KEYWORDS = [
    "ai", "artificial intelligence", "generative ai", "genai", "machine learning",
    "deep learning", "data science", "data scientist", "data engineer", "mlops", "llm",
    "prompt engineer", "ai engineer", "ai developer", "generative ai engineer",
    "software engineer", "software developer", "application developer", "full stack",
    "frontend", "front end", "backend", "back end", "web developer", "react", "angular",
    "vue", "node", "java", "python", "c#", ".net", "dotnet", "spring boot", "mern",
    "mobile developer", "android", "ios", "react native", "flutter", "devops",
    "cloud engineer", "aws", "azure", "gcp", "platform engineer", "site reliability",
    "sre", "cybersecurity", "security engineer", "qa", "quality assurance",
    "test engineer", "automation tester", "sdet", "database", "sql", "data analyst",
    "bi developer", "business intelligence", "technical product manager",
    "technical program manager", "solutions engineer", "sales engineer",
    "developer relations", "devrel", "technical support", "systems engineer",
    "embedded engineer", "firmware", "architect", "programmer", "coding", "coder"
]

# Non-IT roles to strictly exclude unless user explicitly searches for them
EXCLUDED_NON_TECH_KEYWORDS = [
    "hr", "recruiter", "talent acquisition", "human resources", "sales executive",
    "sales manager", "account executive", "marketing manager", "content writer",
    "graphic designer", "finance", "accounting", "accountant", "legal", "counsel",
    "receptionist", "office manager", "customer service", "call center", "telecaller",
    "store manager", "payroll", "custodian", "janitor", "driver", "chef", "cook"
]

def is_tech_job(title: Optional[str], description: Optional[str] = None, user_keyword: Optional[str] = None) -> bool:
    """
    Evaluates whether a job is an IT/Software/AI/Tech role.
    Strictly excludes non-IT roles unless user_keyword specifically asks for one.
    """
    if not title:
        return False

    t_lower = title.lower().strip()
    d_lower = (description or "").lower().strip()
    k_lower = (user_keyword or "").lower().strip()

    # If user explicitly searched for a non-tech term (e.g. 'hr', 'marketing'), bypass exclusion
    user_wants_non_tech = any(ex in k_lower for ex in EXCLUDED_NON_TECH_KEYWORDS)

    if not user_wants_non_tech:
        # Check non-tech exclusions in title
        for ex in EXCLUDED_NON_TECH_KEYWORDS:
            # Word boundary regex check for short words like 'hr'
            if re.search(r'\b' + re.escape(ex) + r'\b', t_lower):
                # Ensure it's not a tech role like 'HR Tech Engineer' or 'Tech Recruiter Developer'
                if not any(re.search(r'\b' + re.escape(tk) + r'\b', t_lower) for tk in ["engineer", "developer", "architect", "programmer"]):
                    return False

    # Check positive tech title keywords
    for tk in TECH_TITLE_KEYWORDS:
        if re.search(r'\b' + re.escape(tk) + r'\b', t_lower):
            return True

    # Check description as fallback
    if d_lower:
        tech_matches = sum(1 for tk in TECH_TITLE_KEYWORDS if re.search(r'\b' + re.escape(tk) + r'\b', d_lower))
        if tech_matches >= 2:
            return True

    return False
