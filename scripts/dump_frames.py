import cv2

# Let's save frames at 0s, 10s, 30s, 60s
cap = cv2.VideoCapture(r"E:\Youtube Project\RankingNoSekai\Tokyo Revenger\Video\Tokyo Revenger Affiliation.mp4")
fps = cap.get(cv2.CAP_PROP_FPS)

for t in [0, 5, 15, 30, 60]:
    cap.set(cv2.CAP_PROP_POS_FRAMES, int(t * fps))
    ret, frame = cap.read()
    if ret:
        cv2.imwrite(f"output/frame_{t}s.png", frame)
        print(f"Saved frame_{t}s.png")
cap.release()
