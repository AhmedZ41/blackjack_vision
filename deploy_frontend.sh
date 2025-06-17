#!/bin/bash

# 🚀 Blackjack Vision - Frontend Deployment Script

echo "🎯 Building Flutter web app..."
cd frontend
flutter build web --release

echo "📤 Deploying to Firebase..."
cd ..
firebase deploy --only hosting

echo "✅ Deployment complete!"
echo ""
echo "🌍 Your app should be available at:"
echo "https://blackjack-vision-ai.web.app"
echo ""
echo "📝 Next steps:"
echo "1. Deploy backend to Render using the guide"
echo "2. Update api_config.dart with backend URL"
echo "3. Run this script again to redeploy"
