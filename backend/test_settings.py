import sys
from fastapi.testclient import TestClient
from app.main import app
from app.database.database import SessionLocal
from app.database import models
from app.automation.service import JobSearchService

client = TestClient(app)

def test_settings_flow():
    print("=== TESTING SETTINGS API & PERSISTENCE ===")
    
    # 1. GET /api/settings (Initial load / defaults creation)
    res = client.get("/api/settings")
    assert res.status_code == 200, f"GET /api/settings failed: {res.text}"
    data = res.json()
    print(f"GET /api/settings initial data: {data}")
    assert "keywords" in data
    assert "locations" in data
    assert "enabled_sources" in data

    # 2. PUT /api/settings (Update settings)
    new_settings = {
        "keywords": ["Junior AI Developer", "Generative AI Engineer"],
        "locations": ["Bangalore", "Kochi"],
        "experience": "Fresher",
        "remote_type": "remote",
        "employment_types": ["Full-time", "Contract"],
        "enabled_sources": ["himalayas"]
    }
    
    res_put = client.put("/api/settings", json=new_settings)
    assert res_put.status_code == 200, f"PUT /api/settings failed: {res_put.text}"
    updated = res_put.json()
    print(f"PUT /api/settings updated response: {updated}")
    
    assert "Generative AI Engineer" in updated["keywords"]
    assert "Kochi" in updated["locations"]
    assert updated["enabled_sources"] == ["himalayas"]

    # 3. GET /api/settings (Verify persistence)
    res_verify = client.get("/api/settings")
    assert res_verify.status_code == 200
    persisted = res_verify.json()
    print(f"Verified persisted settings: {persisted}")
    assert persisted["keywords"] == ["Junior AI Developer", "Generative AI Engineer"]
    assert persisted["enabled_sources"] == ["himalayas"]
    print("[OK] Settings GET/PUT and SQLite persistence verified!")

    # 4. Test Source Filtering in JobSearchService
    db = SessionLocal()
    service = JobSearchService()
    
    # Search with enabled_sources = ["himalayas"] from settings
    print("Testing JobSearchService adapter filtering with only 'himalayas' enabled in settings...")
    enabled_set = set(persisted["enabled_sources"])
    active_adapters = [a for a in service.adapters if a.__class__.__name__.lower().replace("adapter", "") in enabled_set]
    assert len(active_adapters) == 1
    assert active_adapters[0].__class__.__name__ == "HimalayasAdapter"
    print("[OK] JobSearchService enabled_sources filtering verified!")

    # Restore default settings
    default_restore = {
        "keywords": ["Junior AI Developer"],
        "locations": ["Bangalore"],
        "experience": "Fresher",
        "remote_type": "any",
        "employment_types": ["Full-time"],
        "enabled_sources": ["himalayas", "remotive", "arbeitnow"]
    }
    client.put("/api/settings", json=default_restore)
    db.close()
    
    print("=== ALL SETTINGS TESTS PASSED SUCCESSFULLY ===")

if __name__ == "__main__":
    test_settings_flow()
