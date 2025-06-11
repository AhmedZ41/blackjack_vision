#!/usr/bin/env python3
import requests
import cv2
import numpy as np
import os

def simple_card_test():
    print("=== Simple Card Detection Test ===")
    
    # Create a simple test image with one card template
    card_file = "backend/PNG-cards/ace_of_spades.png"
    
    if not os.path.exists(card_file):
        print("Card file not found!")
        return
    
    # Load the card template
    card_template = cv2.imread(card_file)
    print(f"Loaded card template: {card_template.shape}")
    
    # Create a test scene with the card
    test_scene = np.ones((400, 600, 3), dtype=np.uint8) * 200  # Gray background
    
    # Place the card in the scene (scaled down a bit)
    card_height = 120
    scale = card_height / card_template.shape[0]
    card_width = int(card_template.shape[1] * scale)
    card_resized = cv2.resize(card_template, (card_width, card_height))
    
    # Place in player area (bottom half)
    x, y = 50, 250
    test_scene[y:y+card_height, x:x+card_width] = card_resized
    
    # Save test image
    test_path = "/tmp/simple_card_test.jpg"
    cv2.imwrite(test_path, test_scene)
    print(f"Created test image: {test_path}")
    
    # Test the API
    url = "http://localhost:8000/analyze/"
    
    try:
        with open(test_path, 'rb') as f:
            files = {'file': f}
            data = {'players': 1}
            
            print("Sending request to API...")
            response = requests.post(url, files=files, data=data)
            print(f"Status: {response.status_code}")
            print(f"Response: {response.text}")
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    simple_card_test()
