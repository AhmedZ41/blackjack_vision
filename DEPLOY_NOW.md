# 🎯 EXACT STEPS TO DEPLOY YOUR BLACKJACK VISION APP

## ✅ Current Status:
- Frontend code: READY ✅
- Backend code: READY ✅  
- Firebase project: CREATED ✅
- Fixed hardcoded IP: DONE ✅

## 🚀 STEP-BY-STEP DEPLOYMENT:

### STEP 1: Deploy Backend (5 minutes)

1. **Go to**: https://render.com
2. **Sign up/Login** with GitHub
3. **Click**: "New +" → "Web Service"
4. **Select**: Your blackjack_vision repository
5. **Configure**:
   ```
   Name: blackjack-vision-backend
   Root Directory: backend
   Runtime: Python 3
   Build Command: pip install -r requirements.txt
   Start Command: uvicorn main:app --host 0.0.0.0 --port $PORT
   ```
6. **Click Deploy** - You'll get a URL like: `https://blackjack-vision-backend.onrender.com`

### STEP 2: Update Frontend Config

7. **Edit**: `frontend/lib/config/api_config.dart`
8. **Change line 9** from:
   ```dart
   static const String _productionBackendUrl = 'https://your-backend-url.com';
   ```
   **To**:
   ```dart
   static const String _productionBackendUrl = 'https://blackjack-vision-backend.onrender.com';
   ```

### STEP 3: Deploy Frontend

9. **Run this script**:
   ```bash
   cd /Users/ahmedadnan/Desktop/HTWG/S6/Computervision-2D/blackjack_vision
   ./deploy_frontend.sh
   ```

### STEP 4: Test Your App! 🎉

10. **Open**: `https://blackjack-vision-ai.web.app`
11. **Test on**:
    - Your laptop browser ✅
    - iPhone Safari ✅
    - Any mobile device ✅

---

## 🔗 EXPECTED URLS:
- **Frontend**: `https://blackjack-vision-ai.web.app`
- **Backend**: `https://blackjack-vision-backend.onrender.com`

## ⚡ QUICK TEST (Alternative):

If you want to test immediately without waiting for Render:

1. **Run locally**: `cd backend && python main.py`
2. **Download ngrok**: https://ngrok.com/download
3. **Expose**: `./ngrok http 8000`
4. **Use ngrok URL** in api_config.dart temporarily

---

## 🎯 WHAT HAPPENS:

1. **Users visit your Firebase URL**
2. **App loads in their browser**
3. **Camera/upload buttons work**
4. **Images sent to your Render backend**
5. **AI processes cards & returns results**
6. **Works on any device with internet! 🌍**

You're literally 3 steps away from having a fully deployed AI app! 🚀
