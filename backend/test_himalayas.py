import httpx
import json

def test():
    url = "https://himalayas.app/jobs/api?limit=1"
    response = httpx.get(url)
    print(json.dumps(response.json(), indent=2))

if __name__ == "__main__":
    test()
