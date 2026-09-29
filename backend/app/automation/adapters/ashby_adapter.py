import httpx
import logging
import asyncio
from typing import Dict, Any, List
from datetime import datetime, timezone

from app.automation.adapters.base import JobSourceAdapter
from app.automation.registry import load_company_registry
from app.automation.location_utils import (
    is_bangalore_location,
    normalize_location_str,
    matches_location_filter,
    matches_title_or_keyword
)

logger = logging.getLogger(__name__)

class AshbyAdapter(JobSourceAdapter):
    """
    Adapter for Ashby Public Job Board API.
    GET https://api.ashbyhq.com/posting-api/job-board/{JOB_BOARD_NAME}?includeCompensation=true
    Does NOT require authentication.
    """
    BASE_URL = "https://api.ashbyhq.com/posting-api/job-board"

    def validate_source(self) -> bool:
        return True

    async def search_jobs(self, search_params: Dict[str, Any]) -> List[Dict[str, Any]]:
        companies = load_company_registry("ashby")
        if not companies:
            logger.info("No companies registered for Ashby")
            return []

        all_normalized_jobs = []

        async with httpx.AsyncClient(timeout=10.0, follow_redirects=True) as client:
            tasks = [
                self._fetch_company_jobs(client, company, search_params)
                for company in companies
            ]
            results = await asyncio.gather(*tasks, return_exceptions=True)

            for res in results:
                if isinstance(res, list):
                    all_normalized_jobs.extend(res)
                elif isinstance(res, Exception):
                    logger.warning(f"Ashby company fetch exception: {res}")

        logger.info(f"AshbyAdapter retrieved {len(all_normalized_jobs)} matching jobs")
        return all_normalized_jobs

    async def _fetch_company_jobs(
        self,
        client: httpx.AsyncClient,
        company_info: Dict[str, Any],
        search_params: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        board_name = company_info.get("identifier")
        company_name = company_info.get("company", board_name)
        if not board_name:
            return []

        url = f"{self.BASE_URL}/{board_name}?includeCompensation=true"

        try:
            response = await client.get(url)
            if response.status_code == 404:
                logger.info(f"Ashby job board for '{board_name}' returned 404 (unavailable)")
                return []
            response.raise_for_status()

            data = response.json()
            raw_jobs = data.get("jobs", []) if isinstance(data, dict) else []

            matching_jobs = []
            for raw in raw_jobs:
                norm = self.normalize_job(raw, company_name=company_name)
                if not norm.get("title") or not norm.get("source_url"):
                    continue

                if not matches_title_or_keyword(norm["title"], norm["description"], search_params.get("keyword")):
                    continue

                if not matches_location_filter(
                    norm["location"],
                    norm["remote_type"],
                    search_params.get("location"),
                    search_params.get("remote_type")
                ):
                    continue

                matching_jobs.append(norm)

            return matching_jobs

        except httpx.HTTPError as e:
            logger.warning(f"Ashby HTTP error for board '{board_name}': {e}")
            return []
        except Exception as e:
            logger.error(f"Unexpected error fetching Ashby jobs for '{board_name}': {e}")
            return []

    async def get_job_details(self, url: str) -> Dict[str, Any]:
        return {}

    def normalize_job(self, raw_job: Any, company_name: str = "Unknown") -> Dict[str, Any]:
        title = raw_job.get("title")
        source_url = raw_job.get("jobUrl") or raw_job.get("applyUrl")

        raw_location_str = raw_job.get("locationName") or raw_job.get("location") or ""
        is_remote_flag = raw_job.get("isRemote", False)

        loc_lower = raw_location_str.lower()
        title_lower = (title or "").lower()

        is_remote = is_remote_flag or "remote" in loc_lower or "remote" in title_lower
        is_worldwide = "anywhere" in loc_lower or "worldwide" in loc_lower

        remote_type = "Worldwide" if is_worldwide else ("Remote" if is_remote else "Onsite")

        if is_bangalore_location(raw_location_str):
            norm_location = "Bangalore, Karnataka, India"
        elif raw_location_str:
            norm_location = raw_location_str.strip()
        else:
            norm_location = "Remote" if is_remote else None

        # Salary formatting
        salary = None
        comp = raw_job.get("compensation")
        if isinstance(comp, dict):
            salary = comp.get("compensationTierSummary") or comp.get("summary")

        employment_type = raw_job.get("employmentType") or "Full-time"
        if employment_type == "FullTime":
            employment_type = "Full-time"
        elif employment_type == "PartTime":
            employment_type = "Part-time"

        desc = raw_job.get("descriptionHtml") or raw_job.get("descriptionPlain") or ""

        published_at = raw_job.get("publishedAt")
        posted_date = None
        if published_at:
            try:
                dt = datetime.fromisoformat(published_at.replace("Z", "+00:00"))
                posted_date = dt.strftime("%Y-%m-%d")
            except Exception:
                posted_date = str(published_at)[:10]

        return {
            "title": title.strip() if title else None,
            "company": company_name,
            "location": norm_location,
            "remote_type": remote_type,
            "salary": salary,
            "experience": "Entry Level" if ("junior" in title_lower or "entry" in title_lower or "intern" in title_lower) else ("Senior" if ("senior" in title_lower or "lead" in title_lower) else None),
            "employment_type": employment_type,
            "description": desc,
            "source": "Ashby",
            "source_url": source_url,
            "posted_date": posted_date
        }
