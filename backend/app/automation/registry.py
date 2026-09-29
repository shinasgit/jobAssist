import json
import os
import logging
from typing import List, Dict, Any

logger = logging.getLogger(__name__)

PRIMARY_REGISTRY_PATH = os.path.join(os.path.dirname(__file__), "registry", "companies.json")
FALLBACK_REGISTRY_PATH = os.path.join(os.path.dirname(__file__), "company_registry.json")

def load_company_registry(ats_type: str = None) -> List[Dict[str, Any]]:
    """
    Loads active company configs from registry/companies.json or company_registry.json.
    Optionally filters by ats_type (e.g. 'greenhouse', 'lever', 'ashby', 'workday').
    """
    target_path = PRIMARY_REGISTRY_PATH if os.path.exists(PRIMARY_REGISTRY_PATH) else FALLBACK_REGISTRY_PATH

    if not os.path.exists(target_path):
        logger.warning(f"Company registry file not found at {target_path}")
        return []

    try:
        with open(target_path, "r", encoding="utf-8") as f:
            companies = json.load(f)
            
        active = [c for c in companies if c.get("enabled", True)]
        if ats_type:
            active = [c for c in active if c.get("ats", "").lower() == ats_type.lower()]
            
        return active
    except Exception as e:
        logger.error(f"Failed to load company registry: {e}")
        return []

def get_company_category(company_name: str, source_name: str = "") -> str:
    """
    Returns normalized source category for a company (MNC, STARTUP, IT_TECH, REMOTE).
    """
    if not company_name:
        if source_name.lower() in ["himalayas", "remotive", "arbeitnow"]:
            return "REMOTE"
        return "IT_TECH"

    companies = load_company_registry()
    c_lower = company_name.lower().strip()
    
    for comp in companies:
        name = (comp.get("name") or comp.get("company") or "").lower().strip()
        if name and (name in c_lower or c_lower in name):
            raw_cat = (comp.get("category") or "").strip().upper()
            if raw_cat in ["MNC"]:
                return "MNC"
            elif raw_cat in ["STARTUP"]:
                return "STARTUP"
            elif raw_cat in ["PRODUCT", "SAAS", "FINTECH", "AI", "IT SERVICES"]:
                return "IT_TECH"

    # Default fallback heuristics
    if source_name.lower() in ["himalayas", "remotive", "arbeitnow"]:
        return "REMOTE"
    elif any(m in c_lower for m in ["microsoft", "amazon", "google", "ibm", "oracle", "salesforce", "walmart", "accenture", "tcs", "infosys", "cognizant", "capgemini"]):
        return "MNC"

    return "IT_TECH"

