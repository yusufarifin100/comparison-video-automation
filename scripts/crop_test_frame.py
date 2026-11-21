import cv2

img = cv2.imread("output/test_affiliation_preview.png")
print("Panorama preview shape:", img.shape)
# Save 1920x1080 crop (what the viewer sees on screen)
frame_1080 = img[:, :1920]
cv2.imwrite("output/test_frame_1080.png", frame_1080)
print("Saved test_frame_1080.png")
