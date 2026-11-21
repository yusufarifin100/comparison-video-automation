import cv2

card = cv2.imread("output/card_full_5s.png")
if card is not None:
    # Save the text area
    cv2.imwrite("output/card_text_area.png", card[500:1060, :])
    print("Saved card_text_area.png")
