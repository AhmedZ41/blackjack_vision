from fastapi import FastAPI, File, UploadFile, Form
from fastapi import FastAPI, File, UploadFile, Form
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import cv2
import numpy as np
import os
from typing import List, Tuple
import json

app = FastAPI()

# 👇 Now it's safe to call this
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# === CONFIG ===
CARD_TEMPLATES_PATH = "PNG-cards"

# === Load templates ===
def load_templates() -> List[Tuple[str, np.ndarray]]:
    templates = []
    for file in os.listdir(CARD_TEMPLATES_PATH):
        if file.endswith(".png"):
            name = file.replace(".png", "").replace("_of_", " ").title()
            template = cv2.imread(os.path.join(CARD_TEMPLATES_PATH, file), cv2.IMREAD_COLOR)
            
            # Resize templates to a more reasonable size for matching
            target_height = 100
            scale = target_height / template.shape[0]
            target_width = int(template.shape[1] * scale)
            template_resized = cv2.resize(template, (target_width, target_height))
            
            templates.append((name, template_resized))
    return templates

TEMPLATES = load_templates()
print(f"Loaded {len(TEMPLATES)} card templates")

# === Helper functions from notebook ===
def order_points(pts):
    """Order points for perspective transform: top-left, top-right, bottom-right, bottom-left"""
    rect = np.zeros((4, 2), dtype="float32")
    s = pts.sum(axis=1)
    rect[0] = pts[np.argmin(s)]  # top-left
    rect[2] = pts[np.argmax(s)]  # bottom-right
    diff = np.diff(pts, axis=1)
    rect[1] = pts[np.argmin(diff)]  # top-right
    rect[3] = pts[np.argmax(diff)]  # bottom-left
    return rect

def four_point_transform(image, pts, width=200, height=300):
    """Perspective transform to get bird's-eye view of card"""
    rect = order_points(pts)
    dst = np.array([
        [0, 0],
        [width - 1, 0],
        [width - 1, height - 1],
        [0, height - 1]
    ], dtype="float32")
    M = cv2.getPerspectiveTransform(rect, dst)
    return cv2.warpPerspective(image, M, (width, height))

def get_leftmost_x(contour):
    """Get leftmost x coordinate for sorting"""
    pts = contour.reshape(-1, 2)
    return np.min(pts[:, 0])

def combined_card_score(card_img, template_img):
    """Multi-metric scoring like in notebook"""
    # Ensure both are grayscale
    if len(card_img.shape) == 3:
        card_img = cv2.cvtColor(card_img, cv2.COLOR_BGR2GRAY)
    if len(template_img.shape) == 3:
        template_img = cv2.cvtColor(template_img, cv2.COLOR_BGR2GRAY)
    
    # Correlation score
    result = cv2.matchTemplate(card_img, template_img, cv2.TM_CCOEFF_NORMED)
    corr = max(0, result[0, 0])
    
    # Structural similarity (simplified)
    card_grad_x = cv2.Sobel(card_img, cv2.CV_64F, 1, 0, ksize=3)
    card_grad_y = cv2.Sobel(card_img, cv2.CV_64F, 0, 1, ksize=3)
    card_grad = np.sqrt(card_grad_x**2 + card_grad_y**2)
    card_grad /= (np.max(card_grad) + 1e-8)
    
    template_grad_x = cv2.Sobel(template_img, cv2.CV_64F, 1, 0, ksize=3)
    template_grad_y = cv2.Sobel(template_img, cv2.CV_64F, 0, 1, ksize=3)
    template_grad = np.sqrt(template_grad_x**2 + template_grad_y**2)
    template_grad /= (np.max(template_grad) + 1e-8)
    
    diff = np.abs(card_grad - template_grad)
    struct = max(0, 1 - np.mean(diff))
    
    # Histogram correlation
    hist1 = cv2.calcHist([card_img], [0], None, [256], [0, 256])
    hist2 = cv2.calcHist([template_img], [0], None, [256], [0, 256])
    hist1 /= (np.sum(hist1) + 1e-8)
    hist2 /= (np.sum(hist2) + 1e-8)
    hist = max(0, cv2.compareHist(hist1, hist2, cv2.HISTCMP_CORREL))
    
    # Combined score (50% correlation, 30% structural, 20% histogram)
    combined = 0.5 * corr + 0.3 * struct + 0.2 * hist
    return combined

