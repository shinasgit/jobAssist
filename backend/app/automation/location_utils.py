import re
from typing import Optional

BANGALORE_LOCALITIES = [
    "bangalore",
    "bengaluru",
    "bangalore urban",
    "bengaluru urban",
    "electronic city",
    "whitefield",
    "marathahalli",
    "koramangala",
    "hsr layout",
    "indiranagar",
    "bellandur",
    "manyata tech park",
    "manyata",
    "outer ring road",
    "hebbal",
    "yelahanka",
    "hosur road"
]

def is_bangalore_location(location_str: Optional[str]) -> bool:
    """
    Checks if a given location string explicitly matches Bangalore, Bengaluru, BLR,
    or any recognized Bangalore tech locality.
    Does NOT match generic 'Karnataka' unless explicit Bangalore evidence exists.
    """
    if not location_str:
        return False

    loc_lower = location_str.lower().strip()
    
    for locality in BANGALORE_LOCALITIES:
        if locality in loc_lower:
            return True

    # Standalone 'BLR' airport/city code match
    if re.search(r'\bblr\b', loc_lower):
        return True
            
    return False


def normalize_location_str(location_str: Optional[str]) -> str:
    """
    Normalizes location strings to standard 'Bangalore, Karnataka, India' if it matches Bangalore,
    otherwise cleans up whitespace.
    """
    if not location_str:
        return "Unknown"
        
    if is_bangalore_location(location_str):
        # Preserve specific info or return normalized Bangalore
        return "Bangalore, Karnataka, India"
        
    return location_str.strip()

def matches_location_filter(
    job_location: Optional[str],
    remote_type: Optional[str],
    filter_location: Optional[str],
    filter_remote_type: Optional[str] = None
) -> bool:
    """
    Determines whether a job satisfies user location and remote preferences.
    """
    if not filter_location or filter_location.lower() in ["any", "all", "worldwide", "remote"]:
        # No strict location requirement, but check remote_type if specified
        if filter_remote_type and filter_remote_type.lower() == "onsite":
            return (remote_type or "").lower() not in ["remote", "worldwide"]
        return True

    filter_loc_lower = filter_location.lower().strip()
    job_loc_str = (job_location or "").lower().strip()
    remote_str = (remote_type or "").lower().strip()

    # Special handling for Bangalore preference
    if "bangalore" in filter_loc_lower or "bengaluru" in filter_loc_lower:
        # Check explicit Bangalore location match
        if is_bangalore_location(job_loc_str):
            return True
        # Allow Remote / Worldwide if remote preference allows it or isn't strictly 'onsite'
        if remote_str in ["remote", "worldwide"] and (not filter_remote_type or filter_remote_type.lower() != "onsite"):
            return True
        return False

    # Generic location matching fallback
    if filter_loc_lower in job_loc_str:
        return True

    if remote_str in ["remote", "worldwide"] and (not filter_remote_type or filter_remote_type.lower() != "onsite"):
        return True

    return False

def matches_title_or_keyword(
    job_title: Optional[str],
    job_description: Optional[str],
    keyword_filter: Optional[str]
) -> bool:
    """
    Performs flexible title & content keyword matching.
    Example: 'AI Engineer' matches 'Software Engineer - AI Platform' or 'Senior Machine Learning & AI Developer'.
    """
    if not keyword_filter or not keyword_filter.strip():
        return True

    title = (job_title or "").lower().strip()
    desc = (job_description or "").lower().strip()
    kw = keyword_filter.lower().strip()

    # Exact sub-phrase match in title
    if kw in title:
        return True

    # Tokenized keyword match in title
    tokens = [t for t in re.split(r'[\s\-_/]+', kw) if len(t) > 1]
    if tokens:
        # All tokens present in title or description
        if all(token in title for token in tokens):
            return True
        
        # Core tokens present in title (e.g., 'ai' and 'engineer')
        if any(token in title for token in tokens) and any(token in desc for token in tokens):
            return True

    return False
