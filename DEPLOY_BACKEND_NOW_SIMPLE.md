# 🚀 DEPLOY YOUR BACKEND NOW - Render (Easiest Option)

## 📋 5-Minute Manual Deployment to Render

### Step 1: Prepare Your Files (Already Done!)
✅ Your backend is already configured for cloud deployment

### Step 2: Deploy to Render
1. Go to **https://render.com**
2. Click **"Get Started for Free"** and sign up (you can use GitHub login)
3. Click **"New +"** → **"Web Service"**
4. Choose **"Build and deploy from a Git repository"**
5. Connect your GitHub account and select your repository
   - Repository: `blackjack_vision`
   - Branch: `main` (or your current branch)

### Step 3: Configure the Service
Fill in these settings:
- **Name**: `blackjack-vision-backend`
- **Region**: Choose closest to you (e.g., `Oregon (US West)`)
- **Branch**: `main`
- **Root Directory**: `backend`
- **Environment**: `Docker`
- **Build Command**: (leave empty)
- **Start Command**: (leave empty)

### Step 4: Advanced Settings
- **Health Check Path**: `/health`
- **Auto-Deploy**: `Yes`

### Step 5: Deploy!
1. Click **"Create Web Service"**
2. Wait 3-5 minutes for deployment
3. You'll get a URL like: `https://blackjack-vision-backend-xyz.onrender.com`

### Step 6: Update Frontend
Once deployed, copy your Render URL and run:
```bash
# Update the API config with your new URL
# Then redeploy frontend
./deploy_frontend.sh
```

## 🧪 Test Your Deployment
```bash
# Replace with your actual Render URL
curl https://your-render-url.onrender.com/health
```

## 🎯 Alternative: Railway (Command Line)
If you prefer command line:
```bash
./deploy_backend_railway.sh
```

## 📱 Final Result
After both deployments:
- **Frontend**: https://blackjack-vision-ai.web.app
- **Backend**: https://your-render-url.onrender.com
- **Accessible from**: Any device with internet (laptop, phone, tablet)

---
**⏱️ Total Time**: ~10 minutes  
**💰 Cost**: FREE (both Render and Firebase have free tiers)
