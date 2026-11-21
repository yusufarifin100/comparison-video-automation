import cv2
from PIL import Image

# Read original video frame at t=20s
cap = cv2.VideoCapture(r"E:\Youtube Project\RankingNoSekai\Tokyo Revenger\Video\Tokyo Revenger Affiliation.mp4")
fps = cap.get(cv2.CAP_PROP_FPS)
cap.set(cv2.CAP_PROP_POS_FRAMES, int(20 * fps))
ret, frame = cap.read()
if ret:
    cv2.imwrite("output/orig_frame_20s.png", frame)
    # crop bottom right
    # 1920x1080
    h, w, _ = frame.shape
    crop_orig = frame[950:1080, 1600:1920]
    cv2.imwrite("output/crop_orig.png", crop_orig)
    print("Orig frame saved, shape:", frame.shape)
cap.release()

# Read cleaned video frame at t=20s
cap_clean = cv2.VideoCapture(r"E:\Youtube Project\RankingNoSekai\Tokyo Revenger\Video\Tokyo Revenger Affiliation_NoWatermark.mp4")
cap_clean.set(cv2.CAP_PROP_POS_FRAMES, int(20 * fps))
ret2, frame_clean = cap_clean.read()
if ret2:
    crop_clean = frame_clean[950:1080, 1600:1920]
    cv2.imwrite("output/crop_clean.png", crop_clean)
    print("Clean frame saved")
cap_clean.release()
