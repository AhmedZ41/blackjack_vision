#!/usr/bin/env python3
import requests
import cv2
import numpy as np

# Create a test image with some basic card-like shapes
test_image = np.ones((400, 600, 3), dtype=np.uint8) * 255  # White background

# Add some dark rectangles to simulate cards
# Dealer area (top half)
cv2.rectangle(test_image, (50, 50), (150, 150), (200, 200, 200), -1)  # Light gray card
cv2.rectangle(test_image, (200, 50), (300, 150), (180, 180, 180), -1)  # Another card

# Player area (bottom half)
cv2.rectangle(test_image, (50, 250), (150, 350), (160, 160, 160), -1)  # Player card 1
cv2.rectangle(test_image, (200, 250), (300, 350), (140, 140, 140), -1)  # Player card 2

# Add some text-like marks
cv2.putText(test_image, 'A', (75, 100), cv2.FONT_HERSHEY_SIMPLEX, 2, (0, 0, 0), 3)
cv2.putText(test_image, 'K', (225, 100), cv2.FONT_HERSHEY_SIMPLEX, 2, (0, 0, 0), 3)
cv2.putText(test_image, 'Q', (75, 300), cv2.FONT_HERSHEY_SIMPLEX, 2, (0, 0, 0), 3)
cv2.putText(test_image, '10', (215, 300), cv2.FONT_HERSHEY_SIMPLEX, 1.5, (0, 0, 0), 3)

# Save the test image
cv2.imwrite("/tmp/test_blackjack_image.jpg", test_image)
print("Created test image with simulated cards")

# Test the API
url = "http://localhost:8000/analyze/"
files = {'file': open('/tmp/test_blackjack_image.jpg', 'rb')}
data = {'players': 1}

try:
    print("Testing POST request...")
    response = requests.post(url, files=files, data=data)
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.text}")
    
    # Also test GET request
    print("\nTesting GET request...")
    get_response = requests.get(url)
    print(f"GET Status Code: {get_response.status_code}")
    print(f"GET Response: {get_response.text}")
    
except Exception as e:
    print(f"Error: {e}")
finally:
    files['file'].close()

print("\nTest completed!")
