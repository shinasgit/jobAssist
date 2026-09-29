import asyncio
from unittest.mock import patch, MagicMock

from app.automation.location_utils import (
    is_bangalore_location,
    normalize_location_str,
    matches_location_filter,
    matches_title_or_keyword
)
from app.automation.adapters.bamboohr_adapter import BambooHRAdapter
from app.automation.adapters.personio_adapter import PersonioAdapter
from app.automation.adapters.smartrecruiters_adapter import SmartRecruitersAdapter
from app.automation.adapters.teamtailor_adapter import TeamtailorAdapter

def test_bamboohr_normalization():
    adapter = BambooHRAdapter()
    raw = {
        "id": 1234,
        "jobTitle": "Prompt Engineer & AI Specialist",
        "location": {
            "city": "Bengaluru",
            "state": "Karnataka",
            "country": "India"
        },
        "department": "Engineering"
    }
    norm = adapter.normalize_job(raw, company_name="Test BambooHR", domain="testbamboo")

    assert norm["title"] == "Prompt Engineer & AI Specialist"
    assert norm["company"] == "Test BambooHR"
    assert norm["location"] == "Bangalore, Karnataka, India"
    assert norm["source"] == "BambooHR"
    assert norm["source_url"] == "https://testbamboo.bamboohr.com/careers/1234"

def test_personio_normalization():
    adapter = PersonioAdapter()
    raw = {
        "title": "Junior Python Developer",
        "id": "personio-808",
        "office": "Bangalore Urban",
        "employmentType": "Full-time"
    }
    norm = adapter.normalize_job(raw, company_name="Test Personio", slug="testpersonio")

    assert norm["title"] == "Junior Python Developer"
    assert norm["company"] == "Test Personio"
    assert norm["location"] == "Bangalore, Karnataka, India"
    assert norm["source"] == "Personio"
    assert norm["source_url"] == "https://testpersonio.personio.de/job/personio-808"

def test_smartrecruiters_normalization():
    adapter = SmartRecruitersAdapter()
    raw = {
        "id": "sr-777",
        "name": "Backend Node.js Developer",
        "location": {
            "city": "Bangalore",
            "region": "Karnataka",
            "country": "IN",
            "remote": False
        },
        "typeOfEmployment": {
            "label": "Full-time"
        },
        "releasedDate": "2026-09-20T12:00:00Z"
    }
    norm = adapter.normalize_job(raw, company_name="Test SmartRecruiters", company_id="testsr")

    assert norm["title"] == "Backend Node.js Developer"
    assert norm["company"] == "Test SmartRecruiters"
    assert norm["location"] == "Bangalore, Karnataka, India"
    assert norm["source"] == "SmartRecruiters"
    assert norm["source_url"] == "https://jobs.smartrecruiters.com/testsr/sr-777"
    assert norm["posted_date"] == "2026-09-20"

def test_teamtailor_normalization():
    adapter = TeamtailorAdapter()
    raw = {
        "title": "Generative AI Engineer",
        "url": "https://test.teamtailor.com/jobs/123-genai",
        "location": "Electronic City, Bangalore",
        "body": "GenAI role in Electronic City."
    }
    norm = adapter.normalize_job(raw, company_name="Test Teamtailor")

    assert norm["title"] == "Generative AI Engineer"
    assert norm["company"] == "Test Teamtailor"
    assert norm["location"] == "Bangalore, Karnataka, India"
    assert norm["source"] == "Teamtailor"
    assert norm["source_url"] == "https://test.teamtailor.com/jobs/123-genai"

async def test_phase3_source_failure_isolation():
    bamboohr = BambooHRAdapter()
    personio = PersonioAdapter()
    smartrecruiters = SmartRecruitersAdapter()
    teamtailor = TeamtailorAdapter()

    with patch("httpx.AsyncClient.get") as mock_get:
        mock_resp_404 = MagicMock()
        mock_resp_404.status_code = 404
        mock_resp_404.raise_for_status.side_effect = Exception("404 Not Found")
        mock_get.return_value = mock_resp_404

        res_b = await bamboohr.search_jobs({"keyword": "Developer", "location": "Bangalore"})
        res_p = await personio.search_jobs({"keyword": "Developer", "location": "Bangalore"})
        res_s = await smartrecruiters.search_jobs({"keyword": "Developer", "location": "Bangalore"})
        res_t = await teamtailor.search_jobs({"keyword": "Developer", "location": "Bangalore"})

        assert isinstance(res_b, list)
        assert isinstance(res_p, list)
        assert isinstance(res_s, list)
        assert isinstance(res_t, list)

if __name__ == "__main__":
    test_bamboohr_normalization()
    test_personio_normalization()
    test_smartrecruiters_normalization()
    test_teamtailor_normalization()
    asyncio.run(test_phase3_source_failure_isolation())
    print("ALL PHASE 3 ADAPTER TESTS PASSED!")
