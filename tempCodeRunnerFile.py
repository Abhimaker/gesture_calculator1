import cv2
import mediapipe as mp
from collections import deque
import time
import pyttsx3
import math
import subprocess
import re

engine = pyttsx3.init()
engine.setProperty('rate', 150)
engine.setProperty('volume', 1.0)

mp_hands = mp.solutions.hands
mp_draw = mp.solutions.drawing_utils
hands = mp_hands.Hands(max_num_hands=2, min_detection_confidence=0.7)

expression = ""
result = ""
gesture_buffer = deque(maxlen=5)
gesture_cooldown = 1.2
gesture_timestamp = {}

def count_fingers(landmarks, label):
    fingers = []
    if label == "Right":
        fingers.append(1 if landmarks[4].x < landmarks[3].x else 0)
    else:
        fingers.append(1 if landmarks[4].x > landmarks[3].x else 0)
    for tip_id in [8, 12, 16, 20]:
        fingers.append(1 if landmarks[tip_id].y < landmarks[tip_id - 2].y else 0)
    return sum(fingers)

def speak(text):
    subprocess.Popen([
        'powershell',
        '-Command',
        f"Add-Type –AssemblyName System.Speech; (New-Object System.Speech.Synthesis.SpeechSynthesizer).Speak('{text}');"
    ])

def is_ok_sign(landmarks):
    thumb_tip = landmarks[4]
    index_tip = landmarks[8]
    distance = math.hypot(thumb_tip.x - index_tip.x, thumb_tip.y - index_tip.y)
    return distance < 0.05

def is_rock_sign(landmarks, label):
    if label == "Right":
        thumb_up = landmarks[4].x < landmarks[3].x
    else:
        thumb_up = landmarks[4].x > landmarks[3].x
    index_down = landmarks[8].y > landmarks[6].y
    middle_down = landmarks[12].y > landmarks[10].y
    ring_down = landmarks[16].y > landmarks[14].y
    pinky_up = landmarks[20].y < landmarks[18].y
    return thumb_up and index_down and middle_down and ring_down and pinky_up

def is_undo_sign(landmarks):
    thumb_up = landmarks[4].y < landmarks[3].y
    index_up = landmarks[8].y < landmarks[6].y
    middle_down = landmarks[12].y > landmarks[10].y
    ring_down = landmarks[16].y > landmarks[14].y
    pinky_up = landmarks[20].y < landmarks[18].y
    return thumb_up and index_up and pinky_up and middle_down and ring_down

def is_zero_gesture(landmarks, label):
    if label != "Right":
        return False
    thumb_up = landmarks[4].y < landmarks[3].y
    index_down = landmarks[8].y > landmarks[6].y
    middle_down = landmarks[12].y > landmarks[10].y
    ring_down = landmarks[16].y > landmarks[14].y
    pinky_down = landmarks[20].y > landmarks[18].y
    return thumb_up and index_down and middle_down and ring_down and pinky_down

def is_clear_all(right_fingers, left_fingers):
    return right_fingers == 5 and left_fingers == 5

def is_swag_sign(landmarks):
    index_up = landmarks[8].y < landmarks[6].y
    middle_down = landmarks[12].y > landmarks[10].y
    ring_down = landmarks[16].y > landmarks[14].y
    pinky_up = landmarks[20].y < landmarks[18].y
    return index_up and middle_down and ring_down and pinky_up

def is_valid_expression(expr):
    if not expr:
        return False
    
    # Check for consecutive operators (except **)
    if re.search(r'[\+\-/]{2,}', expr):
        return False
    
    # Check for more than 2 consecutive asterisks
    if re.search(r'(?<!\*)\*{3,}', expr):
        return False
    
    # Don't allow starting with operators (except parentheses)
    if expr.startswith(("*", "/", "+")):
        return False
    
    # Don't allow more closing parentheses than opening ones
    if expr.count("(") < expr.count(")"):
        return False
    
    # For incomplete expressions, we need more flexible validation
    # Allow expressions that could become valid with more input
    
    # If expression ends with an operator or open parenthesis, it's potentially valid
    if expr.endswith(('+', '-', '*', '/', '**', '(')):
        return True
    
    # If expression has unmatched opening parentheses, it's potentially valid
    if expr.count("(") > expr.count(")"):
        return True
    
    # Try to evaluate the expression as-is for complete expressions
    try:
        # Only try to compile/evaluate if it looks complete
        # (no trailing operators, balanced parentheses)
        if not expr.endswith(('+', '-', '*', '/', '**', '(')) and expr.count("(") == expr.count(")"):
            compile(expr, "<string>", "eval")
        return True
    except:
        return False

