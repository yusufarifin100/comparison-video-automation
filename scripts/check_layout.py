import cv2
import numpy as np

frame = cv2.imread("output/orig_frame_20s.png")
# Let's inspect where cards are located vertically
# Find columns and rows where pixel value is not black (> 25)
non_black = np.any(frame > 25, axis=2)
row_has_content = np.any(non_black, axis=1)
col_has_content = np.any(non_black, axis=0)

min_y, max_y = np.where(row_has_content)[0][[0, -1]]
min_x, max_x = np.where(col_has_content)[0][[0, -1]]

print(f"Content vertical range: y={min_y} to y={max_y}")
print(f"Content horizontal range: x={min_x} to x={max_x}")

# Let's check what is at y=900 to 1080 across all x
print("Check rows 900 to 1079:")
for y in range(900, 1080, 20):
    active_cols = np.where(non_black[y, :])[0]
    if len(active_cols) > 0:
        print(f"y={y}: non-black cols from {active_cols[0]} to {active_cols[-1]} (count: {len(active_cols)})")
    else:
        print(f"y={y}: entirely black")
