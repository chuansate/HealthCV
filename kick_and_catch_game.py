"""
 The game is about generating objects with icons of foot and hand.
 The objects with foot icon means the user has to hit it using foot,
 while the objects with hand icon means the user has to hit it using hand.
"""
import random
import cv2
import mediapipe as mp
import time
import sys

from Buttons import ButtonImage
from kick_and_catch_game_objects import *


class KickAndCatchGame:
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
        self.__total_game_duration = 50  # the game lasts for this long, in seconds
        self.__game_duration_elapsed = 0
        self.__game_over = False
        self.__stay_duration = 5  # how long the objects stay on the screen
        self.__max_num_objects_on_frame = 4
        self.__current_objects_on_frame = []

    def get_total_game_score(self):
        return self.__total_game_score

    def count_down_game_duration(self, webcam_frame, currentTime, previousTime):
        frame_width = webcam_frame.shape[1]
        frame_height = webcam_frame.shape[0]
        self.__game_duration_elapsed += (currentTime - previousTime)
        if self.__game_duration_elapsed > self.__total_game_duration:
            self.__game_over = True

        else:
            cv2.putText(webcam_frame, "Time left: " + str(
                int(round(self.__total_game_duration - self.__game_duration_elapsed, 0))),
                        (frame_width // 2 - 206 // 2, 25),
                        cv2.FONT_HERSHEY_PLAIN, 1, (255, 0, 255), 1)
            webcam_frame.flags.writeable = False
            pose_results = KickAndCatchGame.pose.process(cv2.cvtColor(webcam_frame, cv2.COLOR_BGR2RGB))
            webcam_frame.flags.writeable = True
            while len(self.__current_objects_on_frame) < self.__max_num_objects_on_frame:
                # print("Printing current objects: ")
                # for obj in self.__current_objects_on_frame:
                #     print(obj)
                # print()
                self.generate_object(webcam_frame)

            self.render_objects_onto_screen(webcam_frame)
            obj_index = 0
            for obj in self.__current_objects_on_frame:
                if obj.isExpired(currentTime, previousTime):
                    self.__current_objects_on_frame.pop(obj_index)
                    self.decrease_game_score()
                else:
                    # Render countdown for each object
                    cv2.putText(webcam_frame, str(
                        int(round(obj.total_stay_duration - obj.stay_duration_elapsed, 0))),
                                obj.coord_top_left_corner,
                                cv2.FONT_HERSHEY_DUPLEX, 1, (0, 0, 255), 1)
                obj_index += 1
            if pose_results.pose_landmarks:
                left_index_finger_tip_x = pose_results.pose_landmarks.landmark[
                    KickAndCatchGame.mp_pose.PoseLandmark.LEFT_INDEX].x * frame_width
                left_index_finger_tip_y = pose_results.pose_landmarks.landmark[
                    KickAndCatchGame.mp_pose.PoseLandmark.LEFT_INDEX].y * frame_height
                right_index_finger_tip_x = pose_results.pose_landmarks.landmark[
                    KickAndCatchGame.mp_pose.PoseLandmark.RIGHT_INDEX].x * frame_width
                right_index_finger_tip_y = pose_results.pose_landmarks.landmark[
                    KickAndCatchGame.mp_pose.PoseLandmark.RIGHT_INDEX].y * frame_height

                left_foot_index_x = pose_results.pose_landmarks.landmark[
                    KickAndCatchGame.mp_pose.PoseLandmark.LEFT_FOOT_INDEX].x * frame_width
                left_foot_index_y = pose_results.pose_landmarks.landmark[
                    KickAndCatchGame.mp_pose.PoseLandmark.LEFT_FOOT_INDEX].y * frame_height
                right_foot_index_x = pose_results.pose_landmarks.landmark[
                    KickAndCatchGame.mp_pose.PoseLandmark.RIGHT_FOOT_INDEX].x * frame_width
                right_foot_index_y = pose_results.pose_landmarks.landmark[
                    KickAndCatchGame.mp_pose.PoseLandmark.RIGHT_FOOT_INDEX].y * frame_height
                KickAndCatchGame.mp_drawing.draw_landmarks(
                    webcam_frame,
                    pose_results.pose_landmarks,
                    KickAndCatchGame.mp_pose.POSE_CONNECTIONS,
                    landmark_drawing_spec=KickAndCatchGame.mp_drawing_styles.get_default_pose_landmarks_style())
                for obj in self.__current_objects_on_frame:
                    if isinstance(obj, PunchObject):
                        if obj.isPunched(left_index_finger_tip_x, left_index_finger_tip_y):
                            self.__current_objects_on_frame.remove(obj)
                            self.increase_game_score()
                            break
                        if obj.isPunched(right_index_finger_tip_x, right_index_finger_tip_y):
                            self.__current_objects_on_frame.remove(obj)
                            self.increase_game_score()
                            break

                    if isinstance(obj, KickObject):
                        if obj.isKicked(left_foot_index_x, left_foot_index_y):
                            self.__current_objects_on_frame.remove(obj)
                            self.increase_game_score()
                            break
                        if obj.isKicked(right_foot_index_x, right_foot_index_y):
                            self.__current_objects_on_frame.remove(obj)
                            self.increase_game_score()
                            break

            else:
                cv2.putText(webcam_frame, "Failed to detect user!",
                            (frame_width // 2 - 206 // 2, 50),
                            cv2.FONT_HERSHEY_PLAIN, 1, (255, 0, 255), 1)

    def generate_object(self, frame):
        """
        It could be kick object or punch object, at random position but not overlapping with the existing objects on screen
        :param frame:
        :return:
        """
        frame_height = frame.shape[0]
        frame_width = frame.shape[1]
        random_coordinates = (0, 0)
        while True:
            duplicated = False
            # the step size is 50 (height and width of the icons), this is too ensure the program is not stucked at random generation too long
            random_coordinates = (random.randrange(0, frame_width - 49, 50), random.randrange(50, frame_height - 49, 50))
            if len(self.__current_objects_on_frame) > 0:
                for obj in self.__current_objects_on_frame:
                    if (obj.coord_top_left_corner[0] - obj.width <= random_coordinates[0] <= obj.coord_top_left_corner[
                        0] + obj.width) and (
                            obj.coord_top_left_corner[1] - obj.height <= random_coordinates[1] <=
                            obj.coord_top_left_corner[1] + obj.height):
                        duplicated = True
                        break

            if not duplicated:
                break

        obj = PunchObject(KickAndCatchGame.punching_img, random_coordinates, self.__stay_duration) if random.randint(0,
                                                                                                                     1) == 0 else KickObject(
            KickAndCatchGame.kicking_img, random_coordinates, self.__stay_duration)
        self.__current_objects_on_frame.append(obj)

    def render_objects_onto_screen(self, frame):
        if len(self.__current_objects_on_frame) != 0:
            for obj in self.__current_objects_on_frame:
                x = obj.coord_top_left_corner[0]
                y = obj.coord_top_left_corner[1]
                frame[y:y + obj.height, x:x + obj.width] = obj.button_img

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

    def increase_game_score(self):
        self.__total_game_score += 2

    def decrease_game_score(self):
        if self.__total_game_score > 0:
            self.__total_game_score -= 1


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
