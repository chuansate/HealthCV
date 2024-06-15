from datetime import datetime
from tkinter import messagebox
import playsound
import cv2
import mediapipe as mp
import time
import threading
import numpy as np
import math

from data_models import PushUpRecord, User, BurnedCalories
from data_models.daily_tasks import DailyTasks


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

    def __init__(self, set_count, rep_count):
        self.__set_count = set_count
        self.__rep_count = rep_count
        self.__current_set_count = 1
        self.__push_up_count = 0
        self.__user_status = 1  # 0 means the user is in push-up DOWN, while 1 means in push-up UP
        self.__user_in_ready_pose = False
        self.__ready_pose_hold_elapsed = 0
        self.__ready_pose_hold_duration_threshold = 3
        self.__grad_left_UP_threshold = 5
        self.__grad_left_DOWN_threshold = 0.1
        self.__push_up_DOWN_angle_threshold = 110
        self.__left_elbow_angle = 0
        self.__push_up_UP_angle_threshold = 150
        self.__workout_over = False
        self.workout_duration = 0  # time elapsed in seconds
        self.calories_burned_per_min = 7
        self.XP = 10

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
        if self.__left_elbow_angle <= self.__push_up_DOWN_angle_threshold and self.__user_status == 1 and self.__push_up_count < self.__rep_count:
            self.__user_status = 0
        elif self.__left_elbow_angle >= self.__push_up_UP_angle_threshold and self.__user_status == 0 and self.__push_up_count < self.__rep_count:
            self.__user_status = 1
            self.__push_up_count += 1
            thread = threading.Thread(target=self.play_audio_for_counter)
            thread.start()

        if self.__current_set_count < self.__set_count and self.__push_up_count == self.__rep_count:
            self.__current_set_count += 1
            self.__push_up_count = 0
        elif self.__current_set_count == self.__set_count and self.__push_up_count == self.__rep_count:
            self.__workout_over = True

    def play_audio_for_counter(self):
        try:
            playsound.playsound(CountingPushUp.path_to_audios + str(self.__push_up_count) + ".mp3")
        except Exception as e:
            print(e)
            print("Probably the number of counter exceeds 20!")

    def get_user_status(self):
        return self.__user_status

    def set_user_status(self, status):
        self.__user_status = status

    def get_left_elbow_angle(self):
        return self.__left_elbow_angle

    def save_data(self, frame):
        WORKOUT_IS_OVER = "Saving data..."
        WORKOUT_IS_OVER_fs = 1
        WORKOUT_IS_OVER_th = 1
        center_opencv_text_horizontally(frame, 100, WORKOUT_IS_OVER, WORKOUT_IS_OVER_fs,
                                        WORKOUT_IS_OVER_th, cv2.FONT_HERSHEY_PLAIN)

    def workout_is_over(self):
        return self.__workout_over

    def get_set_count(self):
        return self.__set_count

    def get_rep_count(self):
        return self.__rep_count

    def get_current_set_count(self):
        return self.__current_set_count


def render_counting_push_up_UI(uname, window, set_count, rep_count):
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
    saved_game_data = False

    # Messages to display on screen
    # `fs` means "font scale"
    # `th` means "thickness"
    USER_NOT_EXIST = "Failed to detect user!"
    USER_NOT_EXIST_fs = 1
    USER_NOT_EXIST_th = 1
    WORKOUT_IS_OVER = "Workout is over, this window will close in 5 seconds!"
    WORKOUT_IS_OVER_fs = 1
    WORKOUT_IS_OVER_th = 1

    game_record = PushUpRecord()
    cpu_obj = CountingPushUp(set_count, rep_count)
    cur_datetime = datetime.now()
    user = User()
    burned_calories_table = BurnedCalories()
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
            cv2.putText(frame, "Timer: " + str(int(cpu_obj.workout_duration)), (50, 100), cv2.FONT_HERSHEY_PLAIN, 1,
                        (255, 0, 255), 1)
            cv2.putText(frame, "Set : " + str(cpu_obj.get_current_set_count()) + "/" + str(
                cpu_obj.get_set_count()), (50, 50),
                        cv2.FONT_HERSHEY_PLAIN, 1,
                        (255, 0, 255), 1)
            cv2.putText(frame, "Count: " + str(cpu_obj.get_push_up_count()) + "/" + str(cpu_obj.get_rep_count()), (50, 75),
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
        else:
            workout_over_time_elapsed += (curTime - prevTime)
            if workout_over_time_elapsed < 5:
                center_opencv_text_horizontally(frame, 50, WORKOUT_IS_OVER, WORKOUT_IS_OVER_fs,
                                                WORKOUT_IS_OVER_th, cv2.FONT_HERSHEY_PLAIN)
                cpu_obj.save_data(frame)
                if not saved_game_data:
                    cpu_obj.workout_duration = int(cpu_obj.workout_duration)
                    print("Time taken for Push-up in secs = ", cpu_obj.workout_duration)
                    game_record.create_new_workout_record(uname, cpu_obj.get_set_count(), cpu_obj.get_rep_count(), cpu_obj.workout_duration, cur_datetime)
                    total_burned_calories = int(
                        cpu_obj.calories_burned_per_min * cpu_obj.workout_duration / 60)
                    cur_datetime = datetime.now()
                    print("Burned calories = ", total_burned_calories)
                    cur_date = datetime(cur_datetime.year, cur_datetime.month, cur_datetime.day, cur_datetime.hour,
                                        cur_datetime.minute)
                    burned_calories_table.update_burned_calories_by_date(uname, total_burned_calories, cur_date)
                    user.add_XP_to_user(uname, cpu_obj.XP)
                    user_goal = user.search_by_uname(uname)["fitness_goal"]
                    goals_with_pushup = ["Weight Loss", "Muscle Gain", "Endurance"]
                    if user_goal in goals_with_pushup:
                        DailyTasks().update_push_up_progress(uname, cur_date, set_count, rep_count)
                    saved_game_data = True
            else:
                break
        if prevTime != 0:
            cpu_obj.workout_duration += (curTime - prevTime)
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
