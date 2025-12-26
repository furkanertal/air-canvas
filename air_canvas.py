import cv2
import numpy as np
import mediapipe as mp
import time

# --- IMPORT FIX ---

mp_draw = mp.solutions.drawing_utils
mp_hands = mp.solutions.hands

# --- 1. Settings and Variables ---
cap = cv2.VideoCapture(0)
cap.set(3, 1280)
cap.set(4, 720)

hands = mp_hands.Hands(
    max_num_hands=1,
    min_detection_confidence=0.7,
    min_tracking_confidence=0.5
)

# Drawing variables
draw_color = (255, 0, 255) # Purple
brush_thickness = 15
eraser_thickness = 50
xp, yp = 0, 0

# Tool constants
TOOL_DRAW = 'draw'
TOOL_ERASER = 'eraser'
TOOL_LINE = 'line'
TOOL_RECTANGLE = 'rectangle'
TOOL_CIRCLE = 'circle'
TOOL_FILL = 'fill'

current_tool = TOOL_DRAW
drawing_mode = True

# Shape drawing variables
shape_start_point = None
preview_canvas = None

# Undo/Redo
canvas_history = []
redo_stack = []
MAX_HISTORY = 20

# Flood Fill Cooldown
last_fill_time = 0
FILL_COOLDOWN = 1.0

colors = {
    'purple': (255, 0, 255),
    'blue': (255, 0, 0),
    'green': (0, 255, 0),
    'red': (0, 0, 255),
    'yellow': (0, 255, 255),
    'cyan': (255, 255, 0),
    'orange': (0, 165, 255),
    'white': (255, 255, 255),
    'pink': (203, 192, 255),
    'lime': (0, 255, 128)
}
current_color_name = 'purple'

img_canvas = np.zeros((720, 1280, 3), np.uint8)

# UI Dimensions
color_bar_height = 60
tool_bar_width = 120 # Biraz genişlettik metinler için
tool_bar_start_y = color_bar_height + 10

# Save initial state
canvas_history.append(img_canvas.copy())

def save_state():
    global canvas_history, redo_stack
    if len(canvas_history) >= MAX_HISTORY:
        canvas_history.pop(0)
    canvas_history.append(img_canvas.copy())
    redo_stack.clear()

def undo():
    global img_canvas, canvas_history, redo_stack
    if len(canvas_history) > 1:
        redo_stack.append(canvas_history.pop())
        img_canvas = canvas_history[-1].copy()
        print("Undo!")

def redo():
    global img_canvas, canvas_history, redo_stack
    if redo_stack:
        state = redo_stack.pop()
        canvas_history.append(state)
        img_canvas = state.copy()
        print("Redo!")

def fingers_up(lm_list):
    fingers = []
    # Thumb (Right hand assumption)
    if lm_list[4][1] > lm_list[3][1]:
        fingers.append(1)
    else:
        fingers.append(0)
    # 4 Fingers
    for id in [8, 12, 16, 20]:
        if lm_list[id][2] < lm_list[id - 2][2]:
            fingers.append(1)
        else:
            fingers.append(0)
    return fingers

