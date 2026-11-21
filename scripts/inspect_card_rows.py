import cv2
import numpy as np

card = cv2.imread("output/card_full_5s.png")
# Let's inspect rows from 0 to 1080
# Mean color of center slice (x=100 to 380)
mid_x = card[:, 100:380]
for y in range(0, 1080, 50):
    row_mean = np.mean(mid_x[y:y+10, :], axis=(0,1))
    print(f"y={y}: BGR={row_mean.astype(int)}")
