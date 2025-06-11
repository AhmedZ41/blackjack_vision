#!/bin/bash

echo "🔍 Testing Blackjack Vision Backend Communication..."
echo

# Test backend health
echo "1. Testing backend health endpoint..."
response=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:8000/health)
if [ "$response" = "200" ]; then
    echo "✅ Backend is running on localhost:8000"
else
    echo "❌ Backend is not responding on localhost:8000"
    exit 1
fi

# Test backend on all interfaces
echo
echo "2. Testing backend on all interfaces..."
ip_address=$(ifconfig en0 | grep "inet " | awk '{print $2}')
if [ ! -z "$ip_address" ]; then
    response=$(curl -s -o /dev/null -w "%{http_code}" http://$ip_address:8000/health)
    if [ "$response" = "200" ]; then
        echo "✅ Backend is accessible on $ip_address:8000 (for mobile devices)"
    else
        echo "❌ Backend is not accessible on $ip_address:8000"
    fi
else
    echo "❌ Could not determine IP address"
fi

echo
echo "3. Flutter Web App:"
echo "   🌐 Open http://localhost:3000 in your browser"
echo
echo "4. Mobile Testing:"
echo "   📱 For Android Emulator: App will use http://10.0.2.2:8000"
echo "   📱 For Physical Devices: App will use http://$ip_address:8000"
echo "   📱 Make sure your mobile device is on the same WiFi network"
echo
echo "5. Testing Backend Connection:"
echo "   🔧 Use the 'Test Backend Connection' button in the app"
echo

# Test if card templates exist
echo "6. Checking card templates..."
if [ -d "../backend/PNG-cards" ]; then
    card_count=$(ls ../backend/PNG-cards/*.png 2>/dev/null | wc -l)
    echo "✅ Found $card_count card template images"
else
    echo "❌ Card templates directory not found"
fi

echo
echo "🎯 Everything looks ready! You can now test the app on both web and mobile."