def map_gesture(right_fingers, left_fingers, right_ok, left_ok, right_undo, left_undo,
                right_zero, clear_all, right_rock, left_rock, left_swag, right_swag):
    if clear_all:
        return 'C'
    if right_rock:
        return 'U'
    if left_rock:
        return '**'
    if right_ok or left_ok:
        return '='
    if right_zero:
        return '0'
    if left_swag:
        return '('
    if right_swag:
        return ')'
    if right_fingers is not None:
        if left_fingers == 5 and 1 <= right_fingers <= 4:
            return str(right_fingers + 5)
        elif 1 <= right_fingers <= 5:
            return str(right_fingers)
    if left_fingers is not None:
        return {1: '+', 2: '-', 3: '*', 4: '/'}.get(left_fingers, None)
    return None

cap = cv2.VideoCapture(0)

while True:
    success, img = cap.read()
    if not success:
        continue

    img = cv2.flip(img, 1)
    img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    results = hands.process(img_rgb)

    right_fingers = left_fingers = None
    right_ok = left_ok = False
    right_undo = left_undo = False
    right_zero = False
    right_rock = left_rock = False
    left_swag = right_swag = False

    if results.multi_hand_landmarks and results.multi_handedness:
        for hand_landmarks, handedness in zip(results.multi_hand_landmarks, results.multi_handedness):
            label = handedness.classification[0].label
            mp_draw.draw_landmarks(img, hand_landmarks, mp_hands.HAND_CONNECTIONS)
            finger_count = count_fingers(hand_landmarks.landmark, label)
            if label == "Right":
                right_fingers = finger_count
                right_ok = is_ok_sign(hand_landmarks.landmark)
                right_undo = is_undo_sign(hand_landmarks.landmark)
                right_zero = is_zero_gesture(hand_landmarks.landmark, label)
                right_rock = is_rock_sign(hand_landmarks.landmark, label)
                right_swag = is_swag_sign(hand_landmarks.landmark)
                if right_zero:
                    right_fingers = None
            elif label == "Left":
                left_fingers = finger_count
                left_ok = is_ok_sign(hand_landmarks.landmark)
                left_undo = is_undo_sign(hand_landmarks.landmark)
                left_rock = is_rock_sign(hand_landmarks.landmark, label)
                left_swag = is_swag_sign(hand_landmarks.landmark)

    clear_all = is_clear_all(right_fingers, left_fingers)

    detected_gesture = map_gesture(
        right_fingers, left_fingers, right_ok, left_ok,
        right_undo, left_undo, right_zero, clear_all,
        right_rock, left_rock, left_swag, right_swag
    )

    if detected_gesture:
        gesture_buffer.append(detected_gesture)
        if len(gesture_buffer) == gesture_buffer.maxlen and all(g == gesture_buffer[0] for g in gesture_buffer):
            stable_gesture = gesture_buffer[0]
            now = time.time()
            last_time = gesture_timestamp.get(stable_gesture, 0)
            if now - last_time > gesture_cooldown:
                gesture_timestamp[stable_gesture] = now

                if result and result != "Invalid Expression" and stable_gesture not in ['=', 'U', 'C']:
                    expression = ""
                    result = ""

                if stable_gesture.isdigit() or stable_gesture in ['+', '-', '*', '/', '**', '(', ')']:
                    expression += stable_gesture
                    if is_valid_expression(expression):
                        speak({
                            '+': "plus", '-': "minus", '*': "multiply", '/': "divide", '**': "power",
                            '(': "open bracket", ')': "close bracket"
                        }.get(stable_gesture, stable_gesture))
                        result = ""
                    else:
                        result = "Invalid Expression"
                        speak("Invalid expression, please undo or try again")

                elif stable_gesture == '=':
                    if is_valid_expression(expression):
                        try:
                            result = str(eval(expression))
                            speak(f"The result is {result}")
                        except:
                            result = "Invalid Expression"
                            speak("Invalid expression, please undo or try again")
                    else:
                        result = "Invalid Expression"
                        speak("Invalid expression, please undo or try again")

                elif stable_gesture == 'U':
                    expression = expression[:-1]
                    result = ""
                    speak("Undo")

                elif stable_gesture == 'C':
                    expression = ""
                    result = ""
                    speak("Cleared all")

                gesture_buffer.clear()

    # Draw expression with label
    font = cv2.FONT_HERSHEY_SIMPLEX
    font_scale = 1.1
    thickness = 2

    cv2.putText(img, "Expression:", (10, 60), font, font_scale, (0, 0, 0), thickness)
    x_offset = 230
    for i, ch in enumerate(expression):
        color = (0, 0, 255) if (i == len(expression)-1 and not is_valid_expression(expression)) else (0, 0, 0)
        cv2.putText(img, ch, (x_offset + i * 30, 60), font, font_scale, color, thickness)

    # Show Result or Error
    if result == "Invalid Expression":
        cv2.putText(img, "Result: Invalid expression!", (10, 110), font, 1.1, (0, 0, 255), 3)
    elif result:
        cv2.putText(img, f"Result: {result}", (10, 110), font, 1.3, (255, 0, 0), 3)

    cv2.imshow("Gesture Calculator", img)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
