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
    FACE_CAMERA = "Face the camera"
    FACE_CAMERA_fs = 1
    FACE_CAMERA_th = 1
    path_to_audios = "audio"

    def __init__(self):
        self.__current_step_index = 1
        # when it is step 1, display an image of a person doing plank with straightened arms!
        self.__correlation_threshold = 0.95  #  this is for telling if the body is straightened
        self.__user_status = 1  # 0 means the user is in push-up DOWN, while 1 means in push-up UP
        self.__user_in_ready_pose = False
        self.__grad_UP_threshold = 5
        self.__grad_left_DOWN_threshold = 0.1
        self.__push_up_DOWN_angle_threshold = 110
        self.__left_elbow_angle = 0
        self.__push_up_UP_angle_threshold = 160
        self.__workout_over = False
        self.__step1_time_elapsed = 0
        self.__played_step1_audio = False
        self.__prev_step1_time_elapsed_int = 0

    def get_current_step_index(self):
        return self.__current_step_index

    def isReadyToPushUp(self, pose_landmarks, prevTime, curTime):
        """
        The logic to determine a user is in ready pose:
        shoulder_x > hip_x AND
        hip_x > knee_x AND
        knee_x > ankle_x AND
        shoulder_y < hip_y AND (maybe no need to care about the y-coor first becoz push-up DOWN might not obey this rule)
        hip_y < knee_y AND
        knee_y < ankle_y AND
        the correlation between the 4 points (shoulder, hip, knee, and ankle) is high enuf
        """
        self.__ready_pose_hold_elapsed += (curTime - prevTime)
        left_shoulder_x = pose_landmarks[GuidesPushUp.features[0]].x
        left_hip_x = pose_landmarks[GuidesPushUp.features[6]].x
        left_knee_x = pose_landmarks[GuidesPushUp.features[8]].x
        left_ankle_x = pose_landmarks[GuidesPushUp.features[10]].x
        left_shoulder_y = pose_landmarks[GuidesPushUp.features[0]].y
        left_ankle_y = pose_landmarks[GuidesPushUp.features[10]].y
        grad_left = (left_shoulder_y - left_ankle_y) / (left_shoulder_x - left_ankle_x)
        grad_left = abs(grad_left)

        right_shoulder_x = pose_landmarks[GuidesPushUp.features[1]].x
        right_hip_x = pose_landmarks[GuidesPushUp.features[7]].x
        right_knee_x = pose_landmarks[GuidesPushUp.features[9]].x
        right_ankle_x = pose_landmarks[GuidesPushUp.features[11]].x
        right_shoulder_y = pose_landmarks[GuidesPushUp.features[1]].y
        right_ankle_y = pose_landmarks[GuidesPushUp.features[11]].y
        grad_right = (right_shoulder_y - right_ankle_y) / (right_shoulder_x - right_ankle_x)
        grad_right = abs(grad_right)
        if left_shoulder_x < left_hip_x and left_hip_x < left_knee_x and left_knee_x < left_ankle_x and grad_left < self.__grad_left_UP_threshold:
            self.__user_in_ready_pose = True
        elif right_shoulder_x > right_hip_x and right_hip_x > right_knee_x and right_knee_x > right_ankle_x and grad_right < self.__grad_left_UP_threshold:
            self.__user_in_ready_pose = True
        else:
            self.__user_in_ready_pose = False
        return self.__user_in_ready_pose

    # Step 1: Hold the plank pose
    def step1(self, frame, pose_landmarks, curTime, prevTime):
        center_opencv_text_horizontally(frame, 70, "Get into plank pose with straightened arms!",
                                        1, 1, cv2.FONT_HERSHEY_PLAIN)
        if not self.__played_step1_audio:
            thread = threading.Thread(target=self.play_audio_step1)
            thread.start()
            self.__played_step1_audio = True

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
        right_knee_x = pose_landmarks[GuidesPushUp.features[9]].x
        right_ankle_x = pose_landmarks[GuidesPushUp.features[11]].x
        right_shoulder_y = pose_landmarks[GuidesPushUp.features[1]].y
        right_ankle_y = pose_landmarks[GuidesPushUp.features[11]].y
        grad_right = (right_shoulder_y - right_ankle_y) / (right_shoulder_x - right_ankle_x)
        grad_right = abs(grad_right)
        body_x = [left_shoulder_x, left_hip_x, left_knee_x, left_ankle_x]
        body_y = [left_shoulder_y, left_hip_y, left_knee_y, left_ankle_y]
        # check for correlation as well, to see if the body is straightened!
        # check for which point of four is not in place, then give instructions like "Raise ur hip" etc.
        corr, _ = pearsonr(body_x, body_y)
        corr = abs(corr)
        self.__step1_time_elapsed += (curTime - prevTime)
        if self.user_is_slanted(left_shoulder_x, left_hip_x, left_knee_x, left_ankle_x, grad_left):
            print("corr = ", corr)
            if corr < self.__correlation_threshold:
                if round(self.__step1_time_elapsed) != self.__prev_step1_time_elapsed_int and round(self.__step1_time_elapsed) % 3 == 0:
                    self.__prev_step1_time_elapsed_int = round(self.__step1_time_elapsed)
                    thread = threading.Thread(target=self.play_audio_step1_body_not_straight)
                    thread.start()
            # check for the placement of the arms
            elif False:
                pass
            else:
                print("Perfect posture for step 1!")
                self.__step1_time_elapsed = 0
                self.__current_step_index += 1
        else:
            center_opencv_text_horizontally(frame, 100, GuidesPushUp.GET_INTO_READY_POSE,
                                            GuidesPushUp.GET_INTO_READY_POSE_fs,
                                            GuidesPushUp.GET_INTO_READY_POSE_th, cv2.FONT_HERSHEY_PLAIN)

        # if left_shoulder_x < left_hip_x and left_hip_x < left_knee_x and left_knee_x < left_ankle_x and grad_left < self.__grad_UP_threshold:
        #     self.__user_in_ready_pose = True
        # elif right_shoulder_x > right_hip_x and right_hip_x > right_knee_x and right_knee_x > right_ankle_x and grad_right < self.__grad_UP_threshold:
        #     self.__user_in_ready_pose = True
        # else:
        #     self.__user_in_ready_pose = False

    def user_is_slanted(self, left_shoulder_x, left_hip_x, left_knee_x, left_ankle_x, grad_left):
        if left_shoulder_x < left_hip_x and left_hip_x < left_knee_x and left_knee_x < left_ankle_x and grad_left < self.__grad_UP_threshold:
            return True
        else:
            return False

    def play_audio_step1(self):
        try:
            playsound.playsound(os.path.join(GuidesPushUp.path_to_audios, "push_up_step1.mp3"))
        except:
            print("Failed to play audio for step 1!")

    def play_audio_step1_body_not_straight(self):
        try:
            playsound.playsound(os.path.join(GuidesPushUp.path_to_audios, "body_not_straight.mp3"))
        except:
            print("Failed to play audio for body not straight of step 1!")

    # Step 2: Go down while maintaining a straightened body
    def step2(self, frame, pose_landmarks):
        center_opencv_text_horizontally(frame, 70, "Go down while maintaining a straight body.",
                                        1, 1, cv2.FONT_HERSHEY_PLAIN)
        center_opencv_text_horizontally(frame, 100, "Make sure your chest is close to the ground.",
                                        1, 1, cv2.FONT_HERSHEY_PLAIN)
        # thread = threading.Thread(target=self.play_audio_step2)
        # thread.start()
        self.__current_step_index += 1


    def play_audio_step2(self):
        try:
            playsound.playsound(os.path.join(GuidesPushUp.path_to_audios, "push_up_step2.mp3"))
        except:
            print("Failed to play audio for step 2!")
    # Step 3: Go up while maintaining a straightened body
    def step3(self, frame, pose_landmarks):
        center_opencv_text_horizontally(frame, 70, "Go up while maintaining a straight body.",
                                        1, 1, cv2.FONT_HERSHEY_PLAIN)
        # thread = threading.Thread(target=self.play_audio_step3)
        # thread.start()
        self.__current_step_index += 1

    def play_audio_step3(self):
        try:
            playsound.playsound(os.path.join(GuidesPushUp.path_to_audios, "push_up_step3.mp3"))
        except:
            print("Failed to play audio for step 3!")

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


    def _get_vector_by_landmark_names(self, landmarks_dict, name_from, name_to):
        vec_from = np.array(landmarks_dict[name_from])
        vec_to = np.array(landmarks_dict[name_to])
        return self._get_vector(vec_from, vec_to)

    def _get_vector(self, vec_from, vec_to):
        return vec_from - vec_to

    def _get_angle_betw_two_vectors(self, vec1, vec2):
        angle_radian = math.acos((np.dot(vec1, vec2)) / (np.linalg.norm(vec1) * np.linalg.norm(vec2)))
        return int(round(math.degrees(angle_radian), 0))

    def get_user_status(self):
        return self.__user_status

    def set_user_status(self, status):
        self.__user_status = status

    def get_left_elbow_angle(self):
        return self.__left_elbow_angle

    def workout_is_over(self):
        return self.__workout_over

    def set_workout_is_over(self):
        self.__workout_over = True


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
                    cpu_obj.step2(frame, pose_results.pose_landmarks.landmark)
                elif cpu_obj.get_current_step_index() == 3:
                    cpu_obj.step3(frame, pose_results.pose_landmarks.landmark)
                else:
                    cpu_obj.set_workout_is_over()

                # if cpu_obj.isReadyToPushUp(pose_results.pose_landmarks.landmark, prevTime, curTime):
                #
                # else:
                #     center_opencv_text_horizontally(frame, 100, GuidesPushUp.GET_INTO_READY_POSE,
                #                                     GuidesPushUp.GET_INTO_READY_POSE_fs,
                #                                     GuidesPushUp.GET_INTO_READY_POSE_th, cv2.FONT_HERSHEY_PLAIN)
                #     center_opencv_text_horizontally(frame, 125, GuidesPushUp.FACE_CAMERA,
                #                                     GuidesPushUp.FACE_CAMERA_fs,
                #                                     GuidesPushUp.FACE_CAMERA_th, cv2.FONT_HERSHEY_PLAIN)

            else:
                # Fails to detect the user
                center_opencv_text_horizontally(frame, 50, USER_NOT_EXIST, USER_NOT_EXIST_fs,
                                                USER_NOT_EXIST_th, cv2.FONT_HERSHEY_PLAIN)
        else:
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
