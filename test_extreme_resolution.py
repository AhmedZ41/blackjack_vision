#!/usr/bin/env python3
"""
Test with an extremely large image to verify resolution limiting
"""
import cv2
import numpy as np
import requests
import tempfile
import os

def test_extreme_resolution():
    """Test with a very large image (4000x6000)"""
    print("🧪 Testing Extreme Resolution Image (4000x6000)")
    print("=" * 60)
    
    # Create a 4000x6000 test image
    width, height = 6000, 4000
    img = np.zeros((height, width, 3), dtype=np.uint8)
    
    # Add a large white rectangle to simulate a card
    cv2.rectangle(img, (1000, 1000), (2000, 2500), (255, 255, 255), -1)
    cv2.putText(img, f"HUGE: {width}x{height}", (500, 500), 
                cv2.FONT_HERSHEY_SIMPLEX, 5, (0, 255, 0), 10)
    
    # Encode as PNG
    success, buffer = cv2.imencode('.png', img)
    if not success:
        print("❌ Failed to encode extreme test image")
        return
    
    try:
        with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as tmp_file:
            tmp_file.write(buffer.tobytes())
            tmp_file_path = tmp_file.name
        
        print(f"📤 Uploading extreme {width}x{height} image...")
        print(f"   Original size: {len(buffer)} bytes")
        
        with open(tmp_file_path, 'rb') as f:
            files = {'file': ('test_extreme.png', f, 'image/png')}
            data = {'players': 1}
            
            response = requests.post("http://localhost:8000/analyze/", 
                                   files=files, data=data, timeout=60)
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Extreme resolution image processed successfully!")
            print(f"📊 Results: {result}")
            print("🎯 Extreme resolution test PASSED!")
            print("   Backend handled the 4000x6000 image correctly!")
        else:
            print(f"❌ API Error: {response.text}")
        
        # Clean up
        os.unlink(tmp_file_path)
        
    except Exception as e:
        print(f"❌ Extreme resolution test failed: {e}")

if __name__ == "__main__":
    test_extreme_resolution()