def draw_ui(image):
    # Color Bar
    bar_width = (image.shape[1] - tool_bar_width) // len(colors)
    x_pos = tool_bar_width
    for color_name, color_value in colors.items():
        cv2.rectangle(image, (x_pos, 0), (x_pos + bar_width, color_bar_height), color_value, -1)
        cv2.rectangle(image, (x_pos, 0), (x_pos + bar_width, color_bar_height), (255, 255, 255), 1)
        x_pos += bar_width
    
    # Highlight current color
    curr_idx = list(colors.keys()).index(current_color_name)
    cv2.rectangle(image, 
                 (tool_bar_width + curr_idx * bar_width, 0), 
                 (tool_bar_width + (curr_idx + 1) * bar_width, color_bar_height), 
                 (0, 255, 0), 3)

    # Tool Bar 
    tools = {
        TOOL_DRAW: 'DRAW',
        TOOL_ERASER: 'ERASE',
        TOOL_LINE: 'LINE',
        TOOL_RECTANGLE: 'RECT',
        TOOL_CIRCLE: 'CIRCLE',
        TOOL_FILL: 'FILL'
    }
    y_pos = tool_bar_start_y
    for tool_name, text in tools.items():
        bg = (100, 200, 100) if tool_name == current_tool else (50, 50, 50)
        cv2.rectangle(image, (0, y_pos), (tool_bar_width, y_pos + 60), bg, -1)
     
        cv2.putText(image, text, (10, y_pos + 40), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
        y_pos += 65

print("Application is running...")

while True:
    success, img = cap.read()
    if not success: break
    img = cv2.flip(img, 1)
    h, w, c = img.shape

    # UI Çizimi
    draw_ui(img)

    img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    result = hands.process(img_rgb)

    if result.multi_hand_landmarks:
        for hand_lms in result.multi_hand_landmarks:
            mp_draw.draw_landmarks(img, hand_lms, mp_hands.HAND_CONNECTIONS)
            lm_list = [[id, int(lm.x * w), int(lm.y * h)] for id, lm in enumerate(hand_lms.landmark)]
            
            if lm_list:
                x1, y1 = lm_list[8][1:]  # Index tip
                x2, y2 = lm_list[12][1:] # Middle tip
                fingers = fingers_up(lm_list)

                # --- MODE: SELECTION (Index + Middle UP) ---
                if fingers[1] and fingers[2]:
                    # Şekil çizimini onaylama (Confirm Shape)
                    if shape_start_point is not None:
                        save_state()
                        if current_tool == TOOL_LINE:
                            cv2.line(img_canvas, shape_start_point, (x1, y1), draw_color, brush_thickness)
                        elif current_tool == TOOL_RECTANGLE:
                            cv2.rectangle(img_canvas, shape_start_point, (x1, y1), draw_color, brush_thickness)
                        elif current_tool == TOOL_CIRCLE:
                            radius = int(np.hypot(x1 - shape_start_point[0], y1 - shape_start_point[1]))
                            cv2.circle(img_canvas, shape_start_point, radius, draw_color, brush_thickness)
                        
                        shape_start_point = None
                        print(f"{current_tool} çizildi!")

                    # Flood Fill Logic (Cooldown'lı)
                    elif current_tool == TOOL_FILL:
                        if time.time() - last_fill_time > FILL_COOLDOWN:
                            # Sadece UI dışındaysa doldur
                            if y1 > color_bar_height and x1 > tool_bar_width:
                                print("Filling...")
                                save_state()
                                mask = np.zeros((h + 2, w + 2), np.uint8)
                                cv2.floodFill(img_canvas, mask, (x1, y1), draw_color)
                                last_fill_time = time.time()

                    xp, yp = 0, 0 
                    cv2.putText(img, "PAUSED / CONFIRM", (x1, y1 - 20), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)

                # --- MODE: DRAWING (Only Index UP) ---
                elif fingers[1] and not fingers[2]:
                    
                    # 1. UI Seçimi (Renk veya Tool)
                    if y1 < color_bar_height: # Renk seçimi alanı
                        if x1 > tool_bar_width:
                            bar_w = (w - tool_bar_width) // len(colors)
                            idx = min((x1 - tool_bar_width) // bar_w, len(colors)-1)
                            current_color_name = list(colors.keys())[idx]
                            draw_color = colors[current_color_name]
                    elif x1 < tool_bar_width: # Tool seçimi alanı
                        if y1 > tool_bar_start_y:
                            t_idx = (y1 - tool_bar_start_y) // 65
                            tools_list = [TOOL_DRAW, TOOL_ERASER, TOOL_LINE, TOOL_RECTANGLE, TOOL_CIRCLE, TOOL_FILL]
                            if 0 <= t_idx < len(tools_list):
                                current_tool = tools_list[t_idx]
                                brush_thickness = eraser_thickness if current_tool == TOOL_ERASER else 15
                    
                    # 2. Çizim Alanı (Kısıtlama Eklendi)
                    # Çizim SADECE renk barının altında VE tool barının sağındaysa yapılabilir.
                    elif y1 > color_bar_height and x1 > tool_bar_width:
                        cv2.circle(img, (x1, y1), 10, draw_color, -1) # Cursor
                        
                        if drawing_mode:
                            # Serbest Çizim
                            if current_tool == TOOL_DRAW:
                                if xp == 0 and yp == 0: xp, yp = x1, y1
                                cv2.line(img_canvas, (xp, yp), (x1, y1), draw_color, brush_thickness)
                                xp, yp = x1, y1
                            
                            # Silgi
                            elif current_tool == TOOL_ERASER:
                                if xp == 0 and yp == 0: xp, yp = x1, y1
                                cv2.line(img_canvas, (xp, yp), (x1, y1), (0,0,0), eraser_thickness)
                                xp, yp = x1, y1

                            # Şekil Önizleme (Preview)
                            elif current_tool in [TOOL_LINE, TOOL_RECTANGLE, TOOL_CIRCLE]:
                                if shape_start_point is None:
                                    shape_start_point = (x1, y1)
                                else:
                                    # Önizlemeyi sadece ekrana (img) çiz, canvas'a değil
                                    if current_tool == TOOL_LINE:
                                        cv2.line(img, shape_start_point, (x1, y1), draw_color, brush_thickness)
                                    elif current_tool == TOOL_RECTANGLE:
                                        cv2.rectangle(img, shape_start_point, (x1, y1), draw_color, brush_thickness)
                                    elif current_tool == TOOL_CIRCLE:
                                        radius = int(np.hypot(x1 - shape_start_point[0], y1 - shape_start_point[1]))
                                        cv2.circle(img, shape_start_point, radius, draw_color, brush_thickness)
                                xp, yp = 0, 0
                    
                    # UI alanındaysak geçmiş koordinatı sıfırla (çizgi çekmesini önler)
                    else:
                        xp, yp = 0, 0

                # Diğer durumlar (El kapalı vs.)
                else:
                    xp, yp = 0, 0
                    shape_start_point = None

    # --- Image Blending ---
    img_gray = cv2.cvtColor(img_canvas, cv2.COLOR_BGR2GRAY)
    _, img_inv = cv2.threshold(img_gray, 10, 255, cv2.THRESH_BINARY_INV)
    img_inv = cv2.cvtColor(img_inv, cv2.COLOR_GRAY2BGR)
    
    img = cv2.bitwise_and(img, img_inv)
    img = cv2.bitwise_or(img, img_canvas)

    # Info UI
    cv2.putText(img, f"TOOL: {current_tool}", (w-200, h-50), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0,255,255), 2)
    
    cv2.imshow("Advanced Air Canvas Fixed", img)
    
    k = cv2.waitKey(1)
    if k == ord('q'): break
    elif k == ord('c'): 
        save_state()
        img_canvas = np.zeros((720, 1280, 3), np.uint8)
    elif k == ord('u'): undo()
    elif k == ord('r'): redo()
    elif k == ord('s'): cv2.imwrite(f"drawing_{int(time.time())}.png", img_canvas)

cap.release()
cv2.destroyAllWindows()