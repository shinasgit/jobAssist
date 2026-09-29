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

class LeverAdapter(JobSourceAdapter):
    """
    Adapter for Lever Public Postings API.
    GET https://api.lever.co/v0/postings/{company}?mode=json
    Does NOT require authentication.
    """
    BASE_URL = "https://api.lever.co/v0/postings"

    def validate_source(self) -> bool:
        return True

    async def search_jobs(self, search_params: Dict[str, Any]) -> List[Dict[str, Any]]:
        companies = load_company_registry("lever")
        if not companies:
            logger.info("No companies registered for Lever")
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
                    logger.warning(f"Lever company fetch exception: {res}")

        logger.info(f"LeverAdapter retrieved {len(all_normalized_jobs)} matching jobs")
        return all_normalized_jobs

    async def _fetch_company_jobs(
        self,
        client: httpx.AsyncClient,
        company_info: Dict[str, Any],
        search_params: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        company_identifier = company_info.get("identifier")
        company_name = company_info.get("company", company_identifier)
        if not company_identifier:
            return []

        url = f"{self.BASE_URL}/{company_identifier}?mode=json"

        try:
            response = await client.get(url)
            if response.status_code == 404:
                logger.info(f"Lever posting endpoint for '{company_identifier}' returned 404 (unavailable)")
                return []
            response.raise_for_status()

            raw_jobs = response.json()
            if not isinstance(raw_jobs, list):
                return []

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
            logger.warning(f"Lever HTTP error for company '{company_identifier}': {e}")
            return []
        except Exception as e:
            logger.error(f"Unexpected error fetching Lever jobs for '{company_identifier}': {e}")
            return []

    async def get_job_details(self, url: str) -> Dict[str, Any]:
        return {}

    def normalize_job(self, raw_job: Any, company_name: str = "Unknown") -> Dict[str, Any]:
        title = raw_job.get("text")
        source_url = raw_job.get("hostedUrl")

        categories = raw_job.get("categories") or {}
        raw_location_str = categories.get("location") or ""
        employment_type = categories.get("commitment") or "Full-time"

        workplace_type = raw_job.get("workplaceType") or ""
        loc_lower = raw_location_str.lower()
        title_lower = (title or "").lower()

        is_remote = workplace_type == "remote" or "remote" in loc_lower or "remote" in title_lower
        is_worldwide = "anywhere" in loc_lower or "worldwide" in loc_lower

        remote_type = "Worldwide" if is_worldwide else ("Remote" if is_remote else "Onsite")

        if is_bangalore_location(raw_location_str):
            norm_location = "Bangalore, Karnataka, India"
        elif raw_location_str:
            norm_location = raw_location_str.strip()
        else:
            norm_location = "Remote" if is_remote else None

        desc = raw_job.get("description") or raw_job.get("descriptionPlain") or ""

        # Created at is millisecond timestamp
        created_at = raw_job.get("createdAt")
        posted_date = None
        if created_at:
            try:
                dt = datetime.fromtimestamp(created_at / 1000.0, tz=timezone.utc)
                posted_date = dt.strftime("%Y-%m-%d")
            except Exception:
                pass

        return {
            "title": title.strip() if title else None,
            "company": company_name,
            "location": norm_location,
            "remote_type": remote_type,
            "salary": None,
            "experience": "Entry Level" if ("junior" in title_lower or "entry" in title_lower or "intern" in title_lower) else ("Senior" if ("senior" in title_lower or "lead" in title_lower) else None),
            "employment_type": employment_type,
            "description": desc,
            "source": "Lever",
            "source_url": source_url,
            "posted_date": posted_date
        }
