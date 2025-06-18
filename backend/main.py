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
    Calculate optimal blackjack strategy advice based on advanced basic strategy
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
    
    # Enhanced soft hand detection
    is_soft, soft_total = detect_soft_hand(player_cards)
    
    # Check for pairs (for splitting advice)
    is_pair = len(player_cards) == 2 and get_card_rank(player_cards[0]) == get_card_rank(player_cards[1])
    
    # Basic strategy without dealer card (conservative approach)
    if dealer_upcard is None:
        return get_basic_advice_no_dealer(player_score, is_soft, len(player_cards), is_pair)
    
    # Basic strategy with dealer card (using existing functions for now)
    return get_basic_strategy_advice(player_score, dealer_upcard, is_soft, len(player_cards))

def detect_soft_hand(player_cards):
    """
    Enhanced soft hand detection - returns (is_soft, soft_total)
    A soft hand has an Ace counted as 11 without busting
    """
    ace_count = sum(1 for card in player_cards if 'Ace' in card)
    if ace_count == 0:
        return False, 0
    
    # Calculate score with all aces as 1
    hard_total = 0
    for card in player_cards:
        if 'Ace' in card:
            hard_total += 1
        elif any(face in card for face in ['Jack', 'Queen', 'King']):
            hard_total += 10
        else:
            # Extract number from card name
            for i in range(2, 11):
                if str(i) in card:
                    hard_total += i
                    break
    
    # Try to make one ace count as 11
    soft_total = hard_total + 10  # +10 because we already counted the ace as 1
    
    # If soft total is 21 or less, it's a soft hand
    if soft_total <= 21:
        return True, soft_total
    else:
        return False, 0

def get_card_rank(card_name):
    """Get the rank of a card for pair checking"""
    if 'Ace' in card_name:
        return 'A'
    elif 'King' in card_name:
        return 'K'
    elif 'Queen' in card_name:
        return 'Q'
    elif 'Jack' in card_name:
        return 'J'
    else:
        # Extract number from card name
        for i in range(2, 11):
            if str(i) in card_name:
                return str(i)
    return 'Unknown'

def get_basic_advice_no_dealer(player_score, is_soft, num_cards, is_pair):
    """Enhanced advice when dealer card is unknown (conservative strategy)"""
    
    # Handle pairs first (conservative splitting advice)
    if is_pair and num_cards == 2:
        return get_pair_splitting_advice_conservative(player_score)
    
    if is_soft:
        # Enhanced soft hand strategy
        if player_score <= 15:
            return {
                "advice": "HIT",
                "win_probability": 75,
                "explanation": f"Soft {player_score} is very safe - the Ace gives you flexibility. Hit to improve without bust risk."
            }
        elif player_score == 16:
            return {
                "advice": "HIT",
                "win_probability": 70,
                "explanation": f"Soft {player_score} - hitting is still safe since Ace can become 1 if needed."
            }
        elif player_score == 17:
            return {
                "advice": "HIT (Conservative: STAND)",
                "win_probability": 65,
                "explanation": f"Soft {player_score} - hitting improves your hand often, but standing is acceptable if conservative."
            }
        elif player_score == 18:
            return {
                "advice": "STAND",
                "win_probability": 60,
                "explanation": f"Soft {player_score} is borderline but decent. Without knowing dealer card, standing is safer."
            }
        else:  # 19+
            return {
                "advice": "STAND",
                "win_probability": 80,
                "explanation": f"Soft {player_score} is an excellent hand. Always stand."
            }
    else:
        # Enhanced hard hand strategy
        if player_score <= 8:
            return {
                "advice": "HIT",
                "win_probability": 75,
                "explanation": f"With {player_score}, impossible to bust. Always hit to improve your weak hand."
            }
        elif player_score <= 11:
            return {
                "advice": "HIT",
                "win_probability": 70,
                "explanation": f"With {player_score}, you cannot bust on the next card. Always hit to improve."
            }
        elif player_score == 12:
            return {
                "advice": "HIT",
                "win_probability": 50,
                "explanation": f"Hard 12 is tricky, but without dealer info, hitting gives you more winning chances."
            }
        elif player_score <= 16:
            return {
                "advice": "HIT",
                "win_probability": 45,
                "explanation": f"Hard {player_score} is weak. Despite bust risk, you need to improve to have a chance."
            }
        elif player_score == 17:
            return {
                "advice": "STAND",
                "win_probability": 65,
                "explanation": f"Hard 17 - while not great, hitting risks busting. Standing is the safer play."
            }
        elif player_score <= 19:
            return {
                "advice": "STAND",
                "win_probability": 75,
                "explanation": f"Hard {player_score} is a good hand. Standing gives you excellent winning chances."
            }
        else:  # 20+
            return {
                "advice": "STAND",
                "win_probability": 85,
                "explanation": f"Hard {player_score} is excellent. Never risk this strong hand."
            }

