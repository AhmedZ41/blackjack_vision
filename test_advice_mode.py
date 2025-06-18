#!/usr/bin/env python3
"""
Test script for the new advice mode functionality
"""
import requests
import cv2
import numpy as np
import json
import os

def create_advice_mode_test_image():
    """Create a test image with cards for advice mode testing"""
    # Create a simple test image with card-like rectangles
    test_image = np.ones((600, 800, 3), dtype=np.uint8) * 240  # Light gray background
    
    # Place some card-like rectangles in the image (simulating player cards only)
    card_positions = [
        (100, 200),  # Card 1
        (300, 200),  # Card 2
        (500, 200),  # Card 3
    ]
    
    for i, (x, y) in enumerate(card_positions):
        # Create a card-like rectangle
        card_color = (200 - i*20, 200 - i*20, 200 - i*20)  # Slightly different grays
        cv2.rectangle(test_image, (x, y), (x + 120, y + 180), card_color, -1)
        cv2.rectangle(test_image, (x, y), (x + 120, y + 180), (0, 0, 0), 2)  # Black border
        
        # Add some simple markings to make it look more card-like
        cv2.putText(test_image, f"C{i+1}", (x + 10, y + 30), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 0), 2)
    
    # Save the test image
    output_path = "/tmp/advice_mode_test.jpg"
    cv2.imwrite(output_path, test_image)
    print(f"Created advice mode test image: {output_path}")
    return output_path

def test_advice_mode_api():
    """Test the advice mode API endpoint"""
    print("=== Testing Advice Mode API ===")
    
    # Create test image
    image_path = create_advice_mode_test_image()
    
    # Test the API with advice mode
    url = "http://localhost:8000/analyze/"
    
    try:
        with open(image_path, 'rb') as f:
            files = {'file': f}
            data = {'players': 'advice'}  # This should trigger advice mode
            
            print("Sending request to API with advice mode...")
            response = requests.post(url, files=files, data=data, timeout=30)
            print(f"Status Code: {response.status_code}")
            
            if response.status_code == 200:
                result = response.json()
                print("✅ SUCCESS! API Response:")
                print(json.dumps(result, indent=2))
                
                # Check for expected advice mode structure
                if 'player1' in result and 'advice' in result:
                    print("\n✅ Advice mode structure correct!")
                    print(f"Player cards: {result['player1']['cards']}")
                    print(f"Player score: {result['player1']['score']}")
                    print(f"AI advice: {result['advice']}")
                    
                    # Check if advice contains expected fields
                    advice = result['advice']
                    if 'recommendation' in advice and 'explanation' in advice:
                        print("✅ AI advice structure is correct!")
                        return True
                    else:
                        print("❌ AI advice missing expected fields")
                        return False
                else:
                    print("❌ Missing expected fields in advice mode response")
                    return False
            else:
                print(f"❌ Error: {response.text}")
                return False
                
    except Exception as e:
        print(f"❌ Exception: {e}")
        return False

def test_normal_mode_still_works():
    """Test that normal mode still works after our changes"""
    print("\n=== Testing Normal Mode Still Works ===")
    
    # Create test image
    image_path = create_advice_mode_test_image()
    
    # Test the API with normal mode
    url = "http://localhost:8000/analyze/"
    
    try:
        with open(image_path, 'rb') as f:
            files = {'file': f}
            data = {'players': '1'}  # Normal mode
            
            print("Sending request to API with normal mode...")
            response = requests.post(url, files=files, data=data, timeout=30)
            print(f"Status Code: {response.status_code}")
            
            if response.status_code == 200:
                result = response.json()
                print("✅ SUCCESS! Normal mode still works:")
                
                # Check for expected normal mode structure
                if 'dealer' in result and 'player1' in result:
                    print("✅ Normal mode structure correct!")
                    print(f"Dealer cards: {result['dealer']['cards']}")
                    print(f"Player cards: {result['player1']['cards']}")
                    return True
                else:
                    print("❌ Missing expected fields in normal mode response")
                    return False
            else:
                print(f"❌ Error: {response.text}")
                return False
                
    except Exception as e:
        print(f"❌ Exception: {e}")
        return False

def main():
    """Run all tests"""
    print("🎯 Starting Advice Mode Integration Tests...")
    
    # Test if backend is running
    try:
        response = requests.get("http://localhost:8000/health", timeout=5)
        if response.status_code != 200:
            print("❌ Backend not running! Please start it first.")
            return
    except:
        print("❌ Backend not running! Please start it first.")
        return
    
    print("✅ Backend is running!")
    
    # Run tests
    advice_test_passed = test_advice_mode_api()
    normal_test_passed = test_normal_mode_still_works()
    
    print(f"\n🎯 Test Results:")
    print(f"Advice Mode: {'✅ PASS' if advice_test_passed else '❌ FAIL'}")
    print(f"Normal Mode: {'✅ PASS' if normal_test_passed else '❌ FAIL'}")
    
    if advice_test_passed and normal_test_passed:
        print("\n🎉 ALL TESTS PASSED! Advice mode is ready!")
    else:
        print("\n❌ Some tests failed. Please check the implementation.")

if __name__ == "__main__":
    main()
