import urllib.request
import json

project_id = "6aecf8c029543f79d695391b"
url = f"https://alienart.io/api/projects/{project_id}"
req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})

with urllib.request.urlopen(req) as resp:
    data = json.loads(resp.read().decode("utf-8"))

s = data["spreadsheets"][0]
print("headers:", s.get("headers"))
print("rows:", s.get("rows"))
print("columns:", s.get("columns"))
print("fileName:", s.get("fileName"))
print("_id:", s.get("_id"))
# Can we fetch spreadsheet via api?
sheet_id = s.get("_id")
sheet_url = f"https://alienart.io/api/spreadsheets/{sheet_id}"
req2 = urllib.request.Request(sheet_url, headers={"User-Agent": "Mozilla/5.0"})
try:
    with urllib.request.urlopen(req2) as resp2:
        sheet_data = json.loads(resp2.read().decode("utf-8"))
        print("Fetched sheet directly:", list(sheet_data.keys()))
        if "data" in sheet_data:
            print("Direct sheet data length:", len(sheet_data["data"]))
            if len(sheet_data["data"]) > 0:
                print("First row:", sheet_data["data"][0])
except Exception as e:
    print("Direct sheet fetch error:", e)
