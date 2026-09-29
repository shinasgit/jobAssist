import asyncio
from unittest.mock import patch, MagicMock

from app.automation.location_utils import (
    is_bangalore_location,
    normalize_location_str,
    matches_location_filter,
    matches_title_or_keyword
)
from app.automation.adapters.greenhouse_adapter import GreenhouseAdapter
from app.automation.adapters.lever_adapter import LeverAdapter
from app.automation.adapters.ashby_adapter import AshbyAdapter

def test_bangalore_location_normalization():

    # Test valid Bangalore localities
    assert is_bangalore_location("Bangalore, India") is True
    assert is_bangalore_location("Bengaluru, Karnataka") is True
    assert is_bangalore_location("Whitefield, Bangalore") is True
    assert is_bangalore_location("Koramangala 4th Block") is True
    assert is_bangalore_location("Electronic City Phase 1") is True
    assert is_bangalore_location("Manyata Tech Park") is True
    assert is_bangalore_location("HSR Layout, Sector 1") is True
    assert is_bangalore_location("Outer Ring Road, Bellandur") is True
    assert is_bangalore_location("Indiranagar 100ft road") is True
    assert is_bangalore_location("Yelahanka, Bengaluru") is True

    # Test normalization function
    assert normalize_location_str("Koramangala, Bengaluru") == "Bangalore, Karnataka, India"

    # Test non-Bangalore Karnataka locations (must NOT match Bangalore)
    assert is_bangalore_location("Mysore, Karnataka") is False
    assert is_bangalore_location("Hubli, Karnataka") is False
    assert is_bangalore_location("Mangalore, India") is False
    assert is_bangalore_location("Belgaum") is False

def test_title_matching():
    # AI Developer match
    assert matches_title_or_keyword("Software Engineer - AI Platform", "", "AI Engineer") is True
    assert matches_title_or_keyword("Junior AI Developer", "", "AI Developer") is True
    assert matches_title_or_keyword("Senior Backend Engineer", "", "AI Engineer") is False
    assert matches_title_or_keyword("Full Stack Developer (React/Node)", "", "Full Stack Developer") is True

def test_greenhouse_normalization():
    adapter = GreenhouseAdapter()
    raw = {
        "id": 101,
        "title": "Senior AI Developer",
        "absolute_url": "https://boards.greenhouse.io/testcompany/jobs/101",
        "location": {"name": "Bengaluru, Karnataka, India"},
        "updated_at": "2026-09-25T14:30:00Z",
        "content": "<p>We are hiring an AI Developer in Bangalore.</p>"
    }
    norm = adapter.normalize_job(raw, company_name="Test Company")

    assert norm["title"] == "Senior AI Developer"
    assert norm["company"] == "Test Company"
    assert norm["location"] == "Bangalore, Karnataka, India"
    assert norm["source"] == "Greenhouse"
    assert norm["source_url"] == "https://boards.greenhouse.io/testcompany/jobs/101"
    assert norm["salary"] is None
    assert norm["posted_date"] == "2026-09-25"

def test_lever_normalization():
    adapter = LeverAdapter()
    raw = {
        "id": "lever-123",
        "text": "React Frontend Engineer",
        "hostedUrl": "https://jobs.lever.co/testcompany/lever-123",
        "createdAt": 1758787200000,
        "categories": {
            "location": "Whitefield, Bengaluru",
            "commitment": "Full-time"
        },
        "workplaceType": "onsite",
        "description": "<p>Join our frontend team in Whitefield.</p>"
    }
    norm = adapter.normalize_job(raw, company_name="Test Lever")

    assert norm["title"] == "React Frontend Engineer"
    assert norm["company"] == "Test Lever"
    assert norm["location"] == "Bangalore, Karnataka, India"
    assert norm["source"] == "Lever"
    assert norm["employment_type"] == "Full-time"
    assert norm["posted_date"] is not None

def test_ashby_normalization():
    adapter = AshbyAdapter()
    raw = {
        "id": "ashby-99",
        "title": "Machine Learning Engineer",
        "locationName": "Bangalore",
        "isRemote": True,
        "jobUrl": "https://jobs.ashbyhq.com/testashby/ashby-99",
        "publishedAt": "2026-09-20T10:00:00.000Z",
        "employmentType": "FullTime",
        "compensation": {
            "compensationTierSummary": "₹20,00,000 - ₹35,00,000 INR"
        },
        "descriptionHtml": "<p>ML position in Bangalore or Remote</p>"
    }
    norm = adapter.normalize_job(raw, company_name="Test Ashby")

    assert norm["title"] == "Machine Learning Engineer"
    assert norm["company"] == "Test Ashby"
    assert norm["location"] == "Bangalore, Karnataka, India"
    assert norm["remote_type"] in ["Remote", "Worldwide"]
    assert norm["salary"] == "₹20,00,000 - ₹35,00,000 INR"
    assert norm["source"] == "Ashby"

async def test_source_failure_isolation():

    greenhouse = GreenhouseAdapter()
    lever = LeverAdapter()
    ashby = AshbyAdapter()

    # Mock client 404/500 errors
    with patch("httpx.AsyncClient.get") as mock_get:
        mock_resp_404 = MagicMock()
        mock_resp_404.status_code = 404
        mock_resp_404.raise_for_status.side_effect = Exception("404 Not Found")
        mock_get.return_value = mock_resp_404

        # Calling search_jobs should isolate errors and return empty list rather than raising
        res_gh = await greenhouse.search_jobs({"keyword": "Developer", "location": "Bangalore"})
        res_lv = await lever.search_jobs({"keyword": "Developer", "location": "Bangalore"})
        res_as = await ashby.search_jobs({"keyword": "Developer", "location": "Bangalore"})

        assert isinstance(res_gh, list)
        assert isinstance(res_lv, list)
        assert isinstance(res_as, list)

if __name__ == "__main__":
    test_bangalore_location_normalization()
    test_title_matching()
    test_greenhouse_normalization()
    test_lever_normalization()
    test_ashby_normalization()
    asyncio.run(test_source_failure_isolation())
    print("ALL PHASE 1 ADAPTER TESTS PASSED!")
