# 🚀 Blackjack Vision AI - Deployment Guide

## 📱 Firebase Frontend Deployment

Your Flutter web app has been configured for Firebase Hosting deployment.

### Current Status:
- ✅ Firebase project created: `blackjack-vision-ai`
- ✅ Web app built for production
- ✅ Firebase configuration files created
- ✅ Mobile-optimized configuration added

### Firebase URLs:
- **Firebase Console**: https://console.firebase.google.com/project/blackjack-vision-ai/overview
- **Hosted App**: https://blackjack-vision-ai.web.app (or https://blackjack-vision-ai.firebaseapp.com)

### To Deploy:
```bash
cd /Users/ahmedadnan/Desktop/HTWG/S6/Computervision-2D/blackjack_vision
firebase deploy --only hosting
```

## 🔧 Backend Deployment Options

Since Firebase Hosting only serves static files, you need to deploy the backend separately. Here are your options:

### Option 1: Railway (Recommended - Free Tier Available)
1. Create account at https://railway.app/
2. Connect your GitHub repository
3. Deploy directly from the `backend/` folder
4. Railway will automatically detect the Dockerfile

### Option 2: Render (Free Tier Available)
1. Create account at https://render.com/
2. Connect your GitHub repository
3. Create a new Web Service from the `backend/` folder
4. Use Docker deployment

### Option 3: Google Cloud Run (Pay-as-you-go)
1. Build and push Docker image to Google Container Registry
2. Deploy to Cloud Run
3. Configure CORS for your Firebase domain

### Option 4: Heroku (Paid)
1. Install Heroku CLI
2. Deploy using Docker container

## 📝 Configuration Steps

### Step 1: Choose a Backend Deployment Platform
Pick one of the options above and deploy your backend.

### Step 2: Update API Configuration
Once your backend is deployed, update the production URL in:
```dart
// frontend/lib/config/api_config.dart
static const String _productionBackendUrl = 'https://your-actual-backend-url.com';
```

### Step 3: Rebuild and Redeploy Frontend
```bash
cd frontend
flutter build web --release --base-href /
cd ..
firebase deploy --only hosting
```

## 🌐 Access Your App

### Desktop/Laptop:
- Visit: https://blackjack-vision-ai.web.app
- Works in Chrome, Firefox, Safari, Edge

### iPhone/Mobile:
- Visit the same URL in Safari or Chrome
- App is optimized for mobile viewing
- Can be "installed" as a PWA (Add to Home Screen)

## 📱 PWA Features Added:
- ✅ Mobile-responsive design
- ✅ Optimized viewport settings
- ✅ Apple touch icons
- ✅ Standalone app mode
- ✅ Custom app name and description

## 🔒 CORS Configuration
Your backend includes CORS configuration for:
- Firebase Hosting domains
- Local development
- Mobile access

## 📋 Deployment Checklist:
- [ ] Backend deployed to cloud platform
- [ ] Production backend URL updated in Flutter app
- [ ] Frontend rebuilt with production config
- [ ] Firebase hosting deployed
- [ ] Tested on desktop browser
- [ ] Tested on mobile browser
- [ ] CORS working correctly

## 🐛 Troubleshooting:
- If images don't upload, check CORS configuration
- If API calls fail, verify backend URL in api_config.dart
- For mobile issues, check browser developer tools
- Ensure backend health endpoint returns 200 OK

## 📊 Current Features:
- ✅ Camera capture and gallery upload
- ✅ Image resolution limiting (max 1500px)
- ✅ PNG format conversion
- ✅ Advanced card detection
- ✅ Multi-player support (1-2 players)
- ✅ Blackjack scoring with Ace adjustment
- ✅ Mobile-optimized UI
