import cv2
import numpy as np

img = cv2.imread("output/card_crop_5s.png")
if img is not None:
    print("Crop 5s shape:", img.shape)
    # Find card borders
    # Let's see what is at y=0:500 (image), y=500:610 (title banner), y=610:1080 (lower box)
    # Let's save slices to inspect
    cv2.imwrite("output/slice_top.png", img[:500, :])
    cv2.imwrite("output/slice_mid.png", img[500:620, :])
    cv2.imwrite("output/slice_bot.png", img[620:, :])
    print("Slices saved successfully")