def get_pair_splitting_advice_conservative(player_total):
    """Conservative pair splitting advice without dealer card"""
    pair_value = player_total // 2
    
    if pair_value == 1 or pair_value == 11:  # Aces
        return {
            "advice": "SPLIT (if allowed)",
            "win_probability": 70,
            "explanation": "Pair of Aces - splitting gives you two chances at blackjack."
        }
    elif pair_value == 8:
        return {
            "advice": "SPLIT (if allowed)",
            "win_probability": 60,
            "explanation": "Pair of 8s - splitting improves your chances from the weak 16."
        }
    elif pair_value == 10:
        return {
            "advice": "STAND (don't split)",
            "win_probability": 85,
            "explanation": "Pair of 10s gives you 20 - excellent hand, never split this."
        }
    elif pair_value in [4, 5]:
        return {
            "advice": "HIT (don't split)",
            "win_probability": 65,
            "explanation": f"Pair of {pair_value}s - better to hit than split into weak hands."
        }
    else:
        return {
            "advice": "CONSERVATIVE: HIT (Split possible)",
            "win_probability": 55,
            "explanation": f"Pair of {pair_value}s - without dealer info, hitting is safer than splitting."
        }

def get_advanced_strategy_advice(player_score, dealer_upcard, is_soft, soft_total, num_cards, is_pair):
    """
    Advanced blackjack basic strategy with enhanced dealer upcard consideration.
    Includes sophisticated soft/hard hand logic and dealer strength analysis.
    """
    dealer_value = get_card_value(dealer_upcard)
    
    # Handle pairs first if applicable
    if is_pair and num_cards == 2:
        return get_pair_splitting_advice_advanced(player_score, dealer_value)
    
    # Enhanced soft hand strategy
    if is_soft:
        return get_enhanced_soft_strategy(player_score, dealer_value)
    else:
        return get_enhanced_hard_strategy(player_score, dealer_value, num_cards)

def get_pair_splitting_advice_advanced(player_total, dealer_value):
    """Advanced pair splitting advice based on dealer upcard"""
    pair_value = player_total // 2
    
    # Determine if dealer has strong or weak upcard
    dealer_weak = dealer_value in [4, 5, 6]  # Bust cards
    dealer_strong = dealer_value in [9, 10, 11]  # Strong cards
    dealer_medium = dealer_value in [2, 3, 7, 8]  # Medium strength
    
    if pair_value == 1 or pair_value == 11:  # Aces
        return {
            "advice": "ALWAYS SPLIT",
            "win_probability": 75,
            "explanation": "Pair of Aces - always split regardless of dealer upcard. Two chances at blackjack!"
        }
    elif pair_value == 8:
        if dealer_value == 11:  # Dealer Ace
            return {
                "advice": "SPLIT (risky vs Ace)",
                "win_probability": 55,
                "explanation": "8s vs dealer Ace - splitting is still better than 16, but dealer has strong card."
            }
        else:
            return {
                "advice": "ALWAYS SPLIT",
                "win_probability": 65,
                "explanation": "Pair of 8s - always split to escape the terrible 16."
            }
    elif pair_value == 10:  # 10s, Jacks, Queens, Kings
        return {
            "advice": "NEVER SPLIT",
            "win_probability": 85,
            "explanation": "20 is excellent vs any dealer card. Never split 10-value cards."
        }
    elif pair_value == 9:
        if dealer_value in [7, 10, 11]:
            return {
                "advice": "STAND (don't split)",
                "win_probability": 75,
                "explanation": f"18 vs dealer {dealer_value} - standing with 18 is better than splitting."
            }
        else:
            return {
                "advice": "SPLIT",
                "win_probability": 70,
                "explanation": f"9s vs dealer {dealer_value} - splitting gives two strong hands."
            }
    elif pair_value == 7:
        if dealer_weak or dealer_value == 7:
            return {
                "advice": "SPLIT",
                "win_probability": 65,
                "explanation": f"7s vs dealer {dealer_value} - good splitting opportunity."
            }
        else:
            return {
                "advice": "HIT (don't split)",
                "win_probability": 55,
                "explanation": f"7s vs strong dealer {dealer_value} - hitting 14 is better than splitting."
            }
    elif pair_value == 6:
        if dealer_weak:
            return {
                "advice": "SPLIT",
                "win_probability": 60,
                "explanation": f"6s vs weak dealer {dealer_value} - split against bust cards."
            }
        else:
            return {
                "advice": "HIT (don't split)",
                "win_probability": 50,
                "explanation": f"6s vs dealer {dealer_value} - hitting 12 is safer than splitting into weak hands."
            }
    elif pair_value in [2, 3]:
        if dealer_weak or dealer_value in [2, 3]:
            return {
                "advice": "SPLIT",
                "win_probability": 55,
                "explanation": f"{pair_value}s vs dealer {dealer_value} - marginal split against weak cards."
            }
        else:
            return {
                "advice": "HIT (don't split)",
                "win_probability": 50,
                "explanation": f"{pair_value}s vs dealer {dealer_value} - hitting is better than splitting weak hands."
            }
    else:  # 4s and 5s
        return {
            "advice": "NEVER SPLIT",
            "win_probability": 60,
            "explanation": f"{pair_value}s should never be split - you'd create weak starting hands."
        }

