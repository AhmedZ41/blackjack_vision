# 🚀 URGENT: Deploy Backend and Fix Frontend

## Current Issue:
- ✅ Frontend deployed to Firebase but using wrong backend URL
- ❌ Backend not deployed yet

## STEP 1: Deploy Backend to Render (5 minutes)

### Option A: Manual Render Deployment
1. **Go to**: https://render.com
2. **Sign in/up** and click "New +" → "Web Service"
3. **Connect GitHub** and select your repository
4. **Configuration**:
   ```
   Name: blackjack-vision-backend
   Root Directory: backend
   Runtime: Python 3
   Build Command: pip install -r requirements.txt
   Start Command: uvicorn main:app --host 0.0.0.0 --port $PORT
   Auto-Deploy: Yes
   ```
5. **Deploy** - You'll get URL: `https://blackjack-vision-backend.onrender.com`

### Option B: Railway Deployment (Alternative)
1. Go to https://railway.app
2. Sign in with GitHub
3. "New Project" → "Deploy from GitHub repo"
4. Select your blackjack_vision repository
5. Choose "backend" folder
6. Deploy automatically

## STEP 2: Verify Backend is Live

1. **Check**: `https://blackjack-vision-backend.onrender.com/health`
2. **Should return**: `{"status":"ok","message":"Backend is running"}`

## STEP 3: Update and Redeploy Frontend

**I've already updated the frontend config to use the Render URL!**

Just run these commands:

```bash
# Build frontend with new backend URL
cd /Users/ahmedadnan/Desktop/HTWG/S6/Computervision-2D/blackjack_vision/frontend
flutter build web --release

# Deploy to Firebase
cd ..
firebase deploy --only hosting
```

## STEP 4: Test Complete App

1. **Open**: https://blackjack-vision-ai.web.app
2. **Test**:
   - Upload image ✅
   - Camera capture ✅  
   - Card detection ✅
   - Works on mobile ✅

---

## 🔧 If Render URL is Different:

If your Render app gets a different URL, update this file:
**`frontend/lib/config/api_config.dart`** line 9:

```dart
static const String _productionBackendUrl = 'https://your-actual-render-url.com';
```

Then rebuild and redeploy frontend.

---

## 🎯 Expected URLs:
- **Frontend**: https://blackjack-vision-ai.web.app
- **Backend**: https://blackjack-vision-backend.onrender.com
- **Health Check**: https://blackjack-vision-backend.onrender.com/health

## ⚡ Quick Test Command:
```bash
curl https://blackjack-vision-backend.onrender.com/health
```

Once both are deployed, your app will work on any device worldwide! 🌍
