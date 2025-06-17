#!/usr/bin/env python3
"""
Test the new marked contours endpoint
"""
import requests
import cv2
import numpy as np
import base64
import os

def test_marked_contours_endpoint():
    """Test the new /analyze/marked-contours/ endpoint"""
    
    print("🧪 Testing Marked Contours Endpoint")
    print("=" * 40)
    
    # Create a simple test image with rectangles (simulating cards)
    test_image = np.ones((400, 600, 3), dtype=np.uint8) * 200  # Gray background
    
    # Add some card-like rectangles
    # Dealer area (top)
    cv2.rectangle(test_image, (50, 50), (150, 150), (100, 100, 100), -1)
    cv2.rectangle(test_image, (200, 50), (300, 150), (100, 100, 100), -1)
    
    # Player area (bottom)
    cv2.rectangle(test_image, (50, 250), (150, 350), (100, 100, 100), -1)
    cv2.rectangle(test_image, (200, 250), (300, 350), (100, 100, 100), -1)
    
    # Save test image
    test_path = "/tmp/marked_contours_test.jpg"
    cv2.imwrite(test_path, test_image)
    print(f"✅ Created test image: {test_path}")
    
    # Test both local and deployed endpoints
    endpoints = [
        "http://localhost:8000",
        "https://blackjack-vision-backend.onrender.com"
    ]
    
    for base_url in endpoints:
        print(f"\n🔗 Testing: {base_url}")
        
        try:
            # Test health first
            health_response = requests.get(f"{base_url}/health", timeout=10)
            if health_response.status_code != 200:
                print(f"❌ Health check failed: {health_response.status_code}")
                continue
            print("✅ Health check passed")
            
            # Test marked contours endpoint
            url = f"{base_url}/analyze/marked-contours/"
            
            with open(test_path, 'rb') as f:
                files = {'file': ('test.jpg', f, 'image/jpeg')}
                data = {'players': '1'}
                
                print("📤 Sending request...")
                response = requests.post(url, files=files, data=data, timeout=30)
            
            print(f"📥 Status Code: {response.status_code}")
            
            if response.status_code == 200:
                result = response.json()
                if result.get('success'):
                    image_data = result.get('image', '')
                    if image_data.startswith('data:image/png;base64,'):
                        print("✅ SUCCESS: Received base64 image data")
                        print(f"   Image data length: {len(image_data)} chars")
                        
                        # Optionally save the marked image
                        base64_data = image_data.split(',')[1]
                        marked_image_bytes = base64.b64decode(base64_data)
                        
                        output_path = f"/tmp/marked_output_{base_url.split('/')[-1].replace('.', '_')}.png"
                        with open(output_path, 'wb') as f:
                            f.write(marked_image_bytes)
                        print(f"💾 Saved marked image: {output_path}")
                    else:
                        print("❌ Invalid image data format")
                else:
                    print(f"❌ API returned success=false: {result}")
            else:
                print(f"❌ Error response: {response.text}")
                
        except requests.exceptions.RequestException as e:
            print(f"❌ Connection error: {e}")
        except Exception as e:
            print(f"❌ Unexpected error: {e}")
    
    # Cleanup
    if os.path.exists(test_path):
        os.remove(test_path)
    
    print("\n" + "=" * 40)
    print("🎯 Test completed!")

if __name__ == "__main__":
    test_marked_contours_endpoint()
