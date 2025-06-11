#!/usr/bin/env python3
"""
Test script using actual card images to verify card detection works.
"""
import requests
import cv2
import numpy as np
import os

def create_test_image_with_real_cards():
    """Create a test image by placing actual card templates in the scene."""
    
    # Load some actual card templates
    card_path = "backend/PNG-cards"
    cards_to_use = [
        "ace_of_spades.png",
        "king_of_hearts.png", 
        "queen_of_clubs.png",
        "10_of_diamonds.png"
    ]
    
    # Create a larger test image
    test_image = np.ones((600, 800, 3), dtype=np.uint8) * 240  # Light gray background
    
    print("Creating test image with real card templates...")
    
    # Load and place cards in the image
    card_positions = [
        (50, 50),    # Dealer card 1
        (200, 50),   # Dealer card 2  
        (50, 350),   # Player card 1
        (200, 350),  # Player card 2
    ]
    
    placed_cards = []
    
    for i, (card_file, (x, y)) in enumerate(zip(cards_to_use, card_positions)):
        card_path_full = os.path.join(card_path, card_file)
        if os.path.exists(card_path_full):
            card_img = cv2.imread(card_path_full)
            if card_img is not None:
                # Resize card to fit nicely in the scene
                card_height = 120
                scale = card_height / card_img.shape[0]
                card_width = int(card_img.shape[1] * scale)
                card_resized = cv2.resize(card_img, (card_width, card_height))
                
                # Place the card in the test image
                if (y + card_height < test_image.shape[0] and 
                    x + card_width < test_image.shape[1]):
                    test_image[y:y+card_height, x:x+card_width] = card_resized
                    placed_cards.append(card_file.replace('.png', '').replace('_of_', ' ').title())
                    print(f"Placed {card_file} at position ({x}, {y})")
    
    # Add some noise and background elements to make it more realistic
    # Add some random rectangles as background elements
    for _ in range(5):
        x1, y1 = np.random.randint(0, test_image.shape[1]-50), np.random.randint(0, test_image.shape[0]-50)
        x2, y2 = x1 + np.random.randint(20, 80), y1 + np.random.randint(20, 80)
        color = tuple(np.random.randint(200, 255, 3).tolist())
        cv2.rectangle(test_image, (x1, y1), (x2, y2), color, -1)
    
    # Save the test image
    output_path = "/tmp/real_cards_test.jpg"
    cv2.imwrite(output_path, test_image)
    print(f"Saved test image to {output_path}")
    print(f"Expected cards in image: {placed_cards}")
    
    return output_path, placed_cards

def test_api_with_real_cards():
    """Test the API with an image containing real card templates."""
    
    # Create test image
    image_path, expected_cards = create_test_image_with_real_cards()
    
    # Test the API
    url = "http://localhost:8000/analyze/"
    
    try:
        with open(image_path, 'rb') as f:
            files = {'file': f}
            data = {'players': 1}
            
            print(f"\nTesting API with real card templates...")
            print(f"Expected cards: {expected_cards}")
            
            response = requests.post(url, files=files, data=data)
            print(f"\nStatus Code: {response.status_code}")
            
            if response.status_code == 200:
                result = response.json()
                print(f"API Response: {result}")
                
                # Extract detected cards
                dealer_cards = result.get('dealer', {}).get('cards', [])
                player_cards = result.get('player1', {}).get('cards', [])
                
                print(f"\nDetected cards:")
                print(f"Dealer: {dealer_cards} (Score: {result.get('dealer', {}).get('score', 0)})")
                print(f"Player: {player_cards} (Score: {result.get('player1', {}).get('score', 0)})")
                
                # Check detection success
                total_detected = len(dealer_cards) + len(player_cards)
                total_expected = len(expected_cards)
                
                print(f"\nDetection Summary:")
                print(f"Expected cards: {total_expected}")
                print(f"Detected cards: {total_detected}")
                
                if total_detected > 0:
                    print("✅ SUCCESS: Cards were detected!")
                    # Check if any expected cards were found
                    all_detected = dealer_cards + player_cards
                    matches = 0
                    for expected in expected_cards:
                        for detected in all_detected:
                            if expected.lower() in detected.lower() or detected.lower() in expected.lower():
                                matches += 1
                                break
                    print(f"Matching cards found: {matches}/{total_expected}")
                else:
                    print("❌ WARNING: No cards detected. This might indicate:")
                    print("   - Template matching threshold is too high")
                    print("   - Card templates don't match the input format")
                    print("   - Image preprocessing issues")
                    
            else:
                print(f"Error: {response.text}")
                
    except Exception as e:
        print(f"Error testing API: {e}")

if __name__ == "__main__":
    test_api_with_real_cards()
