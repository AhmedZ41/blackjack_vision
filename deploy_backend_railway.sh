#!/bin/bash

echo "🚀 Deploying Blackjack Vision Backend to Railway"
echo "================================================"

# Check if railway CLI is installed
if ! command -v railway &> /dev/null; then
    echo "📦 Installing Railway CLI..."
    npm install -g @railway/cli
fi

echo "🚂 Starting Railway deployment..."
echo ""
echo "📋 Steps:"
echo "1. Login to Railway"
echo "2. Initialize project"
echo "3. Deploy backend"
echo ""

# Login to Railway
echo "🔐 Please login to Railway..."
railway login

# Navigate to backend directory
cd backend

# Initialize Railway project
echo "🏗️ Initializing Railway project..."
railway init

# Deploy
echo "🚀 Deploying to Railway..."
railway up

if [ $? -eq 0 ]; then
    echo ""
    echo "🎉 DEPLOYMENT SUCCESSFUL!"
    echo "========================="
    echo ""
    echo "🔗 Your backend is now live!"
    echo "Use 'railway status' to see your deployment URL"
    echo ""
    echo "📝 Next steps:"
    echo "1. Run 'railway status' to get your URL"
    echo "2. Update frontend/lib/config/api_config.dart with the URL"
    echo "3. Run ../deploy_frontend.sh"
    echo ""
else
    echo "❌ Deployment failed!"
    echo "Please check the Railway dashboard for details"
fi
