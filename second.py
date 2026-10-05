import cv2
import mediapipe as mp
import pyautogui
import numpy as np
import time

# ===================== SETUP =====================
pyautogui.FAILSAFE = False
pyautogui.PAUSE = 0  # IMPORTANT: reduce lag

screen_w, screen_h = pyautogui.size()

mp_hands = mp.solutions.hands
mp_draw = mp.solutions.drawing_utils

hands = mp_hands.Hands(
    max_num_hands=1,
    min_detection_confidence=0.7,
    min_tracking_confidence=0.7
)

cap = cv2.VideoCapture(0)
if not cap.isOpened():
    print("ERROR: Camera not found")
    exit()

# Cursor smoothing
prev_x, prev_y = screen_w // 2, screen_h // 2
smoothening = 7

# Finger previous states
prev_index_up = False
prev_middle_up = False

# Click delay
last_click = 0
click_delay = 0.4

# Scroll control
last_scroll = 0
scroll_delay = 0.15
scroll_speed = 40

# Drag control
dragging = False
pinch_threshold = 30

# ===================== LOOP =====================
while True:
    success, frame = cap.read()
    if not success:
        continue

    frame = cv2.flip(frame, 1)
    h, w, _ = frame.shape
    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    result = hands.process(rgb)

    if result.multi_hand_landmarks:
        for hand in result.multi_hand_landmarks:
            lm = hand.landmark

            # -------- Finger States --------
            index_up  = lm[8].y  < lm[6].y
            middle_up = lm[12].y < lm[10].y
            ring_up   = lm[16].y < lm[14].y
            pinky_up  = lm[20].y < lm[18].y

            # Index finger
            x = int(lm[8].x * w)
            y = int(lm[8].y * h)

            # Thumb
            thumb_x = int(lm[4].x * w)
            thumb_y = int(lm[4].y * h)

            distance = np.hypot(thumb_x - x, thumb_y - y)
ng
            # ================= MOVE =================
            if index_up and not middle_up:
                screen_x = np.interp(x, (0, w), (0, screen_w))
                screen_y = np.interp(y, (0, h), (0, screen_h))

                curr_x = prev_x + (screen_x - prev_x) / smoothening
                curr_y = prev_y + (screen_y - prev_y) / smoothening

                pyautogui.moveTo(curr_x, curr_y)
                prev_x, prev_y = curr_x, curr_y

                cv2.putText(frame, "MOVE", (20, 40),
                            cv2.FONT_HERSHEY_SIMPLEX, 1,
                            (0, 255, 0), 3)

            # ================= CLICK MODE =================
            elif index_up and middle_up:
                cv2.putText(frame, "CLICK MODE", (20, 40),
                            cv2.FONT_HERSHEY_SIMPLEX, 1,
                            (0, 0, 255), 3)

            now = time.time()

            # ================= LEFT CLICK =================
            if prev_index_up and not index_up and middle_up and now - last_click > click_delay:
                pyautogui.click()
                last_click = now

            # ================= RIGHT CLICK =================
            if prev_middle_up and not middle_up and index_up and now - last_click > click_delay:
                pyautogui.rightClick()
                last_click = now

            # ================= SCROLL UP =================
            if index_up and middle_up and ring_up and not pinky_up:
                if now - last_scroll > scroll_delay:
                    pyautogui.scroll(scroll_speed)
                    last_scroll = now

            # ================= SCROLL DOWN =================
            elif index_up and middle_up and pinky_up and not ring_up:
                if now - last_scroll > scroll_delay:
                    pyautogui.scroll(-scroll_speed)
                    last_scroll = now

            # ================= DRAG =================
            if index_up and middle_up and distance < pinch_threshold:
                if not dragging:
                    pyautogui.mouseDown()
                    dragging = True
            else:
                if dragging:
                    pyautogui.mouseUp()
                    dragging = False

            prev_index_up = index_up
            prev_middle_up = middle_up

            mp_draw.draw_landmarks(frame, hand, mp_hands.HAND_CONNECTIONS)

    cv2.imshow("Virtual Mouse - Final Version", frame)

    if cv2.waitKey(1) & 0xFF == 27:
        break

cap.release()
cv2.destroyAllWindows()