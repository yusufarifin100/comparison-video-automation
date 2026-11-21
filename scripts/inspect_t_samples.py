import cv2
import numpy as np

# Let's inspect the text in t=5, 15, 30, 50
for t in [5, 15, 30, 50]:
    txt_img = cv2.imread(f"output/sample_affiliation_text_t{t}.png")
    title_img = cv2.imread(f"output/sample_affiliation_title_t{t}.png")
    print(f"--- t={t}s ---")
    print("Title img shape:", title_img.shape)
    print("Text img shape:", txt_img.shape)
    # Check inner pixels in txt_img
    inner = txt_img[:, 20:460]
    print("Inner min/max/mean:", np.min(inner), np.max(inner), np.mean(inner))
