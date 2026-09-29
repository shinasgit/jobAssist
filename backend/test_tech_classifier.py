import asyncio
from app.automation.tech_classifier import is_tech_job
from app.automation.adapters.workday_adapter import WorkdayAdapter

def test_tech_classification():
    # IT/Tech roles must pass
    assert is_tech_job("Junior AI Developer", "Building GenAI models") is True
    assert is_tech_job("Software Engineer - Backend", "Python and Node") is True
    assert is_tech_job("React Frontend Developer", "React and TypeScript") is True
    assert is_tech_job("DevOps Engineer", "Kubernetes and AWS") is True
    assert is_tech_job("QA Test Engineer", "Automation with Selenium") is True
    assert is_tech_job("Data Scientist", "Python and PyTorch") is True
    assert is_tech_job("Prompt Engineer", "LLM fine-tuning") is True

    # Non-tech roles must be excluded
    assert is_tech_job("HR Manager", "Handling employee relations") is False
    assert is_tech_job("Talent Acquisition Specialist", "Recruiting sales personnel") is False
    assert is_tech_job("Senior Accountant", "Managing balance sheets") is False
    assert is_tech_job("Sales Executive", "Closing deals with clients") is False
    assert is_tech_job("Legal Counsel", "Drafting corporate contracts") is False
    assert is_tech_job("Customer Support Agent", "Answering phone calls") is False

def test_workday_normalization():
    adapter = WorkdayAdapter()
    raw = {
        "title": "Software Engineer - AI Platform",
        "externalPath": "/job/Bangalore-India/Software-Engineer_R-505",
        "locationsText": "Bangalore, India",
        "postedOn": "Posted 2 Days Ago",
        "bulletFields": ["R-505", "Full time"]
    }
    norm = adapter.normalize_job(raw, company_name="Walmart", tenant="walmart", datacenter="wd5", site="Walmart_Careers")

    assert norm["title"] == "Software Engineer - AI Platform"
    assert norm["company"] == "Walmart"
    assert norm["location"] == "Bangalore, Karnataka, India"
    assert norm["source"] == "Workday"
    assert norm["source_url"] == "https://walmart.wd5.myworkdayjobs.com/en-US/Walmart_Careers/job/Bangalore-India/Software-Engineer_R-505"

if __name__ == "__main__":
    test_tech_classification()
    test_workday_normalization()
    print("ALL TECH CLASSIFIER & WORKDAY TESTS PASSED!")
