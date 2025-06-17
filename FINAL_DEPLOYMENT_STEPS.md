# 🚀 COMPLETE DEPLOYMENT GUIDE - Blackjack Vision AI

## 📱 Your Frontend is Ready - Just Need Backend!

### STEP 1: Deploy Backend to Render (Free & Easy)

1. **Go to https://render.com and sign up/login**

2. **Create New Web Service:**
   - Click "New +" → "Web Service"
   - Connect your GitHub account
   - Select your blackjack_vision repository
   - **Important Settings:**
     - **Name**: `blackjack-vision-backend`
     - **Region**: Choose closest to you
     - **Branch**: `main` (or your current branch)
     - **Root Directory**: `backend`
     - **Runtime**: `Python 3`
     - **Build Command**: `pip install -r requirements.txt`
     - **Start Command**: `uvicorn main:app --host 0.0.0.0 --port $PORT`

3. **Deploy!** - Render will give you a URL like: `https://blackjack-vision-backend.onrender.com`

### STEP 2: Update Frontend with Backend URL

4. **Edit this file: `frontend/lib/config/api_config.dart`**
   ```dart
   // Line 9 - Replace this:
   static const String _productionBackendUrl = 'https://your-backend-url.com';
   
   // With your Render URL:
   static const String _productionBackendUrl = 'https://blackjack-vision-backend.onrender.com';
   ```

### STEP 3: Rebuild & Deploy Frontend

5. **Run these commands in Terminal:**
   ```bash
   cd /Users/ahmedadnan/Desktop/HTWG/S6/Computervision-2D/blackjack_vision/frontend
   flutter build web --release
   cd ..
   firebase deploy --only hosting
   ```

6. **Firebase will give you a URL like:** `https://blackjack-vision-ai.web.app`

### STEP 4: Test Your App! 🎉

7. **Open your Firebase URL in any browser:**
   - Works on laptop ✅
   - Works on iPhone Safari ✅
   - Works on any mobile browser ✅

---

## 🆘 QUICK TEST OPTION (if you want to test now):

### Use ngrok for temporary backend:

1. **Start your local backend:**
   ```bash
   cd backend
   python main.py
   ```

2. **Download ngrok from https://ngrok.com/download**

3. **Run ngrok:**
   ```bash
   ./ngrok http 8000
   ```

4. **Copy the https URL** (like `https://abc123.ngrok.app`)

5. **Update api_config.dart** with that URL

6. **Rebuild and deploy frontend**

---

## 📋 What You Have:

✅ Backend code ready for deployment
✅ Frontend built and ready
✅ Firebase project created: `blackjack-vision-ai`
✅ All configuration files in place
✅ Fixed hardcoded IP issue

## 🎯 What You Need:

1. Deploy backend to Render (5 minutes)
2. Update API config with backend URL
3. Redeploy frontend to Firebase

**Your app will then work on any device with internet! 🌍**

---

## 📱 Expected URLs:
- **Frontend**: `https://blackjack-vision-ai.web.app`
- **Backend**: `https://blackjack-vision-backend.onrender.com`

Would you like me to help with any specific step?
