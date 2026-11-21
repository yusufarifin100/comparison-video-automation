import cv2

# Crop title and description area from frame_5s and frame_15s
frame_5s = cv2.imread("output/frame_5s.png")
if frame_5s is not None:
    # 1920x1080
    # Let's save a crop of the card at center
    # title is y=500:620
    # desc is y=620:1000
    cv2.imwrite("output/card_crop_5s.png", frame_5s[:, :600])

frame_15s = cv2.imread("output/frame_15s.png")
if frame_15s is not None:
    cv2.imwrite("output/card_crop_15s.png", frame_15s[:, :600])

print("Saved card crops")
