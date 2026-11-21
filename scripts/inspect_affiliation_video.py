import cv2
import numpy as np

# Sample every 5 seconds from Tokyo Revenger Affiliation.mp4
cap = cv2.VideoCapture(r"E:\Youtube Project\RankingNoSekai\Tokyo Revenger\Video\Tokyo Revenger Affiliation.mp4")
fps = cap.get(cv2.CAP_PROP_FPS)
total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
duration = total_frames / fps
print(f"Video duration: {duration:.1f}s, total frames: {total_frames}, fps: {fps}")

# Let's check card titles at different times
# The title banner is at y=502 to 607, let's crop and save title banner samples
timestamps = [2, 10, 20, 30, 45, 60, 80, 100]
for t in timestamps:
    cap.set(cv2.CAP_PROP_POS_FRAMES, int(t * fps))
    ret, frame = cap.read()
    if ret:
        # crop title area across center of screen x=700:1220, y=500:610
        crop = frame[500:610, 700:1220]
        cv2.imwrite(f"output/title_t{t}.png", crop)

cap.release()
print("Saved title crops")
