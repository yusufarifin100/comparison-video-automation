import os
import csv

BASE_DIR = r"e:\App Dev\comparison-video-automation"
CSV_PATH = r"E:\Youtube Project\RankingNoSekai\Tokyo Revenger\Data\all chara evo.csv"
IMG_DIR = r"E:\Youtube Project\RankingNoSekai\Tokyo Revenger\Images\All Chara Evo"

with open(CSV_PATH, mode='r', encoding='utf-8') as f:
    reader = csv.reader(f, delimiter=';')
    header = next(reader)
    print("Header:", header)
    rows = list(reader)

print(f"Total rows in all chara evo: {len(rows)}")
for idx, r in enumerate(rows[:5], 1):
    print(f"{idx}. {r[0]}")
    print(f"   Top: {r[1][:60]}...")
    print(f"   Bot: {r[2][:60]}...")

# Check local images
if os.path.exists(IMG_DIR):
    local_files = os.listdir(IMG_DIR)
    print(f"Local files in All Chara Evo: {len(local_files)}")
    print("Sample local files:", local_files[:6])
