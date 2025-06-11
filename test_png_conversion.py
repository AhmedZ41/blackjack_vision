#!/usr/bin/env python3
"""
Test script to verify PNG conversion functionality in the backend
"""
import requests
import cv2
import numpy as np
import io
import base64

def create_test_image(format='JPEG'):
    """Create a simple test image in the specified format"""
    # Create a simple test image
    img = np.zeros((400, 600, 3), dtype=np.uint8)
    # Add some colored rectangles to simulate cards
    cv2.rectangle(img, (50, 50), (150, 200), (255, 255, 255), -1)  # White card
    cv2.rectangle(img, (200, 50), (300, 200), (128, 128, 128), -1)  # Gray card
    cv2.rectangle(img, (350, 50), (450, 200), (200, 200, 200), -1)  # Light gray card
    
    # Encode as specified format
    if format.upper() == 'JPEG':
        success, buffer = cv2.imencode('.jpg', img)
        content_type = 'image/jpeg'
    elif format.upper() == 'PNG':
        success, buffer = cv2.imencode('.png', img)
        content_type = 'image/png'
    elif format.upper() == 'BMP':
        success, buffer = cv2.imencode('.bmp', img)
        content_type = 'image/bmp'
    else:
        raise ValueError(f"Unsupported format: {format}")
    
    if not success:
        raise ValueError(f"Failed to encode image as {format}")
    
    return buffer.tobytes(), content_type

def test_png_conversion():
    """Test PNG conversion with different input formats"""
    url = "http://localhost:8000/analyze/"
    
    # Test with different image formats
    formats = ['JPEG', 'PNG', 'BMP']
    
    for fmt in formats:
        print(f"\n--- Testing {fmt} input ---")
        try:
            # Create test image
            image_data, content_type = create_test_image(fmt)
            
            # Prepare the request
            files = {
                'file': (f'test.{fmt.lower()}', image_data, content_type)
            }
            data = {
                'players': 1
            }
            
            # Send request
            response = requests.post(url, files=files, data=data)
            
            print(f"Status Code: {response.status_code}")
            if response.status_code == 200:
                result = response.json()
                print(f"Response: {result}")
            else:
                print(f"Error: {response.text}")
                
        except Exception as e:
            print(f"Exception testing {fmt}: {e}")

def test_health_check():
    """Test if the backend is running"""
    try:
        response = requests.get("http://localhost:8000/health")
        if response.status_code == 200:
            print("Backend is running!")
            return True
        else:
            print(f"Backend health check failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"Cannot connect to backend: {e}")
        return False

if __name__ == "__main__":
    print("Testing PNG conversion functionality...")
    
    # First check if backend is running
    if test_health_check():
        test_png_conversion()
    else:
        print("Please start the backend first: cd backend && python main.py")
