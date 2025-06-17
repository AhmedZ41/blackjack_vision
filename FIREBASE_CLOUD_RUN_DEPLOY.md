# 🚀 Firebase + Google Cloud Run Deployment

Since Firebase Hosting only serves static files, we'll deploy the backend to Google Cloud Run (which integrates with your Firebase project) and update the frontend.

## Step 1: Deploy Backend to Google Cloud Run

### Prepare the project:
```bash
# Install Google Cloud SDK
curl https://sdk.cloud.google.com | bash
exec -l $SHELL
gcloud init

# Set your Firebase project
gcloud config set project blackjack-vision-ai

# Build and deploy
cd /Users/ahmedadnan/Desktop/HTWG/S6/Computervision-2D/blackjack_vision/backend
gcloud run deploy blackjack-backend \
  --source . \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated
```

## Step 2: Alternative - Quick Deploy using Docker + Cloud Run

I'll create a deployment script that does this automatically.

## Step 3: Update Frontend Configuration

Once deployed, you'll get a URL like:
`https://blackjack-backend-xyz-uc.a.run.app`

Then update `frontend/lib/config/api_config.dart` and redeploy frontend.

## Step 4: Complete Firebase Deployment

Your final URLs will be:
- Frontend: `https://blackjack-vision-ai.web.app`  
- Backend: `https://blackjack-backend-xyz-uc.a.run.app`

Let me create the deployment scripts now...