def get_enhanced_soft_strategy(player_score, dealer_value):
    """Enhanced soft hand strategy with detailed dealer analysis"""
    # Categorize dealer strength
    dealer_weak = dealer_value in [4, 5, 6]  # Bust cards
    dealer_strong = dealer_value in [9, 10, 11]  # Strong cards
    dealer_medium = dealer_value in [2, 3, 7, 8]  # Medium strength
    
    win_prob = calculate_enhanced_win_probability(player_score, dealer_value, True)
    
    if player_score <= 15:  # Very weak soft hands
        if dealer_weak:
            return {
                "advice": "DOUBLE DOWN (or HIT)",
                "win_probability": win_prob + 15,
                "explanation": f"Soft {player_score} vs weak dealer {dealer_value} - doubling maximizes profit against bust cards."
            }
        else:
            return {
                "advice": "HIT",
                "win_probability": win_prob,
                "explanation": f"Soft {player_score} - hit safely to improve. Ace flexibility prevents busting."
            }
    elif player_score == 16:  # Soft 16
        if dealer_weak:
            return {
                "advice": "DOUBLE DOWN (or HIT)",
                "win_probability": win_prob + 12,
                "explanation": f"Soft 16 vs dealer {dealer_value} - doubling is profitable against bust cards."
            }
        else:
            return {
                "advice": "HIT",
                "win_probability": win_prob,
                "explanation": f"Soft 16 vs dealer {dealer_value} - hit to improve safely."
            }
    elif player_score == 17:  # Soft 17
        if dealer_weak:
            return {
                "advice": "DOUBLE DOWN (or HIT)",
                "win_probability": win_prob + 10,
                "explanation": f"Soft 17 vs dealer {dealer_value} - double down against bust cards."
            }
        elif dealer_strong:
            return {
                "advice": "HIT",
                "win_probability": win_prob - 5,
                "explanation": f"Soft 17 vs strong dealer {dealer_value} - need to improve against powerful cards."
            }
        else:
            return {
                "advice": "HIT",
                "win_probability": win_prob,
                "explanation": f"Soft 17 vs dealer {dealer_value} - hitting gives good improvement chances."
            }
    elif player_score == 18:  # Soft 18 - most complex decision
        if dealer_value in [2, 7, 8]:
            return {
                "advice": "STAND",
                "win_probability": win_prob,
                "explanation": f"Soft 18 vs dealer {dealer_value} - standing is optimal with this decent hand."
            }
        elif dealer_weak:
            return {
                "advice": "DOUBLE DOWN (or STAND)",
                "win_probability": win_prob + 8,
                "explanation": f"Soft 18 vs weak dealer {dealer_value} - double if allowed to maximize profit."
            }
        else:  # vs 9, 10, A
            return {
                "advice": "HIT",
                "win_probability": win_prob - 8,
                "explanation": f"Soft 18 vs strong dealer {dealer_value} - must improve against powerful cards."
            }
    else:  # Soft 19, 20, 21
        return {
            "advice": "STAND",
            "win_probability": win_prob,
            "explanation": f"Soft {player_score} is excellent - never risk this strong hand."
        }

