import os
import csv
from PIL import Image
from render_affiliation_preview import (
    render_affiliation_card, find_local_image, 
    CARD_W, CARD_H, STEP_W, PAD_LEFT, PAD_TOP, PAD_RIGHT, CANVAS_W, CANVAS_H
)

csv_path = r"E:\Youtube Project\RankingNoSekai\Tokyo Revenger\Data\tokyo_revengers_gang_affiliations.csv"
output_preview = r"output/test_affiliation_preview.png"

with open(csv_path, mode='r', encoding='utf-8') as f:
    reader = csv.DictReader(f, delimiter=';')
    rows = list(reader)

# Pick 5 diverse characters:
# 1. Mikey (3 gangs)
# 2. Kokonoi (5 gangs)
# 3. Senju (2 gangs)
# 4. Draken (2 gangs)
# 5. Smiley (1 gang)
test_chars = ["Manjiro Sano", "Hajime Kokonoi", "Senju Kawaragi", "Ken Ryuguji", "Nahoya Kawata"]
selected_rows = [r for r in rows if r["Highlight"] in test_chars]

cards = []
for r in selected_rows:
    img_local = find_local_image(r["Highlight"])
    card = render_affiliation_card({
        "name": r["Highlight"],
        "img_path": img_local,
        "affiliation": r["Element"]
    })
    cards.append(card)

n = len(cards)
total_w = PAD_LEFT + (n - 1) * STEP_W + CARD_W + PAD_RIGHT
panorama = Image.new("RGB", (total_w, CANVAS_H), (255, 255, 255))

for idx, card in enumerate(cards):
    pos_x = PAD_LEFT + idx * STEP_W
    panorama.paste(card, (pos_x, PAD_TOP))

# Save panorama preview
panorama.save(output_preview)
print(f"Saved test preview with {n} cards to {output_preview}")
