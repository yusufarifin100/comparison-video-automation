import cv2

cap = cv2.VideoCapture(r"E:\Youtube Project\RankingNoSekai\Tokyo Revenger\Video\Tokyo Revenger Affiliation.mp4")
fps = cap.get(cv2.CAP_PROP_FPS)

# Sample at t=5s, 15s, 30s, 50s
for t in [5, 15, 30, 50]:
    cap.set(cv2.CAP_PROP_POS_FRAMES, int(t * fps))
    ret, frame = cap.read()
    if ret:
        # Card at center (x=720:1200)
        card = frame[:, 720:1200]
        cv2.imwrite(f"output/sample_affiliation_card_t{t}.png", card)
        # title
        cv2.imwrite(f"output/sample_affiliation_title_t{t}.png", card[490:610, :])
        # text
        cv2.imwrite(f"output/sample_affiliation_text_t{t}.png", card[610:1060, :])
cap.release()
print("Saved sample affiliation cards")