def detect_and_classify_cards(image: np.ndarray, players: int = 1) -> tuple:
    """
    Detect cards using contour detection like in the notebook.
    Returns (dealer_cards, player1_cards, player2_cards)
    """
    print(f"Starting card detection on image shape: {image.shape}")
    
    # 1. Preprocessing (following notebook)
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)
    edges = cv2.Canny(blurred, 50, 150)
    
    # 2. Find contours
    contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    print(f"Found {len(contours)} total contours")
    
    # 3. Filter for card-like contours (quadrilaterals with large area)
    card_contours = []
    min_area = 10000  # Reduced from 10000
    
    for i, cnt in enumerate(contours):
        area = cv2.contourArea(cnt)
        peri = cv2.arcLength(cnt, True)
        approx = cv2.approxPolyDP(cnt, 0.02 * peri, True)
        
        print(f"Contour {i}: area={area:.0f}, vertices={len(approx)}")
        
        # More flexible criteria
        if len(approx) >= 4 and area > min_area:  # Changed from == 4 to >= 4
            # Additional check: aspect ratio should be card-like
            x, y, w, h = cv2.boundingRect(cnt)
            aspect_ratio = w / h if h > 0 else 0
            
            # Cards typically have aspect ratio between 0.6 and 1.8
            if 0.5 <= aspect_ratio <= 2.0:
                card_contours.append(approx)
                print(f"  → Added as card contour (aspect ratio: {aspect_ratio:.2f})")
            else:
                print(f"  → Rejected: bad aspect ratio {aspect_ratio:.2f}")
        else:
            if area <= min_area:
                print(f"  → Rejected: area too small")
            else:
                print(f"  → Rejected: not enough vertices")
    
    print(f"Found {len(card_contours)} card-like contours")
    
    if len(card_contours) == 0:
        print("No card contours detected!")
        return [], [], []
    
    # 4. Classify contours into dealer vs player(s)
    h, w = image.shape[:2]
    dealer_contours = []
    player_contours = []
    
    for cnt in card_contours:
        # Calculate centroid
        M = cv2.moments(cnt)
        if M["m00"] != 0:
            cY = int(M["m01"] / M["m00"])
        else:
            x, y, ww, hh = cv2.boundingRect(cnt)
            cY = y + hh // 2
        
        if cY < h / 2:
            dealer_contours.append(cnt)
            print(f"Classified contour as dealer (cY={cY} < {h/2})")
        else:
            player_contours.append(cnt)
            print(f"Classified contour as player (cY={cY} >= {h/2})")
    
    # Sort by x position (left to right)
    dealer_contours = sorted(dealer_contours, key=get_leftmost_x)
    player_contours = sorted(player_contours, key=get_leftmost_x)
    
    print(f"Classified: {len(dealer_contours)} dealer, {len(player_contours)} player contours")
    
    # 5. Extract and warp cards
    dealer_cards = []
    for i, cnt in enumerate(dealer_contours):
        try:
            # For debugging, let's handle cases where we don't have exactly 4 points
            if len(cnt) >= 4:
                # If more than 4 points, use the 4 corner points
                if len(cnt) > 4:
                    # Use bounding rectangle as fallback
                    x, y, w, h = cv2.boundingRect(cnt)
                    pts = np.array([[x, y], [x+w, y], [x+w, y+h], [x, y+h]], dtype=np.float32)
                else:
                    pts = cnt.reshape(4, 2).astype(np.float32)
                
                warped = four_point_transform(image, pts)
                dealer_cards.append(warped)
                print(f"Successfully warped dealer card {i+1}")
            else:
                print(f"Dealer contour {i+1} has insufficient points: {len(cnt)}")
        except Exception as e:
            print(f"Error warping dealer card {i+1}: {e}")
    
    player1_cards = []
    player2_cards = []
    
    if players == 1:
        for i, cnt in enumerate(player_contours):
            try:
                if len(cnt) >= 4:
                    if len(cnt) > 4:
                        x, y, w, h = cv2.boundingRect(cnt)
                        pts = np.array([[x, y], [x+w, y], [x+w, y+h], [x, y+h]], dtype=np.float32)
                    else:
                        pts = cnt.reshape(4, 2).astype(np.float32)
                    
                    warped = four_point_transform(image, pts)
                    player1_cards.append(warped)
                    print(f"Successfully warped player card {i+1}")
                else:
                    print(f"Player contour {i+1} has insufficient points: {len(cnt)}")
            except Exception as e:
                print(f"Error warping player card {i+1}: {e}")
    else:
        # Split player contours for 2 players
        mid_x = w / 2
        for i, cnt in enumerate(player_contours):
            M = cv2.moments(cnt)
            if M["m00"] != 0:
                cX = int(M["m10"] / M["m00"])
            else:
                x, y, ww, hh = cv2.boundingRect(cnt)
                cX = x + ww // 2
            
            try:
                if len(cnt) >= 4:
                    if len(cnt) > 4:
                        x, y, w, h = cv2.boundingRect(cnt)
                        pts = np.array([[x, y], [x+w, y], [x+w, y+h], [x, y+h]], dtype=np.float32)
                    else:
                        pts = cnt.reshape(4, 2).astype(np.float32)
                    
                    warped = four_point_transform(image, pts)
                    if cX >= mid_x:
                        player1_cards.append(warped)  # Right side
                        print(f"Successfully warped player1 card {len(player1_cards)}")
                    else:
                        player2_cards.append(warped)  # Left side
                        print(f"Successfully warped player2 card {len(player2_cards)}")
                else:
                    print(f"Player contour {i+1} has insufficient points: {len(cnt)}")
            except Exception as e:
                print(f"Error warping player card {i+1}: {e}")
    
    print(f"Extracted cards: {len(dealer_cards)} dealer, {len(player1_cards)} player1, {len(player2_cards)} player2")
    return dealer_cards, player1_cards, player2_cards

