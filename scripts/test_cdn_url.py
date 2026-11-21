import urllib.request
import csv

with open(r"E:\Youtube Project\RankingNoSekai\Tokyo Revenger\Data\Last Hierarchy Toman.csv", mode='r', encoding='utf-8') as f:
    reader = csv.reader(f, delimiter=';')
    header = next(reader)
    print("Header:", header)
    rows = list(reader)
    print("Total rows:", len(rows))
    first_url = rows[0][0]
    print("Testing first URL:", first_url)
    
req = urllib.request.Request(first_url, headers={"User-Agent": "Mozilla/5.0"})
try:
    with urllib.request.urlopen(req, timeout=5) as resp:
        print("URL Status:", resp.status, "Content-Length:", resp.headers.get("Content-Length"))
        print("CDN URL IS 100% ACCESSIBLE AND PUBLIC!")
except Exception as e:
    print("Failed to load CDN URL:", e)
