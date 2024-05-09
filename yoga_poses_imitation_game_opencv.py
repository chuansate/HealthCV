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
import os


class YogaPoseImitationGame:
    mp_pose = mp.solutions.pose
    mp_drawing = mp.solutions.drawing_utils
    mp_drawing_styles = mp.solutions.drawing_styles
    pose = mp_pose.Pose(min_tracking_confidence=0.5, min_detection_confidence=0.5)

    def __init__(self, yoga_poses_names_difficulties, yoga_poses_files_names, yoga_poses_path):
        self.__yoga_poses_names_difficulties = yoga_poses_names_difficulties
        self.__yoga_poses_files_names = yoga_poses_files_names
        self.__yoga_poses_path = yoga_poses_path
        self.__yoga_poses_scores = [0 for i in range(len(self.__yoga_poses_names_difficulties))]
        self.__current_game_score = 0
        self.__current_yoga_pose_index = 0

    def display_sample_yoga_pose(self, webcam_frame):
        """
            Display sample yoga pose on the webcam frame, so that user can imitate
        :param webcam_frame: ndarray, webcam frame
        :return:
        """
        if type(frame) != np.ndarray:
            raise TypeError("The webcam frame should be a numpy array!")
        sample_yoga_pose_img = cv2.imread(
            os.path.join(self.__yoga_poses_path, self.__yoga_poses_files_names[self.__current_yoga_pose_index]))
        sample_yoga_pose_img = cv2.resize(sample_yoga_pose_img, (100, 100))
        display_x = 10
        display_y = 100
        webcam_frame[display_y:display_y + sample_yoga_pose_img.shape[0],
        display_x: display_x + sample_yoga_pose_img.shape[1]] = sample_yoga_pose_img

    def calculate_square_differences(self, webcam_frame):
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

        if pose_results.pose_landmarks:
            # Draw the pose annotation on the webcam frame.
            webcam_frame.flags.writeable = True
            YogaPoseImitationGame.mp_drawing.draw_landmarks(
                webcam_frame,
                pose_results.pose_landmarks,
                YogaPoseImitationGame.mp_pose.POSE_CONNECTIONS,
                landmark_drawing_spec=YogaPoseImitationGame.mp_drawing_styles.get_default_pose_landmarks_style())
        else:
            cv2.putText(webcam_frame, "Failed to detect user!",
                        (frame_width // 2 - 206 // 2, 50),
                        cv2.FONT_HERSHEY_PLAIN, 1, (255, 0, 255), 1)

    def normalize_pose_landmarks(self, pose_landmarks_dict):
        """Calculates pose center as point between hips."""
        left_hip = pose_landmarks_dict['LEFT_HIP']
        right_hip = pose_landmarks_dict['RIGHT_HIP']
        center = []
        for i in range(len(left_hip)):
            center.append((left_hip[i] + right_hip[i]) * 0.5)
        for key, coordinates in pose_landmarks_dict.items():
            for i in range(len(coordinates)):
                coordinates[i] -= center[i]
            pose_landmarks_dict[key] = coordinates
        return pose_landmarks_dict

    def update_current_game_score(self):
        self.__current_game_score = sum(self.__yoga_poses_scores)

    def get_current_game_score(self):
        return self.__current_game_score

    def calculate_game_score_yoga_pose(self):
        pass


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

# Information about the yoga poses
YOGA_POSES_PATH = "yoga_poses_imitation_game_images"

YOGA_POSES_FILE_NAMES = [
    "beginner_chair_pose.jpg"
]

# stores tuples of (yoga pose's name, yoga pose's difficulty)
# difficulty = 0 means beginner,
# difficulty = 1 means intermediate,
# difficulty = 2 means advanced.
YOGA_POSES_NAMES_DIFFICULTIES = [
    ("Chair Pose", 0)
]

# Loading icons
startButtonImg = cv2.imread("icons/start_button.png")
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

    cTime = time.time()
    fps = 1 / (cTime - pTime)
    pTime = cTime
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
            cv2.putText(frame, "Score: " + str(game_object.get_current_game_score()), (frame_width - 200, 50),
                        cv2.FONT_HERSHEY_PLAIN, 2,
                        (255, 0, 255), 2)
            game_object.display_sample_yoga_pose(frame)
            game_object.calculate_square_differences(frame)

    cv2.imshow('Frame', frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break
