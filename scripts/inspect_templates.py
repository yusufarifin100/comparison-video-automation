import cv2
import json

# Let's inspect the dimensions, card layout, and text of frame_15s
frame = cv2.imread("output/frame_15s.png")
print("Frame shape:", frame.shape)

# Let's check which AlienArt template corresponds to Affiliation
# Let's check config/templates/
import os
for f in os.listdir("config/templates"):
    if f.endswith(".json") and f != "catalog.json":
        data = json.load(open(os.path.join("config/templates", f), encoding="utf-8"))
        print(f, "-> project_name:", data.get("project_name"), "boxes:", [b.get("name") for b in data.get("boxes", [])])