def get_enhanced_hard_strategy(player_score, dealer_value, num_cards):
    """Enhanced hard hand strategy with sophisticated dealer analysis"""
    # Categorize dealer strength
    dealer_weak = dealer_value in [4, 5, 6]  # Most likely to bust
    dealer_medium_weak = dealer_value in [2, 3]  # Somewhat likely to bust
    dealer_medium = dealer_value in [7, 8]  # Neutral cards
    dealer_strong = dealer_value in [9, 10, 11]  # Strong cards
    
    win_prob = calculate_enhanced_win_probability(player_score, dealer_value, False)
    
    if player_score <= 8:
        return {
            "advice": "ALWAYS HIT",
            "win_probability": win_prob,
            "explanation": f"With {player_score}, impossible to bust. Always hit regardless of dealer {dealer_value}."
        }
    elif player_score == 9:
        if dealer_weak or dealer_value == 3:
            return {
                "advice": "DOUBLE DOWN (or HIT)",
                "win_probability": win_prob + 12,
                "explanation": f"Hard 9 vs dealer {dealer_value} - excellent doubling opportunity."
            }
        else:
            return {
                "advice": "HIT",
                "win_probability": win_prob,
                "explanation": f"Hard 9 vs dealer {dealer_value} - hit to improve your hand."
            }
    elif player_score == 10:
        if dealer_value <= 9:
            return {
                "advice": "DOUBLE DOWN (or HIT)",
                "win_probability": win_prob + 15,
                "explanation": f"Hard 10 vs dealer {dealer_value} - very strong doubling situation."
            }
        else:
            return {
                "advice": "HIT",
                "win_probability": win_prob,
                "explanation": f"Hard 10 vs dealer {dealer_value} - hit rather than double against strong cards."
            }
    elif player_score == 11:
        if dealer_value == 11:  # vs Ace
            return {
                "advice": "HIT (Double if allowed)",
                "win_probability": win_prob + 10,
                "explanation": "Hard 11 vs dealer Ace - double if rules allow, otherwise hit."
            }
        else:
            return {
                "advice": "ALWAYS DOUBLE DOWN",
                "win_probability": win_prob + 20,
                "explanation": f"Hard 11 vs dealer {dealer_value} - always double this excellent hand."
            }
    elif player_score == 12:
        if dealer_weak:
            return {
                "advice": "STAND",
                "win_probability": win_prob + 8,
                "explanation": f"Hard 12 vs dealer {dealer_value} - stand and let dealer bust."
            }
        else:
            return {
                "advice": "HIT",
                "win_probability": win_prob,
                "explanation": f"Hard 12 vs dealer {dealer_value} - must risk busting to have a chance."
            }
    elif 13 <= player_score <= 16:  # Stiff hands
        if dealer_weak:
            return {
                "advice": "STAND",
                "win_probability": win_prob + 10,
                "explanation": f"Hard {player_score} vs dealer {dealer_value} - dealer likely to bust, stand pat."
            }
        elif dealer_medium_weak:
            return {
                "advice": "STAND",
                "win_probability": win_prob + 5,
                "explanation": f"Hard {player_score} vs dealer {dealer_value} - marginal stand against weak card."
            }
        else:
            return {
                "advice": "HIT",
                "win_probability": win_prob,
                "explanation": f"Hard {player_score} vs dealer {dealer_value} - must hit despite bust risk."
            }
    elif player_score == 17:
        return {
            "advice": "ALWAYS STAND",
            "win_probability": win_prob,
            "explanation": f"Hard 17 vs dealer {dealer_value} - always stand, hitting risks too much."
        }
    else:  # 18+
        return {
            "advice": "ALWAYS STAND",
            "win_probability": win_prob,
            "explanation": f"Hard {player_score} is excellent vs any dealer card - never risk this hand."
        }

