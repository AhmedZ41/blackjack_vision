#!/usr/bin/env python3
"""
Test the improved advice logic
"""
import sys
import os

# Add the backend directory to Python path
sys.path.append('/Users/ahmedadnan/Desktop/HTWG/S6/Computervision-2D/blackjack_vision/backend')

from main import calculate_blackjack_advice, calculate_score

def test_improved_advice():
    """Test various scenarios with the improved advice logic"""
    
    print("🎯 Testing Improved Blackjack Advice Logic")
    print("=" * 50)
    
    # Test scenarios: [cards, expected_advice_type, description]
    test_scenarios = [
        # Hard hands
        (['King', '6'], "HIT", "Hard 16 - should hit against unknown dealer"),
        (['10', '7'], "STAND", "Hard 17 - should always stand"),
        (['King', 'Queen'], "STAND", "Hard 20 - excellent hand"),
        (['9', '2'], "DOUBLE DOWN", "Hard 11 - should double down"),
        (['5', '4'], "HIT", "Hard 9 - should hit or double"),
        
        # Soft hands  
        (['Ace', '6'], "HIT", "Soft 17 - should hit safely"),
        (['Ace', '7'], "STAND", "Soft 18 - borderline hand"),
        (['Ace', '8'], "STAND", "Soft 19 - excellent hand"),
        (['Ace', '4'], "HIT", "Soft 15 - should hit safely"),
        
        # Edge cases
        (['King', 'Ace'], "BLACKJACK", "Natural blackjack"),
        (['King', 'King', '5'], "BUST", "Busted hand"),
    ]
    
    for i, (cards, expected_type, description) in enumerate(test_scenarios, 1):
        print(f"\n{i}. {description}")
        print(f"   Cards: {cards}")
        print(f"   Score: {calculate_score(cards)}")
        
        # Get advice
        advice = calculate_blackjack_advice(cards)
        
        print(f"   Advice: {advice['advice']}")
        print(f"   Win Probability: {advice['win_probability']}%")
        print(f"   Explanation: {advice['explanation']}")
        
        # Check if advice type matches expectation
        if expected_type.upper() in advice['advice'].upper():
            print("   ✅ EXPECTED ADVICE TYPE")
        else:
            print("   ❌ UNEXPECTED ADVICE TYPE")
    
    print(f"\n🎉 Advice logic testing complete!")

if __name__ == "__main__":
    test_improved_advice()
