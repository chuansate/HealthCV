"""
NEWER VERSION, THIS IS USING OPENCV TO DO ALL THE ANIMATION ONLY! INSTEAD OF TKINTER!
for the imitation game, use mediapipe to extract body landmarks from the sample image and users. Then, normalize the coordinates with the middle of the hip (middle of the hip is the new center).
but the distance of the user from camera might vary. If the user is close to camera, the new coordinates are larger; If the user is far away from camera, the new coordinates are smaller.
The new coordinates of the user can be broken down into x-components and y-components, they can be further normalized based on the x range and y range (refer to normalization in structured dataset).
Link to common yoga poses: https://greatist.com/move/common-yoga-poses
"""
from tkinter import messagebox

import cv2
import mediapipe as mp
import time
from Buttons import *
import sys
import os
import csv
import math


class YogaPoseImitationGame:
    mp_pose = mp.solutions.pose
    mp_drawing = mp.solutions.drawing_utils
    mp_drawing_styles = mp.solutions.drawing_styles
    pose = mp_pose.Pose(min_tracking_confidence=0.5, min_detection_confidence=0.5)

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

    def __init__(self, yoga_poses_names_difficulties, yoga_poses_files_names, yoga_poses_path):
        self.__yoga_poses_names_difficulties = yoga_poses_names_difficulties
        self.__yoga_poses_files_names = yoga_poses_files_names
        self.__yoga_poses_path = yoga_poses_path
        self.__yoga_poses_scores = [0 for i in range(len(self.__yoga_poses_names_difficulties))]
        self.__total_game_score = 0
        self.__current_yoga_pose_index = 0
        self.__sample_yoga_poses_landmarks = self.read_sample_yoga_poses_csv()
        self.__difficulty_levels = {0: "Beginner", 1: "Intermediate", 2: "Advanced"}
        self.__similarity_threshold = 0.5  # once the similarity exceeds this threshold, then timer starts counting down
        self.__hold_pose_period = 3  # the user has to hold the yoga pose for this long, in seconds
        self.__hold_pose_time_elapsed = 0

    def read_sample_yoga_poses_csv(self):
        file = open("./yoga_poses_imitation_game_images/sample_yoga_poses_landmarks.csv")
        csvreader = csv.reader(file)
        rows = []
        for row in csvreader:
            rows.append(row)
        return rows

    def display_sample_yoga_pose(self, webcam_frame):
        """
            Display sample yoga pose on the webcam frame, so that user can imitate
        :param webcam_frame: ndarray, webcam frame
        :return:
        """
        if type(webcam_frame) != np.ndarray:
            raise TypeError("The webcam frame should be a numpy array!")
        if self.__current_yoga_pose_index < len(self.__yoga_poses_names_difficulties):
            sample_yoga_pose_img = cv2.imread(
                os.path.join(self.__yoga_poses_path, self.__yoga_poses_files_names[self.__current_yoga_pose_index]))
            sample_yoga_pose_img = cv2.resize(sample_yoga_pose_img, (150, 200))
            display_x = 10
            display_y = 110
            webcam_frame[display_y:display_y + sample_yoga_pose_img.shape[0],
            display_x: display_x + sample_yoga_pose_img.shape[1]] = sample_yoga_pose_img
            cv2.putText(webcam_frame, self.__difficulty_levels[
                self.__yoga_poses_names_difficulties[self.__current_yoga_pose_index][1]] + " level",
                        (10, 85),
                        cv2.FONT_HERSHEY_PLAIN, 1, (255, 0, 255), 1)
            cv2.putText(webcam_frame, self.__yoga_poses_names_difficulties[self.__current_yoga_pose_index][0],
                        (10, 100),
                        cv2.FONT_HERSHEY_PLAIN, 1, (255, 0, 255), 1)
        else:
            self.game_over(webcam_frame)

    def game_over(self, webcam_frame):
        """
        Maybe save the game data into database?
        :return:
        """
        frame_width = webcam_frame.shape[1]
        cv2.putText(webcam_frame, "Game over!",
                    (frame_width // 2 - 206 // 2, 75),
                    cv2.FONT_HERSHEY_PLAIN, 1, (255, 0, 255), 1)

    def evaluate_user_pose(self, webcam_frame):
        """
            Compare the user's body landmarks with the sample's
        :param webcam_frame: a numpy array, webcam frame
        :return:
        """
        frame_width = webcam_frame.shape[1]
        # To improve performance, optionally mark the image as not writeable to
        # pass by reference.
        webcam_frame.flags.writeable = False
        pose_results = YogaPoseImitationGame.pose.process(cv2.cvtColor(webcam_frame, cv2.COLOR_BGR2RGB))
        similarity_score = 0
        if pose_results.pose_landmarks:
            if self.__current_yoga_pose_index < len(self.__yoga_poses_names_difficulties):
                # Draw the pose annotation on the webcam frame.
                webcam_frame.flags.writeable = True
                YogaPoseImitationGame.mp_drawing.draw_landmarks(
                    webcam_frame,
                    pose_results.pose_landmarks,
                    YogaPoseImitationGame.mp_pose.POSE_CONNECTIONS,
                    landmark_drawing_spec=YogaPoseImitationGame.mp_drawing_styles.get_default_pose_landmarks_style())
                # extract the x-, and y-coordinates of the 22 body landmarks as features
                user_landmarks_dict = {}  # by the user
                for index, ft in enumerate(YogaPoseImitationGame.features):
                    landmark_coordinates = pose_results.pose_landmarks.landmark[ft]
                    user_landmarks_dict[YogaPoseImitationGame.feature_names[index]] = [landmark_coordinates.x,
                                                                                       landmark_coordinates.y]
                user_landmarks_dict = self.normalize_pose_landmarks(user_landmarks_dict)
                current_yoga_pose_landmarks = self.__sample_yoga_poses_landmarks[self.__current_yoga_pose_index]
                sum_squared_differences = 0
                user_landmarks = [elem for row in list(user_landmarks_dict.values()) for elem in row]
                for i in range(len(user_landmarks)):
                    sum_squared_differences += (float(current_yoga_pose_landmarks[i]) - user_landmarks[i]) ** 2

                similarity_score = self.calculate_similarity(sum_squared_differences)
                self.__yoga_poses_scores[self.__current_yoga_pose_index] = int(similarity_score * 100)
                cv2.putText(webcam_frame, "Similarity: " + str(round(similarity_score * 100, 1)) + "%",
                            (frame_width - 200, 75),
                            cv2.FONT_HERSHEY_PLAIN, 1.2, (255, 0, 255), 1)

        else:
            cv2.putText(webcam_frame, "Failed to detect user!",
                        (frame_width // 2 - 206 // 2, 50),
                        cv2.FONT_HERSHEY_PLAIN, 1, (255, 0, 255), 1)

        return similarity_score

    def count_down(self, webcam_frame, currentTime, previousTime):
        frame_width = webcam_frame.shape[1]
        self.__hold_pose_time_elapsed += (currentTime - previousTime)
        if self.__hold_pose_time_elapsed > self.__hold_pose_period:
            self.update_total_game_score()
            self.__current_yoga_pose_index += 1

        else:
            cv2.putText(webcam_frame, "Hold this pose for " + str(
                int(round(self.__hold_pose_period - self.__hold_pose_time_elapsed, 0))),
                        (frame_width // 2 - 206 // 2, 75),
                        cv2.FONT_HERSHEY_PLAIN, 1, (255, 0, 255), 1)

    def calculate_similarity(self, sum_squared_differences):
        """
        Return a similarity score that ranges from 0 to 1
        :param sum_squared_differences: sum of squared differences between the user's landmarks and sample yoga pose's landmarks
        :return:
        """
        return math.e ** (-1 * sum_squared_differences)

    def normalize_pose_landmarks(self, pose_landmarks_dict):
        """
        Calculates pose center as point between hips.
        Then, normalize the coordinates with the middle of the hip (middle of the hip is the new center).

        But the distance of the user from camera might vary:
        If the user is close to camera, the new coordinates are larger;
        If the user is far away from camera, the new coordinates are smaller.

        The new coordinates of the user can be broken down into x-components and y-components,
        they can be further normalized based on the x range and y range (refer to normalization in structured dataset).
        """
        left_hip = pose_landmarks_dict['LEFT_HIP']
        right_hip = pose_landmarks_dict['RIGHT_HIP']
        center = []
        for i in range(len(left_hip)):
            center.append((left_hip[i] + right_hip[i]) * 0.5)

        # Changing the origin from top-left corner to the middle of the left hip and right hip
        for key, coordinates in pose_landmarks_dict.items():
            for i in range(len(coordinates)):
                coordinates[i] -= center[i]
            pose_landmarks_dict[key] = coordinates

        # Normalize the x-coordinates and y-coordinates into range [0, 1]
        landmarks_x = []
        landmarks_y = []
        for lm_x, lm_y in pose_landmarks_dict.values():
            landmarks_x.append(lm_x)
            landmarks_y.append(lm_y)
        x_min = min(landmarks_x)
        x_max = max(landmarks_x)
        y_min = min(landmarks_y)
        y_max = max(landmarks_y)
        for ft_name in YogaPoseImitationGame.feature_names:
            pose_landmarks_dict[ft_name][0] = (pose_landmarks_dict[ft_name][0] - x_min) / (x_max - x_min)
            pose_landmarks_dict[ft_name][1] = (pose_landmarks_dict[ft_name][1] - y_min) / (y_max - y_min)

        return pose_landmarks_dict

    def update_total_game_score(self):
        self.__total_game_score = sum(self.__yoga_poses_scores)

    def get_total_game_score(self):
        return self.__total_game_score

    def calculate_game_score_yoga_pose(self):
        pass

    def get_similarity_threshold(self):
        return self.__similarity_threshold

    def set_hold_pose_time_elapsed(self, value):
        self.__hold_pose_time_elapsed = value

    def set_current_yoga_pose_index(self, index):
        if index < 0:
            raise ValueError("Array index cannot be less than 0!")
        self.__current_yoga_pose_index = index

    def get_current_yoga_pose_index(self):
        return self.__current_yoga_pose_index

# Information about the yoga poses
YOGA_POSES_PATH = "yoga_poses_imitation_game_images"

YOGA_POSES_FILE_NAMES = [
    "0_chair_pose.jpg",
    "0_warriorII.jpg",
    "1_intense_side_stretch.jpg",
    "2_side_plank.jpg"
]

# stores tuples of (yoga pose's name, yoga pose's difficulty)
# difficulty = 0 means beginner,
# difficulty = 1 means intermediate,
# difficulty = 2 means advanced.
YOGA_POSES_NAMES_DIFFICULTIES = [
    ("Chair Pose", 0),
    ("Warrior II", 0),
    ("Intense Side Stretch", 1),
    ("Side plank", 2)
]

# Loading icons
startButtonImg = cv2.imread("icons/start_button2.png")
startButtonImg_WIDTH = startButtonImg.shape[1]
startButtonImg_HEIGHT = startButtonImg.shape[0]


def render_yoga_poses_imitation_game_UI(uname, window):
    window.destroy()
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

    # Flag
    game_started = False
    game_object_created = False
    failed_to_turn_on_webcam = False

    while True:
        success, frame = cap.read()
        if not success:
            failed_to_turn_on_webcam = True
            break
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
                game_object = YogaPoseImitationGame(YOGA_POSES_NAMES_DIFFICULTIES, YOGA_POSES_FILE_NAMES, YOGA_POSES_PATH)
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
                game_object.set_current_yoga_pose_index(
                    game_object.get_current_yoga_pose_index() + len(YOGA_POSES_NAMES_DIFFICULTIES))
                game_object.game_over(frame)
                time.sleep(3)
                break

    if failed_to_turn_on_webcam:
        msg = messagebox.showinfo("Warning", "Failed to turn on the webcam.")
    cap.release()
    cv2.destroyAllWindows()
    from fitness_games_page import fitness_games_page
    fitness_games_page(uname, None)
