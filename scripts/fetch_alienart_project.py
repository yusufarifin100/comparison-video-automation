import urllib.request
import json

project_id = "6aecf8c029543f79d695391b"
url = f"https://alienart.io/api/projects/{project_id}"
req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})

try:
    with urllib.request.urlopen(req) as resp:
        data = json.loads(resp.read().decode("utf-8"))
        print("Project keys:", list(data.keys()))
        print("Title:", data.get("title") or data.get("name"))
        cards = data.get("cards", [])
        print("Number of cards:", len(cards))
        if cards:
            print("First card sample:", json.dumps(cards[0], indent=2))
        # Also check elements or data
        if "data" in data:
            print("Data keys:", list(data["data"].keys()) if isinstance(data["data"], dict) else "not dict")
except Exception as e:
    print("Error:", e)
