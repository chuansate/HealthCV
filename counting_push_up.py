from tkinter import messagebox

import cv2
import mediapipe as mp
import time
from tensorflow import keras
import tensorflow as tf
import numpy as np


def center_opencv_text_horizontally(frame, y, text, text_fs, text_thickness, font):
    frame_width = frame.shape[1]
    text_width = cv2.getTextSize(text, font, text_fs, text_thickness)[0][0]
    cv2.putText(frame, text, (frame_width // 2 - text_width // 2, y),
                font, text_fs,
                (255, 0, 255), text_thickness)


class CountingPushUp:
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

    def __init__(self):
        self.__push_up_count = 0
        self.__user_status = 0  # 0 means the user is in push-up DOWN, while 1 means in push-up UP
        self.__user_in_ready_pose = False
        self.__ready_pose_hold_elapsed = 0
        self.__ready_pose_hold_duration_threshold = 3

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

    def isReadyToPushUp(self, pose_landmarks, prevTime, curTime, frame):
        """
        The logic to determine a user is in ready pose:
        shoulder_x > hip_x AND
        hip_x > knee_x AND
        knee_x > ankle_x AND
        shoulder_y < hip_y AND (maybe no need to care about the y-coor first becoz push-up DOWN might not obey this rule)
        hip_y < knee_y AND
        knee_y < ankle_y AND
        the correlation between the 3 points (shoulder, hip, and knee) is high enuf
        """
        prev_user_in_ready_pose = self.__user_in_ready_pose
        # print(curTime, prevTime)
        self.__ready_pose_hold_elapsed += (curTime - prevTime)
        # print("elapsed = ", self.__ready_pose_hold_elapsed)
        if self.__user_in_ready_pose:
            return True
        else:
            return False

    def get_ready_pose_hold_elapsed(self):
        return self.__ready_pose_hold_elapsed

    def get_ready_pose_hold_duration_threshold(self):
        return self.__ready_pose_hold_duration_threshold

    def detect_pose_landmarks(self, frame):
        # To improve performance, optionally mark the image as not writeable to
        # pass by reference.
        frame.flags.writeable = False
        results = CountingPushUp.pose.process(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
        frame.flags.writeable = True
        if results.pose_landmarks:
            CountingPushUp.mp_drawing.draw_landmarks(frame, results.pose_landmarks,
                                                         CountingPushUp.mp_pose.POSE_CONNECTIONS,
                                                         landmark_drawing_spec=CountingPushUp.mp_drawing_styles.get_default_pose_landmarks_style())

        return results

    def reset_ready_pose_hold_elapsed(self):
        self.__ready_pose_hold_elapsed = 0

    def reset_user_status(self):
        self.__user_status = 0

    def get_push_up_count(self):
        return self.__push_up_count

    def update_counter(self, frame_features):
        # if self.__user_status == 0 and y_pred == 1:
        #     self.__user_status = y_pred
        #     self.__push_up_count += 1
        # elif self.__user_status == 1 and y_pred == 0:
        #     self.__user_status = y_pred

    def get_user_status(self):
        return self.__user_status

    def set_user_status(self, status):
        self.__user_status = status


def render_counting_push_up_UI(uname, window):
    window.destroy()
    cap = cv2.VideoCapture(0)
    cv2.namedWindow("Counting push-up", cv2.WINDOW_NORMAL)
    cv2.setWindowProperty("Counting push-up", cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)
    prevTime = 0
    curTime = 0
    FONT_SCALE = 1.2
    # Flags
    failed_to_turn_on_webcam = False
    counting_push_up_object_created = False

    # Messages to display on screen
    # `fs` means "font scale"
    # `th` means "thickness"
    USER_NOT_EXIST = "Failed to detect user!"
    USER_NOT_EXIST_fs = 1
    USER_NOT_EXIST_th = 1
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

        cv2.putText(frame, str(int(fps)) + " FPS", (10, 40), cv2.FONT_HERSHEY_PLAIN, 1.2, (255, 0, 255), 1)

        if not counting_push_up_object_created:
            cpu_obj = CountingPushUp()
            counting_push_up_object_created = True
        else:
            cv2.putText(frame, "Press E to end", (frame_width - 150, 25),
                        cv2.FONT_HERSHEY_PLAIN, 1,
                        (255, 0, 255), 1)
            pose_results = cpu_obj.detect_pose_landmarks(frame)
            cv2.putText(frame, "Count: " + str(cpu_obj.get_push_up_count()), (50, 75),
                        cv2.FONT_HERSHEY_PLAIN, 1,
                        (255, 0, 255), 1)
            if pose_results.pose_landmarks:
                if cpu_obj.isReadyToPushUp(pose_results.pose_landmarks.landmark, prevTime, curTime, frame):
                    if cpu_obj.get_ready_pose_hold_elapsed() >= cpu_obj.get_ready_pose_hold_duration_threshold():
                        cpu_obj.set_user_status(1)  # Set it to push-up UP
                        cpu_obj.update_counter(frame_features)
                    else:
                        center_opencv_text_horizontally(frame, 70, "Hold this pose for " + str(
                            int(round(cpu_obj.get_ready_pose_hold_duration_threshold() - cpu_obj.get_ready_pose_hold_elapsed(), 0))),
                                                        1, 1, cv2.FONT_HERSHEY_PLAIN)

                    if cpu_obj.get_user_status() == 0:
                        cv2.putText(frame, "Push-up DOWN", (frame_width-150, 50),
                                    cv2.FONT_HERSHEY_PLAIN, 1,
                                    (255, 0, 255), 1)
                    else:
                        cv2.putText(frame, "Push-up UP", (frame_width - 150, 50),
                                    cv2.FONT_HERSHEY_PLAIN, 1,
                                    (255, 0, 255), 1)
                else:
                    cpu_obj.reset_ready_pose_hold_elapsed()
                    cpu_obj.reset_user_status()
                    center_opencv_text_horizontally(frame, 100, CountingPushUp.GET_INTO_READY_POSE,
                                                    CountingPushUp.GET_INTO_READY_POSE_fs,
                                                    CountingPushUp.GET_INTO_READY_POSE_th, cv2.FONT_HERSHEY_PLAIN)
                    center_opencv_text_horizontally(frame, 125, CountingPushUp.FACE_CAMERA,
                                                    CountingPushUp.FACE_CAMERA_fs,
                                                    CountingPushUp.FACE_CAMERA_th, cv2.FONT_HERSHEY_PLAIN)

            else:
                # Fails to detect the user
                center_opencv_text_horizontally(frame, 50, USER_NOT_EXIST, USER_NOT_EXIST_fs,
                                                USER_NOT_EXIST_th, cv2.FONT_HERSHEY_PLAIN)
                cpu_obj.reset_user_status()

        prevTime = curTime

        cv2.imshow('Counting push-up', frame)

        if cv2.waitKey(1) & 0xFF == ord('e'):
            msg = messagebox.showinfo("Warning", "The progress in this session has been lost.")
            break

    if failed_to_turn_on_webcam:
        msg = messagebox.showinfo("Warning", "Failed to turn on the webcam.")
    cap.release()
    cv2.destroyAllWindows()
    from workout_plan_page import workout_plan_page
    workout_plan_page(uname, None)

        # OLD LOGIC:
        # if results.pose_landmarks:
        #     # if pose landmarks are detected
        #     # extract the x-, y-, and z-coordinates of the 22 body landmarks as features from the frame
        #     frame_features = []
        #     frame_features_dict = {}
        #     mp_drawing.draw_landmarks(frame, results.pose_landmarks, mp_pose.POSE_CONNECTIONS,
        #                               landmark_drawing_spec=mp_drawing_styles.get_default_pose_landmarks_style())
        #     for index, ft in enumerate(features):
        #         landmark_coordinates = results.pose_landmarks.landmark[ft]
        #         frame_features_dict[feature_names[index]] = [landmark_coordinates.x, landmark_coordinates.y,
        #                                                      landmark_coordinates.z]
        #     frame_features_dict = normalize_pose_landmarks(frame_features_dict)
        #
        #     for normalized_coordinates in frame_features_dict.values():
        #         for normalized_coor in normalized_coordinates:
        #             frame_features.append(normalized_coor)
        #
        #     frame_features = np.array(frame_features)
        #     predicted_pose_text_position = (10, 150)
        #     readyToPushUp = isReadyToPushUp(frame_features)
        #
        #     # while readyToPushUp:
        #     #     # The user has to hold the ready-pose for 3 seconds, then the counter starts
        #     #     # start counting down 3...2...1... then the counting of repetition starts
        #     #     # predict it is a UP or DOWN
        #     #
        #     #     y_pred = pushup_up_down_classifier.predict(tf.expand_dims(frame_features, axis=0), verbose=0)
        #     #     if y_pred == 1:  # push-up UP
        #     #         if y_pred != current_pushup_state:
        #     #             count_pushup += 1
        #     #             current_pushup_state = y_pred
        #     #
        #     #     else:
        #     #         pass
        #     if readyToPushUp == 1:
        #         ready_time_elapsed += (curTime - prevTime)
        #         if ready_time_elapsed >= 3:
        #             cv2.putText(frame, "Pushup Count: 0", predicted_pose_text_position, cv2.FONT_HERSHEY_PLAIN,
        #                         FONT_SCALE, (255, 0, 255),
        #                         1)
        #             cv2.putText(frame, "Start!",
        #                         (predicted_pose_text_position[0], predicted_pose_text_position[1] + 30),
        #                         cv2.FONT_HERSHEY_PLAIN,
        #                         FONT_SCALE, (255, 0, 255),
        #                         1)
        #         else:
        #             cv2.putText(frame, "Push-up Ready Pose", predicted_pose_text_position, cv2.FONT_HERSHEY_PLAIN,
        #                         FONT_SCALE, (255, 0, 255),
        #                         1)
        #             cv2.putText(frame, "Counting down: " + str(3 - int(ready_time_elapsed)),
        #                         (predicted_pose_text_position[0], predicted_pose_text_position[1] + 30),
        #                         cv2.FONT_HERSHEY_PLAIN,
        #                         FONT_SCALE, (255, 0, 255),
        #                         1)
        #
        #     else:
        #         ready_time_elapsed = 0
        #         cv2.putText(frame, "Push-up Non-Ready Pose", predicted_pose_text_position, cv2.FONT_HERSHEY_PLAIN, FONT_SCALE,
        #                     (255, 0, 255), 1)
        #     cv2.imshow('Counting push-up', frame)
        # else:
        #     cv2.putText(frame, "No person detected!", predicted_pose_text_position, cv2.FONT_HERSHEY_PLAIN,
        #                 FONT_SCALE,
        #                 (255, 0, 255), 1)
        #     cv2.imshow('Counting push-up', frame)
        # prevTime = curTime
        # if cv2.waitKey(10) & 0xFF == ord('q'):
        #     break
