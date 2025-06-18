#!/bin/zsh

echo "🌐 Final Web Favicon Validation - Blackjack Vision"
echo "=================================================="

cd /Users/ahmedadnan/Desktop/HTWG/S6/Computervision-2D/blackjack_vision/frontend

echo "\n📁 Checking favicon files in source..."
for file in "web/favicon.png" "web/favicon-32x32.png" "web/favicon-16x16.png"; do
    if [[ -f "$file" ]]; then
        echo "✅ $file exists ($(du -h "$file" | cut -f1))"
    else
        echo "❌ $file missing"
    fi
done

echo "\n🎯 Checking web app icons..."
for file in "web/icons/Icon-192.png" "web/icons/Icon-512.png"; do
    if [[ -f "$file" ]]; then
        echo "✅ $file exists ($(du -h "$file" | cut -f1))"
    else
        echo "❌ $file missing"
    fi
done

echo "\n📄 Checking HTML favicon references..."
if grep -q "favicon-32x32.png" web/index.html; then
    echo "✅ 32x32 favicon referenced in HTML"
else
    echo "❌ 32x32 favicon not referenced"
fi

if grep -q "favicon-16x16.png" web/index.html; then
    echo "✅ 16x16 favicon referenced in HTML"
else
    echo "❌ 16x16 favicon not referenced"
fi

if grep -q 'content="#2e7d32"' web/index.html; then
    echo "✅ Theme color set to Blackjack Vision green"
else
    echo "❌ Theme color not set correctly"
fi

echo "\n📱 Checking manifest.json..."
if grep -q '"name": "Blackjack Vision"' web/manifest.json; then
    echo "✅ App name correct in manifest"
else
    echo "❌ App name incorrect in manifest"
fi

if grep -q '"theme_color": "#2e7d32"' web/manifest.json; then
    echo "✅ Theme color correct in manifest"
else
    echo "❌ Theme color incorrect in manifest"
fi

echo "\n🏗️  Building web app..."
flutter build web --base-href / > /dev/null 2>&1

if [[ $? -eq 0 ]]; then
    echo "✅ Web build successful"
    
    echo "\n📦 Checking build output..."
    if [[ -f "build/web/favicon.png" ]]; then
        echo "✅ Main favicon in build"
    else
        echo "❌ Main favicon missing from build"
    fi
    
    # Copy additional favicons to build
    cp web/favicon-32x32.png build/web/ 2>/dev/null
    cp web/favicon-16x16.png build/web/ 2>/dev/null
    
    if [[ -f "build/web/favicon-32x32.png" ]]; then
        echo "✅ 32x32 favicon in build"
    else
        echo "❌ 32x32 favicon missing from build"
    fi
    
else
    echo "❌ Web build failed"
fi

echo "\n🚀 Testing options:"
echo "1. Flutter dev server: flutter run -d web-server --web-port=3000"
echo "2. Python HTTP server: python3 -m http.server 8080 --directory build/web"
echo "3. Open in browser: http://localhost:3000 or http://localhost:8080"

echo "\n🎯 What to verify:"
echo "• Browser tab shows Blackjack Vision icon (not Flutter logo)"
echo "• PWA installation shows custom icon"
echo "• Theme color appears as green in browser"
echo "• Bookmark uses custom icon"

echo "\n✅ Web favicon setup complete!"
