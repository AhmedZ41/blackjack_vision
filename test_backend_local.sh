#!/bin/bash

echo "🧪 Testing Backend Locally Before Deployment"
echo "============================================"

cd /Users/ahmedadnan/Desktop/HTWG/S6/Computervision-2D/blackjack_vision/backend

echo "📋 Checking requirements..."
if [ ! -f "requirements.txt" ]; then
    echo "❌ requirements.txt not found!"
    exit 1
fi

echo "📋 Checking main.py..."
if [ ! -f "main.py" ]; then
    echo "❌ main.py not found!"
    exit 1
fi

echo "📋 Checking card templates..."
if [ ! -d "PNG-cards" ]; then
    echo "❌ PNG-cards directory not found!"
    exit 1
fi

echo "✅ All files present!"
echo ""
echo "🚀 Starting backend..."
echo "Once running, test: http://localhost:8000/health"
echo ""
echo "Press Ctrl+C to stop, then deploy using:"
echo "1. Go to https://render.com"
echo "2. Deploy from GitHub (backend folder)"
echo "3. Update frontend config with new URL"
echo "4. Redeploy frontend"
echo ""

python3 main.py
