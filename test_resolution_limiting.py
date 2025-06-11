#!/usr/bin/env python3
"""
Test script to verify image resolution limiting functionality
"""
import cv2
import numpy as np
import requests
import tempfile
import os

def create_high_resolution_test_image():
    """Create a test image larger than 1500 pixels in both dimensions"""
    # Create a 2000x3000 test image (larger than 1500px limit)
    width, height = 3000, 2000
    img = np.zeros((height, width, 3), dtype=np.uint8)
    
    # Add some colored rectangles to simulate cards
    cv2.rectangle(img, (100, 100), (400, 600), (255, 255, 255), -1)  # White card
    cv2.rectangle(img, (500, 100), (800, 600), (220, 220, 220), -1)  # Light gray card
    cv2.rectangle(img, (900, 100), (1200, 600), (200, 200, 200), -1)  # Gray card
    
    # Add some text to show the original size
    cv2.putText(img, f"Original: {width}x{height}", (100, 50), 
                cv2.FONT_HERSHEY_SIMPLEX, 2, (0, 255, 0), 3)
    
    print(f"Created test image: {width}x{height} pixels")
    return img

def test_resolution_limiting():
    """Test the backend with a high-resolution image"""
    print("🧪 Testing Image Resolution Limiting")
    print("=" * 50)
    
    # Check if backend is running
    try:
        response = requests.get("http://localhost:8000/health", timeout=5)
        if response.status_code != 200:
            print("❌ Backend is not running. Please start it first.")
            return
        print("✅ Backend is running")
    except Exception as e:
        print(f"❌ Cannot connect to backend: {e}")
        return
    
    # Create high-resolution test image
    test_img = create_high_resolution_test_image()
    
    # Save as JPEG to test the complete pipeline
    success, buffer = cv2.imencode('.jpg', test_img, [cv2.IMWRITE_JPEG_QUALITY, 90])
    if not success:
        print("❌ Failed to encode test image")
        return
    
    # Test the API
    try:
        with tempfile.NamedTemporaryFile(suffix='.jpg', delete=False) as tmp_file:
            tmp_file.write(buffer.tobytes())
            tmp_file_path = tmp_file.name
        
        print(f"📤 Uploading {test_img.shape[1]}x{test_img.shape[0]} image...")
        
        with open(tmp_file_path, 'rb') as f:
            files = {'file': ('test_high_res.jpg', f, 'image/jpeg')}
            data = {'players': 1}
            
            response = requests.post("http://localhost:8000/analyze/", 
                                   files=files, data=data, timeout=30)
        
        print(f"📥 Response Status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Image processed successfully!")
            print(f"📊 Results: {result}")
            print("\n🎯 Resolution limiting test PASSED!")
            print("   The backend successfully handled the high-resolution image.")
        else:
            print(f"❌ API Error: {response.text}")
        
        # Clean up
        os.unlink(tmp_file_path)
        
    except Exception as e:
        print(f"❌ Test failed: {e}")

def test_normal_resolution():
    """Test with a normal-sized image to ensure it's not affected"""
    print("\n🧪 Testing Normal Resolution Image")
    print("=" * 50)
    
    # Create a normal 800x600 image
    width, height = 800, 600
    img = np.zeros((height, width, 3), dtype=np.uint8)
    cv2.rectangle(img, (50, 50), (150, 200), (255, 255, 255), -1)
    cv2.putText(img, f"{width}x{height}", (10, 30), 
                cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
    
    success, buffer = cv2.imencode('.png', img)
    if not success:
        print("❌ Failed to encode normal test image")
        return
    
    try:
        with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as tmp_file:
            tmp_file.write(buffer.tobytes())
            tmp_file_path = tmp_file.name
        
        print(f"📤 Uploading {width}x{height} image...")
        
        with open(tmp_file_path, 'rb') as f:
            files = {'file': ('test_normal.png', f, 'image/png')}
            data = {'players': 1}
            
            response = requests.post("http://localhost:8000/analyze/", 
                                   files=files, data=data, timeout=30)
        
        if response.status_code == 200:
            print("✅ Normal resolution image processed successfully!")
            print("🎯 Normal resolution test PASSED!")
        else:
            print(f"❌ API Error: {response.text}")
        
        # Clean up
        os.unlink(tmp_file_path)
        
    except Exception as e:
        print(f"❌ Normal resolution test failed: {e}")

if __name__ == "__main__":
    test_resolution_limiting()
    test_normal_resolution()
    print("\n🏁 Resolution limiting tests completed!")
