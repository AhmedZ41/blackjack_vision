from fastapi import FastAPI, File, UploadFile, Form
from fastapi import FastAPI, File, UploadFile, Form
from fastapi.responses import JSONResponse, StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
import cv2
import numpy as np
import os
from typing import List, Tuple
import json
import base64
import io

app = FastAPI()

#nothing
# 👇 Now it's safe to call this
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# === CONFIG ===
CARD_TEMPLATES_PATH = "Cards/"

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

def create_marked_contours_image(image, players):
    """Create an image with marked card contours for visualization"""
    # Create a copy of the original image
    marked_image = image.copy()
    
    # Same preprocessing as in analyze endpoint
    max_dimension = 1500
    height, width = image.shape[:2]
    if height > max_dimension or width > max_dimension:
        scale_factor = min(max_dimension / height, max_dimension / width)
        new_width = int(width * scale_factor)
        new_height = int(height * scale_factor)
        marked_image = cv2.resize(marked_image, (new_width, new_height), interpolation=cv2.INTER_AREA)
    
    min_height, min_width = 400, 400
    if marked_image.shape[0] < min_height or marked_image.shape[1] < min_width:
        scale_factor = max(min_height / marked_image.shape[0], min_width / marked_image.shape[1])
        new_width = int(marked_image.shape[1] * scale_factor)
        new_height = int(marked_image.shape[0] * scale_factor)
        marked_image = cv2.resize(marked_image, (new_width, new_height))
    
    # Detect card contours (same logic as detect_and_classify_cards)
    gray = cv2.cvtColor(marked_image, cv2.COLOR_BGR2GRAY)
    edges = cv2.Canny(gray, 50, 150)
    contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    # Filter contours for card-like shapes
    card_contours = []
    min_area = 5000
    
    for contour in contours:
        area = cv2.contourArea(contour)
        if area > min_area:
            # Approximate contour to reduce points
            epsilon = 0.02 * cv2.arcLength(contour, True)
            approx = cv2.approxPolyDP(contour, epsilon, True)
            
            if len(approx) >= 4:
                x, y, w, h = cv2.boundingRect(contour)
                aspect_ratio = float(w) / h
                if 0.5 <= aspect_ratio <= 2.0:
                    card_contours.append(contour)
    
    # Draw contours and classify them
    h, w = marked_image.shape[:2]
    dealer_contours = []
    player_contours = []
    
    for cnt in card_contours:
        # Calculate centroid
        M = cv2.moments(cnt)
        if M["m00"] != 0:
            cY = int(M["m01"] / M["m00"])
            cX = int(M["m10"] / M["m00"])
        else:
            x, y, ww, hh = cv2.boundingRect(cnt)
            cY = y + hh // 2
            cX = x + ww // 2
        
        if cY < h / 2:
            dealer_contours.append(cnt)
            # Draw dealer contours in blue
            cv2.drawContours(marked_image, [cnt], -1, (255, 0, 0), 3)
            cv2.putText(marked_image, 'DEALER', (cX-30, cY-10), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 0, 0), 2)
        else:
            player_contours.append(cnt)
            # Draw player contours in green
            cv2.drawContours(marked_image, [cnt], -1, (0, 255, 0), 3)
            # Determine which player based on x position for 2 players
            if players == 2:
                if cX < w / 2:
                    cv2.putText(marked_image, 'PLAYER 1', (cX-40, cY+20), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
                else:
                    cv2.putText(marked_image, 'PLAYER 2', (cX-40, cY+20), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
            else:
                cv2.putText(marked_image, 'PLAYER 1', (cX-40, cY+20), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
    
    # Add region overlay to show where each player's area is
    overlay = marked_image.copy()
    
    # Dealer area (top half)
    cv2.rectangle(overlay, (0, 0), (w, h//2), (255, 0, 0), -1)
    
    if players == 1:
        # Single player area (bottom half)
        cv2.rectangle(overlay, (0, h//2), (w, h), (0, 255, 0), -1)
    else:
        # Two player areas (bottom half split)
        cv2.rectangle(overlay, (0, h//2), (w//2, h), (0, 255, 0), -1)
        cv2.rectangle(overlay, (w//2, h//2), (w, h), (0, 255, 255), -1)
    
    # Blend overlay with original image
    alpha = 0.1
    marked_image = cv2.addWeighted(marked_image, 1-alpha, overlay, alpha, 0)
    
    # Add title text
    cv2.putText(marked_image, f'Detected Cards ({len(card_contours)} found)', (10, 30), 
                cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
    
    return marked_image

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
    min_area = 5000  # Reduced from 10000
    
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

def detect_and_classify_cards_advice_mode(image: np.ndarray) -> tuple:
    """
    Detect cards in advice mode - treat entire image as player area.
    Returns ([], player_cards, []) - empty dealer and player2 arrays.
    """
    print(f"Starting advice mode card detection on image shape: {image.shape}")
    
    # 1. Preprocessing (same as regular detection)
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)
    edges = cv2.Canny(blurred, 50, 150)
    
    # 2. Find contours
    contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    print(f"Found {len(contours)} total contours in advice mode")
    
    # 3. Filter for card-like contours (same logic as regular detection)
    card_contours = []
    min_area = 5000  # Same threshold as regular detection
    
    for i, cnt in enumerate(contours):
        area = cv2.contourArea(cnt)
        peri = cv2.arcLength(cnt, True)
        approx = cv2.approxPolyDP(cnt, 0.02 * peri, True)
        
        print(f"Advice mode contour {i}: area={area:.0f}, vertices={len(approx)}")
        
        # Same criteria as regular detection
        if len(approx) >= 4 and area > min_area:
            # Check aspect ratio for card-like shape
            x, y, w, h = cv2.boundingRect(cnt)
            aspect_ratio = w / h if h > 0 else 0
            
            # Cards typically have aspect ratio between 0.5 and 2.0
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
    
    print(f"Found {len(card_contours)} card-like contours in advice mode")
    
    if len(card_contours) == 0:
        print("No card contours detected in advice mode!")
        return [], [], []
    
    # 4. In advice mode, ALL detected cards are player cards
    # Sort by x position (left to right) for consistent ordering
    card_contours = sorted(card_contours, key=get_leftmost_x)
    
    # 5. Extract and warp all cards as player cards
    player_cards = []
    for i, cnt in enumerate(card_contours):
        try:
            if len(cnt) >= 4:
                if len(cnt) > 4:
                    # Use bounding rectangle as fallback
                    x, y, w, h = cv2.boundingRect(cnt)
                    pts = np.array([[x, y], [x+w, y], [x+w, y+h], [x, y+h]], dtype=np.float32)
                else:
                    pts = cnt.reshape(4, 2).astype(np.float32)
                
                warped = four_point_transform(image, pts)
                player_cards.append(warped)
                print(f"Successfully warped advice mode card {i+1}")
            else:
                print(f"Advice mode contour {i+1} has insufficient points: {len(cnt)}")
        except Exception as e:
            print(f"Error warping advice mode card {i+1}: {e}")
    
    print(f"Extracted {len(player_cards)} cards in advice mode")
    # Return empty dealer and player2 arrays, all cards go to player1
    return [], player_cards, []

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
        card_blurred = cv2.GaussianBlur(card_gray, (3, 3), 0);
        
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

# === Get marked contours image ===
@app.post("/analyze/marked-contours/")
async def get_marked_contours(file: UploadFile = File(...), players: int = Form(...)):
    """Return the image with detected card contours marked"""
    try:
        image_data = await file.read()
        nparr = np.frombuffer(image_data, np.uint8)
        image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        
        if image is None:
            return JSONResponse(
                status_code=400, 
                content={"error": "Could not decode image"}
            )
        
        print(f"Creating marked contours image for {players} players")
        
        # Create marked image
        marked_image = create_marked_contours_image(image, players)
        
        # Encode image as base64 for JSON response
        success, buffer = cv2.imencode('.png', marked_image)
        if not success:
            return JSONResponse(
                status_code=500,
                content={"error": "Failed to encode marked image"}
            )
        
        # Convert to base64
        image_base64 = base64.b64encode(buffer).decode('utf-8')
        
        return JSONResponse(content={
            "success": True,
            "image": f"data:image/png;base64,{image_base64}",
            "message": "Marked contours image generated successfully"
        })
        
    except Exception as e:
        print(f"Error creating marked contours image: {e}")
        import traceback
        traceback.print_exc()
        return JSONResponse(
            status_code=500,
            content={"error": f"Error creating marked contours image: {str(e)}"}
        )

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
async def analyze_image(file: UploadFile = File(...), players: str = Form(...)):
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
        print(f"Players parameter: {players}")
        
        # Check if this is advice mode
        is_advice_mode = players == "advice"
        num_players = 0 if is_advice_mode else int(players)
        
        print(f"Advice mode: {is_advice_mode}, Number of players: {num_players}")
        
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

        # Use notebook-style detection, but handle advice mode differently
        if is_advice_mode:
            # In advice mode, treat entire image as player area (no dealer)
            # We'll modify detect_and_classify_cards to handle this
            dealer_cards, player1_cards, player2_cards = detect_and_classify_cards_advice_mode(image)
        else:
            dealer_cards, player1_cards, player2_cards = detect_and_classify_cards(image, num_players)
        
        # Match cards to templates
        dealer_ranks = match_cards_to_templates(dealer_cards, TEMPLATES) if not is_advice_mode else []
        player1_ranks = match_cards_to_templates(player1_cards, TEMPLATES)
        player2_ranks = match_cards_to_templates(player2_cards, TEMPLATES) if player2_cards else []
        
        print(f"Detected cards - Dealer: {dealer_ranks}, Player1: {player1_ranks}, Player2: {player2_ranks}")

        if is_advice_mode:
            # Generate AI advice for the detected cards
            advice = calculate_blackjack_advice(player1_ranks)
            
            results = {
                "player1": {
                    "cards": player1_ranks,
                    "score": calculate_score(player1_ranks)
                },
                "advice": advice
            }
        else:
            # Normal game mode
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

            if num_players == 2:
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

# === Blackjack Strategy AI ===
def calculate_blackjack_advice(player_cards, dealer_upcard=None):
    """
    Calculate optimal blackjack strategy advice based on basic strategy
    """
    player_score = calculate_score(player_cards)
    
    # If player has busted, no advice needed
    if player_score > 21:
        return {
            "advice": "BUST - You've exceeded 21",
            "win_probability": 0,
            "explanation": "Your hand value is over 21, so you've automatically lost this hand."
        }
    
    # Check for blackjack
    if player_score == 21 and len(player_cards) == 2:
        return {
            "advice": "BLACKJACK! Stand",
            "win_probability": 95,
            "explanation": "You have a natural blackjack (21 with 2 cards). This is the best possible hand!"
        }
    
    # Check if hand is soft (contains usable ace)
    has_ace = any('Ace' in card for card in player_cards)
    is_soft = has_ace and player_score <= 21
    
    # Basic strategy without dealer card (conservative approach)
    if dealer_upcard is None:
        return get_basic_advice_no_dealer(player_score, is_soft, len(player_cards))
    
    # Basic strategy with dealer card
    return get_basic_strategy_advice(player_score, dealer_upcard, is_soft, len(player_cards))

def get_basic_advice_no_dealer(player_score, is_soft, num_cards):
    """Basic advice when dealer card is unknown (conservative strategy)"""
    
    if is_soft:
        # Soft totals (with Ace counted as 11)
        if player_score <= 17:
            return {
                "advice": "HIT",
                "win_probability": 65,
                "explanation": f"With a soft {player_score}, hitting is safe since the Ace can be counted as 1 if needed."
            }
        elif player_score <= 18:
            return {
                "advice": "STAND (or HIT if feeling aggressive)",
                "win_probability": 55,
                "explanation": f"Soft {player_score} is borderline. Standing is safer, but hitting can improve your hand."
            }
        else:
            return {
                "advice": "STAND",
                "win_probability": 75,
                "explanation": f"Soft {player_score} is a strong hand. Don't risk busting."
            }
    else:
        # Hard totals
        if player_score <= 11:
            return {
                "advice": "HIT",
                "win_probability": 70,
                "explanation": f"With {player_score}, you cannot bust on the next card. Always hit."
            }
        elif player_score <= 16:
            return {
                "advice": "HIT",
                "win_probability": 45,
                "explanation": f"With {player_score}, you're likely to lose if you stand. Hit to try to improve."
            }
        elif player_score <= 19:
            return {
                "advice": "STAND",
                "win_probability": 70,
                "explanation": f"With {player_score}, you have a good hand. Standing is the optimal play."
            }
        else:
            return {
                "advice": "STAND",
                "win_probability": 85,
                "explanation": f"With {player_score}, you have an excellent hand. Always stand."
            }

def get_basic_strategy_advice(player_score, dealer_upcard, is_soft, num_cards):
    """Advanced basic strategy with dealer upcard consideration"""
    
    dealer_value = get_card_value(dealer_upcard)
    
    if is_soft:
        return get_soft_strategy(player_score, dealer_value)
    else:
        return get_hard_strategy(player_score, dealer_value, num_cards)

def get_card_value(card_name):
    """Get numerical value of a card for strategy purposes"""
    if 'Ace' in card_name:
        return 11  # For dealer upcard purposes, assume Ace = 11
    elif any(face in card_name for face in ['Jack', 'Queen', 'King']):
        return 10
    else:
        # Extract number from card name
        for i in range(2, 11):
            if str(i) in card_name:
                return i
    return 10  # Default to 10 if parsing fails

def get_hard_strategy(player_score, dealer_value, num_cards):
    """Hard total basic strategy"""
    
    # Pair splitting logic (if 2 cards of same rank)
    if num_cards == 2:
        # Note: We'd need to check if it's actually a pair, but for simplicity
        # we'll focus on total-based strategy
        pass
    
    win_prob = estimate_win_probability(player_score, dealer_value, False)
    
    if player_score <= 8:
        return {
            "advice": "HIT",
            "win_probability": win_prob,
            "explanation": f"With {player_score} vs dealer {dealer_value}, always hit to improve your hand."
        }
    elif player_score == 9:
        if dealer_value in [3, 4, 5, 6]:
            return {
                "advice": "DOUBLE DOWN (or HIT)",
                "win_probability": win_prob + 10,
                "explanation": f"With 9 vs dealer {dealer_value}, doubling down is optimal if allowed."
            }
        else:
            return {
                "advice": "HIT",
                "win_probability": win_prob,
                "explanation": f"With 9 vs dealer {dealer_value}, hit to improve your hand."
            }
    elif player_score == 10:
        if dealer_value <= 9:
            return {
                "advice": "DOUBLE DOWN (or HIT)",
                "win_probability": win_prob + 15,
                "explanation": f"With 10 vs dealer {dealer_value}, doubling down is very favorable."
            }
        else:
            return {
                "advice": "HIT",
                "win_probability": win_prob,
                "explanation": f"With 10 vs dealer {dealer_value}, hit rather than double."
            }
    elif player_score == 11:
        return {
            "advice": "DOUBLE DOWN (or HIT)",
            "win_probability": win_prob + 20,
            "explanation": f"With 11, doubling down is almost always the best play."
        }
    elif 12 <= player_score <= 16:
        if dealer_value in [2, 3, 7, 8, 9, 10, 11]:
            return {
                "advice": "HIT",
                "win_probability": win_prob,
                "explanation": f"With {player_score} vs dealer {dealer_value}, you must hit despite bust risk."
            }
        else:  # Dealer 4, 5, 6
            return {
                "advice": "STAND",
                "win_probability": win_prob + 10,
                "explanation": f"With {player_score} vs dealer {dealer_value}, stand and hope dealer busts."
            }
    else:  # 17+
        return {
            "advice": "STAND",
            "win_probability": win_prob,
            "explanation": f"With {player_score}, always stand - excellent hand!"
        }

def get_soft_strategy(player_score, dealer_value):
    """Soft total basic strategy"""
    
    win_prob = estimate_win_probability(player_score, dealer_value, True)
    
    if player_score <= 17:
        if dealer_value in [4, 5, 6]:
            return {
                "advice": "DOUBLE DOWN (or HIT)",
                "win_probability": win_prob + 15,
                "explanation": f"Soft {player_score} vs dealer {dealer_value} - double down is optimal."
            }
        else:
            return {
                "advice": "HIT",
                "win_probability": win_prob,
                "explanation": f"Soft {player_score} - hit to improve without bust risk."
            }
    elif player_score == 18:
        if dealer_value in [2, 7, 8]:
            return {
                "advice": "STAND",
                "win_probability": win_prob,
                "explanation": f"Soft 18 vs dealer {dealer_value} - standing is optimal."
            }
        elif dealer_value in [3, 4, 5, 6]:
            return {
                "advice": "DOUBLE DOWN (or STAND)",
                "win_probability": win_prob + 10,
                "explanation": f"Soft 18 vs dealer {dealer_value} - double if allowed, otherwise stand."
            }
        else:  # 9, 10, A
            return {
                "advice": "HIT",
                "win_probability": win_prob - 5,
                "explanation": f"Soft 18 vs dealer {dealer_value} - hit to try to improve."
            }
    else:  # 19+
        return {
            "advice": "STAND",
            "win_probability": win_prob,
            "explanation": f"Soft {player_score} is an excellent hand - always stand."
        }

def estimate_win_probability(player_score, dealer_value, is_soft):
    """Estimate win probability based on basic strategy statistics"""
    
    # Base probabilities from basic strategy charts
    base_prob = 50
    
    # Adjust for player hand strength
    if player_score >= 20:
        base_prob += 35
    elif player_score >= 18:
        base_prob += 20
    elif player_score >= 17:
        base_prob += 10
    elif player_score <= 12:
        base_prob -= 15
    
    # Adjust for dealer upcard
    if dealer_value in [4, 5, 6]:  # Dealer bust cards
        base_prob += 15
    elif dealer_value in [2, 3]:
        base_prob += 5
    elif dealer_value in [9, 10, 11]:  # Strong dealer cards
        base_prob -= 10
    elif dealer_value in [7, 8]:
        base_prob -= 5
    
    # Soft hands are slightly better
    if is_soft and player_score <= 18:
        base_prob += 5
    
    # Clamp between 5 and 95
    return max(5, min(95, base_prob))

# === Server Startup ===
if __name__ == "__main__":
    import uvicorn
    import os
    
    # Use PORT environment variable if available (for cloud deployment)
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
