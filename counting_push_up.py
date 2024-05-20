from tkinter import messagebox
import playsound
import cv2
import mediapipe as mp
import time
import threading
import numpy as np
import math


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
    path_to_audios = "./audio/"

    def __init__(self):
        self.__push_up_count = 0
        self.__user_status = 1  # 0 means the user is in push-up DOWN, while 1 means in push-up UP
        self.__user_in_ready_pose = False
        self.__ready_pose_hold_elapsed = 0
        self.__ready_pose_hold_duration_threshold = 3
        self.__grad_left_UP_threshold = 5
        self.__grad_left_DOWN_threshold = 0.1
        self.__push_up_DOWN_angle_threshold = 110
        self.__left_elbow_angle = 0
        self.__push_up_UP_angle_threshold = 160

    # OLD version, this method only works if the webcam is directly seeing the side of the user
    # def isReadyToPushUp(self, pose_landmarks, prevTime, curTime, W, H):
    #     """
    #     The logic to determine a user is in ready pose:
    #     shoulder_x > hip_x AND
    #     hip_x > knee_x AND
    #     knee_x > ankle_x AND
    #     shoulder_y < hip_y AND (maybe no need to care about the y-coor first becoz push-up DOWN might not obey this rule)
    #     hip_y < knee_y AND
    #     knee_y < ankle_y AND
    #     the correlation between the 4 points (shoulder, hip, knee, and ankle) is high enuf
    #     """
    #     # print(curTime, prevTime)
    #     self.__ready_pose_hold_elapsed += (curTime - prevTime)
    #     # print("elapsed = ", self.__ready_pose_hold_elapsed)
    #     # Since the frame has been flipped initially, so to detect the left shoulder, we have to extract the right shoulder
    #     left_shoulder_x = pose_landmarks[CountingPushUp.features[0]].x * W
    #     left_hip_x = pose_landmarks[CountingPushUp.features[6]].x * W
    #     left_knee_x = pose_landmarks[CountingPushUp.features[8]].x * W
    #     left_ankle_x = pose_landmarks[CountingPushUp.features[10]].x * W
    #     left_shoulder_y = pose_landmarks[CountingPushUp.features[0]].y * H
    #     left_hip_y = pose_landmarks[CountingPushUp.features[6]].y * H
    #     left_knee_y = pose_landmarks[CountingPushUp.features[8]].y * H
    #     left_ankle_y = pose_landmarks[CountingPushUp.features[10]].y * H
    #     grad_left = (left_shoulder_y - left_ankle_y) / (left_shoulder_x - left_ankle_x)
    #     grad_left = abs(grad_left)
    #
    #     if left_shoulder_x > left_hip_x and left_hip_x > left_knee_x and left_knee_x > left_ankle_x and grad_left < self.__grad_left_UP_threshold:
    #         self.__user_in_ready_pose = True
    #         return True
    #     else:
    #         self.__user_in_ready_pose = False
    #         return False

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
        # print("elapsed = ", self.__ready_pose_hold_elapsed)
        left_shoulder_x = pose_landmarks[CountingPushUp.features[0]].x
        left_hip_x = pose_landmarks[CountingPushUp.features[6]].x
        left_knee_x = pose_landmarks[CountingPushUp.features[8]].x
        left_ankle_x = pose_landmarks[CountingPushUp.features[10]].x
        left_shoulder_y = pose_landmarks[CountingPushUp.features[0]].y
        left_ankle_y = pose_landmarks[CountingPushUp.features[10]].y
        grad_left = (left_shoulder_y - left_ankle_y) / (left_shoulder_x - left_ankle_x)
        grad_left = abs(grad_left)

        right_shoulder_x = pose_landmarks[CountingPushUp.features[1]].x
        right_hip_x = pose_landmarks[CountingPushUp.features[7]].x
        right_knee_x = pose_landmarks[CountingPushUp.features[9]].x
        right_ankle_x = pose_landmarks[CountingPushUp.features[11]].x
        right_shoulder_y = pose_landmarks[CountingPushUp.features[1]].y
        right_ankle_y = pose_landmarks[CountingPushUp.features[11]].y
        grad_right = (right_shoulder_y - right_ankle_y) / (right_shoulder_x - right_ankle_x)
        grad_right = abs(grad_right)
        if left_shoulder_x < left_hip_x and left_hip_x < left_knee_x and left_knee_x < left_ankle_x and grad_left < self.__grad_left_UP_threshold:
            self.__user_in_ready_pose = True
        elif right_shoulder_x > right_hip_x and right_hip_x > right_knee_x and right_knee_x > right_ankle_x and grad_right < self.__grad_left_UP_threshold:
            self.__user_in_ready_pose = True
        else:
            self.__user_in_ready_pose = False
        return self.__user_in_ready_pose

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
        print("RESET USER STATUS TO UP!")
        self.__user_status = 1

    def get_push_up_count(self):
        return self.__push_up_count

    def _get_vector_by_landmark_names(self, landmarks_dict, name_from, name_to):
        vec_from = np.array(landmarks_dict[name_from])
        vec_to = np.array(landmarks_dict[name_to])
        return self._get_vector(vec_from, vec_to)

    def _get_vector(self, vec_from, vec_to):
        return vec_from - vec_to

    def _get_angle_betw_two_vectors(self, vec1, vec2):
        angle_radian = math.acos((np.dot(vec1, vec2)) / (np.linalg.norm(vec1) * np.linalg.norm(vec2)))
        return int(round(math.degrees(angle_radian), 0))

    # OLD VERSION: this only works when the webcam is facing the user
    # def update_counter(self, pose_landmarks, W, H):
    #     left_shoulder_x = pose_landmarks[CountingPushUp.features[0]].x * W
    #     left_hip_x = pose_landmarks[CountingPushUp.features[6]].x * W
    #     left_knee_x = pose_landmarks[CountingPushUp.features[8]].x * W
    #     left_ankle_x = pose_landmarks[CountingPushUp.features[10]].x * W
    #     left_shoulder_y = pose_landmarks[CountingPushUp.features[0]].y * H
    #     left_hip_y = pose_landmarks[CountingPushUp.features[6]].y * H
    #     left_knee_y = pose_landmarks[CountingPushUp.features[8]].y * H
    #     left_ankle_y = pose_landmarks[CountingPushUp.features[10]].y * H
    #     grad_left = (left_shoulder_y - left_ankle_y) / (left_shoulder_x - left_ankle_x)
    #     print("grad_left when push-up UP = ", grad_left)
    #     grad_left = abs(grad_left)
    #
    #     if self.__user_status == 1 and left_shoulder_x > left_hip_x and left_hip_x > left_knee_x and left_knee_x > left_ankle_x and grad_left < self.__grad_left_DOWN_threshold:
    #         self.__user_status = 0
    #
    #     elif self.__user_status == 0 and left_shoulder_x > left_hip_x and left_hip_x > left_knee_x and left_knee_x > left_ankle_x and grad_left < self.__grad_left_UP_threshold:
    #         self.__user_status = 1  # push-up UP
    #         self.__push_up_count += 1

    def update_counter(self, pose_landmarks):
        # pass in the body landmarks and calculate the angle at ankle
        # keyword: calculate the angle betw 2 vectors
        # extract the x-, and y-coordinates of the 8 body landmarks as features
        landmarks_dict = {}
        for index, ft in enumerate(CountingPushUp.features):
            landmark_coordinates = pose_landmarks[ft]
            landmarks_dict[CountingPushUp.features_names[index]] = [landmark_coordinates.x, landmark_coordinates.y]

        left_vec_elbow_to_shoulder = self._get_vector_by_landmark_names(landmarks_dict, "LEFT_ELBOW", "LEFT_SHOULDER")
        left_vec_elbow_to_wrist = self._get_vector_by_landmark_names(landmarks_dict, "LEFT_ELBOW", "LEFT_WRIST")
        self.__left_elbow_angle = self._get_angle_betw_two_vectors(left_vec_elbow_to_shoulder, left_vec_elbow_to_wrist)
        if self.__left_elbow_angle <= self.__push_up_DOWN_angle_threshold and self.__user_status == 1:
            self.__user_status = 0
        elif self.__left_elbow_angle >= self.__push_up_UP_angle_threshold and self.__user_status == 0:
            self.__user_status = 1
            self.__push_up_count += 1
            thread = threading.Thread(target=self.play_audio_for_counter)
            thread.start()

    def play_audio_for_counter(self):
        try:
            playsound.playsound(CountingPushUp.path_to_audios + str(self.__push_up_count) + ".mp3")
        except:
            print("Probably the number of counter exceeds 20!")

    def get_user_status(self):
        return self.__user_status

    def set_user_status(self, status):
        self.__user_status = status

    def get_left_elbow_angle(self):
        return self.__left_elbow_angle


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

    # Messages to display on screen
    # `fs` means "font scale"
    # `th` means "thickness"
    USER_NOT_EXIST = "Failed to detect user!"
    USER_NOT_EXIST_fs = 1
    USER_NOT_EXIST_th = 1

    cpu_obj = CountingPushUp()
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
        cv2.putText(frame, "Press E to end", (frame_width - 150, 25),
                    cv2.FONT_HERSHEY_PLAIN, 1,
                    (255, 0, 255), 1)
        cv2.putText(frame, "Count: " + str(cpu_obj.get_push_up_count()), (50, 75),
                    cv2.FONT_HERSHEY_PLAIN, 1,
                    (255, 0, 255), 1)
        if pose_results.pose_landmarks:
            if cpu_obj.isReadyToPushUp(pose_results.pose_landmarks.landmark, prevTime, curTime):
                if cpu_obj.get_ready_pose_hold_elapsed() >= cpu_obj.get_ready_pose_hold_duration_threshold():
                    # cpu_obj.set_user_status(1)  # Set it to push-up UP
                    cpu_obj.update_counter(pose_results.pose_landmarks.landmark)
                else:
                    center_opencv_text_horizontally(frame, 70, "Hold this pose for " + str(
                        int(round(cpu_obj.get_ready_pose_hold_duration_threshold() - cpu_obj.get_ready_pose_hold_elapsed(), 0))),
                                                    1, 1, cv2.FONT_HERSHEY_PLAIN)
                cv2.putText(frame, "L. elbow deg: " + str(cpu_obj.get_left_elbow_angle()), (frame_width - 150, 100),
                            cv2.FONT_HERSHEY_PLAIN, 1,
                            (255, 0, 255), 1)
                if cpu_obj.get_user_status() == 0:
                    cv2.putText(frame, "Push-up DOWN", (frame_width-150, 50),
                                cv2.FONT_HERSHEY_PLAIN, 1,
                                (255, 0, 255), 1)
                else:
                    cv2.putText(frame, "Push-up UP", (frame_width - 150, 50),
                                cv2.FONT_HERSHEY_PLAIN, 1,
                                (255, 0, 255), 1)
            else:
                # cpu_obj.reset_ready_pose_hold_elapsed()
                # cpu_obj.reset_user_status()
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
            # cpu_obj.reset_user_status()
        cv2.putText(frame, str(int(fps)) + " FPS", (10, 40), cv2.FONT_HERSHEY_PLAIN, 1.2, (255, 0, 255), 1)
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
