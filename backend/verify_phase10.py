import asyncio
import logging
from app.database.database import SessionLocal
from app.automation.service import job_search_service
from app.database import models
from sqlalchemy import func

logging.basicConfig(level=logging.INFO)

async def run_verification():
    print("==================================================")
    print("  PHASE 10 FINAL VERIFICATION — MULTI-SOURCE SEARCH")
    print("==================================================\n")
    
    db = SessionLocal()
    
    # 1. Run real multi-source search
    search_params = {
        "keyword": "Junior AI Developer",
        "location": "Bangalore",
        "experience": "Fresher",
        "remote_type": "any"
    }
    
    print(f"1. Executing real search with parameters:")
    print(f"   Keyword: {search_params['keyword']}")
    print(f"   Location: {search_params['location']}")
    print(f"   Experience: {search_params['experience']}")
    print(f"   Remote: {search_params['remote_type']}\n")
    
    res1 = await job_search_service.run_search(search_params, db)
    print(f"Search Execution #1 Result:")
    print(f" - Jobs Found across sources: {res1['jobs_found']}")
    print(f" - Jobs Inserted to SQLite: {res1['jobs_inserted']}")
    print(f" - Duplicates Skipped: {res1['duplicates_skipped']}\n")

    # 2. Re-run search to verify deduplication behavior
    print("2. Re-executing exact same search to verify deduplication...")
    res2 = await job_search_service.run_search(search_params, db)
    print(f"Search Execution #2 Result:")
    print(f" - Jobs Found across sources: {res2['jobs_found']}")
    print(f" - Jobs Inserted to SQLite: {res2['jobs_inserted']}")
    print(f" - Duplicates Skipped: {res2['duplicates_skipped']}\n")

    assert res2['jobs_inserted'] == 0, f"Expected 0 new insertions on repeated search, got {res2['jobs_inserted']}"
    assert res2['duplicates_skipped'] == res2['jobs_found'], "All found jobs should be flagged as duplicates on repeat"
    print("[OK] Deduplication logic verified: Repeated search correctly skipped all duplicates!\n")

    # 3. Database Breakdown & Inspection
    print("3. SQLite Database Inspection & Statistics:")
    total_jobs = db.query(models.Job).count()
    saved_jobs = db.query(models.SavedJob).count()
    applications = db.query(models.Application).count()

    print(f" - Total Jobs in Database: {total_jobs}")
    print(f" - Total Saved Jobs: {saved_jobs}")
    print(f" - Total Applications Tracked: {applications}\n")

    # Jobs by Source
    source_counts = db.query(models.Job.source, func.count(models.Job.id)).group_by(models.Job.source).all()
    print(" - Breakdown of Jobs by Source:")
    for src, count in source_counts:
        print(f"     • {src or 'Unknown'}: {count} jobs")

    print("\n4. Sample Jobs Inspection (verifying fields & Bangalore filter):")
    recent_jobs = db.query(models.Job).order_by(models.Job.id.desc()).limit(5).all()
    for idx, j in enumerate(recent_jobs, 1):
        print(f"   [{idx}] Title: {j.title}")
        print(f"       Company: {j.company}")
        print(f"       Location: {j.location}")
        print(f"       Source: {j.source} ({j.source_url})")
        print(f"       Remote: {j.remote_type} | Exp: {j.experience} | Salary: {j.salary}")
        print(f"       Posted: {j.posted_date} | Discovered: {j.discovered_at}\n")

    db.close()
    print("==================================================")
    print("  PHASE 10 VERIFICATION SCRIPT EXECUTED CLEANLY   ")
    print("==================================================")

if __name__ == "__main__":
    asyncio.run(run_verification())
