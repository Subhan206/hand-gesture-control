import cv2
import mediapipe as mp
import pyautogui
import numpy as np
import time
import math
from ctypes import cast, POINTER
from comtypes import CLSCTX_ALL
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
import pyautogui
# ... other imports ...

# --- SPEED HACKS ---
pyautogui.PAUSE = 0
pyautogui.FAILSAFE = False

# --- Configuration ---
CAM_WIDTH, CAM_HEIGHT = 640, 480
SCREEN_WIDTH, SCREEN_HEIGHT = pyautogui.size()
SMOOTHING = 2
FRAME_REDUCTION = 100

# --- Initialize MediaPipe ---
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(
    max_num_hands=1,
    min_detection_confidence=0.7,
    min_tracking_confidence=0.7
)
mp_draw = mp.solutions.drawing_utils

# --- Initialize Audio Control (Windows) ---
devices = AudioUtilities.GetSpeakers()
try:
    # Try the standard way (for older pycaw)
    interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
except AttributeError:
    # Fallback for newer pycaw (which wraps the device)
    interface = devices._device.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)

volume = cast(interface, POINTER(IAudioEndpointVolume))
volRange = volume.GetVolumeRange()
minVol = volRange[0]
maxVol = volRange[1]

# --- Variables ---
plocX, plocY = 0, 0
clocX, clocY = 0, 0
vol = 0
volBar = 400
volPer = 0

cap = cv2.VideoCapture(0)
cap.set(3, CAM_WIDTH)
cap.set(4, CAM_HEIGHT)

print("Gesture Controller Started...")
print("  - Index Up: Move Mouse")
print("  - Index + Thumb Pinch: Click")
print("  - Pinky UP: Volume Control Mode")

try:
    while True:
        success, img = cap.read()
        if not success: break

        img = cv2.flip(img, 1)
        img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        results = hands.process(img_rgb)

        if results.multi_hand_landmarks:
            for hand_lms in results.multi_hand_landmarks:
                lm_list = []
                for id, lm in enumerate(hand_lms.landmark):
                    h, w, c = img.shape
                    cx, cy = int(lm.x * w), int(lm.y * h)
                    lm_list.append([id, cx, cy])

                if len(lm_list) != 0:
                    # --- Landmarks ---
                    x1, y1 = lm_list[8][1:]   # Index Tip
                    x2, y2 = lm_list[4][1:]   # Thumb Tip
                    x3, y3 = lm_list[12][1:]  # Middle Tip
                    
                    # Check Finger States (Tip vs PIP joint) - Simple "Is Finger Up?" check
                    index_up = y1 < lm_list[6][2]
                    middle_up = y3 < lm_list[10][2]
                    
                    x_pinky, y_pinky = lm_list[20][1:]
                    x_pinky_base, y_pinky_base = lm_list[17][1:]
                    pinky_up = y_pinky < y_pinky_base

                    # --- MODE 1: VOLUME CONTROL (Pinky Up) ---
                    if pinky_up:
                        cv2.putText(img, "VOLUME MODE", (20, 50), cv2.FONT_HERSHEY_PLAIN, 2, (0, 0, 255), 2)
                        
                        length = math.hypot(x2 - x1, y2 - y1)
                        # Visuals
                        cv2.line(img, (x1, y1), (x2, y2), (255, 0, 255), 3)
                        
                        # Set Volume (Adjust [30, 170] to your calibrated range!)
                        vol = np.interp(length, [30, 170], [minVol, maxVol])
                        volBar = np.interp(length, [30, 170], [400, 150])
                        volPer = np.interp(length, [30, 170], [0, 100])
                        volume.SetMasterVolumeLevel(vol, None)

                    # --- MODE 2: SCROLL CONTROL (Index + Middle Up) ---
                    elif index_up and middle_up:
                        cv2.putText(img, "SCROLL MODE", (20, 50), cv2.FONT_HERSHEY_PLAIN, 2, (255, 0, 0), 2)
                        
                        # Distance between Index and Middle (Visual only)
                        cv2.line(img, (x1, y1), (x3, y3), (255, 0, 0), 3)

                        # Scroll Logic: Map Hand Y Position to Scroll Speed
                        # If hand is in Top part of screen -> Scroll Up
                        # If hand is in Bottom part -> Scroll Down
                        
                        scroll_threshold = 50 # Sensitivity
                        if y1 < (CAM_HEIGHT // 2) - scroll_threshold:
                            pyautogui.scroll(100) # Scroll Up
                            cv2.circle(img, (x1, y1), 15, (255, 255, 0), cv2.FILLED)
                        elif y1 > (CAM_HEIGHT // 2) + scroll_threshold:
                            pyautogui.scroll(-100) # Scroll Down
                            cv2.circle(img, (x1, y1), 15, (255, 255, 0), cv2.FILLED)

                    # --- MODE 3: CURSOR CONTROL (Only Index Up) ---
                    elif index_up:
                        cv2.putText(img, "CURSOR MODE", (20, 50), cv2.FONT_HERSHEY_PLAIN, 2, (0, 255, 0), 2)
                        
                        # Move Mouse
                        x3_screen = np.interp(x1, (FRAME_REDUCTION, CAM_WIDTH - FRAME_REDUCTION), (0, SCREEN_WIDTH))
                        y3_screen = np.interp(y1, (FRAME_REDUCTION, CAM_HEIGHT - FRAME_REDUCTION), (0, SCREEN_HEIGHT))

                        clocX = plocX + (x3_screen - plocX) / SMOOTHING
                        clocY = plocY + (y3_screen - plocY) / SMOOTHING
                        pyautogui.moveTo(clocX, clocY)
                        plocX, plocY = clocX, clocY

                        # --- LEFT CLICK (Index + Thumb) ---
                        dist_left = math.hypot(x2 - x1, y2 - y1)
                        if dist_left < 40:
                            cv2.circle(img, (x1, y1), 15, (0, 255, 0), cv2.FILLED)
                            pyautogui.click()
                            time.sleep(0.1)

                        # --- RIGHT CLICK (Middle + Thumb) ---
                        # Note: We check Middle finger distance even if it's "down" to allow for the pinch gesture
                        dist_right = math.hypot(x2 - x3, y2 - y3)
                        if dist_right < 40:
                            cv2.circle(img, (x3, y3), 15, (0, 0, 255), cv2.FILLED)
                            pyautogui.rightClick()
                            time.sleep(0.2)
                
                mp_draw.draw_landmarks(img, hand_lms, mp_hands.HAND_CONNECTIONS)

        # Draw Volume Bar
        cv2.rectangle(img, (50, 150), (85, 400), (0, 255, 0), 3)
        cv2.rectangle(img, (50, int(volBar)), (85, 400), (0, 255, 0), cv2.FILLED)
        cv2.putText(img, f'{int(volPer)} %', (40, 450), cv2.FONT_HERSHEY_COMPLEX, 1, (0, 250, 0), 3)

        cv2.imshow("Advanced Gesture Control", img)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

except KeyboardInterrupt:
    print("Stopping...")
finally:
    cap.release()
    cv2.destroyAllWindows()