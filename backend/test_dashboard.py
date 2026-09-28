from fastapi.testclient import TestClient
from app.main import app
from app.database.database import SessionLocal
from app.database import models
from datetime import datetime, timezone, timedelta

client = TestClient(app)

def test_dashboard_endpoint():
    print("=== TESTING DASHBOARD API ===")
    
    # Query database directly
    db = SessionLocal()
    total_jobs = db.query(models.Job).count()
    seven_days_ago = datetime.now(timezone.utc) - timedelta(days=7)
    new_jobs = db.query(models.Job).filter(models.Job.discovered_at >= seven_days_ago).count()
    saved_jobs = db.query(models.SavedJob).count()
    applications = db.query(models.Application).count()
    db.close()

    # Call /api/dashboard
    response = client.get("/api/dashboard")
    assert response.status_code == 200, f"Dashboard API failed: {response.text}"
    data = response.json()

    print(f"API Response Counts:")
    print(f" - total_jobs: {data['total_jobs']} (DB: {total_jobs})")
    print(f" - new_jobs: {data['new_jobs']} (DB: {new_jobs})")
    print(f" - saved_jobs: {data['saved_jobs']} (DB: {saved_jobs})")
    print(f" - applications: {data['applications']} (DB: {applications})")

    assert data["total_jobs"] == total_jobs, "total_jobs API count does not match SQLite"
    assert data["new_jobs"] == new_jobs, "new_jobs API count does not match SQLite"
    assert data["saved_jobs"] == saved_jobs, "saved_jobs API count does not match SQLite"
    assert data["applications"] == applications, "applications API count does not match SQLite"

    assert isinstance(data["recent_jobs"], list)
    assert isinstance(data["recent_saved_jobs"], list)
    assert isinstance(data["recent_applications"], list)

    print(f" - Recent Jobs returned: {len(data['recent_jobs'])}")
    print(f" - Recent Saved Jobs returned: {len(data['recent_saved_jobs'])}")
    print(f" - Recent Applications returned: {len(data['recent_applications'])}")

    print("=== DASHBOARD API TESTS PASSED SUCCESSFULLY ===")

if __name__ == "__main__":
    test_dashboard_endpoint()
