import urllib.request
import json

project_id = "6aecf8c029543f79d695391b"
url = f"https://alienart.io/api/projects/{project_id}"
req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})

with urllib.request.urlopen(req) as resp:
    data = json.loads(resp.read().decode("utf-8"))

sheet_id = data["spreadsheets"][0]["_id"]
req2 = urllib.request.Request(f"https://alienart.io/api/spreadsheets/{sheet_id}", headers={"User-Agent": "Mozilla/5.0"})
with urllib.request.urlopen(req2) as resp2:
    s_full = json.loads(resp2.read().decode("utf-8"))

print(json.dumps(s_full, indent=2)[:1500])