def calculate_enhanced_win_probability(player_score, dealer_value, is_soft):
    """
    Enhanced win probability calculation with sophisticated dealer analysis
    """
    # Base probability
    base_prob = 50
    
    # Player hand strength adjustments
    if is_soft:
        # Soft hands have flexibility advantage
        if player_score <= 16:
            base_prob += 10  # Soft hands are safer
        elif player_score == 17:
            base_prob += 5
        elif player_score == 18:
            base_prob += 15
        else:  # 19+
            base_prob += 25
    else:
        # Hard hand adjustments
        if player_score <= 11:
            base_prob -= 10  # Weak hands
        elif player_score <= 16:
            base_prob -= 5   # Vulnerable to busting
        elif player_score == 17:
            base_prob += 5   # Decent hand
        elif player_score <= 19:
            base_prob += 15  # Good hands
        else:  # 20+
            base_prob += 30  # Excellent hands
    
    # Dealer upcard strength adjustments (more nuanced)
    if dealer_value == 2:
        base_prob += 8   # Dealer often makes 17-19
    elif dealer_value == 3:
        base_prob += 10  # Slightly weaker than 2
    elif dealer_value == 4:
        base_prob += 15  # Good bust card
    elif dealer_value == 5:
        base_prob += 18  # Best bust card
    elif dealer_value == 6:
        base_prob += 16  # Very good bust card
    elif dealer_value == 7:
        base_prob -= 5   # Dealer often makes 17
    elif dealer_value == 8:
        base_prob -= 8   # Dealer often makes 18
    elif dealer_value == 9:
        base_prob -= 12  # Strong dealer card
    elif dealer_value == 10:
        base_prob -= 15  # Very strong dealer card
    elif dealer_value == 11:  # Ace
        base_prob -= 18  # Strongest dealer card
    
    # Strategic situation adjustments
    if is_soft and dealer_value in [4, 5, 6]:
        base_prob += 5  # Soft hands can double against weak dealer
    elif not is_soft and player_score >= 17 and dealer_value in [4, 5, 6]:
        base_prob += 8  # Standing with good hand vs weak dealer
    
    # Clamp between 5 and 95
    return max(5, min(95, base_prob))

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
    """Enhanced hard total basic strategy with detailed dealer analysis"""
    
    # Categorize dealer strength for better explanations
    dealer_weak = dealer_value in [4, 5, 6]  # Bust cards
    dealer_medium_weak = dealer_value in [2, 3]  # Somewhat weak
    dealer_medium = dealer_value in [7, 8]  # Neutral
    dealer_strong = dealer_value in [9, 10, 11]  # Strong cards
    
    win_prob = estimate_win_probability(player_score, dealer_value, False)
    
    if player_score <= 8:
        return {
            "advice": "ALWAYS HIT",
            "win_probability": win_prob,
            "explanation": f"Hard {player_score} vs dealer {dealer_value} - impossible to bust, always hit to improve."
        }
    elif player_score == 9:
        if dealer_value in [3, 4, 5, 6]:
            return {
                "advice": "DOUBLE DOWN (or HIT)",
                "win_probability": win_prob + 12,
                "explanation": f"Hard 9 vs weak dealer {dealer_value} - excellent doubling opportunity. Dealer likely to bust or make weak total."
            }
        else:
            return {
                "advice": "HIT",
                "win_probability": win_prob,
                "explanation": f"Hard 9 vs dealer {dealer_value} - too risky to double against strong card, just hit to improve."
            }
    elif player_score == 10:
        if dealer_value <= 9:
            return {
                "advice": "DOUBLE DOWN (or HIT)",
                "win_probability": win_prob + 15,
                "explanation": f"Hard 10 vs dealer {dealer_value} - very strong doubling situation. Many cards give you 20."
            }
        else:
            return {
                "advice": "HIT",
                "win_probability": win_prob,
                "explanation": f"Hard 10 vs strong dealer {dealer_value} - hit rather than double against Ace/10."
            }
    elif player_score == 11:
        if dealer_value == 11:  # vs Ace
            return {
                "advice": "DOUBLE DOWN (or HIT)",
                "win_probability": win_prob + 15,
                "explanation": "Hard 11 vs dealer Ace - still favorable to double, many cards give you 21."
            }
        else:
            return {
                "advice": "ALWAYS DOUBLE DOWN",
                "win_probability": win_prob + 20,
                "explanation": f"Hard 11 vs dealer {dealer_value} - always double this premium hand. Best doubling situation."
            }
    elif player_score == 12:
        if dealer_weak:
            return {
                "advice": "STAND",
                "win_probability": win_prob + 8,
                "explanation": f"Hard 12 vs weak dealer {dealer_value} - dealer likely to bust, stand despite weak hand."
            }
        elif dealer_medium_weak:
            return {
                "advice": "HIT",
                "win_probability": win_prob,
                "explanation": f"Hard 12 vs dealer {dealer_value} - marginal situation, but hitting gives better long-term results."
            }
        else:
            return {
                "advice": "HIT",
                "win_probability": win_prob,
                "explanation": f"Hard 12 vs strong dealer {dealer_value} - must improve despite bust risk."
            }
    elif 13 <= player_score <= 16:  # The dreaded stiff hands
        if dealer_weak:
            return {
                "advice": "STAND",
                "win_probability": win_prob + 12,
                "explanation": f"Hard {player_score} vs weak dealer {dealer_value} - dealer has high bust probability, let them take the risk."
            }
        elif dealer_medium_weak:
            return {
                "advice": "STAND",
                "win_probability": win_prob + 5,
                "explanation": f"Hard {player_score} vs dealer {dealer_value} - slight edge to standing against weaker dealer card."
            }
        else:
            return {
                "advice": "HIT",
                "win_probability": win_prob,
                "explanation": f"Hard {player_score} vs strong dealer {dealer_value} - terrible situation but must risk busting to have a chance."
            }
    elif player_score == 17:
        return {
            "advice": "ALWAYS STAND",
            "win_probability": win_prob,
            "explanation": f"Hard 17 vs dealer {dealer_value} - never hit 17, the bust risk far outweighs potential gains."
        }
    else:  # 18+
        strength_desc = "excellent" if player_score >= 20 else "very good"
        return {
            "advice": "ALWAYS STAND",
            "win_probability": win_prob,
            "explanation": f"Hard {player_score} is {strength_desc} vs any dealer card - never risk this strong hand."
        }

