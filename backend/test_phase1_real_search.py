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
            "enabled_sources": ["greenhouse", "lever", "ashby", "himalayas", "remotive", "arbeitnow"]
        }
        print("--- RUNNING REAL MULTI-SOURCE SEARCH (PHASE 1) ---")
        res = await job_search_service.run_search(search_params, db)
        print("Search Results Summary:", res)
    finally:
        db.close()

if __name__ == "__main__":
    asyncio.run(main())
