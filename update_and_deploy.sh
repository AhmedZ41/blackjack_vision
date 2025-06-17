#!/bin/bash

echo "🔧 Update Frontend with Backend URL"
echo "==================================="

# Check if URL is provided
if [ -z "$1" ]; then
    echo "❌ Please provide your backend URL"
    echo ""
    echo "Usage: $0 <backend-url>"
    echo "Example: $0 https://blackjack-vision-backend-xyz.onrender.com"
    echo ""
    echo "To get your backend URL:"
    echo "• Render: Check your dashboard at render.com"
    echo "• Railway: Run 'railway status' in backend folder"
    echo "• Cloud Run: Check Google Cloud Console"
    exit 1
fi

BACKEND_URL="$1"

# Remove trailing slash if present
BACKEND_URL="${BACKEND_URL%/}"

echo "🔗 Backend URL: $BACKEND_URL"
echo ""

# Update api_config.dart
API_CONFIG_FILE="frontend/lib/config/api_config.dart"

if [ ! -f "$API_CONFIG_FILE" ]; then
    echo "❌ File not found: $API_CONFIG_FILE"
    exit 1
fi

echo "📝 Updating $API_CONFIG_FILE..."

# Create backup
cp "$API_CONFIG_FILE" "$API_CONFIG_FILE.backup"

# Update the production URL
sed -i.tmp "s|static String _productionBackendUrl = '[^']*'|static String _productionBackendUrl = '$BACKEND_URL'|g" "$API_CONFIG_FILE"

# Remove the temporary file created by sed on macOS
rm -f "$API_CONFIG_FILE.tmp"

echo "✅ Updated production backend URL to: $BACKEND_URL"
echo ""

# Verify the change
echo "🔍 Verification:"
grep "_productionBackendUrl" "$API_CONFIG_FILE"
echo ""

echo "📱 Now deploying frontend..."
echo "=============================="

# Deploy frontend
./deploy_frontend.sh

echo ""
echo "🎉 DEPLOYMENT COMPLETE!"
echo "======================"
echo ""
echo "🌐 Your app is now live at:"
echo "Frontend: https://blackjack-vision-ai.web.app"
echo "Backend: $BACKEND_URL"
echo ""
echo "🧪 Test your backend:"
echo "curl $BACKEND_URL/health"
echo ""
echo "📱 Test your app:"
echo "Open https://blackjack-vision-ai.web.app on any device!"
