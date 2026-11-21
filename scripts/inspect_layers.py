import urllib.request
import json

project_id = "6aecf8c029543f79d695391b"
url = f"https://alienart.io/api/projects/{project_id}"
req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})

with urllib.request.urlopen(req) as resp:
    data = json.loads(resp.read().decode("utf-8"))

proj = data["project"]
print("thumbnailUrl:", proj.get("thumbnailUrl"))
print("layers count:", len(proj.get("layers", [])))
if proj.get("layers"):
    print("first layer:", json.dumps(proj["layers"][0], indent=2)[:500])
print("scenes:", proj.get("scenes"))
