import asyncio
from unittest.mock import patch, MagicMock

from app.automation.location_utils import (
    is_bangalore_location,
    normalize_location_str,
    matches_location_filter,
    matches_title_or_keyword
)
from app.automation.adapters.workable_adapter import WorkableAdapter
from app.automation.adapters.recruitee_adapter import RecruiteeAdapter
from app.automation.adapters.breezy_adapter import BreezyAdapter

def test_workable_normalization():
    adapter = WorkableAdapter()
    raw = {
        "title": "Junior GenAI Engineer",
        "shortcode": "WORK-101",
        "url": "https://apply.workable.com/testcompany/j/WORK-101/",
        "location": {
            "city": "Bengaluru",
            "region": "Karnataka",
            "country": "India"
        },
        "telecommute": True,
        "published": "2026-09-24",
        "description": "Building Generative AI applications in Bangalore."
    }
    norm = adapter.normalize_job(raw, company_name="Test Workable", account_slug="testcompany")

    assert norm["title"] == "Junior GenAI Engineer"
    assert norm["company"] == "Test Workable"
    assert norm["location"] == "Bangalore, Karnataka, India"
    assert norm["remote_type"] in ["Remote", "Worldwide"]
    assert norm["source"] == "Workable"
    assert norm["source_url"] == "https://apply.workable.com/testcompany/j/WORK-101/"
    assert norm["posted_date"] == "2026-09-24"

def test_recruitee_normalization():
    adapter = RecruiteeAdapter()
    raw = {
        "id": 99912,
        "title": "Full Stack Developer (React / Node)",
        "careers_url": "https://testco.recruitee.com/o/full-stack-developer",
        "city": "Bellandur, Bangalore",
        "country_code": "IN",
        "remote": False,
        "created_at": "2026-09-22T08:00:00Z",
        "description": "MERN stack developer needed in Bellandur, Bangalore."
    }
    norm = adapter.normalize_job(raw, company_name="Test Recruitee")

    assert norm["title"] == "Full Stack Developer (React / Node)"
    assert norm["company"] == "Test Recruitee"
    assert norm["location"] == "Bangalore, Karnataka, India"
    assert norm["source"] == "Recruitee"
    assert norm["source_url"] == "https://testco.recruitee.com/o/full-stack-developer"
    assert norm["posted_date"] == "2026-09-22"

def test_breezy_normalization():
    adapter = BreezyAdapter()
    raw = {
        "_id": "brz-505",
        "name": "Python & AI Developer",
        "url": "https://testco.breezy.hr/p/brz-505-python-ai-developer",
        "location": {
            "name": "HSR Layout, Bengaluru",
            "city": "Bengaluru",
            "is_remote": False
        },
        "creation_date": "2026-09-21T10:00:00.000Z",
        "type": {
            "name": "Full Time"
        },
        "description": "Python developer in HSR Layout."
    }
    norm = adapter.normalize_job(raw, company_name="Test Breezy")

    assert norm["title"] == "Python & AI Developer"
    assert norm["company"] == "Test Breezy"
    assert norm["location"] == "Bangalore, Karnataka, India"
    assert norm["source"] == "Breezy"
    assert norm["source_url"] == "https://testco.breezy.hr/p/brz-505-python-ai-developer"
    assert norm["posted_date"] == "2026-09-21"

async def test_phase2_source_failure_isolation():
    workable = WorkableAdapter()
    recruitee = RecruiteeAdapter()
    breezy = BreezyAdapter()

    with patch("httpx.AsyncClient.get") as mock_get:
        mock_resp_404 = MagicMock()
        mock_resp_404.status_code = 404
        mock_resp_404.raise_for_status.side_effect = Exception("404 Not Found")
        mock_get.return_value = mock_resp_404

        res_wk = await workable.search_jobs({"keyword": "Developer", "location": "Bangalore"})
        res_rc = await recruitee.search_jobs({"keyword": "Developer", "location": "Bangalore"})
        res_bz = await breezy.search_jobs({"keyword": "Developer", "location": "Bangalore"})

        assert isinstance(res_wk, list)
        assert isinstance(res_rc, list)
        assert isinstance(res_bz, list)

if __name__ == "__main__":
    test_workable_normalization()
    test_recruitee_normalization()
    test_breezy_normalization()
    asyncio.run(test_phase2_source_failure_isolation())
    print("ALL PHASE 2 ADAPTER TESTS PASSED!")
