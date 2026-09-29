import asyncio
import logging
from app.database.database import SessionLocal
from app.automation.service import job_search_service

logging.basicConfig(level=logging.INFO)

async def main():
    db = SessionLocal()
    try:
        search_params = {
            "keyword": "Developer",
            "location": "Bangalore",
            "remote_type": "any",
            "enabled_sources": [
                "himalayas", "remotive", "arbeitnow",
                "greenhouse", "lever", "ashby",
                "workable", "recruitee", "breezy",
                "bamboohr", "personio", "smartrecruiters", "teamtailor"
            ]
        }

        print("=== FINAL ACCEPTANCE VERIFICATION — MULTI-SOURCE SEARCH ===")
        res = await job_search_service.run_search(search_params, db)
        print("\n--- SEARCH SUMMARY METRICS ---")
        print(f"Total jobs found across sources: {res['jobs_found']}")
        print(f"Total jobs inserted into SQLite: {res['jobs_inserted']}")
        print(f"Total duplicates skipped: {res['duplicates_skipped']}")
        print("\nPer-Source Breakdown:")
        for source_name, count in res["sources"].items():
            print(f"  - {source_name}: {count} jobs")

    finally:
        db.close()

if __name__ == "__main__":
    asyncio.run(main())
