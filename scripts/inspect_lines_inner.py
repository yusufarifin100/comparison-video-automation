import cv2
import numpy as np

bot = cv2.imread("output/inspect_bottom_area.png")
# Exclude borders x < 15 and x > 465
inner = bot[:, 15:465]
row_max = np.max(inner, axis=(1, 2))
text_rows = np.where(row_max > 180)[0]
print("Rows with text (inner):", len(text_rows))
if len(text_rows) > 0:
    diffs = np.diff(text_rows)
    split_indices = np.where(diffs > 10)[0]
    line_bounds = []
    start = text_rows[0]
    for idx in split_indices:
        end = text_rows[idx]
        line_bounds.append((start, end))
        start = text_rows[idx+1]
    line_bounds.append((start, text_rows[-1]))
    print("Found text lines:", len(line_bounds))
    for i, (s, e) in enumerate(line_bounds):
        print(f"Line {i+1}: y={s} to {e} (height {e-s+1})")
        cv2.imwrite(f"output/line_{i+1}.png", inner[max(0, s-5):min(bot.shape[0], e+5), :])
