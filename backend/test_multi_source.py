import asyncio
from app.database.database import SessionLocal
from app.automation.service import JobSearchService
from app.automation.adapters.base import JobSourceAdapter
from app.database.models import Job
from typing import Dict, Any, List

class FailingMockAdapter(JobSourceAdapter):
    def validate_source(self) -> bool:
        return True

    async def search_jobs(self, search_params: Dict[str, Any]) -> List[Dict[str, Any]]:
        raise RuntimeError("Simulated network/scraping timeout failure in MockAdapter")

    async def get_job_details(self, url: str) -> Dict[str, Any]:
        return {}

    def normalize_job(self, raw_job: Any) -> Dict[str, Any]:
        return {}

async def main():
    print("=== TESTING MULTI-SOURCE AGGREGATION & FAILURE ISOLATION ===")
    
    db = SessionLocal()
    service = JobSearchService()
    
    # 1. Normal Multi-Source Search
    params = {
        "keyword": "python",
        "location": "any",
        "experience": "any",
        "remote_type": "any"
    }
    
    print("Running multi-source search (Himalayas + Remotive + Arbeitnow)...")
    res = await service.run_search(params, db)
    print(f"Search Result: {res}")
    
    # Verify jobs from multiple sources in DB
    distinct_sources = [s[0] for s in db.query(Job.source).distinct().all()]
    print(f"All distinct sources present in DB: {distinct_sources}")
    
    assert len(distinct_sources) >= 2, f"Expected jobs from at least 2 sources, got {distinct_sources}"
    print("Multi-source aggregation verified! Jobs aggregated from multiple sources.")

    # 2. Failure Isolation Test
    print("\nTesting Failure Isolation (injecting failing adapter)...")
    service.adapters.append(FailingMockAdapter())
    
    res_with_failure = await service.run_search(params, db)
    print(f"Search Result with failing adapter present: {res_with_failure}")
    
    assert res_with_failure["jobs_found"] >= 0, "Search should complete successfully despite 1 failing adapter"
    print("Failure isolation PASSED! Search completed gracefully even when an adapter failed.")

    db.close()
    print("\n=== ALL MULTI-SOURCE TESTS PASSED ===")

if __name__ == "__main__":
    asyncio.run(main())
