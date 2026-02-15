# Blackjack Vision

A computer vision-based blackjack card detection and strategy recommendation system that uses real-time image analysis to identify playing cards and provide optimal gameplay advice based on advanced blackjack basic strategy.

## Overview

Blackjack Vision is a full-stack application that combines computer vision, machine learning, and game theory to analyze blackjack hands from images. The system detects playing cards using contour detection and template matching, calculates hand values, and provides strategic recommendations based on mathematical probability models.

## Architecture

The project follows a client-server architecture with three main components:

```
┌─────────────────┐
│  Flutter Web    │  Frontend (Firebase Hosting)
│   Application   │  - Camera interface
└────────┬────────┘  - Image upload
         │           - Results display
         │ HTTP
         ▼
┌─────────────────┐
│  FastAPI Server │  Backend (Render.com)
│   Python 3.10   │  - Image processing
└────────┬────────┘  - Card detection
         │           - Strategy engine
         │
         ▼
┌─────────────────┐
│  OpenCV Engine  │  Computer Vision
│  Card Templates │  - Contour detection
└─────────────────┘  - Template matching
                     - Perspective transform
```

### Data Flow

1. User captures or uploads an image of blackjack cards
2. Frontend sends image to backend API endpoint
3. Backend processes image using OpenCV:
   - Detects card contours via edge detection
   - Applies perspective transformation
   - Matches cards against template database
4. Backend calculates hand values and strategy recommendations
5. Results are returned to frontend for display

## Tech Stack

### Frontend
- **Framework**: Flutter 3.32.2 (Dart)
- **Platform**: Web (cross-platform capable)
- **Deployment**: Firebase Hosting
- **Key Libraries**:
  - `camera`: Camera access for image capture
  - `image_picker`: Image selection from gallery
  - `http`: REST API communication

### Backend
- **Framework**: FastAPI (Python 3.10)
- **Deployment**: Render.com (containerized)
- **Core Libraries**:
  - `opencv-python`: Computer vision operations
  - `numpy`: Numerical computations
  - `uvicorn`: ASGI server
- **API**: RESTful HTTP endpoints

### Computer Vision Pipeline
- **Edge Detection**: Canny edge detection algorithm
- **Contour Analysis**: OpenCV contour detection with area/aspect ratio filtering
- **Perspective Transform**: Four-point transformation for card normalization
- **Template Matching**: Multi-metric scoring (correlation, structural similarity, histogram comparison)

### Infrastructure
- **Version Control**: Git/GitHub
- **CI/CD**: Automated deployment via Git push
- **Containerization**: Docker (backend)
- **CORS**: Enabled for cross-origin requests

## Features

### Card Detection
- Detects 1-7 playing cards in a single image
- Supports multiple player configurations (1-2 players + dealer)
- Automatic card classification by position (dealer vs player zones)
- Robust to varying lighting conditions and camera angles

### Game Modes
1. **Standard Mode**: Analyze full table (dealer + players)
2. **AI Advice Mode**: Personal hand analysis with strategic recommendations

### Strategy Engine
- Advanced blackjack basic strategy implementation
- Dealer-specific recommendations
- Probability calculations for win likelihood
- Soft/hard hand detection and strategy
- Pair splitting advice
- Double down recommendations

### User Interface
- Clean, modern design with dark theme
- Responsive layout for web browsers
- Real-time camera preview (mobile devices)
- Visual feedback for card detection
- Backend connection status indicator

## API Endpoints

### Core Endpoints
- `GET /` - Health check
- `GET /docs` - Interactive API documentation (Swagger UI)
- `POST /analyze/` - Main card analysis endpoint
  - Parameters: `file` (image), `players` (1, 2, or "advice")
  - Returns: Card ranks, scores, and strategy advice
- `POST /analyze/marked-contours/` - Debug endpoint with visual contour overlay
- `GET /debug/templates` - List loaded card templates

## Project Structure

```
blackjack_vision/
├── backend/
│   ├── main.py              # FastAPI application
│   ├── requirements.txt     # Python dependencies
│   ├── Dockerfile          # Container configuration
│   ├── render.yaml         # Render deployment config
│   └── Cards/              # Card template images (52 cards)
├── frontend/
│   ├── lib/
│   │   ├── main.dart       # Application entry point
│   │   ├── config/
│   │   │   └── api_config.dart  # Backend URL configuration
│   │   ├── screens/
│   │   │   ├── welcome_screen.dart
│   │   │   ├── player_selection_screen.dart
│   │   │   ├── camera_screen.dart
│   │   │   └── results_screen.dart
│   │   └── widgets/
│   │       └── connection_footer.dart
│   ├── web/                # Web-specific assets
│   └── pubspec.yaml        # Flutter dependencies
├── firebase.json           # Firebase Hosting configuration
└── docker-compose.yml      # Local development setup
```

## Algorithm Details

### Card Detection Pipeline

1. **Preprocessing**:
   - Image resizing (min 400x400, max 1500x1500)
   - Gaussian blur for noise reduction
   - Grayscale conversion

2. **Contour Detection**:
   - Canny edge detection (thresholds: 50, 150)
   - External contour extraction
   - Minimum area filtering (5000 pixels)
   - Aspect ratio validation (0.5-2.0)

3. **Spatial Classification**:
   - Dealer cards: centroid in top 50% of image
   - Player 1 cards: centroid in bottom 50% (or right side for 2 players)
   - Player 2 cards: centroid in bottom left (2-player mode)

4. **Card Recognition**:
   - Four-point perspective transform to 200x300 pixels
   - Multi-metric template matching:
     - 50% correlation coefficient
     - 30% structural similarity (gradient-based)
     - 20% histogram correlation
   - Confidence threshold: 0.3

### Strategy Calculation

The strategy engine implements professional blackjack basic strategy with:
- Soft vs hard hand detection
- Dealer upcard strength analysis (weak: 4-6, medium: 2-3,7-8, strong: 9-A)
- Pair splitting recommendations
- Double down opportunities
- Win probability estimation

## Development Setup

### Prerequisites
- Python 3.10+
- Flutter 3.32+
- Node.js (for Firebase CLI)
- Git

### Backend Local Development
```bash
cd backend
pip install -r requirements.txt
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### Frontend Local Development
```bash
cd frontend
flutter pub get
flutter run -d chrome
```

### Deploy Backend
Push to GitHub main branch - Render auto-deploys

### Deploy Frontend
```bash
cd frontend
flutter build web
cd ..
firebase deploy --only hosting
```

## Configuration

### Backend URL
Edit `frontend/lib/config/api_config.dart`:
- Development: Points to local IP/localhost
- Production: Points to Render.com deployment

### Firebase Hosting
Configure in `firebase.json`:
- Public directory: `frontend/build/web`
- Single-page app rewrites enabled

## Performance

- Card detection: ~2-5 seconds per image
- Template matching: 52 templates per card
- API response time: ~3-6 seconds (including network)
- Frontend rendering: <100ms

## Limitations

- Requires clear card visibility
- Works best with standard poker-sized cards
- Needs adequate lighting
- Maximum 7 cards reliably detected
- Template database limited to standard 52-card deck

## Team

Computer Vision 2D - Summer Semester 2025
- Ahmed
- Eugen  
- Nico

HTWG Konstanz

## License

Academic project - HTWG Konstanz

## Live Demo

- Frontend: https://blackjack-vision-ai.web.app
- Backend API: https://blackjack-vision-backend.onrender.com/docs
