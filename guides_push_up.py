import threading

import cv2
import time
from tkinter import messagebox
import mediapipe as mp
import math
import numpy as np
import playsound
import os
from scipy.stats import pearsonr


def center_opencv_text_horizontally(frame, y, text, text_fs, text_thickness, font):
    frame_width = frame.shape[1]
    text_width = cv2.getTextSize(text, font, text_fs, text_thickness)[0][0]
    cv2.putText(frame, text, (frame_width // 2 - text_width // 2, y),
                font, text_fs,
                (255, 0, 255), text_thickness)


class GuidesPushUp:
    mp_pose = mp.solutions.pose
    mp_drawing = mp.solutions.drawing_utils
    mp_drawing_styles = mp.solutions.drawing_styles
    pose = mp_pose.Pose(min_tracking_confidence=0.5, min_detection_confidence=0.5)
    # the features exclude the facial landmarks, becoz those are not helpful at determining push-up
    features = [
        mp_pose.PoseLandmark.LEFT_SHOULDER,
        mp_pose.PoseLandmark.RIGHT_SHOULDER,
        mp_pose.PoseLandmark.LEFT_ELBOW,
        mp_pose.PoseLandmark.RIGHT_ELBOW,
        mp_pose.PoseLandmark.LEFT_WRIST,
        mp_pose.PoseLandmark.RIGHT_WRIST,
        mp_pose.PoseLandmark.LEFT_HIP,
        mp_pose.PoseLandmark.RIGHT_HIP,
        mp_pose.PoseLandmark.LEFT_KNEE,
        mp_pose.PoseLandmark.RIGHT_KNEE,
        mp_pose.PoseLandmark.LEFT_ANKLE,
        mp_pose.PoseLandmark.RIGHT_ANKLE
    ]

    features_names = [
        "LEFT_SHOULDER",
        "RIGHT_SHOULDER",
        "LEFT_ELBOW",
        "RIGHT_ELBOW",
        "LEFT_WRIST",
        "RIGHT_WRIST",
        "LEFT_HIP",
        "RIGHT_HIP",
        "LEFT_KNEE",
        "RIGHT_KNEE",
        "LEFT_ANKLE",
        "RIGHT_ANKLE"
    ]

    classes = {
        "push_up_DOWN": 0,
        "push_up_UP": 1
    }

    GET_INTO_READY_POSE = "Please get into ready pose"
    GET_INTO_READY_POSE_fs = 1
    GET_INTO_READY_POSE_th = 1
    path_to_audios = "audio"

    def __init__(self):
        self.__current_step_index = 1
        self.__correlation_threshold = 0.95  # telling if the body is straightened
        self.__user_status = 1  # 0 means the user is in push-up DOWN, while 1 means in push-up UP
        self.__user_in_ready_pose = False
        self.__grad_UP_threshold = 0.6  # For step 1 and step 3
        self.__arms_straightened_threshold = 0.05  # For step 1
        self.__grad_DOWN_threshold = 0.15  # For step 2
        self.__grad_left_DOWN_threshold = 0.1
        self.__left_elbow_angle = 0
        self.__push_up_UP_angle_threshold = 145  # For step 3
        self.__workout_over = False
        self.__step1_time_elapsed = 0
        self.__step2_time_elapsed = 0
        self.__step3_time_elapsed = 0

        # avoid playing audio for instructions of every step
        self.__played_step1_audio = False
        self.__played_step2_audio = False
        self.__played_step3_audio = False
        # these `prev_time_elapsed` are to prevent an alert audio being played many times
        self.__prev_step1_time_elapsed_int = 0
        self.__prev_step2_time_elapsed_int = 0
        self.__prev_step3_time_elapsed_int = 0

        # defining y-coordinates for the texts rendered on OpenCV window
        self.step_y_coor = 50
        self.body_not_straight_y_coor = 75
        self.arms_not_align_with_shoulders_y_coor = 75
        self.body_not_parallel_to_ground_y_coor = 75

        # flags of inappropriate postures
        self.step1_body_not_straight = False
        self.step1_arms_not_align_with_shoulders = False
        self.step2_body_not_parallel_to_ground = True
        self.step3_body_not_straight = False
        self.step3_arms_not_align_with_shoulders = False

    def get_current_step_index(self):
        return self.__current_step_index

    # Step 1: Hold the plank pose
    def step1(self, frame, pose_landmarks, curTime, prevTime):
        center_opencv_text_horizontally(frame, self.step_y_coor, "Step 1: Hold plank pose with straightened arms!",
                                        1, 1, cv2.FONT_HERSHEY_PLAIN)
        if not self.__played_step1_audio:
            thread = threading.Thread(target=self.play_audio_step1)
            thread.start()
            self.__played_step1_audio = True

        # render the warnings on OpenCV window for inappropriate postures
        if self.step1_body_not_straight:
            center_opencv_text_horizontally(frame, self.body_not_straight_y_coor,
                                            "Body not straight!",
                                            1, 1, cv2.FONT_HERSHEY_PLAIN)
        elif self.step1_arms_not_align_with_shoulders:
            center_opencv_text_horizontally(frame, self.arms_not_align_with_shoulders_y_coor,
                                            "Arms must align with shoulders!",
                                            1, 1, cv2.FONT_HERSHEY_PLAIN)

        left_shoulder_x = pose_landmarks[GuidesPushUp.features[0]].x
        left_hip_x = pose_landmarks[GuidesPushUp.features[6]].x
        left_hip_y = pose_landmarks[GuidesPushUp.features[6]].y
        left_knee_x = pose_landmarks[GuidesPushUp.features[8]].x
        left_knee_y = pose_landmarks[GuidesPushUp.features[8]].y
        left_ankle_x = pose_landmarks[GuidesPushUp.features[10]].x
        left_shoulder_y = pose_landmarks[GuidesPushUp.features[0]].y
        left_ankle_y = pose_landmarks[GuidesPushUp.features[10]].y
        grad_left = (left_shoulder_y - left_ankle_y) / (left_shoulder_x - left_ankle_x)
        grad_left = abs(grad_left)
        right_shoulder_x = pose_landmarks[GuidesPushUp.features[1]].x
        right_hip_x = pose_landmarks[GuidesPushUp.features[7]].x
        right_hip_y = pose_landmarks[GuidesPushUp.features[7]].y
        right_knee_x = pose_landmarks[GuidesPushUp.features[9]].x
        right_knee_y = pose_landmarks[GuidesPushUp.features[9]].y
        right_ankle_x = pose_landmarks[GuidesPushUp.features[11]].x
        right_shoulder_y = pose_landmarks[GuidesPushUp.features[1]].y
        right_ankle_y = pose_landmarks[GuidesPushUp.features[11]].y
        grad_right = (right_shoulder_y - right_ankle_y) / (right_shoulder_x - right_ankle_x)
        grad_right = abs(grad_right)
        left_body_x = [left_shoulder_x, left_hip_x, left_knee_x, left_ankle_x]
        left_body_y = [left_shoulder_y, left_hip_y, left_knee_y, left_ankle_y]
        left_corr, _ = pearsonr(left_body_x, left_body_y)
        left_corr = abs(left_corr)
        right_body_x = [right_shoulder_x, right_hip_x, right_knee_x, right_ankle_x]
        right_body_y = [right_shoulder_y, right_hip_y, right_knee_y, right_ankle_y]
        right_corr, _ = pearsonr(right_body_x, right_body_y)
        right_corr = abs(right_corr)
        self.__step1_time_elapsed += (curTime - prevTime)
        if self.user_in_ready_pose(left_shoulder_x, left_hip_x, left_knee_x, left_ankle_x, grad_left, right_shoulder_x, right_hip_x, right_knee_x, right_ankle_x, grad_right):
            left_wrist_x = pose_landmarks[GuidesPushUp.features[4]].x
            right_wrist_x = pose_landmarks[GuidesPushUp.features[5]].x
            if left_corr < self.__correlation_threshold and right_corr < self.__correlation_threshold:
                # first condition: to ensure the audio is not played multiple times
                # second condition: to check the inappropriate postures and play the alert audio every 3 seconds
                if round(self.__step1_time_elapsed) != self.__prev_step1_time_elapsed_int and round(self.__step1_time_elapsed) % 3 == 0:
                    self.__prev_step1_time_elapsed_int = round(self.__step1_time_elapsed)
                    self.step1_body_not_straight = True
                    self.step1_arms_not_align_with_shoulders = False
                    thread = threading.Thread(target=self.play_audio_step1_body_not_straight)
                    thread.start()

            # check for the placement of the arms
            elif not self.arms_align_with_shoulders(left_shoulder_x, left_wrist_x, right_shoulder_x, right_wrist_x):
                if round(self.__step1_time_elapsed) != self.__prev_step1_time_elapsed_int and round(self.__step1_time_elapsed) % 3 == 0:
                    self.__prev_step1_time_elapsed_int = round(self.__step1_time_elapsed)
                    self.step1_body_not_straight = False
                    self.step1_arms_not_align_with_shoulders = True
                    thread = threading.Thread(target=self.play_audio_step1_arms_align_shoulders)
                    thread.start()
            else:
                print("Perfect posture for step 1!")
                self.__step1_time_elapsed = 0
                self.__current_step_index += 1
        else:
            center_opencv_text_horizontally(frame, 100, GuidesPushUp.GET_INTO_READY_POSE,
                                            GuidesPushUp.GET_INTO_READY_POSE_fs,
                                            GuidesPushUp.GET_INTO_READY_POSE_th, cv2.FONT_HERSHEY_PLAIN)

    # Step 2: Go down while maintaining a straightened body
    def step2(self, frame, pose_landmarks, curTime, prevTime):
        center_opencv_text_horizontally(frame, self.step_y_coor, "Step 2: Go down while maintaining a straight body.",
                                        1, 1, cv2.FONT_HERSHEY_PLAIN)
        if not self.__played_step2_audio:
            thread = threading.Thread(target=self.play_audio_step2)
            thread.start()
            self.__played_step2_audio = True
        self.__step2_time_elapsed += (curTime - prevTime)
        # render the warnings on OpenCV window for inappropriate postures
        if self.step2_body_not_parallel_to_ground:
            center_opencv_text_horizontally(frame, self.body_not_parallel_to_ground_y_coor,
                                            "Body not parallel to ground!",
                                            1, 1, cv2.FONT_HERSHEY_PLAIN)
        left_shoulder_x = pose_landmarks[GuidesPushUp.features[0]].x
        left_hip_x = pose_landmarks[GuidesPushUp.features[6]].x
        left_hip_y = pose_landmarks[GuidesPushUp.features[6]].y
        left_knee_x = pose_landmarks[GuidesPushUp.features[8]].x
        left_knee_y = pose_landmarks[GuidesPushUp.features[8]].y
        left_ankle_x = pose_landmarks[GuidesPushUp.features[10]].x
        left_shoulder_y = pose_landmarks[GuidesPushUp.features[0]].y
        left_ankle_y = pose_landmarks[GuidesPushUp.features[10]].y
        grad_left = (left_shoulder_y - left_ankle_y) / (left_shoulder_x - left_ankle_x)
        grad_left = abs(grad_left)
        right_shoulder_x = pose_landmarks[GuidesPushUp.features[1]].x
        right_hip_x = pose_landmarks[GuidesPushUp.features[7]].x
        right_hip_y = pose_landmarks[GuidesPushUp.features[7]].y
        right_knee_x = pose_landmarks[GuidesPushUp.features[9]].x
        right_knee_y = pose_landmarks[GuidesPushUp.features[9]].y
        right_ankle_x = pose_landmarks[GuidesPushUp.features[11]].x
        right_shoulder_y = pose_landmarks[GuidesPushUp.features[1]].y
        right_ankle_y = pose_landmarks[GuidesPushUp.features[11]].y
        grad_right = (right_shoulder_y - right_ankle_y) / (right_shoulder_x - right_ankle_x)
        grad_right = abs(grad_right)
        if self.user_in_ready_pose(left_shoulder_x, left_hip_x, left_knee_x, left_ankle_x, grad_left, right_shoulder_x,
                                   right_hip_x, right_knee_x, right_ankle_x, grad_right):
            left_wrist_x = pose_landmarks[GuidesPushUp.features[4]].x
            right_wrist_x = pose_landmarks[GuidesPushUp.features[5]].x
            # check for body not being parallel to the ground
            if not self.body_parallel_to_ground(grad_left, grad_right):
                if round(self.__step2_time_elapsed) != self.__prev_step2_time_elapsed_int and round(
                        self.__step2_time_elapsed) % 3 == 0:
                    self.__prev_step2_time_elapsed_int = round(self.__step2_time_elapsed)
                    self.step2_body_not_parallel_to_ground = True
                    thread = threading.Thread(target=self.play_audio_step2_arms_body_not_parallel_to_ground)
                    thread.start()
            else:
                print("Perfect posture for step 2!")
                self.__step2_time_elapsed = 0
                self.__current_step_index += 1
        else:
            center_opencv_text_horizontally(frame, 100, GuidesPushUp.GET_INTO_READY_POSE,
                                            GuidesPushUp.GET_INTO_READY_POSE_fs,
                                            GuidesPushUp.GET_INTO_READY_POSE_th, cv2.FONT_HERSHEY_PLAIN)

    # Step 3: Go up while maintaining a straightened body
    def step3(self, frame, pose_landmarks, curTime, prevTime):
        center_opencv_text_horizontally(frame, self.step_y_coor, "Step3: Go up while maintaining a straight body.",
                                        1, 1, cv2.FONT_HERSHEY_PLAIN)
        if not self.__played_step3_audio:
            thread = threading.Thread(target=self.play_audio_step3)
            thread.start()
            self.__played_step3_audio = True
        self.__step3_time_elapsed += (curTime - prevTime)

        # render the warnings on OpenCV window for inappropriate postures
        if self.step3_body_not_straight:
            center_opencv_text_horizontally(frame, self.body_not_straight_y_coor,
                                            "Body not straight!",
                                            1, 1, cv2.FONT_HERSHEY_PLAIN)
        elif self.step3_arms_not_align_with_shoulders:
            center_opencv_text_horizontally(frame, self.arms_not_align_with_shoulders_y_coor,
                                            "Arms must align with shoulders!",
                                            1, 1, cv2.FONT_HERSHEY_PLAIN)

        left_shoulder_x = pose_landmarks[GuidesPushUp.features[0]].x
        left_hip_x = pose_landmarks[GuidesPushUp.features[6]].x
        left_hip_y = pose_landmarks[GuidesPushUp.features[6]].y
        left_knee_x = pose_landmarks[GuidesPushUp.features[8]].x
        left_knee_y = pose_landmarks[GuidesPushUp.features[8]].y
        left_ankle_x = pose_landmarks[GuidesPushUp.features[10]].x
        left_shoulder_y = pose_landmarks[GuidesPushUp.features[0]].y
        left_ankle_y = pose_landmarks[GuidesPushUp.features[10]].y
        grad_left = (left_shoulder_y - left_ankle_y) / (left_shoulder_x - left_ankle_x)
        grad_left = abs(grad_left)

        right_shoulder_x = pose_landmarks[GuidesPushUp.features[1]].x
        right_hip_x = pose_landmarks[GuidesPushUp.features[7]].x
        right_hip_y = pose_landmarks[GuidesPushUp.features[7]].y
        right_knee_x = pose_landmarks[GuidesPushUp.features[9]].x
        right_knee_y = pose_landmarks[GuidesPushUp.features[9]].y
        right_ankle_x = pose_landmarks[GuidesPushUp.features[11]].x
        right_shoulder_y = pose_landmarks[GuidesPushUp.features[1]].y
        right_ankle_y = pose_landmarks[GuidesPushUp.features[11]].y
        grad_right = (right_shoulder_y - right_ankle_y) / (right_shoulder_x - right_ankle_x)
        grad_right = abs(grad_right)
        left_body_x = [left_shoulder_x, left_hip_x, left_knee_x, left_ankle_x]
        left_body_y = [left_shoulder_y, left_hip_y, left_knee_y, left_ankle_y]
        left_corr, _ = pearsonr(left_body_x, left_body_y)
        left_corr = abs(left_corr)

        right_body_x = [right_shoulder_x, right_hip_x, right_knee_x, right_ankle_x]
        right_body_y = [right_shoulder_y, right_hip_y, right_knee_y, right_ankle_y]
        right_corr, _ = pearsonr(right_body_x, right_body_y)
        right_corr = abs(right_corr)
        left_wrist_x = pose_landmarks[GuidesPushUp.features[4]].x
        left_wrist_y = pose_landmarks[GuidesPushUp.features[4]].y
        right_wrist_x = pose_landmarks[GuidesPushUp.features[5]].x

        left_elbow_vec = np.array([pose_landmarks[GuidesPushUp.features[2]].x, pose_landmarks[GuidesPushUp.features[2]].y])
        left_shoulder_vec = np.array([left_shoulder_x, left_shoulder_y])
        left_wrist_vec = np.array([left_wrist_x, left_wrist_y])
        left_vec_elbow_to_shoulder = left_shoulder_vec - left_elbow_vec
        left_vec_elbow_to_wrist = left_wrist_vec - left_elbow_vec
        self.__left_elbow_angle = self._get_angle_betw_two_vectors(left_vec_elbow_to_shoulder, left_vec_elbow_to_wrist)
        if self.user_go_back_ready_pose(left_shoulder_x, left_hip_x, left_knee_x, left_ankle_x, grad_left, right_shoulder_x,
                                   right_hip_x, right_knee_x, right_ankle_x, grad_right, self.__left_elbow_angle):

            if left_corr < self.__correlation_threshold and right_corr < self.__correlation_threshold:
                if round(self.__step3_time_elapsed) != self.__prev_step3_time_elapsed_int and round(
                        self.__step3_time_elapsed) % 3 == 0:
                    self.step3_body_not_straight = True
                    self.step3_arms_not_align_with_shoulders = False
                    self.__prev_step3_time_elapsed_int = round(self.__step3_time_elapsed)
                    thread = threading.Thread(target=self.play_audio_step1_body_not_straight)
                    thread.start()

            # check for the placement of the arms
            elif not self.arms_align_with_shoulders(left_shoulder_x, left_wrist_x, right_shoulder_x, right_wrist_x):
                if round(self.__step3_time_elapsed) != self.__prev_step3_time_elapsed_int and round(
                        self.__step3_time_elapsed) % 3 == 0:
                    self.step3_body_not_straight = False
                    self.step3_arms_not_align_with_shoulders = True
                    self.__prev_step3_time_elapsed_int = round(self.__step3_time_elapsed)
                    thread = threading.Thread(target=self.play_audio_step1_arms_align_shoulders)
                    thread.start()
            else:
                print("Perfect posture for step 3!")
                self.__step3_time_elapsed = 0
                self.__current_step_index += 1
        else:
            center_opencv_text_horizontally(frame, 100, GuidesPushUp.GET_INTO_READY_POSE,
                                            GuidesPushUp.GET_INTO_READY_POSE_fs,
                                            GuidesPushUp.GET_INTO_READY_POSE_th, cv2.FONT_HERSHEY_PLAIN)

    def body_parallel_to_ground(self, grad_left, grad_right):
        if grad_left < self.__grad_DOWN_threshold and grad_right < self.__grad_DOWN_threshold:
            return True
        else:
            return False

    def arms_align_with_shoulders(self, left_shoulder_x, left_wrist_x, right_shoulder_x, right_wrist_x):
        if abs(left_shoulder_x - left_wrist_x) < self.__arms_straightened_threshold and abs(right_shoulder_x - right_wrist_x) < self.__arms_straightened_threshold:
            return True
        else:
            return False

    def user_in_ready_pose(self, left_shoulder_x, left_hip_x, left_knee_x, left_ankle_x, grad_left, right_shoulder_x, right_hip_x, right_knee_x, right_ankle_x, grad_right):
        if left_shoulder_x < left_hip_x and left_hip_x < left_knee_x and left_knee_x < left_ankle_x and grad_left < self.__grad_UP_threshold:
            return True
        elif right_shoulder_x > right_hip_x and right_hip_x > right_knee_x and right_knee_x > right_ankle_x and grad_right < self.__grad_UP_threshold:
            return True
        else:
            return False

    def user_go_back_ready_pose(self, left_shoulder_x, left_hip_x, left_knee_x, left_ankle_x, grad_left, right_shoulder_x, right_hip_x, right_knee_x, right_ankle_x, grad_right, left_elbow_angle):
        if left_shoulder_x < left_hip_x and left_hip_x < left_knee_x and left_knee_x < left_ankle_x and grad_left < self.__grad_UP_threshold and left_elbow_angle >= self.__push_up_UP_angle_threshold:
            return True
        elif right_shoulder_x > right_hip_x and right_hip_x > right_knee_x and right_knee_x > right_ankle_x and grad_right < self.__grad_UP_threshold and left_elbow_angle >= self.__push_up_UP_angle_threshold:
            return True
        else:
            return False

    def detect_pose_landmarks(self, frame):
        # To improve performance, optionally mark the image as not writeable to
        # pass by reference.
        frame.flags.writeable = False
        results = GuidesPushUp.pose.process(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
        frame.flags.writeable = True
        if results.pose_landmarks:
            GuidesPushUp.mp_drawing.draw_landmarks(frame, results.pose_landmarks,
                                                         GuidesPushUp.mp_pose.POSE_CONNECTIONS,
                                                         landmark_drawing_spec=GuidesPushUp.mp_drawing_styles.get_default_pose_landmarks_style())

        return results

    def reset_user_status(self):
        self.__user_status = 1

    def get_user_status(self):
        return self.__user_status

    def set_user_status(self, status):
        self.__user_status = status

    def _get_angle_betw_two_vectors(self, vec1, vec2):
        angle_radian = math.acos((np.dot(vec1, vec2)) / (np.linalg.norm(vec1) * np.linalg.norm(vec2)))
        return int(round(math.degrees(angle_radian), 0))

    def get_left_elbow_angle(self):
        return self.__left_elbow_angle

    def workout_is_over(self):
        return self.__workout_over

    def set_workout_is_over(self):
        self.__workout_over = True

    def play_audio_step1(self):
        try:
            playsound.playsound(os.path.join(GuidesPushUp.path_to_audios, "push_up_step1.mp3"))
        except:
            print("Failed to play audio for step 1!")

    def play_audio_step2(self):
        try:
            playsound.playsound(os.path.join(GuidesPushUp.path_to_audios, "push_up_step2.mp3"))
        except:
            print("Failed to play audio for step 2!")

    def play_audio_step3(self):
        try:
            playsound.playsound(os.path.join(GuidesPushUp.path_to_audios, "push_up_step3.mp3"))
        except:
            print("Failed to play audio for step 3!")

    def play_audio_step1_body_not_straight(self):
        try:
            playsound.playsound(os.path.join(GuidesPushUp.path_to_audios, "body_not_straight.mp3"))
        except:
            print("Failed to play audio for body not straight of step 1!")

    def play_audio_step1_arms_align_shoulders(self):
        try:
            playsound.playsound(os.path.join(GuidesPushUp.path_to_audios, "arms_align_shoulders.mp3"))
        except:
            print("Failed to play audio for the arms must align with shoulders of step 1!")

    def play_audio_step2_arms_body_not_parallel_to_ground(self):
        try:
            playsound.playsound(os.path.join(GuidesPushUp.path_to_audios, "body_not_parallel_to_ground.mp3"))
        except:
            print("Failed to play audio for the body not parallel to ground of step 2!")

    def play_audio_workout_over(self):
        try:
            playsound.playsound(os.path.join(GuidesPushUp.path_to_audios, "congrats_pushup.mp3"))
        except:
            print("Failed to play audio for the user completing the push-up guide!!")


def guides_push_up_page(uname, window):
    window.destroy()
    cap = cv2.VideoCapture(0)
    cv2.namedWindow("Counting push-up", cv2.WINDOW_NORMAL)
    cv2.setWindowProperty("Counting push-up", cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)
    prevTime = 0
    curTime = 0
    FONT_SCALE = 1.2
    workout_over_time_elapsed = 0

    # Flags
    failed_to_turn_on_webcam = False
    played_workout_over_audio = False
    # Messages to display on screen
    # `fs` means "font scale"
    # `th` means "thickness"
    USER_NOT_EXIST = "Failed to detect user!"
    USER_NOT_EXIST_fs = 1
    USER_NOT_EXIST_th = 1
    WORKOUT_IS_OVER = "Workout is over, this window will close in 5 seconds!"
    WORKOUT_IS_OVER_fs = 1
    WORKOUT_IS_OVER_th = 1

    cpu_obj = GuidesPushUp()
    while True:
        success, frame = cap.read()
        if not success:
            failed_to_turn_on_webcam = True
            break

        frame_height = frame.shape[0]
        frame_width = frame.shape[1]
        curTime = time.time()
        fps = 1 / (curTime - prevTime)

        pose_results = cpu_obj.detect_pose_landmarks(frame)
        # Flip the frame horizontally
        frame = cv2.flip(frame, 1)
        cv2.putText(frame, str(int(fps)) + " FPS", (10, 40), cv2.FONT_HERSHEY_PLAIN, 1.2, (255, 0, 255), 1)

        if not cpu_obj.workout_is_over():
            cv2.putText(frame, "Press E to end", (frame_width - 150, 25),
                        cv2.FONT_HERSHEY_PLAIN, 1,
                        (255, 0, 255), 1)
            if pose_results.pose_landmarks:
                if cpu_obj.get_current_step_index() == 1:
                    cpu_obj.step1(frame, pose_results.pose_landmarks.landmark, curTime, prevTime)
                elif cpu_obj.get_current_step_index() == 2:
                    cpu_obj.step2(frame, pose_results.pose_landmarks.landmark, curTime, prevTime)
                elif cpu_obj.get_current_step_index() == 3:
                    cpu_obj.step3(frame, pose_results.pose_landmarks.landmark, curTime, prevTime)
                else:
                    cpu_obj.set_workout_is_over()

            else:
                # Fails to detect the user
                center_opencv_text_horizontally(frame, 25, USER_NOT_EXIST, USER_NOT_EXIST_fs,
                                                USER_NOT_EXIST_th, cv2.FONT_HERSHEY_PLAIN)
        else:
            if not played_workout_over_audio:
                thread = threading.Thread(target=cpu_obj.play_audio_workout_over)
                thread.start()
                played_workout_over_audio = True
            workout_over_time_elapsed += (curTime - prevTime)
            if workout_over_time_elapsed < 5:
                center_opencv_text_horizontally(frame, 50, WORKOUT_IS_OVER, WORKOUT_IS_OVER_fs,
                                                WORKOUT_IS_OVER_th, cv2.FONT_HERSHEY_PLAIN)
            else:
                break

        prevTime = curTime

        cv2.imshow('Counting push-up', frame)

        if cv2.waitKey(1) & 0xFF == ord('e'):
            msg = messagebox.showinfo("Warning", "The progress in this session has been lost.")
            break

    if failed_to_turn_on_webcam:
        msg = messagebox.showinfo("Warning", "Failed to turn on the webcam.")
    cap.release()
    cv2.destroyAllWindows()
    from guides_page import guides_page
    guides_page(uname, None)
