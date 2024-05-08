"""
NEWER VERSION, THIS IS USING OPENCV TO DO ALL THE ANIMATION ONLY! INSTEAD OF TKINTER!
for the imitation game, use mediapipe to extract body landmarks from the sample image and users. Then, normalize the coordinates with the middle of the hip (middle of the hip is the new center).
but the distance of the user from camera might vary. If the user is close to camera, the new coordinates are larger; If the user is far away from camera, the new coordinates are smaller.
The new coordinates of the user can be broken down into x-components and y-components, they can be further normalized based on the x range and y range (refer to normalization in structured dataset).
Link to common yoga poses: https://greatist.com/move/common-yoga-poses
"""
import cv2
import mediapipe as mp
import time
from Buttons import *
import sys

cap = cv2.VideoCapture(0)
cv2.namedWindow("Frame", cv2.WINDOW_NORMAL)
cv2.setWindowProperty("Frame", cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)

# x and y refers to coordinates of top left corner of the window
# x, y, WINDOW_WIDTH, WINDOW_HEIGHT = cv2.getWindowImageRect("Frame")

mpHands = mp.solutions.hands
hands = mpHands.Hands(False)  # modify `max_num_hands`
mpDraw = mp.solutions.drawing_utils

pTime = 0
cTime = 0

# Loading icons
startButtonImg = cv2.imread("icons/start_button.png")
startButtonImg_WIDTH = startButtonImg.shape[1]
startButtonImg_HEIGHT = startButtonImg.shape[0]

while True:
    success, frame = cap.read()
    if not success:
        print("Failed to read frames!")
        sys.exit()
    # Flip the frame horizontally
    frame = cv2.flip(frame, 1)
    frame_height = frame.shape[0]
    frame_width = frame.shape[1]
    rgbFrame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = hands.process(rgbFrame)

    cTime = time.time()
    fps = 1/(cTime-pTime)
    pTime = cTime
    cv2.putText(frame, str(int(fps)) + " FPS", (10, 70), cv2.FONT_HERSHEY_PLAIN, 3, (255, 0, 255), 3)
    # the 206 and 32 are got from cv2.getTextSize()
    cv2.putText(frame, "HealthCV", (frame_width//2 - 206//2, int((0.4 * frame_height)/2) - 32//2), cv2.FONT_ITALIC, 1.5, (255, 0, 255), 1)
    startButton = ButtonImage(frame, startButtonImg, (frame_width//2 - startButtonImg_WIDTH//2, 200), "start_but")


    if results.multi_hand_landmarks:
        for handLms in results.multi_hand_landmarks:
            # don't pass HAND_CONNECTIONS if u just want the landmarks
            mpDraw.draw_landmarks(frame, handLms)
            index_finger_tip_x = handLms.landmark[mpHands.HandLandmark.INDEX_FINGER_TIP].x * frame_width
            index_finger_tip_y = handLms.landmark[mpHands.HandLandmark.INDEX_FINGER_TIP].y * frame_height

            if startButton.isTapped(index_finger_tip_x, index_finger_tip_y):
                # redirecting to other pages
                pass

    cv2.imshow('Frame', frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break