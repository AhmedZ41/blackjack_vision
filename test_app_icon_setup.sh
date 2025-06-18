#!/bin/bash

# Test App Icon Setup Script
echo "🎨 Testing Blackjack Vision App Icon Setup"
echo "=" * 50

cd /Users/ahmedadnan/Desktop/HTWG/S6/Computervision-2D/blackjack_vision/frontend

echo "📱 Checking Android Icons..."
if [ -f "android/app/src/main/res/mipmap-hdpi/ic_launcher.png" ]; then
    echo "✅ Android hdpi icon exists"
else
    echo "❌ Android hdpi icon missing"
fi

if [ -f "android/app/src/main/res/mipmap-xxxhdpi/ic_launcher.png" ]; then
    echo "✅ Android xxxhdpi icon exists"
else
    echo "❌ Android xxxhdpi icon missing"
fi

echo "🍎 Checking iOS Icons..."
if [ -f "ios/Runner/Assets.xcassets/AppIcon.appiconset/Contents.json" ]; then
    echo "✅ iOS AppIcon.appiconset exists"
else
    echo "❌ iOS AppIcon.appiconset missing"
fi

if [ -f "ios/Runner/Assets.xcassets/AppIcon.appiconset/Icon-App-1024x1024@1x.png" ]; then
    echo "✅ iOS App Store icon exists"
else
    echo "❌ iOS App Store icon missing"
fi

echo "🌐 Checking Web Icons..."
if [ -f "icons/android/ic_launcher-web.png" ]; then
    echo "✅ Web icon source exists"
else
    echo "❌ Web icon source missing"
fi

echo "📋 Checking Configuration..."
if grep -q "Blackjack Vision" android/app/src/main/AndroidManifest.xml; then
    echo "✅ Android app name updated"
else
    echo "❌ Android app name not updated"
fi

if grep -q "Blackjack Vision" ios/Runner/Info.plist; then
    echo "✅ iOS app name updated"
else
    echo "❌ iOS app name not updated"
fi

if grep -q "blackjack_vision" pubspec.yaml; then
    echo "✅ Package name updated"
else
    echo "❌ Package name not updated"
fi

echo ""
echo "🎉 App Icon Setup Test Complete!"
echo "Ready to build: flutter build android/ios/web"
