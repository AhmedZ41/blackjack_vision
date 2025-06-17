#!/bin/bash

echo "🚀 Deploying Blackjack Vision Backend to Google Cloud Run"
echo "========================================================"

# Check if gcloud is installed
if ! command -v gcloud &> /dev/null; then
    echo "❌ Google Cloud SDK not found. Installing..."
    curl https://sdk.cloud.google.com | bash
    exec -l $SHELL
    echo "✅ Please run this script again after installation completes."
    exit 1
fi

# Set project
echo "🔧 Setting up Google Cloud project..."
gcloud config set project blackjack-vision-ai

# Enable required APIs
echo "🔧 Enabling required APIs..."
gcloud services enable run.googleapis.com
gcloud services enable cloudbuild.googleapis.com

# Deploy to Cloud Run
echo "🚀 Deploying backend to Cloud Run..."
cd backend

gcloud run deploy blackjack-backend \
  --source . \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --port 8000 \
  --memory 2Gi \
  --cpu 1 \
  --max-instances 10

if [ $? -eq 0 ]; then
    echo ""
    echo "🎉 BACKEND DEPLOYMENT SUCCESSFUL!"
    echo "================================="
    echo ""
    echo "🔗 Your backend URL:"
    echo "https://blackjack-backend-xyz-uc.a.run.app"
    echo ""
    echo "📝 Next steps:"
    echo "1. Copy the actual URL from above"
    echo "2. Update frontend/lib/config/api_config.dart"
    echo "3. Run ./deploy_frontend.sh"
    echo ""
    echo "🧪 Test your backend:"
    echo "curl https://your-backend-url/health"
else
    echo "❌ Deployment failed!"
    exit 1
fi
