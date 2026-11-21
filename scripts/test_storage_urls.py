import urllib.request

fname = "6aecf8c029543f79d6953850.1794225775438.json"
candidates = [
    f"https://alienart.io/api/files/{fname}",
    f"https://alienart.io/files/{fname}",
    f"https://alienart.io/uploads/{fname}",
    f"https://storage.googleapis.com/alienart/{fname}",
    f"https://storage.googleapis.com/alienart-app/{fname}",
    f"https://storage.googleapis.com/alienart-production/{fname}",
    f"https://cdn.alienart.io/{fname}",
    f"https://assets.alienart.io/{fname}",
    f"https://alienart.io/api/spreadsheets/6aecf8c029543f79d6953850/data",
    f"https://alienart.io/api/spreadsheets/6aecf8c029543f79d6953850/download",
    f"https://alienart.io/api/spreadsheets/6aecf8c029543f79d6953850/export"
]

for url in candidates:
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    try:
        with urllib.request.urlopen(req, timeout=3) as resp:
            print("SUCCESS:", url, "Status:", resp.status, "Length:", len(resp.read()))
    except Exception as e:
        print("Failed:", url, "->", e)
