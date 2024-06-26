"""
implement a class. Draw landmarks on elbow and the two adjacent joints,
then compute the angle to determine whether it is a ready pose or bicep curl pose. Make a counter for it
The guidelines are from: https://www.mayoclinic.org/healthy-lifestyle/fitness/multimedia/biceps-curl/vid-20084675#:~:text=Campbell%3A%20To%20do%20a%20biceps,front%20of%20your%20upper%20arm.
"""
import random
from datetime import datetime

import cv2
import mediapipe as mp
import time
import sys
import numpy as np
import math
from tkinter import ttk, messagebox
import threading
import playsound
from scipy.stats import pearsonr

from data_models.biceps_curl_records import BicepsCurlRecord


def center_opencv_text_horizontally(frame, y, text, text_fs, text_thickness, font):
    frame_width = frame.shape[1]
    text_width = cv2.getTextSize(text, font, text_fs, text_thickness)[0][0]
    cv2.putText(frame, text, (frame_width // 2 - text_width // 2, y),
                font, text_fs,
                (255, 0, 255), text_thickness)


class CountingBicepsCurl:
    mp_pose = mp.solutions.pose
    mp_drawing = mp.solutions.drawing_utils
    mp_drawing_styles = mp.solutions.drawing_styles
    pose = mp_pose.Pose(min_tracking_confidence=0.5, min_detection_confidence=0.5)
    # exclude the facial landmarks detected by the mediapipe pose model
    features = [
        mp_pose.PoseLandmark.LEFT_SHOULDER,
        mp_pose.PoseLandmark.RIGHT_SHOULDER,
        mp_pose.PoseLandmark.LEFT_ELBOW,
        mp_pose.PoseLandmark.RIGHT_ELBOW,
        mp_pose.PoseLandmark.LEFT_WRIST,
        mp_pose.PoseLandmark.RIGHT_WRIST,
        mp_pose.PoseLandmark.LEFT_HIP,
        mp_pose.PoseLandmark.RIGHT_HIP
    ]

    feature_names = [
        "LEFT_SHOULDER",
        "RIGHT_SHOULDER",
        "LEFT_ELBOW",
        "RIGHT_ELBOW",
        "LEFT_WRIST",
        "RIGHT_WRIST",
        "LEFT_HIP",
        "RIGHT_HIP"
    ]

    path_to_audios = "./audio/"

    def __init__(self, set_count, rep_count):
        self.__set_count = set_count
        self.__rep_count = rep_count
        self.__current_set_count = 1
        self.__left_biceps_curl_count = 0
        self.__left_arm_status = 0  # 0 means left arm is straightened, 1 means lifting the dumbbell.
        self.__right_biceps_curl_count = 0
        self.__right_arm_status = 0  # 0 means right arm is straightened, 1 means lifting the dumbbell.
        self.__left_elbow_angle = 0
        self.__right_elbow_angle = 0
        self.__user_in_ready_pose = False  # when the user straightens their arm
        self.__ready_pose_ankle_angle = 165  # threshold to determine if the arms are straightened
        self.__lift_angle = 40  # threshold to determine if the dumbbell is raised high enough
        self.__workout_over = False
        self.workout_duration = 0  # time elapsed in seconds

    def userInReadyPose(self, pose_results):
        # pass in the body landmarks and calculate the angle at ankle
        # keyword: calculate the angle betw 2 vectors
        # extract the x-, and y-coordinates of the 8 body landmarks as features
        landmarks_dict = {}
        for index, ft in enumerate(CountingBicepsCurl.features):
            landmark_coordinates = pose_results.pose_landmarks.landmark[ft]
            landmarks_dict[CountingBicepsCurl.feature_names[index]] = [landmark_coordinates.x, landmark_coordinates.y]
        landmarks_dict = self.normalize_pose_landmarks(landmarks_dict)

        # To find the left arm, we have to extract the right arm landmarks. The same goes to the right arm.
        # This is because the webcam frame got flipped horizontally at the beginning!
        left_vec_elbow_to_shoulder = self._get_vector_by_landmark_names(landmarks_dict, "RIGHT_ELBOW", "RIGHT_SHOULDER")
        left_vec_elbow_to_wrist = self._get_vector_by_landmark_names(landmarks_dict, "RIGHT_ELBOW", "RIGHT_WRIST")
        self.__left_elbow_angle = self._get_angle_betw_two_vectors(left_vec_elbow_to_shoulder, left_vec_elbow_to_wrist)
        right_vec_elbow_to_shoulder = self._get_vector_by_landmark_names(landmarks_dict, "LEFT_ELBOW", "LEFT_SHOULDER")
        right_vec_elbow_to_wrist = self._get_vector_by_landmark_names(landmarks_dict, "LEFT_ELBOW", "LEFT_WRIST")
        self.__right_elbow_angle = self._get_angle_betw_two_vectors(right_vec_elbow_to_shoulder, right_vec_elbow_to_wrist)
        if self.__left_elbow_angle >= self.__ready_pose_ankle_angle or self.__right_elbow_angle >= self.__ready_pose_ankle_angle:
            return True
        elif self.__right_elbow_angle >= self.__ready_pose_ankle_angle:
            self.__right_arm_status = 0
            return True
        else:
            return False

    def detect_pose_landmarks(self, frame):
        # To improve performance, optionally mark the image as not writeable to
        # pass by reference.
        frame.flags.writeable = False
        results = CountingBicepsCurl.pose.process(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
        frame.flags.writeable = True
        if results.pose_landmarks:
            CountingBicepsCurl.mp_drawing.draw_landmarks(frame, results.pose_landmarks,
                                                         CountingBicepsCurl.mp_pose.POSE_CONNECTIONS,
                                                         landmark_drawing_spec=CountingBicepsCurl.mp_drawing_styles.get_default_pose_landmarks_style())

        return results

    def update_counter(self):
        if self.__left_arm_status == 0 and self.__left_elbow_angle <= self.__lift_angle and self.__left_biceps_curl_count < self.__rep_count:
            self.__left_arm_status = 1
        elif self.__left_arm_status == 1 and self.__left_elbow_angle >= self.__ready_pose_ankle_angle and self.__left_biceps_curl_count < self.__rep_count:
            self.__left_arm_status = 0
            self.__left_biceps_curl_count += 1
            thread = threading.Thread(target=self.play_audio_for_counter_left_arm)
            thread.start()

        if self.__right_arm_status == 0 and self.__right_elbow_angle <= self.__lift_angle and self.__right_biceps_curl_count < self.__rep_count:
            self.__right_arm_status = 1
        elif self.__right_arm_status == 1 and self.__right_elbow_angle >= self.__ready_pose_ankle_angle and self.__right_biceps_curl_count < self.__rep_count:
            self.__right_arm_status = 0
            self.__right_biceps_curl_count += 1
            thread = threading.Thread(target=self.play_audio_for_counter_right_arm)
            thread.start()

        if self.__current_set_count < self.__set_count and self.__left_biceps_curl_count == self.__rep_count and self.__right_biceps_curl_count == self.__rep_count:
            self.__current_set_count += 1
            self.__left_biceps_curl_count = 0
            self.__right_biceps_curl_count = 0
        elif self.__current_set_count == self.__set_count and self.__left_biceps_curl_count == self.__rep_count and self.__right_biceps_curl_count == self.__rep_count:
            self.__workout_over = True

    def play_audio_for_counter_left_arm(self):
        try:
            playsound.playsound(CountingBicepsCurl.path_to_audios + str(self.__left_biceps_curl_count) + ".mp3")
        except:
            print("Probably the number of counter exceeds 20!")

    def play_audio_for_counter_right_arm(self):
        try:
            playsound.playsound(CountingBicepsCurl.path_to_audios + str(self.__right_biceps_curl_count) + ".mp3")
        except:
            print("Probably the number of counter exceeds 20!")

    def get_left_biceps_curl_count(self):
        return self.__left_biceps_curl_count

    def get_right_biceps_curl_count(self):
        return self.__right_biceps_curl_count

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

    def _get_vector_by_landmark_names(self, landmarks_dict, name_from, name_to):
        vec_from = np.array(landmarks_dict[name_from])
        vec_to = np.array(landmarks_dict[name_to])
        return self._get_vector(vec_from, vec_to)

    def _get_vector(self, vec_from, vec_to):
        return vec_from - vec_to

    def _get_angle_betw_two_vectors(self, vec1, vec2):
        angle_radian = math.acos((np.dot(vec1, vec2)) / (np.linalg.norm(vec1) * np.linalg.norm(vec2)))
        return int(round(math.degrees(angle_radian), 0))

    def get_left_elbow_angle(self):
        return self.__left_elbow_angle

    def get_right_elbow_angle(self):
        return self.__right_elbow_angle

    def get_left_arm_status(self):
        return self.__left_arm_status

    def get_right_arm_status(self):
        return self.__right_arm_status

    def reset_arms_status(self):
        self.__left_arm_status = 0
        self.__right_arm_status = 0

    def get_current_set_count(self):
        return self.__current_set_count

    def get_set_count(self):
        return self.__set_count

    def get_rep_count(self):
        return self.__rep_count

    def workout_is_over(self):
        return self.__workout_over

    def save_data(self, frame):
        WORKOUT_IS_OVER = "Saving data..."
        WORKOUT_IS_OVER_fs = 1
        WORKOUT_IS_OVER_th = 1
        center_opencv_text_horizontally(frame, 100, WORKOUT_IS_OVER, WORKOUT_IS_OVER_fs,
                                        WORKOUT_IS_OVER_th, cv2.FONT_HERSHEY_PLAIN)


def render_counting_biceps_curl_UI(uname, window, set_count, rep_count):
    from workout_plan_page import workout_plan_page
    window.destroy()
    cap = cv2.VideoCapture(0)
    cv2.namedWindow("Frame", cv2.WINDOW_NORMAL)
    cv2.setWindowProperty("Frame", cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)
    prevTime = 0
    curTime = 0
    workout_over_time_elapsed = 0
    # Flag
    game_started = False
    saved_game_data = False
    counting_biceps_curl_object_created = False
    failed_to_turn_on_webcam = False
    # Messages to display on screen
    # `fs` means "font scale"
    # `th` means "thickness"
    GET_INTO_READY_POSE = "Please get into ready pose"
    GET_INTO_READY_POSE_fs = 1
    GET_INTO_READY_POSE_th = 1
    FACE_CAMERA = "Face the camera"
    FACE_CAMERA_fs = 1
    FACE_CAMERA_th = 1
    USER_NOT_EXIST = "Failed to detect user!"
    USER_NOT_EXIST_fs = 1
    USER_NOT_EXIST_th = 1
    WORKOUT_IS_OVER = "Workout is over, this window will close in 5 seconds!"
    WORKOUT_IS_OVER_fs = 1
    WORKOUT_IS_OVER_th = 1

    game_record = BicepsCurlRecord()
    cur_datetime = datetime.now()
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
        if not counting_biceps_curl_object_created:
            cbc_obj = CountingBicepsCurl(set_count, rep_count)
            counting_biceps_curl_object_created = True
        else:
            if not cbc_obj.workout_is_over():
                cv2.putText(frame, "Press E to end", (frame_width - 150, 25),
                            cv2.FONT_HERSHEY_PLAIN, 1,
                            (255, 0, 255), 1)
                cv2.putText(frame, "Timer: " + str(int(cbc_obj.workout_duration)), (50, 150), cv2.FONT_HERSHEY_PLAIN, 1,
                            (255, 0, 255), 1)
                pose_results = cbc_obj.detect_pose_landmarks(frame)
                if pose_results.pose_landmarks:
                    # cv2.putText(frame, "L.Elbow angle: " + str(cbc_obj.get_left_elbow_angle()), (50, 150),
                    #             cv2.FONT_HERSHEY_PLAIN, 1,
                    #             (255, 0, 255), 1)
                    # cv2.putText(frame, "R.Elbow angle: " + str(cbc_obj.get_right_elbow_angle()), (50, 175),
                    #             cv2.FONT_HERSHEY_PLAIN, 1,
                    #             (255, 0, 255), 1)
                    if cbc_obj.userInReadyPose(pose_results):
                        cbc_obj.update_counter()
                        cv2.putText(frame, "Set : " + str(cbc_obj.get_current_set_count()) + "/" + str(cbc_obj.get_set_count()), (50, 75),
                                    cv2.FONT_HERSHEY_PLAIN, 1,
                                    (255, 0, 255), 1)
                        cv2.putText(frame, "Left Count: " + str(cbc_obj.get_left_biceps_curl_count()) + "/" + str(cbc_obj.get_rep_count()), (50, 100),
                                    cv2.FONT_HERSHEY_PLAIN, 1,
                                    (255, 0, 255), 1)
                        cv2.putText(frame, "Right Count: " + str(cbc_obj.get_right_biceps_curl_count()) + "/" + str(cbc_obj.get_rep_count()), (50, 125),
                                    cv2.FONT_HERSHEY_PLAIN, 1,
                                    (255, 0, 255), 1)
                        if cbc_obj.get_left_arm_status() == 0:
                            cv2.putText(frame, "L. Arm: DOWN", (frame_width-150, 50),
                                        cv2.FONT_HERSHEY_PLAIN, 1,
                                        (255, 0, 255), 1)
                        else:
                            cv2.putText(frame, "L. Arm: UP", (frame_width - 150, 50),
                                        cv2.FONT_HERSHEY_PLAIN, 1,
                                        (255, 0, 255), 1)
                        if cbc_obj.get_right_arm_status() == 0:
                            cv2.putText(frame, "R. Arm: DOWN", (frame_width-150, 75),
                                        cv2.FONT_HERSHEY_PLAIN, 1,
                                        (255, 0, 255), 1)
                        else:
                            cv2.putText(frame, "R. Arm: UP", (frame_width - 150, 75),
                                        cv2.FONT_HERSHEY_PLAIN, 1,
                                        (255, 0, 255), 1)

                    else:
                        # Ask the user to get into the ready pose of biceps curl
                        cbc_obj.reset_arms_status()
                        center_opencv_text_horizontally(frame, 100, GET_INTO_READY_POSE, GET_INTO_READY_POSE_fs,
                                                        GET_INTO_READY_POSE_th, cv2.FONT_HERSHEY_PLAIN)
                        center_opencv_text_horizontally(frame, 125, FACE_CAMERA, FACE_CAMERA_fs,
                                                        FACE_CAMERA_th, cv2.FONT_HERSHEY_PLAIN)
                else:
                    # Fails to detect the user
                    center_opencv_text_horizontally(frame, 50, USER_NOT_EXIST, USER_NOT_EXIST_fs,
                                                    USER_NOT_EXIST_th, cv2.FONT_HERSHEY_PLAIN)
                    cbc_obj.reset_arms_status()
            else:
                workout_over_time_elapsed += (curTime - prevTime)
                if workout_over_time_elapsed < 5:
                    center_opencv_text_horizontally(frame, 50, WORKOUT_IS_OVER, WORKOUT_IS_OVER_fs,
                                                    WORKOUT_IS_OVER_th, cv2.FONT_HERSHEY_PLAIN)
                    cbc_obj.save_data(frame)
                    if not saved_game_data:
                        print("Time taken for biceps curl in secs = ", cbc_obj.workout_duration)
                        game_record.create_new_workout_record(uname, cbc_obj.get_set_count(), cbc_obj.get_rep_count(),
                                                              cbc_obj.workout_duration, cur_datetime)
                        saved_game_data = True
                else:
                    break
        if prevTime != 0:
            cbc_obj.workout_duration += (curTime - prevTime)
        prevTime = curTime

        cv2.imshow('Frame', frame)

        if cv2.waitKey(1) & 0xFF == ord('e'):
            msg = messagebox.showinfo("Warning", "The progress in this session has been lost.")
            break
    if failed_to_turn_on_webcam:
        msg = messagebox.showinfo("Warning", "Failed to turn on the webcam.")

    cap.release()
    cv2.destroyAllWindows()
    workout_plan_page(uname, None)

