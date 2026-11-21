import cv2
import numpy as np

# Let's inspect inspect_text_t5, t20, t40
for t in [5, 20, 40]:
    txt = cv2.imread(f"output/inspect_text_t{t}.png")
    if txt is not None:
        # Check text rows
        inner = txt[:, 30:450]
        mean_row = np.mean(inner, axis=(1,2))
        active = np.where(mean_row > 15)[0]
        print(f"t={t}s active rows: {len(active)}, ranges: {active[0] if len(active) else 0} to {active[-1] if len(active) else 0}")
        # Save high contrast binarized
        gray = cv2.cvtColor(txt, cv2.COLOR_BGR2GRAY)
        _, thresh = cv2.threshold(gray, 120, 255, cv2.THRESH_BINARY)
        cv2.imwrite(f"output/thresh_t{t}.png", thresh)

print("Binarized text saved")
