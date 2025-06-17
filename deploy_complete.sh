#!/bin/bash

echo "🚀 Blackjack Vision - Complete Deployment"
echo "=========================================="

# Check if backend URL is set correctly
echo "📋 Checking current backend URL..."
grep "_productionBackendUrl" frontend/lib/config/api_config.dart

echo ""
echo "🔧 Building frontend with production backend..."
cd frontend
flutter build web --release

if [ $? -eq 0 ]; then
    echo "✅ Frontend build successful!"
else
    echo "❌ Frontend build failed!"
    exit 1
fi

echo ""
echo "📤 Deploying to Firebase..."
cd ..
firebase deploy --only hosting

if [ $? -eq 0 ]; then
    echo ""
    echo "🎉 DEPLOYMENT COMPLETE!"
    echo "========================"
    echo ""
    echo "🌍 Your app is live at:"
    echo "https://blackjack-vision-ai.web.app"
    echo ""
    echo "🔍 Test your backend at:"
    echo "https://blackjack-vision-backend.onrender.com/health"
    echo ""
    echo "📱 Test the complete flow:"
    echo "1. Open the app URL on any device"
    echo "2. Upload an image or use camera"
    echo "3. Check card detection results"
else
    echo "❌ Firebase deployment failed!"
    exit 1
fi
