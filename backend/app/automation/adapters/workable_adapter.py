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

class WorkableAdapter(JobSourceAdapter):
    """
    Adapter for Workable Public Job Board Endpoint.
    GET https://apply.workable.com/api/v1/widget/accounts/{company}?details=true
    or POST https://apply.workable.com/api/v1/accounts/{company}/jobs
    Does NOT require authentication.
    """
    BASE_URL = "https://apply.workable.com/api/v1/widget/accounts"

    def validate_source(self) -> bool:
        return True

    async def search_jobs(self, search_params: Dict[str, Any]) -> List[Dict[str, Any]]:
        companies = load_company_registry("workable")
        if not companies:
            logger.info("No companies registered for Workable")
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
                    logger.warning(f"Workable company fetch exception: {res}")

        logger.info(f"WorkableAdapter retrieved {len(all_normalized_jobs)} matching jobs")
        return all_normalized_jobs

    async def _fetch_company_jobs(
        self,
        client: httpx.AsyncClient,
        company_info: Dict[str, Any],
        search_params: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        account_name = company_info.get("identifier")
        company_name = company_info.get("company", account_name)
        if not account_name:
            return []

        url = f"{self.BASE_URL}/{account_name}?details=true"

        try:
            response = await client.get(url)
            if response.status_code == 404:
                logger.info(f"Workable board '{account_name}' returned 404 (unavailable)")
                return []
            response.raise_for_status()

            data = response.json()
            raw_jobs = data.get("jobs", []) if isinstance(data, dict) else []

            matching_jobs = []
            for raw in raw_jobs:
                norm = self.normalize_job(raw, company_name=company_name, account_slug=account_name)
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
            logger.warning(f"Workable HTTP error for account '{account_name}': {e}")
            return []
        except Exception as e:
            logger.error(f"Unexpected error fetching Workable jobs for '{account_name}': {e}")
            return []

    async def get_job_details(self, url: str) -> Dict[str, Any]:
        return {}

    def normalize_job(self, raw_job: Any, company_name: str = "Unknown", account_slug: str = "") -> Dict[str, Any]:
        title = raw_job.get("title")
        shortcode = raw_job.get("shortcode") or raw_job.get("id")
        
        source_url = raw_job.get("url")
        if not source_url and shortcode and account_slug:
            source_url = f"https://apply.workable.com/{account_slug}/j/{shortcode}/"

        location_dict = raw_job.get("location") or {}
        city = location_dict.get("city") or ""
        region = location_dict.get("region") or ""
        country = location_dict.get("country") or ""
        
        parts = [p for p in [city, region, country] if p]
        raw_location_str = ", ".join(parts) if parts else (raw_job.get("location_str") or "")

        is_telecommute = raw_job.get("telecommute", False) or raw_job.get("workplace", "").lower() == "remote"
        loc_lower = raw_location_str.lower()
        title_lower = (title or "").lower()

        is_remote = is_telecommute or "remote" in loc_lower or "remote" in title_lower
        is_worldwide = "worldwide" in loc_lower or "anywhere" in loc_lower

        remote_type = "Worldwide" if is_worldwide else ("Remote" if is_remote else "Onsite")

        if is_bangalore_location(raw_location_str):
            norm_location = "Bangalore, Karnataka, India"
        elif raw_location_str:
            norm_location = raw_location_str.strip()
        else:
            norm_location = "Remote" if is_remote else None

        desc = raw_job.get("description") or raw_job.get("summary") or ""

        published = raw_job.get("published") or raw_job.get("created_at")
        posted_date = None
        if published:
            try:
                posted_date = str(published)[:10]
            except Exception:
                pass

        return {
            "title": title.strip() if title else None,
            "company": company_name,
            "location": norm_location,
            "remote_type": remote_type,
            "salary": None,
            "experience": "Entry Level" if ("junior" in title_lower or "entry" in title_lower or "intern" in title_lower) else ("Senior" if ("senior" in title_lower or "lead" in title_lower) else None),
            "employment_type": raw_job.get("employment_type") or "Full-time",
            "description": desc,
            "source": "Workable",
            "source_url": source_url,
            "posted_date": posted_date
        }
