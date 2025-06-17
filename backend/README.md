# Blackjack Vision

Blackjack Vision is a computer vision-powered app that detects playing cards from an image and calculates the blackjack score for the dealer and one or two players. It consists of a FastAPI backend and a Flutter-based frontend.

## Features

- Detects and classifies cards in real images
- Supports 1 or 2 player configurations
- Computes blackjack points automatically
- Cross-device support (via browser or mobile)
- Backend runs fully inside Docker

## Tech Stack

- **Backend**: FastAPI + OpenCV
- **Frontend**: Flutter (web)
- **Containerization**: Docker & Docker Compose

## Setup Instructions

### 🐳 Backend (via Docker)

1. Install [Docker Desktop](https://www.docker.com/products/docker-desktop)
2. Clone this repository
3. From the project root, run:

```bash
docker-compose up --build
```

4. Test it in your browser:  
   `http://localhost:8000/health`

---

### 🌐 Frontend (Flutter Web)

1. Make sure you have Flutter installed:
   ```bash
   flutter doctor
   ```

2. Navigate to the frontend directory:
   ```bash
   cd frontend
   ```

3. Run the app in Chrome:
   ```bash
   flutter run -d chrome
   ```

4. Open your browser and go to:
   ```
   http://localhost:8080
   ```

> ⚠️ If you want to use the app from another device, make sure to update the backend URL in the frontend to your local IP.

## Notes

- Make sure your card templates are in `backend/Cards/`
- All processing is done on the backend
- Supports .png card templates with filenames like `ace_of_hearts.png`