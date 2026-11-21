import cv2
import numpy as np

img = cv2.imread("output/sample_affiliation_text_t30.png")
# Let's find horizontal projection (row intensity) of text
inner = img[:, 30:450]
row_intensity = np.mean(inner, axis=(1, 2))
# Print rows that have characters
active_rows = []
for y, val in enumerate(row_intensity):
    if val > 15:
        active_rows.append(y)

print(f"Total active text rows at t=30s: {len(active_rows)}")
# Group contiguous rows
lines = []
if active_rows:
    cur = [active_rows[0]]
    for r in active_rows[1:]:
        if r == cur[-1] + 1:
            cur.append(r)
        else:
            if len(cur) > 8: # meaningful line height
                lines.append((cur[0], cur[-1]))
            cur = [r]
    if len(cur) > 8:
        lines.append((cur[0], cur[-1]))

print(f"Detected lines: {len(lines)}")
for idx, (y1, y2) in enumerate(lines):
    print(f"Line {idx+1}: y={y1} to {y2} (h={y2-y1+1})")
