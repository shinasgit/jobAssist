import sys
from fastapi.testclient import TestClient
from app.main import app
from app.database.database import SessionLocal
from app.database import models

client = TestClient(app)

def test_applications_flow():
    print("=== TESTING APPLICATIONS FLOW ===")
    
    # 1. Create a test job directly in DB or via endpoint
    db = SessionLocal()
    job = models.Job(
        title="Test Applications Engineer",
        company="Test Corp",
        location="Remote",
        remote_type="Remote",
        source="himalayas",
        source_url="https://example.com/test-app-job-1"
    )
    db.add(job)
    try:
        db.commit()
        db.refresh(job)
        job_id = job.id
        print(f"Created test job ID: {job_id}")
    except Exception as e:
        db.rollback()
        existing = db.query(models.Job).filter(models.Job.source_url == "https://example.com/test-app-job-1").first()
        job_id = existing.id
        print(f"Using existing test job ID: {job_id}")
    finally:
        db.close()

    # 2. Clean up any existing application for this job
    db = SessionLocal()
    existing_app = db.query(models.Application).filter(models.Application.job_id == job_id).first()
    if existing_app:
        db.delete(existing_app)
        db.commit()
    db.close()

    # 3. GET /api/applications initially
    res = client.get("/api/applications")
    assert res.status_code == 200, f"GET /api/applications failed: {res.text}"
    print("GET /api/applications status code 200 OK")

    # 4. POST /api/applications/{job_id} (Mark Applied)
    res = client.post(f"/api/applications/{job_id}")
    assert res.status_code == 200, f"POST /api/applications/{job_id} failed: {res.text}"
    app_data = res.json()
    assert app_data["status"] == "APPLIED", f"Expected APPLIED, got {app_data['status']}"
    assert app_data["job_id"] == job_id
    assert app_data["applied_at"] is not None
    print(f"POST /api/applications/{job_id} PASSED. Status: {app_data['status']}")

    # 5. TEST DUPLICATE APPLICATION: POST again to same job_id
    res_dup = client.post(f"/api/applications/{job_id}")
    assert res_dup.status_code == 409, f"Expected 409 for duplicate application, got {res_dup.status_code}: {res_dup.text}"
    print("POST duplicate application correctly returned HTTP 409 Conflict")

    # 6. TEST NONEXISTENT JOB: POST /api/applications/999999
    res_404 = client.post("/api/applications/999999")
    assert res_404.status_code == 404, f"Expected 404 for nonexistent job, got {res_404.status_code}"
    print("POST nonexistent job correctly returned HTTP 404 Not Found")

    # 7. PATCH /api/applications/{job_id} (Update status to INTERVIEW and add notes)
    res_patch = client.patch(
        f"/api/applications/{job_id}",
        json={"status": "INTERVIEW", "notes": "Technical interview scheduled."}
    )
    assert res_patch.status_code == 200, f"PATCH failed: {res_patch.text}"
    updated_data = res_patch.json()
    assert updated_data["status"] == "INTERVIEW"
    assert updated_data["notes"] == "Technical interview scheduled."
    assert updated_data["applied_at"] == app_data["applied_at"], "applied_at timestamp should remain unchanged"
    print("PATCH /api/applications status & notes update PASSED")

    # 8. GET /api/applications (Verify job structure included)
    res_list = client.get("/api/applications")
    assert res_list.status_code == 200
    apps_list = res_list.json()
    found = [a for a in apps_list if a["job_id"] == job_id]
    assert len(found) == 1, f"Expected 1 application record, found {len(found)}"
    assert found[0]["job"]["title"] == "Test Applications Engineer"
    print("GET /api/applications contains populated job object PASSED")

    # 9. Clean up test application and job
    db = SessionLocal()
    app_to_del = db.query(models.Application).filter(models.Application.job_id == job_id).first()
    if app_to_del:
        db.delete(app_to_del)
    job_to_del = db.query(models.Job).filter(models.Job.id == job_id).first()
    if job_to_del:
        db.delete(job_to_del)
    db.commit()
    db.close()

    print("=== ALL APPLICATION API TESTS PASSED SUCCESSFULLY ===")

if __name__ == "__main__":
    test_applications_flow()
