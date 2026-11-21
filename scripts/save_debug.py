import cv2
import numpy as np

frame = cv2.imread("output/orig_frame_20s.png")
# Let's see what is at column 1600 to 1920 across rows 900 to 1080 WITHOUT the watermark
# Save a patch around x=1500 to 1920, y=850 to 1080
cv2.imwrite("output/debug_corner.png", frame[850:1080, 1500:1920])

# Let's inspect where cards actually are in this video
# What does the whole frame look like?
# Let's save a resized version to output/preview.png
preview = cv2.resize(frame, (960, 540))
cv2.imwrite("output/preview.png", preview)
print("Preview and debug corner saved")
