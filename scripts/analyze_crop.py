import cv2
import numpy as np

# Let's inspect the original frame
frame = cv2.imread("output/orig_frame_20s.png")
if frame is not None:
    print("Frame loaded successfully:", frame.shape)
    # watermark is at x=1650:y=980:w=235:h=55
    # Let's print the colors around it and in it
    crop_orig = frame[950:1080, 1600:1920]
    cv2.imwrite("output/crop_orig.png", crop_orig)
    
    # What is the background under the cards at y=950:1080?
    # Are cards present at y=980?
    # Where do cards end vertically?
    # Let's inspect rows around y=980
    print("Row 950 mean color (BGR):", np.mean(frame[950, :, :], axis=0))
    print("Row 980 mean color (BGR):", np.mean(frame[980, :, :], axis=0))
    print("Row 1000 mean color (BGR):", np.mean(frame[1000, :, :], axis=0))
    print("Row 1050 mean color (BGR):", np.mean(frame[1050, :, :], axis=0))
