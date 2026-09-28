import httpx
import logging
from typing import Dict, Any, List
from datetime import datetime, timezone
from app.automation.adapters.base import JobSourceAdapter

logger = logging.getLogger(__name__)

class RemotiveAdapter(JobSourceAdapter):
    """
    Adapter for Remotive Public Jobs API.
    API documentation: https://remotive.com/api/remote-jobs
    Provides public JSON feed for remote tech jobs without requiring authentication.
    """
    BASE_URL = "https://remotive.com/api/remote-jobs"

    def validate_source(self) -> bool:
        # Remotive provides an explicit public API for integrations
        return True

    async def search_jobs(self, search_params: Dict[str, Any]) -> List[Dict[str, Any]]:
        keyword = search_params.get("keyword", "").strip()
        location_filter = search_params.get("location", "").strip().lower()
        experience_filter = search_params.get("experience", "").strip().lower()
        remote_filter = search_params.get("remote_type", "").strip().lower()

        # If user explicitly requested non-remote/onsite only, skip remotive
        if remote_filter == "onsite":
            return []

        params = {}
        if keyword:
            params["search"] = keyword
        params["limit"] = 50

        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        }

        try:
            async with httpx.AsyncClient(timeout=15.0) as client:
                response = await client.get(self.BASE_URL, params=params, headers=headers)
                response.raise_for_status()
                data = response.json()
                raw_jobs = data.get("jobs", [])
        except Exception as e:
            logger.error(f"Remotive API request failed: {e}")
            return []

        normalized_jobs = []
        for raw in raw_jobs:
            normalized = self.normalize_job(raw)
            if not normalized or not normalized.get("title") or not normalized.get("source_url"):
                continue

            # Local location filter
            if location_filter and location_filter != "any":
                job_loc = (normalized.get("location") or "").lower()
                if location_filter not in job_loc and "worldwide text" not in job_loc and "anywhere" not in job_loc and "remote" not in job_loc:
                    continue

            # Local experience filter check
            if experience_filter and experience_filter != "any":
                job_exp = (normalized.get("experience") or "").lower()
                job_title = normalized.get("title", "").lower()
                if experience_filter == "fresher" or "0-2" in experience_filter or "entry" in experience_filter:
                    if "senior" in job_title or "lead" in job_title or "principal" in job_title:
                        continue

            normalized_jobs.append(normalized)

        return normalized_jobs

    async def get_job_details(self, url: str) -> Dict[str, Any]:
        # Detailed descriptions are already included in search_jobs payload
        return {}

    def normalize_job(self, raw: Dict[str, Any]) -> Dict[str, Any]:
        title = raw.get("title")
        company = raw.get("company_name")
        source_url = raw.get("url")

        if not title or not source_url:
            return {}

        raw_location = raw.get("candidate_required_location") or "Worldwide / Remote"
        salary = raw.get("salary") or None
        
        # Clean salary if available
        if salary and salary.strip() and salary.lower() != "null":
            salary = salary.strip()
        else:
            salary = None

        description = raw.get("description") or ""
        
        # Format publication date
        pub_date = raw.get("publication_date")
        posted_date = None
        if pub_date:
            try:
                # e.g., "2026-09-25T12:00:00"
                dt = datetime.fromisoformat(pub_date.replace("Z", "+00:00"))
                posted_date = dt.strftime("%Y-%m-%d")
            except Exception:
                posted_date = str(pub_date)[:10]

        # Job type formatting
        job_type_raw = raw.get("job_type") or "full_time"
        employment_type = "Full-time"
        if "part" in job_type_raw.lower():
            employment_type = "Part-time"
        elif "contract" in job_type_raw.lower() or "freelance" in job_type_raw.lower():
            employment_type = "Contract"
        elif "intern" in job_type_raw.lower():
            employment_type = "Internship"

        return {
            "title": title.strip(),
            "company": company.strip() if company else None,
            "location": raw_location.strip(),
            "remote_type": "Remote",
            "salary": salary,
            "experience": "Entry Level" if ("junior" in title.lower() or "entry" in title.lower()) else "Mid-Senior Level" if ("senior" in title.lower() or "lead" in title.lower()) else "Flexible",
            "employment_type": employment_type,
            "description": description,
            "source": "remotive",
            "source_url": source_url.strip(),
            "posted_date": posted_date
        }
