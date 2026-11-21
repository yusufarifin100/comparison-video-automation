import cv2
import numpy as np

# In card_full_t5, what character is it?
card5 = cv2.imread("output/card_full_t5.png")
# Title banner is y=480:600
# Text banner is y=600:1060
# Let's save both in high contrast
title5 = card5[480:600, :]
text5 = card5[600:1060, :]

cv2.imwrite("output/title5.png", title5)
cv2.imwrite("output/text5.png", text5)

card30 = cv2.imread("output/card_full_t30.png")
cv2.imwrite("output/title30.png", card30[480:600, :])
cv2.imwrite("output/text30.png", card30[600:1060, :])
print("Saved titles and texts for t=5 and t=30")
