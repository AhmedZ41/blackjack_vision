#!/bin/bash

echo "🌐 Testing Web Favicon Setup for Blackjack Vision"
echo "================================================"

cd /Users/ahmedadnan/Desktop/HTWG/S6/Computervision-2D/blackjack_vision/frontend

echo "📁 Checking web favicon files..."
if [ -f "web/favicon.png" ]; then
    echo "✅ favicon.png exists"
    ls -la web/favicon.png
else
    echo "❌ favicon.png missing"
fi

if [ -f "web/favicon-32x32.png" ]; then
    echo "✅ favicon-32x32.png exists"
    ls -la web/favicon-32x32.png
else
    echo "❌ favicon-32x32.png missing"
fi

if [ -f "web/favicon-16x16.png" ]; then
    echo "✅ favicon-16x16.png exists"
    ls -la web/favicon-16x16.png
else
    echo "❌ favicon-16x16.png missing"
fi

echo ""
echo "🔍 Checking web app icons..."
for size in 192 512; do
    if [ -f "web/icons/Icon-${size}.png" ]; then
        echo "✅ Icon-${size}.png exists"
        ls -la "web/icons/Icon-${size}.png"
    else
        echo "❌ Icon-${size}.png missing"
    fi
done

echo ""
echo "📄 Checking index.html favicon references..."
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

if grep -q "Blackjack Vision" web/index.html; then
    echo "✅ App title updated in HTML"
else
    echo "❌ App title not updated"
fi

echo ""
echo "🎯 Ready to test! To verify the new favicon:"
echo "1. Run: flutter run -d web-server --web-port=3000"
echo "2. Open: http://localhost:3000"
echo "3. Check browser tab for new Blackjack Vision icon"
echo ""
echo "Or build and deploy:"
echo "flutter build web && python3 -m http.server 8080 --directory build/web"
