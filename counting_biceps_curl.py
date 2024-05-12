"""
implement a class. Draw landmarks on elbow and the two adjacent joints,
then compute the angle to determine whether it is a ready pose or bicep curl pose. Make a counter for it
The guidelines are from: https://www.mayoclinic.org/healthy-lifestyle/fitness/multimedia/biceps-curl/vid-20084675#:~:text=Campbell%3A%20To%20do%20a%20biceps,front%20of%20your%20upper%20arm.
"""
import random
import cv2
import mediapipe as mp
import time
import sys


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
        self.__biceps_curl_count = 0
        self.__user_in_ready_pose = False  # when the user straightens their arm

    def userInReadyPose(self):
        # pass in the body landmarks and calculate the angle at ankle
        return False

    def get_biceps_curl_count(self):
        return self.__biceps_curl_count


def render_counting_biceps_curl_UI():
    cap = cv2.VideoCapture(0)
    cv2.namedWindow("Frame", cv2.WINDOW_NORMAL)
    cv2.setWindowProperty("Frame", cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)
    prevTime = 0
    curTime = 0
    # Flag
    game_started = False
    counting_biceps_curl_object_created = False

    # Messages to display on screen
    # `fs` means "font scale"
    # `th` means "thickness"
    GET_INTO_READY_POSE = "Please get into ready pose"
    GET_INTO_READY_POSE_fs = 1
    GET_INTO_READY_POSE_th = 1

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

        if not counting_biceps_curl_object_created:
            cbc_obj = CountingBicepsCurl()
            counting_biceps_curl_object_created = True
        else:
            if cbc_obj.userInReadyPose():
                cv2.putText(frame, "Count: " + str(cbc_obj.get_biceps_curl_count()), (50, 25),
                            cv2.FONT_HERSHEY_PLAIN, 1,
                            (255, 0, 255), 1)
            else:
                # Ask the user to get into the ready pose of biceps curl
                center_opencv_text_horizontally(frame, 100, GET_INTO_READY_POSE, GET_INTO_READY_POSE_fs,
                                                GET_INTO_READY_POSE_th, cv2.FONT_HERSHEY_PLAIN)

        prevTime = curTime
        cv2.imshow('Frame', frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    cv2.destroyAllWindows()


render_counting_biceps_curl_UI()
