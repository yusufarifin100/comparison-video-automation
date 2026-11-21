import os
import csv
import re

img_dir = r"E:\Youtube Project\RankingNoSekai\Tokyo Revenger\Images\Height"
csv_path = r"E:\Youtube Project\RankingNoSekai\Tokyo Revenger\Data\tokyo_revengers_gang_affiliations.csv"

images = os.listdir(img_dir)
print(f"Total images in Height: {len(images)}")

# Load affiliations CSV
with open(csv_path, mode='r', encoding='utf-8') as f:
    reader = csv.DictReader(f)
    rows = list(reader)

print(f"Total characters in affiliations CSV: {len(rows)}")

def clean_name(n):
    # remove parenthetical nickname
    base = re.sub(r'\(.*?\)', '', n).strip().lower()
    return re.sub(r'[^a-z0-9]', '', base)

matched = []
unmatched = []

for r in rows:
    name = r["name"]
    c_name = clean_name(name)
    found_img = None
    for img in images:
        img_base = os.path.splitext(img)[0]
        c_img = clean_name(img_base)
        if c_name == c_img or c_name in c_img or c_img in c_name:
            found_img = img
            break
    if found_img:
        matched.append((name, found_img, r["current_affiliation"], r["former_positions"]))
    else:
        unmatched.append(name)

print(f"Matched: {len(matched)}")
print(f"Unmatched: {len(unmatched)}")
if unmatched:
    print("Unmatched character names:", unmatched)
