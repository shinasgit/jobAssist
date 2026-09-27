import asyncio
from app.database.database import SessionLocal
from app.automation.service import job_search_service

async def test_search():
    db = SessionLocal()
    search_params = {
        "keyword": "Junior AI Developer",
        "location": "Bangalore",
        "experience": "Fresher",
        "remote_type": "Any"
    }
    
    result = await job_search_service.run_search(search_params, db)
    print("Search Result:", result)
    db.close()

if __name__ == "__main__":
    asyncio.run(test_search())
