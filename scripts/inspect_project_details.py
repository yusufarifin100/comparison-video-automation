import urllib.request
import json

project_id = "6aecf8c029543f79d695391b"
url = f"https://alienart.io/api/projects/{project_id}"
req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})

with urllib.request.urlopen(req) as resp:
    data = json.loads(resp.read().decode("utf-8"))
    
proj = data.get("project", {})
print("Project title:", proj.get("title"))
print("Spreadsheets count:", len(data.get("spreadsheets", [])))
spreadsheets = data.get("spreadsheets", [])
for s in spreadsheets:
    print("Spreadsheet keys:", list(s.keys()))
    if "data" in s:
        print("Spreadsheet data type:", type(s["data"]))
        if isinstance(s["data"], list):
            print("Spreadsheet rows:", len(s["data"]))
            if len(s["data"]) > 0:
                print("First row:", s["data"][0])
                print("Second row:", s["data"][1] if len(s["data"]) > 1 else "None")
        elif isinstance(s["data"], dict):
            print("Spreadsheet data keys:", list(s["data"].keys()))

# Also check proj elements / cards
print("Project keys:", list(proj.keys()))
if "elements" in proj:
    print("Elements count:", len(proj["elements"]))
    for el in proj["elements"]:
        print(" - Element:", el.get("title"), el.get("type"), el.get("mediaUrl"))