def get_soft_strategy(player_score, dealer_value):
    """Enhanced soft total basic strategy with detailed analysis"""
    
    # Categorize dealer strength
    dealer_weak = dealer_value in [4, 5, 6]  # Bust cards
    dealer_medium_weak = dealer_value in [2, 3]  # Somewhat weak
    dealer_medium = dealer_value in [7, 8]  # Neutral
    dealer_strong = dealer_value in [9, 10, 11]  # Strong cards
    
    win_prob = estimate_win_probability(player_score, dealer_value, True)
    
    if player_score <= 15:  # Very weak soft hands (A,2 through A,4)
        if dealer_weak:
            return {
                "advice": "DOUBLE DOWN (or HIT)",
                "win_probability": win_prob + 18,
                "explanation": f"Soft {player_score} vs weak dealer {dealer_value} - double to maximize profit. Ace flexibility makes this safe."
            }
        else:
            return {
                "advice": "HIT",
                "win_probability": win_prob,
                "explanation": f"Soft {player_score} vs dealer {dealer_value} - hit safely to improve. Ace can become 1 if needed."
            }
    elif player_score == 16:  # Soft 16 (A,5)
        if dealer_weak:
            return {
                "advice": "DOUBLE DOWN (or HIT)",
                "win_probability": win_prob + 15,
                "explanation": f"Soft 16 vs weak dealer {dealer_value} - good doubling spot against bust cards."
            }
        else:
            return {
                "advice": "HIT",
                "win_probability": win_prob,
                "explanation": f"Soft 16 vs dealer {dealer_value} - hit to improve safely with Ace flexibility."
            }
    elif player_score == 17:  # Soft 17 (A,6)
        if dealer_weak:
            return {
                "advice": "DOUBLE DOWN (or HIT)",
                "win_probability": win_prob + 12,
                "explanation": f"Soft 17 vs weak dealer {dealer_value} - double down against bust cards for maximum profit."
            }
        elif dealer_strong:
            return {
                "advice": "HIT",
                "win_probability": win_prob - 3,
                "explanation": f"Soft 17 vs strong dealer {dealer_value} - need to improve against powerful cards."
            }
        else:
            return {
                "advice": "HIT",
                "win_probability": win_prob,
                "explanation": f"Soft 17 vs dealer {dealer_value} - hit for improvement chances with safety net."
            }
    elif player_score == 18:  # Soft 18 (A,7) - most complex soft hand
        if dealer_value in [2, 7, 8]:
            return {
                "advice": "STAND",
                "win_probability": win_prob,
                "explanation": f"Soft 18 vs dealer {dealer_value} - standing is optimal. Good hand against these dealer cards."
            }
        elif dealer_weak:
            return {
                "advice": "DOUBLE DOWN (or STAND)",
                "win_probability": win_prob + 8,
                "explanation": f"Soft 18 vs weak dealer {dealer_value} - double if allowed to extract more value, otherwise stand."
            }
        elif dealer_value == 3:
            return {
                "advice": "DOUBLE DOWN (or STAND)",
                "win_probability": win_prob + 5,
                "explanation": f"Soft 18 vs dealer 3 - marginal doubling situation, but profitable long-term."
            }
        else:  # vs 9, 10, A
            return {
                "advice": "HIT",
                "win_probability": win_prob - 8,
                "explanation": f"Soft 18 vs strong dealer {dealer_value} - must improve against powerful cards. Hitting is safer than it looks."
            }
    elif player_score == 19:  # Soft 19 (A,8)
        return {
            "advice": "ALWAYS STAND",
            "win_probability": win_prob,
            "explanation": f"Soft 19 vs dealer {dealer_value} - excellent hand, never risk improving it."
        }
    else:  # Soft 20+ (A,9 or A,A after split)
        return {
            "advice": "ALWAYS STAND",
            "win_probability": win_prob,
            "explanation": f"Soft {player_score} is premium - never risk this outstanding hand."
        }

