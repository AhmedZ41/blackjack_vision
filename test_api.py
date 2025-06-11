#!/usr/bin/env python3
import requests
import cv2
import numpy as np

# Create a simple test image
test_image = np.zeros((200, 300, 3), dtype=np.uint8)
test_image[:] = (50, 50, 50)  # Dark gray background

# Save it temporarily
cv2.imwrite("/tmp/test_card_image.jpg", test_image)

# Test the API
url = "http://localhost:8000/analyze/"
files = {'file': open('/tmp/test_card_image.jpg', 'rb')}
data = {'players': 1}

try:
    response = requests.post(url, files=files, data=data)
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.text}")
except Exception as e:
    print(f"Error: {e}")
finally:
    files['file'].close()
