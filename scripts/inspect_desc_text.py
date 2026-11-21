import cv2
import numpy as np

img = cv2.imread("output/card_text_area.png")
# Title banner is around y=0:110 in this crop
title_area = img[10:105, :]
# Text area is around y=110:560
desc_area = img[110:560, :]

# Let's check non-black pixels in desc_area
white_pixels = np.where(desc_area > 150)
if len(white_pixels[0]) > 0:
    min_y, max_y = np.min(white_pixels[0]), np.max(white_pixels[0])
    min_x, max_x = np.min(white_pixels[1]), np.max(white_pixels[1])
    print(f"White text in desc area: y={min_y} to {max_y}, x={min_x} to {max_x}")
    # Let's save the text region
    text_crop = desc_area[min_y-10:max_y+10, min_x-10:max_x+10]
    cv2.imwrite("output/text_crop.png", text_crop)
    print("Saved text_crop.png, shape:", text_crop.shape)
