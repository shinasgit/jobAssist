import httpx
import logging
from typing import Dict, Any, List
from datetime import datetime, timezone
from app.automation.adapters.base import JobSourceAdapter

logger = logging.getLogger(__name__)

class ArbeitnowAdapter(JobSourceAdapter):
    """
    Adapter for Arbeitnow Public Job Board API.
    API documentation: https://www.arbeitnow.com/api/job-board-api
    Provides public JSON feed for tech and remote jobs.
    """
    BASE_URL = "https://www.arbeitnow.com/api/job-board-api"

    def validate_source(self) -> bool:
        return True

    async def search_jobs(self, search_params: Dict[str, Any]) -> List[Dict[str, Any]]:
        keyword = search_params.get("keyword", "").strip().lower()
        location_filter = search_params.get("location", "").strip().lower()
        experience_filter = search_params.get("experience", "").strip().lower()
        remote_filter = search_params.get("remote_type", "").strip().lower()

        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        }

        try:
            async with httpx.AsyncClient(timeout=15.0) as client:
                response = await client.get(self.BASE_URL, headers=headers)
                response.raise_for_status()
                data = response.json()
                raw_jobs = data.get("data", [])
        except Exception as e:
            logger.error(f"Arbeitnow API request failed: {e}")
            return []

        normalized_jobs = []
        for raw in raw_jobs:
            normalized = self.normalize_job(raw)
            if not normalized or not normalized.get("title") or not normalized.get("source_url"):
                continue

            # Keyword filter check (against title, tags, description)
            if keyword:
                title_lower = normalized.get("title", "").lower()
                desc_lower = (normalized.get("description") or "").lower()
                company_lower = (normalized.get("company") or "").lower()
                if keyword not in title_lower and keyword not in desc_lower and keyword not in company_lower:
                    continue

            # Remote filter check
            if remote_filter and remote_filter != "any":
                job_remote = normalized.get("remote_type", "").lower()
                if remote_filter == "remote" and job_remote != "remote":
                    continue
                elif remote_filter == "onsite" and job_remote == "remote":
                    continue

            # Location filter check
            if location_filter and location_filter != "any":
                job_loc = (normalized.get("location") or "").lower()
                if location_filter not in job_loc and "remote" not in job_loc and "anywhere" not in job_loc:
                    continue

            # Experience filter check
            if experience_filter and experience_filter != "any":
                job_title = normalized.get("title", "").lower()
                if experience_filter == "fresher" or "0-2" in experience_filter or "entry" in experience_filter:
                    if "senior" in job_title or "lead" in job_title or "principal" in job_title:
                        continue

            normalized_jobs.append(normalized)

        return normalized_jobs

    async def get_job_details(self, url: str) -> Dict[str, Any]:
        return {}

    def normalize_job(self, raw: Dict[str, Any]) -> Dict[str, Any]:
        title = raw.get("title")
        company = raw.get("company_name")
        source_url = raw.get("url")

        if not title or not source_url:
            return {}

        is_remote = raw.get("remote", False)
        remote_type = "Remote" if is_remote else "Onsite"
        location = raw.get("location") or ("Remote" if is_remote else "Flexible")

        # Format creation timestamp
        created_at = raw.get("created_at")
        posted_date = None
        if created_at:
            try:
                dt = datetime.fromtimestamp(created_at, tz=timezone.utc)
                posted_date = dt.strftime("%Y-%m-%d")
            except Exception:
                posted_date = None

        job_types = raw.get("job_types") or []
        employment_type = job_types[0] if job_types else "Full-time"

        return {
            "title": title.strip(),
            "company": company.strip() if company else None,
            "location": location.strip(),
            "remote_type": remote_type,
            "salary": None,
            "experience": "Entry Level" if ("junior" in title.lower() or "entry" in title.lower()) else "Mid-Senior Level" if ("senior" in title.lower() or "lead" in title.lower()) else "Flexible",
            "employment_type": employment_type,
            "description": raw.get("description") or "",
            "source": "arbeitnow",
            "source_url": source_url.strip(),
            "posted_date": posted_date
        }
