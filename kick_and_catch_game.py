"""
 The game is about generating objects with icons of foot and hand.
 The objects with foot icon means the user has to hit it using foot,
 while the objects with hand icon means the user has to hit it using hand.
"""

import cv2
import mediapipe as mp
import time
from Buttons import *
import sys


class KickAndCatchGame():
    def __init__(self):
        pass


def render_kick_and_catch_game_UI():
    cap = cv2.VideoCapture(0)
    cv2.namedWindow("Frame", cv2.WINDOW_NORMAL)
    cv2.setWindowProperty("Frame", cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)

    # x and y refers to coordinates of top left corner of the window
    # x, y, WINDOW_WIDTH, WINDOW_HEIGHT = cv2.getWindowImageRect("Frame")

    mpHands = mp.solutions.hands
    hands = mpHands.Hands(False)  # modify `max_num_hands`
    mpDraw = mp.solutions.drawing_utils
    prevTime = 0
    curTime = 0


    # Loading icons
    startButtonImg = cv2.imread("icons/start_button2.png")
    startButtonImg_WIDTH = startButtonImg.shape[1]
    startButtonImg_HEIGHT = startButtonImg.shape[0]

    # Flag
    game_started = False
    game_object_created = False

    while True:
        success, frame = cap.read()
        if not success:
            print("Failed to read frames!")
            sys.exit()
        # Flip the frame horizontally
        frame = cv2.flip(frame, 1)
        frame_height = frame.shape[0]
        frame_width = frame.shape[1]

        curTime = time.time()
        fps = 1 / (curTime - prevTime)

        cv2.putText(frame, str(int(fps)) + " FPS", (10, 50), cv2.FONT_HERSHEY_PLAIN, 2, (255, 0, 255), 2)
        if not game_started:
            rgbFrame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            results = hands.process(rgbFrame)
            startButton = ButtonImage(frame, startButtonImg, (frame_width // 2 - startButtonImg_WIDTH // 2, 200),
                                      "start_but")
            if results.multi_hand_landmarks:
                for handLms in results.multi_hand_landmarks:
                    # don't pass HAND_CONNECTIONS if u just want the landmarks
                    mpDraw.draw_landmarks(frame, handLms)
                    index_finger_tip_x = handLms.landmark[mpHands.HandLandmark.INDEX_FINGER_TIP].x * frame_width
                    index_finger_tip_y = handLms.landmark[mpHands.HandLandmark.INDEX_FINGER_TIP].y * frame_height

                    if startButton.isTapped(index_finger_tip_x, index_finger_tip_y):
                        game_started = True
        else:
            if not game_object_created:
                game_object = KickAndCatchGame()
                game_object_created = True
            else:
                cv2.putText(frame, "Press E to end", (frame_width - 150, 25),
                            cv2.FONT_HERSHEY_PLAIN, 1,
                            (255, 0, 255), 1)
                cv2.putText(frame, "Score: " + str(game_object.get_total_game_score()), (frame_width - 200, 50),
                            cv2.FONT_HERSHEY_PLAIN, 2,
                            (255, 0, 255), 2)
                game_object.display_sample_yoga_pose(frame)
                cur_similarity_score = game_object.evaluate_user_pose(frame)
                if cur_similarity_score > game_object.get_similarity_threshold():
                    game_object.count_down(frame, curTime, prevTime)
                else:
                    game_object.set_hold_pose_time_elapsed(0)
        prevTime = curTime
        cv2.imshow('Frame', frame)
        if cv2.waitKey(1) & 0xFF == ord('e'):  # which key comes first then it responds faster to the user input
            if game_started and game_object_created:
                print("Game over!")

        if cv2.waitKey(1) & 0xFF == ord('q'):  # key Q comes after key E, hence user needs to press several times!
            break


render_kick_and_catch_game_UI()