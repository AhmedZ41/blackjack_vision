# Deployment Guide for Blackjack Vision

## Current Status:
- ✅ **Frontend**: Deployed to Firebase Hosting
- ❌ **Backend**: Needs deployment (currently local only)

## Backend Deployment Options:

### Option 1: Railway (Recommended - Free tier available)

1. **Install Railway CLI:**
   ```bash
   npm install -g @railway/cli
   ```

2. **Login to Railway:**
   ```bash
   railway login
   ```

3. **Deploy from backend directory:**
   ```bash
   cd backend
   railway init
   railway up
   ```

### Option 2: Render (Free tier available)

1. Create account at https://render.com
2. Connect your GitHub repository
3. Create a new Web Service
4. Set build command: `pip install -r requirements.txt`
5. Set start command: `uvicorn main:app --host 0.0.0.0 --port $PORT`

### Option 3: Heroku (Requires paid plan)

1. Install Heroku CLI
2. Create Heroku app
3. Deploy using Git

## Quick Fix for Testing:

If you want to test the deployed frontend with your local backend:

1. **Run backend locally:**
   ```bash
   cd backend
   python main.py
   ```

2. **Use ngrok to expose it:**
   ```bash
   ngrok http 8000
   ```

3. **Update the production URL in api_config.dart**

## Files that need backend URL update:
- `frontend/lib/config/api_config.dart` (line 9)
- Make sure camera_screen.dart uses ApiConfig.baseUrl ✅ (just fixed)

## Next Steps:
1. Choose a backend deployment option
2. Update the production URL in api_config.dart
3. Rebuild and redeploy frontend
4. Test the complete flow
