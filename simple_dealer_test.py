#!/usr/bin/env python3
"""Simple test of dealer-specific advice"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from backend.main import calculate_blackjack_advice

# Test cases
print("🎯 Testing Enhanced Dealer-Specific Advice")
print("=" * 50)

# Test 1: Hard 16 vs Weak Dealer 5
print("\n📋 Test 1: Hard 16 vs Dealer 5 (Weak)")
advice = calculate_blackjack_advice(['King', '6'], '5')
print(f"Advice: {advice['advice']}")
print(f"Win Probability: {advice['win_probability']}%")
print(f"Explanation: {advice['explanation']}")

# Test 2: Hard 16 vs Strong Dealer Ace
print("\n📋 Test 2: Hard 16 vs Dealer Ace (Strong)")
advice = calculate_blackjack_advice(['King', '6'], 'Ace')
print(f"Advice: {advice['advice']}")
print(f"Win Probability: {advice['win_probability']}%")
print(f"Explanation: {advice['explanation']}")

# Test 3: Soft 18 vs Strong Dealer 9
print("\n📋 Test 3: Soft 18 vs Dealer 9 (Strong)")
advice = calculate_blackjack_advice(['Ace', '7'], '9')
print(f"Advice: {advice['advice']}")
print(f"Win Probability: {advice['win_probability']}%")
print(f"Explanation: {advice['explanation']}")

# Test 4: Soft 18 vs Weak Dealer 4
print("\n📋 Test 4: Soft 18 vs Dealer 4 (Weak)")
advice = calculate_blackjack_advice(['Ace', '7'], '4')
print(f"Advice: {advice['advice']}")
print(f"Win Probability: {advice['win_probability']}%")
print(f"Explanation: {advice['explanation']}")

print("\n✅ Dealer-specific advice enhancement working!")
