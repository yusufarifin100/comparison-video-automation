import cv2

frame = cv2.imread("output/frame_5s.png")
if frame is not None:
    print("Frame 5s loaded:", frame.shape)
    # Save slices from the card in the middle around x=700 to 1200
    card = frame[:, 720:1200]
    cv2.imwrite("output/card_full_5s.png", card)
    print("Card full saved")
