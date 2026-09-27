import httpx
import json

def test():
    url = "https://himalayas.app/jobs/api?q=Junior+AI+Developer+Bangalore&limit=1"
    response = httpx.get(url)
    print("q=...Bangalore:", [j['title'] for j in response.json().get('jobs', [])])

if __name__ == "__main__":
    test()
