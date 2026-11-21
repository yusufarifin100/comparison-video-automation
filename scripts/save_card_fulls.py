import cv2

# Let's save a clear visual of text_t5, text_t15, text_t30, text_t50
for t in [5, 15, 30, 50]:
    card = cv2.imread(f"output/sample_affiliation_card_t{t}.png")
    if card is not None:
        cv2.imwrite(f"output/card_full_t{t}.png", card)
print("Saved card_full images")
