# WORKING CODES FOR DETECTING HANDS' LANDMARKS
# a maximum of 2 hands can be detected inside a webcam (modify `max_num_hands`)
import cv2
import mediapipe as mp
import time
from Buttons import Button


def create_pause_button(img, side_length, coord_top_left):
    cv2.rectangle(img, coord_top_left, (coord_top_left[0] + side_length, coord_top_left[1] + side_length), (0, 0, 255), -1)
    white_bars_height = int(side_length * 0.8)
    white_bars_width = int(side_length * 0.2)
    start_pt_white_bar1 = (coord_top_left[0] + int(0.2 * side_length), coord_top_left[1] + int(0.1 * side_length))
    start_pt_white_bar2 = (coord_top_left[0] + side_length - int(0.4 * side_length), coord_top_left[1] + int(0.1 * side_length))
    cv2.rectangle(img, start_pt_white_bar1, (start_pt_white_bar1[0] + white_bars_width, start_pt_white_bar1[1] + white_bars_height), (255, 255, 255), -1)
    cv2.rectangle(img, start_pt_white_bar2,
                  (start_pt_white_bar2[0] + white_bars_width, start_pt_white_bar2[1] + white_bars_height),
                  (255, 255, 255), -1)


def create_resume_button(img, side_length, coord_top_left):
    cv2.rectangle(img, coord_top_left, (coord_top_left[0] + side_length, coord_top_left[1] + side_length), (0, 255, 0), -1)
    cv2.line(img, (coord_top_left[0] + side_length//3, coord_top_left[1] + side_length//3), (coord_top_left[0] + side_length//3, coord_top_left[1] + int(2/3*side_length)), (255, 255, 255), 2)
    cv2.line(img, (coord_top_left[0] + side_length//3, coord_top_left[1] + int(2/3*side_length)),
             (coord_top_left[0] + int(2/3*side_length), coord_top_left[1] + side_length//2), (255, 255, 255), 2)
    cv2.line(img, (coord_top_left[0] + int(2/3*side_length), coord_top_left[1] + side_length//2),
             (coord_top_left[0] + side_length//3, coord_top_left[1] + side_length//3), (255, 255, 255), 2)


cap = cv2.VideoCapture(0)
# WIDTH = 300
# HEIGHT = 300
PAUSE_BUTTON_SIDE_LENGTH = 45
RESUME_BUTTON_SIDE_LENGTH = 45
cv2.namedWindow("Frame", cv2.WINDOW_NORMAL)
cv2.setWindowProperty("Frame", cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)

# x and y refers to coordinates of top left corner of the window
# x, y, WINDOW_WIDTH, WINDOW_HEIGHT = cv2.getWindowImageRect("Frame")

mpHands = mp.solutions.hands
hands = mpHands.Hands(False)  # modify `max_num_hands`
mpDraw = mp.solutions.drawing_utils

pTime = 0
cTime = 0

game_paused = False

while True:
    success, frame = cap.read()
    # Flip the frame horizontally
    frame = cv2.flip(frame, 1)
    frame_height = frame.shape[0]
    frame_width = frame.shape[1]
    rgbFrame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = hands.process(rgbFrame)

    # getting the coordinates of the landmarks
    # print(results.multi_hand_landmarks)
    cTime = time.time()
    fps = 1/(cTime-pTime)
    pTime = cTime
    cv2.putText(frame, str(int(fps)) + " FPS", (10, 70), cv2.FONT_HERSHEY_PLAIN, 3, (255, 0, 255), 3)
    # the 206 and 32 are got from cv2.getTextSize()
    cv2.putText(frame, "HealthCV", (frame_width//2 - 206//2, int((0.4 * frame_height)/2) - 32//2), cv2.FONT_ITALIC, 1.5, (255, 0, 255), 1)

    but1 = Button(frame, (100, 100), 50, 50, (255, 0, 0), -1, "But1")
    but2 = Button(frame, (400, 100), 50, 50, (255, 0, 0), -1, "But2")
    coord_top_left_pause_button = (frame_width - 55, 10)
    coord_top_left_resume_button = ((frame_width-RESUME_BUTTON_SIDE_LENGTH)//2, (frame_height-RESUME_BUTTON_SIDE_LENGTH)//2)
    if results.multi_hand_landmarks:
        for handLms in results.multi_hand_landmarks:
            # don't pass HAND_CONNECTIONS if u just want the landmarks
            mpDraw.draw_landmarks(frame, handLms)
            index_finger_tip_x = handLms.landmark[mpHands.HandLandmark.INDEX_FINGER_TIP].x * frame_width
            index_finger_tip_y = handLms.landmark[mpHands.HandLandmark.INDEX_FINGER_TIP].y * frame_height
            # if the pause button is clicked by the index fingertip
            if not game_paused and (coord_top_left_pause_button[0] <= index_finger_tip_x <=
                coord_top_left_pause_button[0] + PAUSE_BUTTON_SIDE_LENGTH) and (
                    coord_top_left_pause_button[1] <= index_finger_tip_y <=
                    coord_top_left_pause_button[1] + PAUSE_BUTTON_SIDE_LENGTH):
                game_paused = not game_paused
            # if the resume button is clicked by the index fingertip
            if game_paused and (coord_top_left_resume_button[0] <= index_finger_tip_x <=
                coord_top_left_resume_button[0] + RESUME_BUTTON_SIDE_LENGTH) and (
                    coord_top_left_resume_button[1] <= index_finger_tip_y <=
                    coord_top_left_resume_button[1] + RESUME_BUTTON_SIDE_LENGTH):
                game_paused = not game_paused

            if but1.isTapped(index_finger_tip_x, index_finger_tip_y):
                # redirecting to other pages
                pass
            elif but2.isTapped(index_finger_tip_x, index_finger_tip_y):
                pass

    # after clicking the pause button, spawn a green resume button at the middle
    # if the green button is still at the same place as the pause button, then the game will keep pausing and resuming
    if game_paused:
        create_resume_button(frame, RESUME_BUTTON_SIDE_LENGTH, coord_top_left_resume_button)
    else:
        create_pause_button(frame, PAUSE_BUTTON_SIDE_LENGTH, coord_top_left_pause_button)
    cv2.imshow('Frame', frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break
