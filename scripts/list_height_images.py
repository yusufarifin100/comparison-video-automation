import os
import csv
import re

img_dir = r"E:\Youtube Project\RankingNoSekai\Tokyo Revenger\Images\Height"
images = sorted(os.listdir(img_dir))

# Check who is in Images/Height
print(f"Total images in Images/Height: {len(images)}")
for idx, img in enumerate(images, 1):
    print(f"{idx}. {img}")
