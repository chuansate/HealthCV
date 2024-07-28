"""
 The game is about generating objects with icons of foot and hand.
 The objects with foot icon means the user has to hit it using foot,
 while the objects with hand icon means the user has to hit it using hand.
"""
import random
from datetime import datetime
from tkinter import messagebox
import threading
import cv2
import mediapipe as mp
import time
import sys
from data_models import User

import playsound

from Buttons import ButtonImage
from data_models.daily_tasks import DailyTasks
from data_models.kick_and_catch_match_records import KickAndCatchMatchRecord
from data_models.burned_calories import BurnedCalories
from kick_and_catch_game_objects import *


def center_opencv_text_horizontally(frame, y, text, text_fs, text_thickness, font):
    frame_width = frame.shape[1]
    text_width = cv2.getTextSize(text, font, text_fs, text_thickness)[0][0]
    cv2.putText(frame, text, (frame_width // 2 - text_width // 2, y),
                font, text_fs,
                (255, 0, 255), text_thickness)


class KickAndCatchGame:
    mp_pose = mp.solutions.pose
    mp_drawing = mp.solutions.drawing_utils
    mp_drawing_styles = mp.solutions.drawing_styles
    pose = mp_pose.Pose(min_tracking_confidence=0.5, min_detection_confidence=0.5)
    punching_img = cv2.imread("icons/punching_smaller.png")
    kicking_img = cv2.imread("icons/kicking_smaller.png")
    path_to_audios = "./audio/"
    def __init__(self, num_objects, stay_duration):
        self.__total_game_score = 0
        self.total_game_duration = 60  # the game lasts for this long, in seconds
        self.__game_duration_elapsed = 0
        self.__game_over = False
        self.__stay_duration = stay_duration  # how long the objects stay on the screen
        self.__max_num_objects_on_frame = num_objects
        self.__current_objects_on_frame = []
        self.__num_punches = 0
        self.__num_kicks = 0
        self.calories_burned_per_min = 13
        self.XP = 10

    def get_total_game_score(self):
        return self.__total_game_score

    def count_down_game_duration(self, webcam_frame, currentTime, previousTime):
        frame_width = webcam_frame.shape[1]
        frame_height = webcam_frame.shape[0]
        self.__game_duration_elapsed += (currentTime - previousTime)
        if self.__game_duration_elapsed > self.total_game_duration:
            self.__game_over = True
        else:
            cv2.putText(webcam_frame, "Time left: " + str(
                int(round(self.total_game_duration - self.__game_duration_elapsed, 0))),
                        (frame_width // 2 - 206 // 2, 25),
                        cv2.FONT_HERSHEY_PLAIN, 1, (255, 0, 255), 1)
            webcam_frame.flags.writeable = False
            pose_results = KickAndCatchGame.pose.process(cv2.cvtColor(webcam_frame, cv2.COLOR_BGR2RGB))
            webcam_frame.flags.writeable = True
            while len(self.__current_objects_on_frame) < self.__max_num_objects_on_frame:
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
                            thread = threading.Thread(target=self.play_audio_for_breaking_rock)
                            thread.start()
                            self.__num_punches += 1
                            self.__current_objects_on_frame.remove(obj)
                            self.increase_game_score()
                            break
                        if obj.isPunched(right_index_finger_tip_x, right_index_finger_tip_y):
                            thread = threading.Thread(target=self.play_audio_for_breaking_rock)
                            thread.start()
                            self.__num_punches += 1
                            self.__current_objects_on_frame.remove(obj)
                            self.increase_game_score()
                            break
                    if isinstance(obj, KickObject):
                        if obj.isKicked(left_foot_index_x, left_foot_index_y):
                            thread = threading.Thread(target=self.play_audio_for_breaking_rock)
                            thread.start()
                            self.__num_kicks += 1
                            self.__current_objects_on_frame.remove(obj)
                            self.increase_game_score()
                            break
                        if obj.isKicked(right_foot_index_x, right_foot_index_y):
                            thread = threading.Thread(target=self.play_audio_for_breaking_rock)
                            thread.start()
                            self.__num_kicks += 1
                            self.__current_objects_on_frame.remove(obj)
                            self.increase_game_score()
                            break
            else:
                cv2.putText(webcam_frame, "Failed to detect user!",
                            (frame_width // 2 - 206 // 2, 50),
                            cv2.FONT_HERSHEY_PLAIN, 1, (255, 0, 255), 1)

    def play_audio_for_breaking_rock(self):
        try:
            playsound.playsound(KickAndCatchGame.path_to_audios + "rock_breaking.mp3")
        except:
            print("Failed to play the audio!")

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
        WORKOUT_IS_OVER = "Game over, this window will close in 5 seconds!"
        WORKOUT_IS_OVER_fs = 1
        WORKOUT_IS_OVER_th = 1
        frame_width = webcam_frame.shape[1]
        center_opencv_text_horizontally(webcam_frame, 100, WORKOUT_IS_OVER, WORKOUT_IS_OVER_fs,
                                        WORKOUT_IS_OVER_th, cv2.FONT_HERSHEY_PLAIN)
        cv2.putText(webcam_frame, "Score: " + str(self.__total_game_score),
                    (frame_width // 2 - 206 // 2, 150),
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

    def get_num_punches(self):
        return self.__num_punches

    def get_num_kicks(self):
        return self.__num_kicks


def render_kick_and_catch_game_UI(uname, window):
    window.destroy()
    cap = cv2.VideoCapture(0)
    cv2.namedWindow("Frame", cv2.WINDOW_NORMAL)
    cv2.setWindowProperty("Frame", cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)
    diff_level = "NULL"
    mpHands = mp.solutions.hands
    hands = mpHands.Hands(False)  # modify `max_num_hands`
    mpDraw = mp.solutions.drawing_utils
    prevTime = 0
    curTime = 0
    workout_over_time_elapsed = 0
    # Loading icons
    easyButtonImg = cv2.imread("icons/easy.jpg")
    easyButtonImg_WIDTH = easyButtonImg.shape[1]
    easyButtonImg_HEIGHT = easyButtonImg.shape[0]
    normalButtonImg = cv2.imread("icons/normal.jpg")
    normalButtonImg_WIDTH = normalButtonImg.shape[1]
    normalButtonImg_HEIGHT = normalButtonImg.shape[0]
    hardButtonImg = cv2.imread("icons/hard.jpg")
    hardButtonImg_WIDTH = hardButtonImg.shape[1]
    hardButtonImg_HEIGHT = hardButtonImg.shape[0]

    # Flag
    game_started = False
    game_object_created = False
    failed_to_turn_on_webcam = False
    saved_game_data = False

    user = User()
    best_record = user.get_best_record(uname, "Kick-And-Catch")
    game_record = KickAndCatchMatchRecord()
    burned_calories_table = BurnedCalories()
    dt_table = DailyTasks()
    cur_datetime = datetime.now()
    if best_record is None:
        print("Either username doesnt exist or the game doesnt exist!")
        best_record = -1
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
            easyButton = ButtonImage(frame, easyButtonImg, (frame_width // 2 - easyButtonImg_WIDTH // 2, 100), "easy_but")
            normalButton = ButtonImage(frame, normalButtonImg, (frame_width // 2 - normalButtonImg_WIDTH // 2, 200), "normal_but")
            hardButton = ButtonImage(frame, hardButtonImg, (frame_width // 2 - hardButtonImg_WIDTH // 2, 300), "hard_but")
            if results.multi_hand_landmarks:
                for handLms in results.multi_hand_landmarks:
                    # don't pass HAND_CONNECTIONS if u just want the landmarks
                    mpDraw.draw_landmarks(frame, handLms)
                    index_finger_tip_x = handLms.landmark[mpHands.HandLandmark.INDEX_FINGER_TIP].x * frame_width
                    index_finger_tip_y = handLms.landmark[mpHands.HandLandmark.INDEX_FINGER_TIP].y * frame_height

                    if easyButton.isTapped(index_finger_tip_x, index_finger_tip_y):
                        game_started = True
                        diff_level = "EASY"
                    elif normalButton.isTapped(index_finger_tip_x, index_finger_tip_y):
                        game_started = True
                        diff_level = "NORMAL"
                    elif hardButton.isTapped(index_finger_tip_x, index_finger_tip_y):
                        game_started = True
                        diff_level = "HARD"
        else:
            if not game_object_created:
                if diff_level == "EASY":
                    game_object = KickAndCatchGame(4, 8)
                elif diff_level == "NORMAL":
                    game_object = KickAndCatchGame(5, 7)
                elif diff_level == "HARD":
                    game_object = KickAndCatchGame(6, 6)
                else:
                    game_object = KickAndCatchGame(4, 8)
                game_object_created = True
            else:
                if not game_object.get_game_over():
                    cv2.putText(frame, "Press E to end", (frame_width - 150, 25),
                                cv2.FONT_HERSHEY_PLAIN, 1,
                                (255, 0, 255), 1)
                    cv2.putText(frame, "Score: " + str(game_object.get_total_game_score()), (frame_width - 150, 50),
                                cv2.FONT_HERSHEY_PLAIN, 1.2,
                                (255, 0, 255), 1)
                    cv2.putText(frame, "Best: " + str(best_record), (frame_width - 150, 75),
                                cv2.FONT_HERSHEY_PLAIN, 1.2,
                                (255, 0, 255), 1)
                    game_object.count_down_game_duration(frame, curTime, prevTime)
                else:
                    workout_over_time_elapsed += (curTime - prevTime)
                    if workout_over_time_elapsed < 5:
                        game_object.render_final_results(frame)
                        game_object.save_game_data(frame)
                        if not saved_game_data:
                            game_record.create_new_match_record(uname, game_object.get_total_game_score(), cur_datetime)
                            # add 10 XP into `users`, then write the total calories burnt
                            total_burned_calories = int(game_object.calories_burned_per_min * game_object.total_game_duration/60)
                            cur_datetime = datetime.now()
                            cur_date = datetime(cur_datetime.year, cur_datetime.month, cur_datetime.day, cur_datetime.hour, cur_datetime.minute)
                            burned_calories_table.update_burned_calories_by_date(uname, total_burned_calories, cur_date)
                            user.add_XP_to_user(uname, game_object.XP)
                            user_goal = user.search_by_uname(uname)["fitness_goal"]
                            goals_with_kick_and_catch = ["Weight Loss", "Endurance", "Flexibility"]
                            if user_goal in goals_with_kick_and_catch:
                                dt_table.update_kick_and_catch_progress(uname, cur_date, user_goal, game_object.get_total_game_score(), game_object.get_num_punches(), game_object.get_num_kicks())
                            saved_game_data = True
                    else:
                        break

        prevTime = curTime
        cv2.imshow('Frame', frame)
        if cv2.waitKey(1) & 0xFF == ord('e'):  # which key comes first then it responds faster to the user input
            msg = messagebox.showinfo("Warning", "The progress in this session has been lost.")
            break

    if failed_to_turn_on_webcam:
        msg = messagebox.showinfo("Warning", "Failed to turn on the webcam.")
    cap.release()
    cv2.destroyAllWindows()
    from fitness_games_page import fitness_games_page
    fitness_games_page(uname, None)

