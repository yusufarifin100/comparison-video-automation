import cv2
import numpy as np

thresh = cv2.imread("output/thresh_t5.png", cv2.IMREAD_GRAYSCALE)
# Crop inner text area (y=100:300, x=50:430)
crop = thresh[100:300, 50:430]
# Downsample to 40x80 ASCII
small = cv2.resize(crop, (70, 25))
ascii_chars = " .:-=+*#%@"
lines = []
for row in small:
    line = "".join(ascii_chars[int(val / 255 * (len(ascii_chars) - 1))] for val in row)
    lines.append(line)
print("\n".join(lines))
