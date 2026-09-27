import asyncio
from app.database.database import SessionLocal
from app.automation.service import job_search_service

async def test_searches():
    db = SessionLocal()
    
    tests = [
        {
            "name": "TEST 1",
            "params": {
                "keyword": "Junior AI Developer",
                "location": "Bangalore",
                "experience": "Fresher",
                "remote_type": "Any",
                "posted_date": "Last 7 days"
            }
        },
        {
            "name": "TEST 2",
            "params": {
                "keyword": "React Developer",
                "location": "Bangalore",
                "experience": "Fresher",
                "remote_type": "Any",
                "posted_date": "Last 30 days"
            }
        },
        {
            "name": "TEST 3",
            "params": {
                "keyword": "Software Engineer",
                "location": "Any",
                "experience": "Any",
                "remote_type": "Remote",
                "posted_date": "Any"
            }
        }
    ]
    
    for t in tests:
        print(f"--- {t['name']} ---")
        result = await job_search_service.run_search(t["params"], db)
        print("Result:", result)
        print()
        
    db.close()

if __name__ == "__main__":
    asyncio.run(test_searches())
