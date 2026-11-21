import os
import csv
import re

csv_path = r"E:\Youtube Project\RankingNoSekai\Tokyo Revenger\Data\tokyo_revengers_gang_affiliations.csv"
img_dir = r"E:\Youtube Project\RankingNoSekai\Tokyo Revenger\Images\Height"

with open(csv_path, mode='r', encoding='utf-8') as f:
    reader = csv.DictReader(f, delimiter=';')
    rows = list(reader)

print(f"Loaded {len(rows)} rows from affiliations CSV.")

# Let's inspect what gangs / lines each character has
for r in rows:
    name = r["Highlight"]
    elem = r["Element"]
    print(f"{name:25} | {elem}")
