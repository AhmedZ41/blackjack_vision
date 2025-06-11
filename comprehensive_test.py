#!/usr/bin/env python3
"""
Comprehensive test to verify PNG conversion and upload functionality
"""
import requests
import cv2
import numpy as np
import tempfile
import os

def test_backend_with_different_formats():
    """Test the backend with different image formats to verify PNG conversion"""
    url = "http://localhost:8000/analyze/"
    
    # Create a test image with some simple card-like rectangles
    img = np.zeros((400, 600, 3), dtype=np.uint8)
    # Add white rectangles to simulate cards
    cv2.rectangle(img, (50, 50), (150, 200), (255, 255, 255), -1)  # Card 1
    cv2.rectangle(img, (200, 50), (300, 200), (240, 240, 240), -1)  # Card 2
    cv2.rectangle(img, (350, 50), (450, 200), (220, 220, 220), -1)  # Card 3
    
    formats_to_test = [
        ('.jpg', 'image/jpeg', [cv2.IMWRITE_JPEG_QUALITY, 90]),
        ('.png', 'image/png', []),
        ('.bmp', 'image/bmp', [])
    ]
    
    results = {}
    
    for ext, content_type, encode_params in formats_to_test:
        print(f"\n--- Testing {ext.upper()} format ---")
        
        try:
            # Encode image in the specified format
            success, buffer = cv2.imencode(ext, img, encode_params)
            if not success:
                print(f"Failed to encode image as {ext}")
                continue
            
            # Create temporary file
            with tempfile.NamedTemporaryFile(suffix=ext, delete=False) as tmp_file:
                tmp_file.write(buffer.tobytes())
                tmp_file_path = tmp_file.name
            
            # Test the API
            try:
                with open(tmp_file_path, 'rb') as f:
                    files = {'file': (f'test{ext}', f, content_type)}
                    data = {'players': 1}
                    
                    response = requests.post(url, files=files, data=data, timeout=30)
                    
                print(f"Status Code: {response.status_code}")
                
                if response.status_code == 200:
                    result = response.json()
                    print(f"✅ Success! Response: {result}")
                    results[ext] = {
                        'status': 'success',
                        'response': result
                    }
                else:
                    print(f"❌ Error: {response.text}")
                    results[ext] = {
                        'status': 'error',
                        'error': response.text
                    }
                    
            except requests.exceptions.RequestException as e:
                print(f"❌ Request failed: {e}")
                results[ext] = {
                    'status': 'request_failed',
                    'error': str(e)
                }
            
            # Clean up
            os.unlink(tmp_file_path)
            
        except Exception as e:
            print(f"❌ Exception: {e}")
            results[ext] = {
                'status': 'exception',
                'error': str(e)
            }
    
    return results

def test_with_real_card():
    """Test with an actual card image from the templates"""
    url = "http://localhost:8000/analyze/"
    card_path = "backend/PNG-cards/ace_of_spades.png"
    
    print(f"\n--- Testing with real card: {card_path} ---")
    
    if not os.path.exists(card_path):
        print(f"❌ Card file not found: {card_path}")
        return None
    
    try:
        with open(card_path, 'rb') as f:
            files = {'file': ('ace_of_spades.png', f, 'image/png')}
            data = {'players': 1}
            
            response = requests.post(url, files=files, data=data, timeout=30)
            
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Success! Response: {result}")
            return result
        else:
            print(f"❌ Error: {response.text}")
            return None
            
    except Exception as e:
        print(f"❌ Exception: {e}")
        return None

def check_backend_health():
    """Check if backend is running"""
    try:
        response = requests.get("http://localhost:8000/health", timeout=5)
        if response.status_code == 200:
            print("✅ Backend is running!")
            return True
        else:
            print(f"❌ Backend health check failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Cannot connect to backend: {e}")
        return False

def main():
    print("🧪 Comprehensive Blackjack Vision Backend Test")
    print("=" * 50)
    
    # Check backend health
    if not check_backend_health():
        print("\n❌ Backend is not running. Please start it with:")
        print("cd backend && python main.py")
        return
    
    # Test PNG conversion with different formats
    print("\n🔄 Testing PNG conversion with different input formats...")
    format_results = test_backend_with_different_formats()
    
    # Test with real card
    print("\n🃏 Testing with real card image...")
    real_card_result = test_with_real_card()
    
    # Summary
    print("\n📊 Test Summary")
    print("=" * 30)
    
    successful_formats = [fmt for fmt, result in format_results.items() if result['status'] == 'success']
    print(f"✅ PNG conversion working for: {', '.join(successful_formats)}")
    
    if real_card_result:
        print("✅ Real card detection working")
    else:
        print("❌ Real card detection failed")
    
    if len(successful_formats) > 0 and real_card_result:
        print("\n🎉 All tests passed! The backend is ready for production.")
    else:
        print("\n⚠️ Some tests failed. Please check the backend implementation.")

if __name__ == "__main__":
    main()
