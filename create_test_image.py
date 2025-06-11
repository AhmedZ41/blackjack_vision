import cv2
import numpy as np

# Create a simple test image
img = np.zeros((200, 300, 3), dtype=np.uint8)
cv2.rectangle(img, (50, 50), (150, 150), (255, 255, 255), -1)

# Save as JPEG
cv2.imwrite('test_image.jpg', img)
print("Created test_image.jpg")
