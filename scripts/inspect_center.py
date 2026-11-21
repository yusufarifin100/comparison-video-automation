import cv2
import numpy as np

bot = cv2.imread("output/inspect_bottom_area.png")
print("bot shape:", bot.shape)
# Print central pixels sample
print("Center (y=225, x=240):", bot[225, 240])
print("Mean BGR of bot[100:350, 50:430]:", np.mean(bot[100:350, 50:430], axis=(0,1)))
print("Max pixel in that area:", np.max(bot[100:350, 50:430]))
print("Min pixel in that area:", np.min(bot[100:350, 50:430]))
