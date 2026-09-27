import requests

def test_saved_jobs():
    BASE_URL = "http://localhost:8000/api"
    
    print("Testing GET /saved-jobs (initial)")
    res = requests.get(f"{BASE_URL}/saved-jobs")
    print(res.status_code, res.json())
    
    print("\nTesting POST /saved-jobs/6")
    res = requests.post(f"{BASE_URL}/saved-jobs/6")
    print(res.status_code, res.json())
    
    print("\nTesting POST /saved-jobs/6 (duplicate)")
    res = requests.post(f"{BASE_URL}/saved-jobs/6")
    print(res.status_code, res.json())
    
    print("\nTesting GET /saved-jobs (after save)")
    res = requests.get(f"{BASE_URL}/saved-jobs")
    print(res.status_code, res.json())
    
    print("\nTesting DELETE /saved-jobs/6")
    res = requests.delete(f"{BASE_URL}/saved-jobs/6")
    print(res.status_code)
    
    print("\nTesting DELETE /saved-jobs/6 (not found)")
    res = requests.delete(f"{BASE_URL}/saved-jobs/6")
    print(res.status_code, res.json())

if __name__ == "__main__":
    test_saved_jobs()
