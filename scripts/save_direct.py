import cv2

cap = cv2.VideoCapture(r"E:\Youtube Project\RankingNoSekai\Tokyo Revenger\Video\Tokyo Revenger Affiliation.mp4")
fps = cap.get(cv2.CAP_PROP_FPS)

for t in [5, 20, 40]:
    cap.set(cv2.CAP_PROP_POS_FRAMES, int(t * fps))
    ret, frame = cap.read()
    if ret:
        card = frame[:, 720:1200]
        cv2.imwrite(f"output/inspect_card_t{t}.png", card)
        cv2.imwrite(f"output/inspect_title_t{t}.png", card[480:605, :])
        cv2.imwrite(f"output/inspect_text_t{t}.png", card[605:1060, :])
cap.release()
print("Saved inspect images directly from video")
