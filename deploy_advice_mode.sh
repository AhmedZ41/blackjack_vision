#!/bin/bash
# Deploy Blackjack Vision with Advice Mode

echo "🚀 Deploying Blackjack Vision with Advice Mode..."

# Check if we're in the right directory
if [ ! -f "ADVICE_MODE_COMPLETE.md" ]; then
    echo "❌ Please run this script from the blackjack_vision root directory"
    exit 1
fi

echo "📦 Building Frontend..."
cd frontend
flutter build web --release
if [ $? -ne 0 ]; then
    echo "❌ Frontend build failed"
    exit 1
fi

echo "🔥 Deploying Frontend to Firebase..."
firebase deploy --only hosting
if [ $? -ne 0 ]; then
    echo "❌ Frontend deployment failed"
    exit 1
fi

cd ..

echo "🐳 Deploying Backend to Render..."
# Note: This assumes you have the Render deployment configured
# You may need to manually trigger deployment or use the Render CLI

echo "✅ Deployment initiated!"
echo ""
echo "🎯 Next Steps:"
echo "1. Check Firebase deployment: https://blackjack-vision-ai.web.app"
echo "2. Monitor Render backend deployment: https://dashboard.render.com"
echo "3. Test the new Advice Mode feature end-to-end"
echo ""
echo "🎉 New Features Available:"
echo "- Orange 'Get an Advice' button on player selection"
echo "- Full-screen advice mode camera overlay"
echo "- AI strategy recommendations with win probabilities"
echo "- Educational explanations for each recommendation"
echo ""
echo "Happy blackjack playing! 🃏✨"