def estimate_win_probability(player_score, dealer_value, is_soft):
    """Enhanced win probability calculation with sophisticated dealer analysis"""
    
    # Base probability starts at 50%
    base_prob = 50
    
    # Enhanced player hand strength adjustments
    if is_soft:
        # Soft hands have flexibility advantage
        if player_score <= 15:
            base_prob -= 5   # Very weak soft hands
        elif player_score == 16:
            base_prob += 0   # Neutral soft 16
        elif player_score == 17:
            base_prob += 5   # Decent soft 17
        elif player_score == 18:
            base_prob += 15  # Good soft 18
        elif player_score == 19:
            base_prob += 25  # Very good soft 19
        else:  # 20+
            base_prob += 35  # Excellent soft 20+
    else:
        # Hard hand adjustments - more nuanced
        if player_score <= 8:
            base_prob -= 20  # Very weak
        elif player_score <= 11:
            base_prob -= 10  # Weak but safe to hit
        elif player_score == 12:
            base_prob -= 15  # Dangerous stiff hand
        elif player_score <= 16:
            base_prob -= 10  # Stiff hands
        elif player_score == 17:
            base_prob += 8   # Decent hand
        elif player_score == 18:
            base_prob += 18  # Good hand
        elif player_score == 19:
            base_prob += 25  # Very good hand
        elif player_score == 20:
            base_prob += 35  # Excellent hand
        else:  # 21
            base_prob += 40  # Perfect hand
    
    # Enhanced dealer upcard strength adjustments
    if dealer_value == 2:
        base_prob += 6   # Dealer often makes 17-19, some bust chance
    elif dealer_value == 3:
        base_prob += 8   # Slightly weaker than 2
    elif dealer_value == 4:
        base_prob += 12  # Good bust card
    elif dealer_value == 5:
        base_prob += 15  # Best bust card for player
    elif dealer_value == 6:
        base_prob += 13  # Very good bust card
    elif dealer_value == 7:
        base_prob -= 3   # Dealer often makes 17
    elif dealer_value == 8:
        base_prob -= 6   # Dealer often makes 18
    elif dealer_value == 9:
        base_prob -= 10  # Strong dealer card
    elif dealer_value == 10:
        base_prob -= 13  # Very strong dealer card
    elif dealer_value == 11:  # Ace
        base_prob -= 16  # Strongest dealer card
    
    # Strategic situation bonuses
    if is_soft and dealer_value in [4, 5, 6]:
        base_prob += 3  # Soft hands can be aggressive against weak dealer
    elif not is_soft and player_score >= 17 and dealer_value in [4, 5, 6]:
        base_prob += 5  # Standing with good hand vs weak dealer
    elif not is_soft and player_score <= 16 and dealer_value in [9, 10, 11]:
        base_prob -= 5  # Bad situation - weak hand vs strong dealer
    
    # Clamp probability between realistic bounds
    return max(5, min(95, base_prob))

# === Server Startup ===
if __name__ == "__main__":
    import uvicorn
    import os
    
    # Use PORT environment variable if available (for cloud deployment)
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