def match_cards_to_templates(warped_cards: List[np.ndarray], templates: List[Tuple[str, np.ndarray]]) -> List[str]:
    """Match warped cards to templates using multi-metric scoring"""
    detected_ranks = []
    
    # Prepare template dict by rank (like in notebook)
    card_templates = {}
    for name, template in templates:
        # Resize template to match warped card size
        template_resized = cv2.resize(template, (200, 300))
        template_blurred = cv2.GaussianBlur(template_resized, (3, 3), 0)
        
        # Extract rank
        rank_name = name.split()[0]  # "Ace", "King", etc.
        if rank_name not in card_templates:
            card_templates[rank_name] = []
        card_templates[rank_name].append(template_blurred)
    
    # Match each warped card
    for i, card in enumerate(warped_cards):
        # Convert to grayscale and blur
        card_gray = cv2.cvtColor(card, cv2.COLOR_BGR2GRAY)
        card_blurred = cv2.GaussianBlur(card_gray, (3, 3), 0)
        
        best_rank = None
        best_score = -1
        
        # Try each rank
        for rank, rank_templates in card_templates.items():
            max_score_for_rank = -1
            
            # Try each template variant for this rank
            for template in rank_templates:
                score = combined_card_score(card_blurred, template)
                if score > max_score_for_rank:
                    max_score_for_rank = score
            
            if max_score_for_rank > best_score:
                best_score = max_score_for_rank
                best_rank = rank
        
        if best_rank and best_score > 0.3:  # Minimum confidence threshold
            detected_ranks.append(best_rank)
            print(f"Card {i+1}: {best_rank} (confidence: {best_score:.3f})")
        else:
            print(f"Card {i+1}: No match found (best score: {best_score:.3f})")
    
    return detected_ranks

# === Calculate Blackjack score ===
def calculate_score(cards: List[str]) -> int:
    """Calculate blackjack score from list of rank names"""
    if not cards:
        return 0
        
    value_map = {
        '2': 2, '3': 3, '4': 4, '5': 5,
        '6': 6, '7': 7, '8': 8, '9': 9, '10': 10,
        'Jack': 10, 'Queen': 10, 'King': 10,
        'Ace': 11
    }
    score = 0
    aces = 0
    
    for card_rank in cards:
        print(f"Processing card rank: {card_rank}")
        
        if card_rank == 'Ace':
            aces += 1
            score += 11
        else:
            card_value = value_map.get(card_rank, 0)
            if card_value == 0:
                # Try to parse as number for cases like "10"
                try:
                    card_value = int(card_rank)
                    if 2 <= card_value <= 10:
                        score += card_value
                except ValueError:
                    print(f"Warning: Unknown card rank '{card_rank}'")
            else:
                score += card_value

    # Handle aces (convert 11 to 1 if over 21)
    while score > 21 and aces:
        score -= 10
        aces -= 1

    print(f"Final score for {cards}: {score}")
    return score

