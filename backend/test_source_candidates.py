import urllib.request
import json
import ssl

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
}

def check_remotive():
    print("--- Testing Remotive API ---")
    url = "https://remotive.com/api/remote-jobs?search=python&limit=10"
    try:
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, timeout=10, context=ctx) as resp:
            data = json.loads(resp.read().decode())
            jobs = data.get("jobs", [])
            print(f"Remotive jobs returned: {len(jobs)}")
            if jobs:
                j = jobs[0]
                print(f"Sample: Title: {j.get('title')}, Company: {j.get('company_name')}, Location: {j.get('candidate_required_location')}, URL: {j.get('url')}")
            return True
    except Exception as e:
        print(f"Remotive failed: {e}")
        return False

def check_arbeitnow():
    print("\n--- Testing Arbeitnow API ---")
    url = "https://www.arbeitnow.com/api/job-board-api"
    try:
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, timeout=10, context=ctx) as resp:
            data = json.loads(resp.read().decode())
            jobs = data.get("data", [])
            print(f"Arbeitnow jobs returned: {len(jobs)}")
            if jobs:
                j = jobs[0]
                print(f"Sample: Title: {j.get('title')}, Company: {j.get('company_name')}, Location: {j.get('location')}, URL: {j.get('url')}")
            return True
    except Exception as e:
        print(f"Arbeitnow failed: {e}")
        return False

if __name__ == "__main__":
    check_remotive()
    check_arbeitnow()
