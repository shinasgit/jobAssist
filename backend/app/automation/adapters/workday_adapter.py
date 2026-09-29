import httpx
import logging
import asyncio
from typing import Dict, Any, List

from app.automation.adapters.base import JobSourceAdapter
from app.automation.registry import load_company_registry
from app.automation.location_utils import (
    is_bangalore_location,
    normalize_location_str,
    matches_location_filter,
    matches_title_or_keyword
)
from app.automation.tech_classifier import is_tech_job

logger = logging.getLogger(__name__)

class WorkdayAdapter(JobSourceAdapter):
    """
    Adapter for Workday Public Career Site CXS API Endpoint.
    POST https://{tenant}.{datacenter}.myworkdayjobs.com/wday/cxs/{tenant}/{site}/jobs
    Does NOT require authentication.
    """

    def validate_source(self) -> bool:
        return True

    async def search_jobs(self, search_params: Dict[str, Any]) -> List[Dict[str, Any]]:
        companies = load_company_registry("workday")
        if not companies:
            logger.info("No companies registered for Workday")
            return []

        all_normalized_jobs = []

        async with httpx.AsyncClient(timeout=15.0, follow_redirects=True) as client:
            tasks = [
                self._fetch_company_jobs(client, company, search_params)
                for company in companies
            ]
            results = await asyncio.gather(*tasks, return_exceptions=True)

            for res in results:
                if isinstance(res, list):
                    all_normalized_jobs.extend(res)
                elif isinstance(res, Exception):
                    logger.warning(f"Workday company fetch exception: {res}")

        logger.info(f"WorkdayAdapter retrieved {len(all_normalized_jobs)} matching jobs")
        return all_normalized_jobs

    async def _fetch_company_jobs(
        self,
        client: httpx.AsyncClient,
        company_info: Dict[str, Any],
        search_params: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        tenant = company_info.get("tenant") or company_info.get("identifier")
        datacenter = company_info.get("datacenter", "wd5")
        site = company_info.get("site") or f"{company_info.get('name')}_Careers"
        company_name = company_info.get("name", tenant)

        if not tenant:
            return []

        url = f"https://{tenant}.{datacenter}.myworkdayjobs.com/wday/cxs/{tenant}/{site}/jobs"

        payload = {
            "appliedFacets": {},
            "limit": 20,
            "offset": 0,
            "searchText": search_params.get("keyword", "")
        }

        try:
            response = await client.post(url, json=payload)
            if response.status_code in [404, 403]:
                logger.info(f"Workday endpoint for '{tenant}' returned {response.status_code} (unavailable)")
                return []
            response.raise_for_status()

            data = response.json()
            raw_postings = data.get("jobPostings", []) if isinstance(data, dict) else []

            matching_jobs = []
            for raw in raw_postings:
                norm = self.normalize_job(raw, company_name=company_name, tenant=tenant, datacenter=datacenter, site=site)
                if not norm.get("title") or not norm.get("source_url"):
                    continue

                # Filter IT/tech jobs only
                if not is_tech_job(norm["title"], norm["description"]):
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
            logger.warning(f"Workday HTTP error for '{tenant}': {e}")
            return []
        except Exception as e:
            logger.error(f"Unexpected error fetching Workday jobs for '{tenant}': {e}")
            return []

    async def get_job_details(self, url: str) -> Dict[str, Any]:
        return {}

    def normalize_job(
        self,
        raw_job: Any,
        company_name: str = "Unknown",
        tenant: str = "",
        datacenter: str = "wd5",
        site: str = ""
    ) -> Dict[str, Any]:
        title = raw_job.get("title")
        ext_path = raw_job.get("externalPath") or ""

        if ext_path and tenant and site:
            source_url = f"https://{tenant}.{datacenter}.myworkdayjobs.com/en-US/{site}{ext_path}"
        else:
            source_url = raw_job.get("jobPostingUrl")

        raw_location_str = raw_job.get("locationsText") or ""

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

        bullets = raw_job.get("bulletFields") or []
        emp_type = "Full-time"
        for b in bullets:
            if "part" in str(b).lower():
                emp_type = "Part-time"
            elif "contract" in str(b).lower():
                emp_type = "Contract"

        return {
            "title": title.strip() if title else None,
            "company": company_name,
            "location": norm_location,
            "remote_type": remote_type,
            "salary": None,
            "experience": "Entry Level" if ("junior" in title_lower or "entry" in title_lower or "intern" in title_lower) else ("Senior" if ("senior" in title_lower or "lead" in title_lower) else None),
            "employment_type": emp_type,
            "description": f"Workday posting {raw_job.get('postedOn', '')}",
            "source": "Workday",
            "source_url": source_url,
            "posted_date": None
        }