# === Debug endpoint ===
@app.get("/debug/templates")
async def debug_templates():
    template_info = []
    for name, template in TEMPLATES:
        template_info.append({
            "name": name,
            "shape": template.shape,
            "size": f"{template.shape[1]}x{template.shape[0]}"
        })
    return {"templates": template_info, "total": len(TEMPLATES)}

# === Health Check Endpoint ===
@app.get("/health")
async def health_check():
    return {"status": "ok", "message": "Backend is running"}

# === Main API Endpoints ===
@app.get("/analyze/")
async def analyze_get():
    return {
        "message": "This endpoint requires a POST request with an image file.",
        "usage": "POST /analyze/ with 'file' (image) and 'players' (1 or 2) parameters",
        "test_endpoint": "/debug/templates"
    }

@app.post("/analyze/")
async def analyze_image(file: UploadFile = File(...), players: int = Form(...)):
    try:
        image_data = await file.read()
        nparr = np.frombuffer(image_data, np.uint8)
        image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        
        if image is None:
            return JSONResponse(
                status_code=400, 
                content={"error": "Could not decode image"}
            )
        
        print(f"Original image format: {file.content_type}")
        print(f"Image shape: {image.shape}")
        print(f"Number of players: {players}")
        
        # Convert to PNG format as part of preprocessing
        # Encode as PNG and decode back to ensure consistent format
        success, png_buffer = cv2.imencode('.png', image)
        if not success:
            return JSONResponse(
                status_code=500,
                content={"error": "Failed to convert image to PNG format"}
            )
        
        # Decode the PNG back to ensure we're working with PNG-processed image
        image = cv2.imdecode(png_buffer, cv2.IMREAD_COLOR)
        print(f"Converted to PNG format - Image shape: {image.shape}")
        
        # Limit image resolution to max 1500 pixels in any direction
        max_dimension = 1500
        height, width = image.shape[:2]
        if height > max_dimension or width > max_dimension:
            # Calculate scale factor to fit within max_dimension x max_dimension
            scale_factor = min(max_dimension / height, max_dimension / width)
            new_width = int(width * scale_factor)
            new_height = int(height * scale_factor)
            image = cv2.resize(image, (new_width, new_height), interpolation=cv2.INTER_AREA)
            print(f"Reduced resolution from {width}x{height} to {new_width}x{new_height} (scale: {scale_factor:.3f})")
        
        # Resize image if it's too small (but maintain aspect ratio)
        min_height, min_width = 400, 400
        if image.shape[0] < min_height or image.shape[1] < min_width:
            scale_factor = max(min_height / image.shape[0], min_width / image.shape[1])
            new_width = int(image.shape[1] * scale_factor)
            new_height = int(image.shape[0] * scale_factor)
            image = cv2.resize(image, (new_width, new_height))
            print(f"Upscaled small image to: {image.shape}")

        # Use notebook-style detection instead of simple region splitting
        dealer_cards, player1_cards, player2_cards = detect_and_classify_cards(image, players)
        
        # Match cards to templates
        dealer_ranks = match_cards_to_templates(dealer_cards, TEMPLATES)
        player1_ranks = match_cards_to_templates(player1_cards, TEMPLATES)
        player2_ranks = match_cards_to_templates(player2_cards, TEMPLATES) if player2_cards else []
        
        print(f"Detected cards - Dealer: {dealer_ranks}, Player1: {player1_ranks}, Player2: {player2_ranks}")

        results = {
            "dealer": {
                "cards": dealer_ranks,
                "score": calculate_score(dealer_ranks)
            },
            "player1": {
                "cards": player1_ranks,
                "score": calculate_score(player1_ranks)
            }
        }

        if players == 2:
            results["player2"] = {
                "cards": player2_ranks,
                "score": calculate_score(player2_ranks)
            }

        return JSONResponse(content=results)
    
    except Exception as e:
        print(f"Error processing image: {e}")
        import traceback
        traceback.print_exc()
        return JSONResponse(
            status_code=500,
            content={"error": f"Error processing image: {str(e)}"}
        )

# === Server Startup ===
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
