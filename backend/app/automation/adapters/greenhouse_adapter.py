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

class GreenhouseAdapter(JobSourceAdapter):
    """
    Adapter for Greenhouse Public Job Board API.
    GET https://boards-api.greenhouse.io/v1/boards/{board_token}/jobs?content=true
    Does NOT require authentication.
    """
    BASE_URL = "https://boards-api.greenhouse.io/v1/boards"

    def validate_source(self) -> bool:
        return True

    async def search_jobs(self, search_params: Dict[str, Any]) -> List[Dict[str, Any]]:
        companies = load_company_registry("greenhouse")
        if not companies:
            logger.info("No companies registered for Greenhouse")
            return []

        keyword = search_params.get("keyword", "")
        filter_location = search_params.get("location", "")
        filter_remote = search_params.get("remote_type", "")

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
                    logger.warning(f"Greenhouse company fetch exception: {res}")

        logger.info(f"GreenhouseAdapter retrieved {len(all_normalized_jobs)} matching jobs")
        return all_normalized_jobs

    async def _fetch_company_jobs(
        self,
        client: httpx.AsyncClient,
        company_info: Dict[str, Any],
        search_params: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        board_token = company_info.get("identifier")
        company_name = company_info.get("company", board_token)
        if not board_token:
            return []

        url = f"{self.BASE_URL}/{board_token}/jobs?content=true"

        try:
            response = await client.get(url)
            if response.status_code == 404:
                logger.info(f"Greenhouse board '{board_token}' returned 404 (unavailable)")
                return []
            response.raise_for_status()

            data = response.json()
            raw_jobs = data.get("jobs", [])
            
            matching_jobs = []
            for raw in raw_jobs:
                norm = self.normalize_job(raw, company_name=company_name)
                if not norm.get("title") or not norm.get("source_url"):
                    continue

                # Filtering checks
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
            logger.warning(f"Greenhouse HTTP error for board '{board_token}': {e}")
            return []
        except Exception as e:
            logger.error(f"Unexpected error fetching Greenhouse board '{board_token}': {e}")
            return []

    async def get_job_details(self, url: str) -> Dict[str, Any]:
        return {}

    def normalize_job(self, raw_job: Any, company_name: str = "Unknown") -> Dict[str, Any]:
        title = raw_job.get("title")
        source_url = raw_job.get("absolute_url")
        
        location_obj = raw_job.get("location") or {}
        raw_location_str = location_obj.get("name") if isinstance(location_obj, dict) else str(location_obj)

        # Detect remote_type & location normalization
        loc_lower = (raw_location_str or "").lower()
        title_lower = (title or "").lower()
        
        is_remote = "remote" in loc_lower or "remote" in title_lower
        is_worldwide = "anywhere" in loc_lower or "worldwide" in loc_lower
        
        remote_type = "Worldwide" if is_worldwide else ("Remote" if is_remote else "Onsite")
        
        if is_bangalore_location(raw_location_str):
            norm_location = "Bangalore, Karnataka, India"
        elif raw_location_str:
            norm_location = raw_location_str.strip()
        else:
            norm_location = "Remote" if is_remote else None

        # Description HTML
        desc = raw_job.get("content") or ""

        # Posted date
        updated_at = raw_job.get("updated_at")
        posted_date = None
        if updated_at:
            try:
                dt = datetime.fromisoformat(updated_at.replace("Z", "+00:00"))
                posted_date = dt.strftime("%Y-%m-%d")
            except Exception:
                posted_date = str(updated_at)[:10]

        return {
            "title": title.strip() if title else None,
            "company": company_name,
            "location": norm_location,
            "remote_type": remote_type,
            "salary": None,  # Greenhouse API standard response doesn't provide salary in listing
            "experience": "Entry Level" if ("junior" in title_lower or "entry" in title_lower or "intern" in title_lower) else ("Senior" if ("senior" in title_lower or "lead" in title_lower) else None),
            "employment_type": "Full-time",
            "description": desc,
            "source": "Greenhouse",
            "source_url": source_url,
            "posted_date": posted_date
        }
