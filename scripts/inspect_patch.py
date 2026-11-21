import cv2
import numpy as np

corner = cv2.imread("output/debug_corner.png")
# corner shape: y is 850:1080 (height 230), x is 1500:1920 (width 420)
# Let's inspect what is in corner
print("Corner shape:", corner.shape)
# Watermark y is 980 - 850 = 130 to 130+55 = 185
# Watermark x is 1650 - 1500 = 150 to 150+235 = 385

# What is to the left of the watermark in the corner (x=0 to 140)?
left_of_wm = corner[:, :140]
print("Left of watermark mean:", np.mean(left_of_wm, axis=(0,1)))

# What is below the watermark (y=190 to 230)?
below_wm = corner[190:, 150:385]
print("Below watermark mean:", np.mean(below_wm, axis=(0,1)))

# What is above the watermark (y=0 to 125)?
above_wm = corner[:125, 150:385]
print("Above watermark mean:", np.mean(above_wm, axis=(0,1)))
print("Above watermark min/max:", np.min(above_wm), np.max(above_wm))

# What does the cleaned video have in that box?
clean_frame = cv2.imread("output/sample_cleaned_frame.png")
if clean_frame is not None:
    clean_box = clean_frame[980:1035, 1650:1885]
    print("Clean box mean:", np.mean(clean_box, axis=(0,1)))
    print("Clean box min/max:", np.min(clean_box), np.max(clean_box))
