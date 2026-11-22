import os
import csv
import urllib.request
import hashlib
from PIL import Image

BASE_DIR = r"e:\App Dev\comparison-video-automation"
CSV_PATH = r"E:\Youtube Project\RankingNoSekai\Tokyo Revenger\Data\all chara evo.csv"
CACHE_DIR = os.path.join(BASE_DIR, "output", ".cache_images")
os.makedirs(CACHE_DIR, exist_ok=True)

with open(CSV_PATH, mode='r', encoding='utf-8') as f:
    reader = csv.reader(f, delimiter=';')
    header = next(reader)
    rows = list(reader)

print(f"Checking & caching images for {len(rows)} characters...")

def fetch_img(url):
    if not url or not url.startswith("http"):
        return None
    h = hashlib.md5(url.encode("utf-8")).hexdigest()
    local_path = os.path.join(CACHE_DIR, f"{h}.jpg")
    if os.path.exists(local_path) and os.path.getsize(local_path) > 1000:
        return local_path
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=10) as res, open(local_path, "wb") as f_out:
            f_out.write(res.read())
        return local_path
    except Exception as e:
        print(f"Error fetching {url}: {e}")
        return None

success = 0
for idx, r in enumerate(rows, 1):
    name, top_url, bot_url = r[0], r[1], r[2]
    p1 = fetch_img(top_url)
    p2 = fetch_img(bot_url)
    if p1 and p2:
        success += 1
    if idx % 10 == 0 or idx == len(rows):
        print(f"  Processed [{idx}/{len(rows)}]: {success} pairs ready.")

print(f"✅ Total successful character image pairs cached: {success}/{len(rows)}")
