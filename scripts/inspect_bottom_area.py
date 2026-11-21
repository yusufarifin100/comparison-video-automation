import cv2
import numpy as np

# Load the text area image
img = cv2.imread("output/card_text_area.png")
if img is not None:
    # Save a slice of the bottom text area
    cv2.imwrite("output/inspect_bottom_area.png", img[110:, :])
    # Let's inspect unique colors or mean color in bottom area
    bot = img[110:, :]
    print("Bottom area shape:", bot.shape)
    print("Bottom area mean color BGR:", np.mean(bot, axis=(0,1)))
    print("Bottom area min/max:", np.min(bot), np.max(bot))
