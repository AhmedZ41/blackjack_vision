# 🚀 Complete Deployment Solution for Blackjack Vision

## Current Status:
- ✅ **Frontend**: Deployed to Firebase
- ❌ **Backend**: Needs deployment
- ✅ **Fixed**: Camera screen now uses ApiConfig.baseUrl instead of hardcoded IP

## 🎯 Quick Solution (Test deployed frontend with local backend):

### Option 1: Use ngrok (Temporary tunnel)

1. **Start your backend locally:**
   ```bash
   cd backend
   python main.py
   ```

2. **Install and use ngrok:**
   ```bash
   # Install ngrok
   brew install ngrok/ngrok/ngrok
   
   # In a new terminal, expose your local backend
   ngrok http 8000
   ```

3. **Copy the ngrok URL** (looks like: `https://abc123.ngrok.io`)

4. **Update your API config:**
   ```dart
   // In frontend/lib/config/api_config.dart, line 9:
   static const String _productionBackendUrl = 'https://abc123.ngrok.io';
   ```

5. **Rebuild and redeploy frontend:**
   ```bash
   cd frontend
   flutter build web --release
   firebase deploy --only hosting
   ```

## 🌐 Permanent Backend Deployment Options:

### Option 1: Render (Recommended - Free tier)

1. **Create account at**: https://render.com
2. **Connect your GitHub repository**
3. **Create New Web Service**
4. **Settings:**
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `uvicorn main:app --host 0.0.0.0 --port $PORT`
   - Root Directory: `backend`
   - Environment: Python 3

### Option 2: Railway (If CLI works)

1. **Install Railway CLI:**
   ```bash
   npm install -g @railway/cli
   ```

2. **Deploy:**
   ```bash
   cd backend
   railway login
   railway init
   railway up
   ```

### Option 3: Heroku (Paid)

1. **Install Heroku CLI**
2. **Create app and deploy**

## 📱 Testing Your Deployed App:

Once backend is deployed:

1. **Get your backend URL** (e.g., `https://your-app.render.com`)

2. **Update API config:**
   ```dart
   static const String _productionBackendUrl = 'https://your-app.render.com';
   ```

3. **Rebuild and redeploy frontend:**
   ```bash
   cd frontend
   flutter build web --release
   firebase deploy --only hosting
   ```

4. **Your app will be available at:**
   - `https://blackjack-vision-ai.web.app`
   - Works on laptop and iPhone browsers

## 🔧 Files Changed:

✅ **camera_screen.dart**: Fixed hardcoded IP to use `ApiConfig.baseUrl`
✅ **main.py**: Added PORT environment variable support
✅ **start.sh**: Created start script for cloud deployment

## 🎯 Next Steps:

1. Choose a backend deployment method (Render recommended)
2. Deploy backend and get URL
3. Update `_productionBackendUrl` in api_config.dart
4. Redeploy frontend
5. Test on laptop and iPhone browsers

## 📱 Your Frontend URL:
https://blackjack-vision-ai.web.app (or similar Firebase URL)

Would you like me to help you with any specific deployment method?
