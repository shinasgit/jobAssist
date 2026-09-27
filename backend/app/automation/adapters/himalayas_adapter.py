from app.automation.adapters.base import JobSourceAdapter
from typing import Dict, Any, List
import httpx
import logging
from datetime import datetime, timezone, timedelta

logger = logging.getLogger(__name__)

class HimalayasAdapter(JobSourceAdapter):
    BASE_URL = "https://himalayas.app/jobs/api"

    async def search_jobs(self, search_params: Dict[str, Any]) -> List[Dict[str, Any]]:
        url = f"{self.BASE_URL}/search"
        
        # Map parameters
        params = {}
        if search_params.get("keyword"):
            params["q"] = search_params["keyword"]
            
        # Remote (Himalayas is all remote, but worldwide limits to truly worldwide jobs)
        remote = search_params.get("remote_type", "").lower()
        if remote in ["any", "worldwide"]:
            params["worldwide"] = "true"
            
        # Experience
        exp = search_params.get("experience", "").lower()
        if exp and ("fresher" in exp or "0" in exp or "entry" in exp):
            params["seniority"] = "entry-level"
        elif exp and "mid" in exp:
            params["seniority"] = "mid-level"
            
        params["limit"] = 50 # Fetch a bit more so we can filter locally
        
        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(url, params=params, timeout=15.0)
                response.raise_for_status()
                data = response.json()
                
                raw_jobs = data.get("jobs", [])
                
                normalized_jobs = []
                for raw in raw_jobs:
                    norm = self.normalize_job(raw)
                    if self._passes_local_filters(norm, search_params):
                        normalized_jobs.append(norm)
                        if len(normalized_jobs) >= 15: # Stop once we have enough good matches
                            break
                            
                return normalized_jobs
            except httpx.HTTPStatusError as e:
                logger.error(f"Himalayas API HTTP error: {e}")
                return []
            except Exception as e:
                logger.error(f"Error fetching from Himalayas API: {e}")
                return []

    def _passes_local_filters(self, job: Dict[str, Any], search_params: Dict[str, Any]) -> bool:
        # Location filter
        location = search_params.get("location", "").lower()
        if location and location not in ["any", "worldwide", "remote"]:
            job_loc = (job.get("location") or "").lower()
            job_title = (job.get("title") or "").lower()
            # If job is strictly worldwide, we can assume it applies to this location
            # If it's not worldwide, check if the location matches
            if job_loc != "worldwide":
                if location not in job_loc and location not in job_title:
                    return False
        
        # Posted date filter
        posted_filter = search_params.get("posted_date", "").lower()
        if posted_filter and posted_filter != "any":
            posted_str = job.get("posted_date")
            if not posted_str:
                return False
            
            try:
                posted = datetime.fromisoformat(posted_str).replace(tzinfo=timezone.utc)
                now = datetime.now(timezone.utc)
                
                if "today" in posted_filter:
                    if now - posted > timedelta(days=1):
                        return False
                elif "3 days" in posted_filter:
                    if now - posted > timedelta(days=3):
                        return False
                elif "7 days" in posted_filter:
                    if now - posted > timedelta(days=7):
                        return False
                elif "30 days" in posted_filter:
                    if now - posted > timedelta(days=30):
                        return False
            except Exception as e:
                pass
                
        return True

    async def get_job_details(self, url: str) -> Dict[str, Any]:
        return {}

    def normalize_job(self, raw_job: Any) -> Dict[str, Any]:
        title = raw_job.get("title")
        company = raw_job.get("companyName")
        
        # Determine remote_type
        worldwide = False
        location = raw_job.get("locationRestrictions", [])
        if not location:
            worldwide = True
            
        remote_type = "Worldwide" if worldwide else "Remote"
        loc_str = ", ".join(location) if location else "Worldwide"
        
        # Salary formatting
        salary_min = raw_job.get("minSalary")
        salary_max = raw_job.get("maxSalary")
        currency = raw_job.get("currency", "USD")
        
        if salary_min is not None and salary_max is not None and salary_min > 0:
            if raw_job.get("salaryPeriod") == "hourly":
                salary = f"${salary_min} - ${salary_max} {currency}/hr"
            else:
                # Some APIs return 160000, some return 160. Let's format properly
                min_fmt = f"{salary_min // 1000}k" if salary_min >= 1000 else f"{salary_min}k"
                max_fmt = f"{salary_max // 1000}k" if salary_max >= 1000 else f"{salary_max}k"
                salary = f"${min_fmt} - ${max_fmt} {currency}"
        else:
            salary = None
            
        seniority = raw_job.get("seniority", [])
        exp = ", ".join(seniority) if seniority else None
        emp_type = raw_job.get("employmentType")
        desc = raw_job.get("description")
        
        pub_date = raw_job.get("pubDate")
        posted_date = None
        if pub_date:
            try:
                posted_date = datetime.fromtimestamp(pub_date, tz=timezone.utc).isoformat()
            except:
                pass
        
        return {
            "title": title or None,
            "company": company or None,
            "location": loc_str or None,
            "remote_type": remote_type or None,
            "salary": salary or None,
            "experience": exp or None,
            "employment_type": emp_type or None,
            "description": desc or None,
            "source": "Himalayas",
            "source_url": raw_job.get("applicationLink") or raw_job.get("himalayasLink"),
            "posted_date": posted_date
        }

    def validate_source(self) -> bool:
        return True
