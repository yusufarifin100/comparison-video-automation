import os
import csv
import re

img_dir = r"E:\Youtube Project\RankingNoSekai\Tokyo Revenger\Images\Height"
csv_path = r"E:\Youtube Project\RankingNoSekai\Tokyo Revenger\Data\tokyo_revengers_gang_affiliations.csv"

images = os.listdir(img_dir)
print(f"Total images in Height: {len(images)}")

with open(csv_path, mode='r', encoding='utf-8') as f:
    reader = csv.DictReader(f, delimiter=';')
    rows = list(reader)

print(f"Total rows in CSV: {len(rows)}")

def clean_name(n):
    base = re.sub(r'\(.*?\)', '', n).strip().lower()
    return re.sub(r'[^a-z0-9]', '', base)

matched = []
unmatched = []

for r in rows:
    name = r["Highlight"]
    c_name = clean_name(name)
    found_img = None
    for img in images:
        img_base = os.path.splitext(img)[0]
        c_img = clean_name(img_base)
        if c_name == c_img or c_name in c_img or c_img in c_name:
            found_img = img
            break
    if found_img:
        matched.append((name, found_img, r["Element"]))
    else:
        unmatched.append(name)

print(f"Matched: {len(matched)} / {len(rows)}")
for m in matched[:10]:
    print(f" - {m[0]} -> {m[1]} ({m[2]})")
if unmatched:
    print("Unmatched:", unmatched)
