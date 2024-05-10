"""
 The game is about generating objects with icons of foot and hand.
 The objects with foot icon means the user has to hit it using foot,
 while the objects with hand icon means the user has to hit it using hand.
"""

import cv2
import mediapipe as mp
import time
import sys

from Buttons import ButtonImage
from kick_and_catch_game_objects import *


class KickAndCatchGame():
    mp_pose = mp.solutions.pose
    mp_drawing = mp.solutions.drawing_utils
    mp_drawing_styles = mp.solutions.drawing_styles
    pose = mp_pose.Pose(min_tracking_confidence=0.5, min_detection_confidence=0.5)
    punching_img = cv2.imread("icons/punching_smaller.png")
    kicking_img = cv2.imread("icons/kicking_smaller.png")
    features = [
        mp_pose.PoseLandmark.LEFT_SHOULDER,
        mp_pose.PoseLandmark.RIGHT_SHOULDER,
        mp_pose.PoseLandmark.LEFT_ELBOW,
        mp_pose.PoseLandmark.RIGHT_ELBOW,
        mp_pose.PoseLandmark.LEFT_WRIST,
        mp_pose.PoseLandmark.RIGHT_WRIST,
        mp_pose.PoseLandmark.LEFT_PINKY,
        mp_pose.PoseLandmark.RIGHT_PINKY,
        mp_pose.PoseLandmark.LEFT_INDEX,
        mp_pose.PoseLandmark.RIGHT_INDEX,
        mp_pose.PoseLandmark.LEFT_THUMB,
        mp_pose.PoseLandmark.RIGHT_THUMB,
        mp_pose.PoseLandmark.LEFT_HIP,
        mp_pose.PoseLandmark.RIGHT_HIP,
        mp_pose.PoseLandmark.LEFT_KNEE,
        mp_pose.PoseLandmark.RIGHT_KNEE,
        mp_pose.PoseLandmark.LEFT_ANKLE,
        mp_pose.PoseLandmark.RIGHT_ANKLE,
        mp_pose.PoseLandmark.LEFT_HEEL,
        mp_pose.PoseLandmark.RIGHT_HEEL,
        mp_pose.PoseLandmark.LEFT_FOOT_INDEX,
        mp_pose.PoseLandmark.RIGHT_FOOT_INDEX
    ]

    feature_names = [
        "LEFT_SHOULDER",
        "RIGHT_SHOULDER",
        "LEFT_ELBOW",
        "RIGHT_ELBOW",
        "LEFT_WRIST",
        "RIGHT_WRIST",
        "LEFT_PINKY",
        "RIGHT_PINKY",
        "LEFT_INDEX",
        "RIGHT_INDEX",
        "LEFT_THUMB",
        "RIGHT_THUMB",
        "LEFT_HIP",
        "RIGHT_HIP",
        "LEFT_KNEE",
        "RIGHT_KNEE",
        "LEFT_ANKLE",
        "RIGHT_ANKLE",
        "LEFT_HEEL",
        "RIGHT_HEEL",
        "LEFT_FOOT_INDEX",
        "RIGHT_FOOT_INDEX"
    ]

    def __init__(self):
        self.__total_game_score = 0
        self.__similarity_threshold = 0.5  # once the similarity exceeds this threshold, then timer starts counting down
        self.__total_game_duration = 12  # the user has to hold the yoga pose for this long, in seconds
        self.__game_duration_elapsed = 0
        self.__game_over = False
        self.__current_objects_on_frame = []
        self.__stay_duration = 5  # how long the objects stay on the screen
        self.__max_num_objects_on_frame = 4

    def get_total_game_score(self):
        return self.__total_game_score

    def count_down_game_duration(self, webcam_frame, currentTime, previousTime):
        frame_width = webcam_frame.shape[1]
        self.__game_duration_elapsed += (currentTime - previousTime)
        if self.__game_duration_elapsed > self.__total_game_duration:
            self.__game_over = True

        else:
            cv2.putText(webcam_frame, "Time left: " + str(
                int(round(self.__total_game_duration - self.__game_duration_elapsed, 0))),
                        (frame_width // 2 - 206 // 2, 75),
                        cv2.FONT_HERSHEY_PLAIN, 1, (255, 0, 255), 1)
            if len(self.__current_objects_on_frame) <= self.__max_num_objects_on_frame:
                self.generate_object(webcam_frame)

    def generate_object(self, frame):
        """
        It could be kick object or punch object, at random position but not overlapping with the existing objects on screen
        :param frame:
        :return:
        """
        self.__current_objects_on_frame.append(
            PunchObject(frame, KickAndCatchGame.punching_img, (100, 50), self.__stay_duration))

        self.__current_objects_on_frame.append(
            PunchObject(frame, KickAndCatchGame.punching_img, (180, 100), self.__stay_duration))
        self.__current_objects_on_frame.append(
            KickObject(frame, KickAndCatchGame.kicking_img, (300, 50), self.__stay_duration))

    def set_game_over(self, value):
        self.__game_over = value

    def get_game_over(self):
        return self.__game_over

    def render_final_results(self, webcam_frame):
        """
        Render final game results of the user, such as total score, best record, some messages...
        """
        frame_width = webcam_frame.shape[1]
        cv2.putText(webcam_frame, "Game over!",
                    (frame_width // 2 - 206 // 2, 75),
                    cv2.FONT_HERSHEY_PLAIN, 1, (255, 0, 255), 1)
        cv2.putText(webcam_frame, "Score: " + str(self.__total_game_score),
                    (frame_width // 2 - 206 // 2, 100),
                    cv2.FONT_HERSHEY_PLAIN, 1, (255, 0, 255), 1)

    def save_game_data(self, webcam_frame):
        """
        Saving game data into the database
        :return:
        """
        frame_width = webcam_frame.shape[1]
        cv2.putText(webcam_frame, "Saving game data...",
                    (frame_width // 2 - 206 // 2, 125),
                    cv2.FONT_HERSHEY_PLAIN, 1, (255, 0, 255), 1)


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

                if not game_object.get_game_over():
                    cv2.putText(frame, "Press E to end", (frame_width - 150, 25),
                                cv2.FONT_HERSHEY_PLAIN, 1,
                                (255, 0, 255), 1)
                    cv2.putText(frame, "Score: " + str(game_object.get_total_game_score()), (frame_width - 200, 50),
                                cv2.FONT_HERSHEY_PLAIN, 2,
                                (255, 0, 255), 2)
                    game_object.count_down_game_duration(frame, curTime, prevTime)
                    # game_object.display_sample_yoga_pose(frame)
                    # cur_similarity_score = game_object.evaluate_user_pose(frame)
                    # if cur_similarity_score > game_object.get_similarity_threshold():
                    #     game_object.count_down(frame, curTime, prevTime)
                    # else:
                    #     game_object.set_hold_pose_time_elapsed(0)
                else:
                    game_object.render_final_results(frame)
                    game_object.save_game_data(frame)

        prevTime = curTime
        cv2.imshow('Frame', frame)
        if cv2.waitKey(1) & 0xFF == ord('e'):  # which key comes first then it responds faster to the user input
            if game_started and game_object_created:
                game_object.set_game_over(True)
                game_object.render_final_results(frame)
                game_object.save_game_data(frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):  # key Q comes after key E, hence user needs to press several times!
            break


render_kick_and_catch_game_UI()
