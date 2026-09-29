import httpx
import logging
import asyncio
import xml.etree.ElementTree as ET
from typing import Dict, Any, List

from app.automation.adapters.base import JobSourceAdapter
from app.automation.registry import load_company_registry
from app.automation.location_utils import (
    is_bangalore_location,
    normalize_location_str,
    matches_location_filter,
    matches_title_or_keyword
)

logger = logging.getLogger(__name__)

class PersonioAdapter(JobSourceAdapter):
    """
    Adapter for Personio Public Job XML Feed Endpoint.
    GET https://{company}.personio.de/xml
    Does NOT require authentication.
    """

    def validate_source(self) -> bool:
        return True

    async def search_jobs(self, search_params: Dict[str, Any]) -> List[Dict[str, Any]]:
        companies = load_company_registry("personio")
        if not companies:
            logger.info("No companies registered for Personio")
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
                    logger.warning(f"Personio company fetch exception: {res}")

        logger.info(f"PersonioAdapter retrieved {len(all_normalized_jobs)} matching jobs")
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

        # Try .de then .com if needed
        url = f"https://{slug}.personio.de/xml"

        try:
            response = await client.get(url)
            if response.status_code == 404:
                url = f"https://{slug}.personio.com/xml"
                response = await client.get(url)
                if response.status_code == 404:
                    logger.info(f"Personio XML feed for '{slug}' returned 404 (unavailable)")
                    return []
            response.raise_for_status()

            raw_xml = response.text
            matching_jobs = self._parse_xml_feed(raw_xml, company_name=company_name, slug=slug, search_params=search_params)
            return matching_jobs

        except httpx.HTTPError as e:
            logger.warning(f"Personio HTTP error for '{slug}': {e}")
            return []
        except Exception as e:
            logger.error(f"Unexpected error fetching Personio jobs for '{slug}': {e}")
            return []

    def _parse_xml_feed(self, xml_text: str, company_name: str, slug: str, search_params: Dict[str, Any]) -> List[Dict[str, Any]]:
        matching_jobs = []
        try:
            root = ET.fromstring(xml_text)
            for pos in root.findall(".//position"):
                title_elem = pos.find("name")
                title = title_elem.text if title_elem is not None else None
                job_id_elem = pos.find("id")
                job_id = job_id_elem.text if job_id_elem is not None else None

                office_elem = pos.find("office")
                office = office_elem.text if office_elem is not None else ""

                emp_elem = pos.find("employmentType")
                emp_type = emp_elem.text if emp_elem is not None else "Full-time"

                raw_job = {
                    "title": title,
                    "id": job_id,
                    "office": office,
                    "employmentType": emp_type
                }
                norm = self.normalize_job(raw_job, company_name=company_name, slug=slug)
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

        except Exception as e:
            logger.warning(f"Error parsing Personio XML: {e}")

        return matching_jobs

    async def get_job_details(self, url: str) -> Dict[str, Any]:
        return {}

    def normalize_job(self, raw_job: Any, company_name: str = "Unknown", slug: str = "") -> Dict[str, Any]:
        title = raw_job.get("title")
        job_id = raw_job.get("id")

        source_url = f"https://{slug}.personio.de/job/{job_id}" if slug and job_id else f"https://{slug}.personio.de"

        raw_location_str = raw_job.get("office") or ""

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

        return {
            "title": title.strip() if title else None,
            "company": company_name,
            "location": norm_location,
            "remote_type": remote_type,
            "salary": None,
            "experience": "Entry Level" if ("junior" in title_lower or "entry" in title_lower or "intern" in title_lower) else ("Senior" if ("senior" in title_lower or "lead" in title_lower) else None),
            "employment_type": raw_job.get("employmentType") or "Full-time",
            "description": "",
            "source": "Personio",
            "source_url": source_url,
            "posted_date": None
        }
