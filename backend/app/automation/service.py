import asyncio
import logging
from typing import List, Dict, Any
from sqlalchemy.orm import Session

from app.automation.adapters.himalayas_adapter import HimalayasAdapter
from app.automation.adapters.remotive_adapter import RemotiveAdapter
from app.automation.adapters.arbeitnow_adapter import ArbeitnowAdapter
from app.automation.adapters.greenhouse_adapter import GreenhouseAdapter
from app.automation.adapters.lever_adapter import LeverAdapter
from app.automation.adapters.ashby_adapter import AshbyAdapter
from app.automation.adapters.workable_adapter import WorkableAdapter
from app.automation.adapters.recruitee_adapter import RecruiteeAdapter
from app.automation.adapters.breezy_adapter import BreezyAdapter
from app.automation.adapters.bamboohr_adapter import BambooHRAdapter
from app.automation.adapters.personio_adapter import PersonioAdapter
from app.automation.adapters.smartrecruiters_adapter import SmartRecruitersAdapter
from app.automation.adapters.teamtailor_adapter import TeamtailorAdapter
from app.automation.adapters.workday_adapter import WorkdayAdapter
from app.automation.tech_classifier import is_tech_job
from app.automation.registry import get_company_category
from app.database.models import Job


logger = logging.getLogger(__name__)

class JobSearchService:
    def __init__(self):
        # Register active job source adapters
        self.adapters = [
            HimalayasAdapter(),
            RemotiveAdapter(),
            ArbeitnowAdapter(),
            GreenhouseAdapter(),
            LeverAdapter(),
            AshbyAdapter(),
            WorkableAdapter(),
            RecruiteeAdapter(),
            BreezyAdapter(),
            BambooHRAdapter(),
            PersonioAdapter(),
            SmartRecruitersAdapter(),
            TeamtailorAdapter(),
            WorkdayAdapter(),
        ]

    async def _fetch_from_adapter(self, adapter, search_params: dict) -> List[Dict[str, Any]]:
        adapter_name = adapter.__class__.__name__
        if not adapter.validate_source():
            logger.info(f"Adapter {adapter_name} validation failed or source disabled")
            return []
        
        logger.info(f"Executing search with {adapter_name}")
        try:
            jobs = await adapter.search_jobs(search_params)
            logger.info(f"Adapter {adapter_name} returned {len(jobs)} jobs")
            return jobs
        except Exception as e:
            logger.error(f"Adapter {adapter_name} failed with error: {e}", exc_info=True)
            return []

    async def run_search(self, search_params: dict, db: Session) -> Dict[str, Any]:
        # Filter adapters by enabled_sources
        enabled_sources = search_params.get("enabled_sources")
        if enabled_sources is None:
            from app.database import models
            import json
            setting_obj = db.query(models.Setting).first()
            if setting_obj and setting_obj.enabled_sources:
                try:
                    enabled_sources = json.loads(setting_obj.enabled_sources)
                except Exception:
                    enabled_sources = None

        if enabled_sources is not None:
            enabled_set = set(s.lower().strip() for s in enabled_sources)
            active_adapters = [
                a for a in self.adapters
                if a.__class__.__name__.lower().replace("adapter", "") in enabled_set
            ]
        else:
            active_adapters = self.adapters

        logger.info(f"Starting multi-source job search with {len(active_adapters)} active adapters: {[a.__class__.__name__ for a in active_adapters]}")

        # Run active adapters concurrently with failure isolation
        tasks = [self._fetch_from_adapter(adapter, search_params) for adapter in active_adapters]
        results = await asyncio.gather(*tasks, return_exceptions=True)

        all_jobs = []
        source_counts: Dict[str, int] = {}
        failed_sources: List[Dict[str, str]] = []

        for adapter, res in zip(active_adapters, results):
            source_key = adapter.__class__.__name__.lower().replace("adapter", "")
            if isinstance(res, list):
                all_jobs.extend(res)
                source_counts[source_key] = len(res)
            elif isinstance(res, Exception):
                logger.error(f"Async gather returned exception for {source_key}: {res}")
                source_counts[source_key] = 0
                failed_sources.append({
                    "source": source_key,
                    "reason": str(res)
                })

        logger.info(f"Total raw jobs aggregated across sources: {len(all_jobs)}")

        # Filter jobs for IT/Tech roles only
        tech_filtered_jobs = []
        for j in all_jobs:
            if is_tech_job(j.get("title"), j.get("description")):
                tech_filtered_jobs.append(j)

        logger.info(f"Jobs after IT/Tech filter: {len(tech_filtered_jobs)} (from {len(all_jobs)} raw)")

        # Deduplicate and save
        inserted_count = 0
        skipped_count = 0

        for job_dict in tech_filtered_jobs:
            if not job_dict.get("title") or not job_dict.get("source_url"):
                continue

            # Primary deduplication: (source + source_url)
            existing = db.query(Job).filter(
                Job.source == job_dict["source"],
                Job.source_url == job_dict["source_url"]
            ).first()

            if not existing:
                # Secondary fallback deduplication: (company + title + location)
                existing_fallback = db.query(Job).filter(
                    Job.company == job_dict.get("company"),
                    Job.title == job_dict.get("title"),
                    Job.location == job_dict.get("location")
                ).first()
                if existing_fallback:
                    skipped_count += 1
                    continue
            else:
                skipped_count += 1
                continue

            # Determine source category (MNC, STARTUP, IT_TECH, REMOTE)
            cat = get_company_category(job_dict.get("company"), job_dict.get("source"))

            # Insert new job into SQLite
            new_job = Job(
                title=job_dict["title"],
                company=job_dict.get("company"),
                location=job_dict.get("location"),
                remote_type=job_dict.get("remote_type"),
                salary=job_dict.get("salary"),
                experience=job_dict.get("experience"),
                employment_type=job_dict.get("employment_type"),
                description=job_dict.get("description"),
                source=job_dict["source"],
                source_category=cat,
                source_url=job_dict["source_url"],
                posted_date=job_dict.get("posted_date")
            )

            db.add(new_job)
            inserted_count += 1

        db.commit()
        logger.info(f"Multi-source search complete. Inserted: {inserted_count}, Skipped duplicates: {skipped_count}")

        return {
            "jobs_found": len(tech_filtered_jobs),
            "jobs_inserted": inserted_count,
            "duplicates_skipped": skipped_count,
            "sources": source_counts,
            "failed_sources": failed_sources,
            "location": search_params.get("location", "Bangalore"),
            "category": "IT / Tech"
        }

job_search_service = JobSearchService()


