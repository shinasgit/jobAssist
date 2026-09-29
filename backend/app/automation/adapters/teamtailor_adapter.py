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

class TeamtailorAdapter(JobSourceAdapter):
    """
    Adapter for Teamtailor Public Jobs Feed Endpoint (only where publicly accessible).
    GET https://{company}.teamtailor.com/jobs.json
    If authenticated or restricted, treats source as unavailable without bypassing controls.
    """

    def validate_source(self) -> bool:
        return True

    async def search_jobs(self, search_params: Dict[str, Any]) -> List[Dict[str, Any]]:
        companies = load_company_registry("teamtailor")
        if not companies:
            logger.info("No companies registered for Teamtailor")
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
                    logger.warning(f"Teamtailor company fetch exception: {res}")

        logger.info(f"TeamtailorAdapter retrieved {len(all_normalized_jobs)} matching jobs")
        return all_normalized_jobs

    async def _fetch_company_jobs(
        self,
        client: httpx.AsyncClient,
        company_info: Dict[str, Any],
        search_params: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        slug = company_info.get("identifier")
        company_name = company_info.get("company", slug)
        if not slug:
            return []

        url = f"https://{slug}.teamtailor.com/jobs.json"

        try:
            response = await client.get(url)
            if response.status_code in [401, 403, 404]:
                logger.info(f"Teamtailor public feed for '{slug}' returned {response.status_code} (access restricted/unavailable)")
                return []
            response.raise_for_status()

            data = response.json()
            raw_jobs = data.get("jobs", []) if isinstance(data, dict) else (data if isinstance(data, list) else [])

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
            logger.info(f"Teamtailor feed unavailable for '{slug}': {e}")
            return []
        except Exception as e:
            logger.info(f"Teamtailor feed parse failed for '{slug}': {e}")
            return []

    async def get_job_details(self, url: str) -> Dict[str, Any]:
        return {}

    def normalize_job(self, raw_job: Any, company_name: str = "Unknown") -> Dict[str, Any]:
        title = raw_job.get("title") or raw_job.get("name")
        source_url = raw_job.get("url") or raw_job.get("links", {}).get("careers_url")

        raw_location_str = raw_job.get("location") or raw_job.get("city") or ""

        loc_lower = raw_location_str.lower()
        title_lower = (title or "").lower()

        is_remote = "remote" in loc_lower or "remote" in title_lower
        is_worldwide = "worldwide" in loc_lower or "anywhere" in loc_lower

        remote_type = "Worldwide" if is_worldwide else ("Remote" if is_remote else "Onsite")

        if is_bangalore_location(raw_location_str):
            norm_location = "Bangalore, Karnataka, India"
        elif raw_location_str:
            norm_location = raw_location_str.strip()
        else:
            norm_location = "Remote" if is_remote else None

        desc = raw_job.get("body") or raw_job.get("description") or ""

        return {
            "title": title.strip() if title else None,
            "company": company_name,
            "location": norm_location,
            "remote_type": remote_type,
            "salary": None,
            "experience": "Entry Level" if ("junior" in title_lower or "entry" in title_lower or "intern" in title_lower) else ("Senior" if ("senior" in title_lower or "lead" in title_lower) else None),
            "employment_type": "Full-time",
            "description": desc,
            "source": "Teamtailor",
            "source_url": source_url,
            "posted_date": None
        }
