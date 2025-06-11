# 🎰 Blackjack Vision - Usage Guide

## 🚀 Quick Start

### Web Browser (Chrome)
1. Open: `http://localhost:3000`
2. Click "Let's Start"
3. Select number of players (1 or 2) 
4. Click "Capture with Webcam"
5. Grant camera permissions when prompted
6. Take a photo of your blackjack setup
7. View the results with detected cards and scores!

### Mobile Device
1. Ensure your mobile device is on the same WiFi network
2. Run: `flutter run -d <your-device-id>`
3. Use the camera capture button to take photos
4. The app will automatically analyze the cards

## 🔧 Troubleshooting

### Test Backend Connection
- Use the "Test Backend Connection" button in the app
- Should show: "✅ Backend connection successful!"

### Manual API Test
```bash
cd /Users/ahmedadnan/Desktop/HTWG/S6/Computervision-2D/blackjack_vision
python3 test_api.py
```

### Check Backend Status
```bash
curl http://localhost:8000/health
# Should return: {"status":"ok","message":"Backend is running"}
```

## 📱 Device Configuration

### For Physical Mobile Devices:
- Android: Uses `http://192.168.178.26:8000`
- iOS: Uses `http://192.168.178.26:8000`

### For Emulators:
- Android Emulator: Uses `http://10.0.2.2:8000`
- iOS Simulator: Uses `http://localhost:8000`

## 🎯 How to Use

1. **Setup**: Arrange your blackjack cards on a table
2. **Regions**: 
   - Top half of image = Dealer cards
   - Bottom half = Player cards
   - For 2 players: Bottom splits left/right
3. **Capture**: Take a clear photo with good lighting
4. **Results**: View detected cards and calculated scores

## 🎴 Supported Cards

The app recognizes all standard playing cards:
- Aces through Kings
- All four suits (Hearts, Diamonds, Clubs, Spades)
- Proper blackjack scoring (Ace = 1 or 11)

## ⚡ Servers Running

- **Backend**: `http://0.0.0.0:8000` (FastAPI)
- **Frontend**: `http://localhost:3000` (Flutter Web)
- **Mobile Access**: `http://192.168.178.26:8000`

## 🎊 Enjoy Your AI-Powered Blackjack Experience!
