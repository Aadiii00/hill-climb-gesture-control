import cv2
import mediapipe as mp
import pyautogui

mp_hands = mp.solutions.hands
hands = mp_hands.Hands(
    model_complexity=0,
    min_detection_confidence=0.6,
    min_tracking_confidence=0.6
)
mp_draw = mp.solutions.drawing_utils

cap = cv2.VideoCapture(0)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
cap.set(cv2.CAP_PROP_FPS, 30)

def fingers_up(hand_landmarks):
    tips = [4, 8, 12, 16, 20]
    fingers = []

    # Thumb
    fingers.append(
        hand_landmarks.landmark[tips[0]].x <
        hand_landmarks.landmark[tips[0] - 1].x
    )

    # Other fingers
    for i in range(1, 5):
        fingers.append(
            hand_landmarks.landmark[tips[i]].y <
            hand_landmarks.landmark[tips[i] - 2].y
        )

    return fingers.count(True)

last_action = ""

while True:
    ret, frame = cap.read()
    if not ret:
        break

    frame = cv2.flip(frame, 1)
    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    result = hands.process(rgb)

    action = "No Hand"

    if result.multi_hand_landmarks:
        for hand_landmarks in result.multi_hand_landmarks:
            mp_draw.draw_landmarks(
                frame, hand_landmarks, mp_hands.HAND_CONNECTIONS
            )

            count = fingers_up(hand_landmarks)

            if count >= 4:
                if last_action != "ACCELERATE":
                    pyautogui.keyDown('right')
                    pyautogui.keyUp('left')
                    last_action = "ACCELERATE"
                action = "ACCELERATE"

            elif count == 0:
                if last_action != "BRAKE":
                    pyautogui.keyDown('left')
                    pyautogui.keyUp('right')
                    last_action = "BRAKE"
                action = "BRAKE"

            else:
                if last_action != "IDLE":
                    pyautogui.keyUp('left')
                    pyautogui.keyUp('right')
                    last_action = "IDLE"
                action = "IDLE"

    else:
        if last_action != "IDLE":
            pyautogui.keyUp('left')
            pyautogui.keyUp('right')
            last_action = "IDLE"

    cv2.putText(frame, action, (30, 50),
                cv2.FONT_HERSHEY_SIMPLEX, 1,
                (0, 255, 0), 2)

    cv2.imshow("Hill Climb Hand Control", frame)

    if cv2.waitKey(1) & 0xFF == 27:
        break

cap.release()
cv2.destroyAllWindows()
