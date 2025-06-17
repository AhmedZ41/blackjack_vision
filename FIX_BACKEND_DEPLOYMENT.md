# 🚀 URGENT: Deploy Backend to Render

## Problem: Backend URL doesn't exist yet!
- The URL `https://blackjack-vision-backend.onrender.com/health` returns "Not Found" 
- This is because we haven't deployed the backend yet

## Solution: Deploy Backend to Render (5 minutes)

### Step 1: Go to Render
1. **Open**: https://render.com
2. **Sign up/Login** (use GitHub for easier setup)

### Step 2: Create Web Service
1. **Click**: "New +" button (top right)
2. **Select**: "Web Service"
3. **Choose**: "Build and deploy from a Git repository"
4. **Click**: "Connect account" (connect your GitHub)

### Step 3: Configure Repository
1. **Find and select**: your `blackjack_vision` repository
2. **Click**: "Connect"

### Step 4: Configure Service Settings
Fill in these EXACT settings:

```
Name: blackjack-vision-backend
Region: (choose closest to you)
Branch: main (or your current branch)
Root Directory: backend
Runtime: Python 3
Build Command: pip install -r requirements.txt
Start Command: uvicorn main:app --host 0.0.0.0 --port $PORT
```

**Important**: Make sure "Root Directory" is set to `backend`

### Step 5: Deploy
1. **Click**: "Create Web Service"
2. **Wait**: 5-10 minutes for deployment
3. **Get URL**: Render will give you a URL like `https://blackjack-vision-backend-abc123.onrender.com`

### Step 6: Test Backend
1. **Visit**: `https://your-render-url.onrender.com/health`
2. **Should see**: `{"status":"ok","message":"Backend is running"}`

---

## Alternative: Deploy with Railway

If Render doesn't work, try Railway:

1. **Go to**: https://railway.app
2. **Sign in** with GitHub
3. **Click**: "New Project" → "Deploy from GitHub repo"
4. **Select**: your blackjack_vision repository
5. **Choose**: backend folder
6. **Deploy automatically**

---

## Alternative: Use Docker Locally + ngrok (Quick Test)

If you want to test immediately:

1. **Build and run with Docker**:
   ```bash
   cd /Users/ahmedadnan/Desktop/HTWG/S6/Computervision-2D/blackjack_vision
   docker-compose up --build
   ```

2. **Install ngrok** (if not installed):
   ```bash
   brew install ngrok/ngrok/ngrok
   ```

3. **Expose locally**:
   ```bash
   ngrok http 8000
   ```

4. **Use ngrok URL** in frontend config temporarily

---

## Once Backend is Deployed:

1. **Copy your actual backend URL** (from Render/Railway)
2. **Update** `frontend/lib/config/api_config.dart`:
   ```dart
   static const String _productionBackendUrl = 'https://your-actual-url.com';
   ```
3. **Redeploy frontend**:
   ```bash
   ./deploy_complete.sh
   ```

## Expected Timeline:
- Backend deployment: 5-10 minutes
- Frontend update: 2 minutes
- **Total**: ~15 minutes to full working app

The backend needs to be deployed first before the frontend can connect to it!
