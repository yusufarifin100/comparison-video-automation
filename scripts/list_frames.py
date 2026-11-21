import cv2
import glob

# Let's inspect text or print details from frame_0s and frame_15s
for path in sorted(glob.glob("output/frame_*s.png")):
    print("Found frame:", path)
