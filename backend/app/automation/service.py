from app.automation.adapters.himalayas_adapter import HimalayasAdapter
from app.database.models import Job
from sqlalchemy.orm import Session
import logging

logger = logging.getLogger(__name__)

class JobSearchService:
    def __init__(self):
        # We can eventually make this a registry, but for now just use Himalayas
        self.adapters = [HimalayasAdapter()]

    async def run_search(self, search_params: dict, db: Session):
        all_jobs = []
        for adapter in self.adapters:
            logger.info(f"Running search with {adapter.__class__.__name__}")
            if adapter.validate_source():
                try:
                    jobs = await adapter.search_jobs(search_params)
                    all_jobs.extend(jobs)
                except Exception as e:
                    logger.error(f"Adapter {adapter.__class__.__name__} failed: {e}")
        
        # Deduplicate and save
        inserted_count = 0
        skipped_count = 0
        
        for job_dict in all_jobs:
            if not job_dict.get("title") or not job_dict.get("source_url"):
                continue
                
            # Deduplication: Primary (source + source_url)
            existing = db.query(Job).filter(
                Job.source == job_dict["source"],
                Job.source_url == job_dict["source_url"]
            ).first()
            
            if not existing:
                # Fallback: company + title + location
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
                
            # Insert
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
                source_url=job_dict["source_url"],
                posted_date=job_dict.get("posted_date")
            )
            db.add(new_job)
            inserted_count += 1
            
        db.commit()
        return {
            "jobs_found": len(all_jobs),
            "jobs_inserted": inserted_count,
            "duplicates_skipped": skipped_count
        }

job_search_service = JobSearchService()
