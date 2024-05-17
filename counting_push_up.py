import cv2
import mediapipe as mp
import time
from tensorflow import keras
import tensorflow as tf
import numpy as np
mp_drawing = mp.solutions.drawing_utils
mp_drawing_styles = mp.solutions.drawing_styles
mp_pose = mp.solutions.pose
pushup_up_down_classifier = keras.models.load_model("push_up_classification_100_test_acc.keras")
pushup_ready_pose_classifier = keras.models.load_model("push_up_ready_poses_classification_v2.keras")
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


def normalize_pose_landmarks(pose_landmarks_dict):
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


def isReadyToPushUp(frame_features):
    y_pred = pushup_ready_pose_classifier.predict(tf.expand_dims(frame_features, axis=0), verbose=0)
    y_pred = 1 if y_pred[0] >= 0.5 else 0
    return y_pred


count_pushup = 0
current_pushup_state = 1
readyToPushUp = 0

cap = cv2.VideoCapture(0)
cv2.namedWindow("Counting push-up", cv2.WINDOW_NORMAL)
cv2.setWindowProperty("Counting push-up", cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)
prevTime = 0
curTime = 0
TOTAL_COUNT_PUSHUP = 0
FONT_SCALE = 1.2
ready_time_elapsed = 0
failed_to_turn_on_webcam = False
with mp_pose.Pose(min_detection_confidence=0.5, min_tracking_confidence=0.5) as pose:
    while cap.isOpened():
        success, frame = cap.read()
        if not success:
            print("Failed to read frames from webcam, please try again!")
            failed_to_turn_on_webcam = True
            break

        # Flip the frame horizontally
        frame = cv2.flip(frame, 1)
        frame_height = frame.shape[0]
        frame_width = frame.shape[1]
        curTime = time.time()
        fps = 1 / (curTime - prevTime)

        cv2.putText(frame, str(int(fps)) + " FPS", (10, 70), cv2.FONT_HERSHEY_PLAIN, 1.2, (255, 0, 255), 1)
        # To improve performance, optionally mark the image as not writeable to
        # pass by reference.
        frame.flags.writeable = False
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = pose.process(frame)

        # Draw the pose annotation on the image.
        frame.flags.writeable = True
        frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)

        if results.pose_landmarks:
            # if pose landmarks are detected
            # extract the x-, y-, and z-coordinates of the 22 body landmarks as features from the frame
            frame_features = []
            frame_features_dict = {}
            mp_drawing.draw_landmarks(frame, results.pose_landmarks, mp_pose.POSE_CONNECTIONS,
                                      landmark_drawing_spec=mp_drawing_styles.get_default_pose_landmarks_style())
            for index, ft in enumerate(features):
                landmark_coordinates = results.pose_landmarks.landmark[ft]
                frame_features_dict[feature_names[index]] = [landmark_coordinates.x, landmark_coordinates.y,
                                                             landmark_coordinates.z]
            frame_features_dict = normalize_pose_landmarks(frame_features_dict)

            for normalized_coordinates in frame_features_dict.values():
                for normalized_coor in normalized_coordinates:
                    frame_features.append(normalized_coor)

            frame_features = np.array(frame_features)
            predicted_pose_text_position = (10, 150)
            readyToPushUp = isReadyToPushUp(frame_features)

            # while readyToPushUp:
            #     # The user has to hold the ready-pose for 3 seconds, then the counter starts
            #     # start counting down 3...2...1... then the counting of repetition starts
            #     # predict it is a UP or DOWN
            #
            #     y_pred = pushup_up_down_classifier.predict(tf.expand_dims(frame_features, axis=0), verbose=0)
            #     if y_pred == 1:  # push-up UP
            #         if y_pred != current_pushup_state:
            #             count_pushup += 1
            #             current_pushup_state = y_pred
            #
            #     else:
            #         pass
            if readyToPushUp == 1:
                ready_time_elapsed += (curTime - prevTime)
                if ready_time_elapsed >= 3:
                    cv2.putText(frame, "Pushup Count: 0", predicted_pose_text_position, cv2.FONT_HERSHEY_PLAIN,
                                FONT_SCALE, (255, 0, 255),
                                1)
                    cv2.putText(frame, "Start!",
                                (predicted_pose_text_position[0], predicted_pose_text_position[1] + 30),
                                cv2.FONT_HERSHEY_PLAIN,
                                FONT_SCALE, (255, 0, 255),
                                1)
                else:
                    cv2.putText(frame, "Push-up Ready Pose", predicted_pose_text_position, cv2.FONT_HERSHEY_PLAIN,
                                FONT_SCALE, (255, 0, 255),
                                1)
                    cv2.putText(frame, "Counting down: " + str(3 - int(ready_time_elapsed)),
                                (predicted_pose_text_position[0], predicted_pose_text_position[1] + 30),
                                cv2.FONT_HERSHEY_PLAIN,
                                FONT_SCALE, (255, 0, 255),
                                1)

            else:
                ready_time_elapsed = 0
                cv2.putText(frame, "Push-up Non-Ready Pose", predicted_pose_text_position, cv2.FONT_HERSHEY_PLAIN, FONT_SCALE,
                            (255, 0, 255), 1)
            cv2.imshow('Counting push-up', frame)
        else:
            cv2.putText(frame, "No person detected!", predicted_pose_text_position, cv2.FONT_HERSHEY_PLAIN,
                        FONT_SCALE,
                        (255, 0, 255), 1)
            cv2.imshow('Counting push-up', frame)
        prevTime = curTime
        if cv2.waitKey(10) & 0xFF == ord('q'):
            break
cap.release()
cv2.destroyAllWindows()