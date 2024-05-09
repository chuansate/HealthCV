"""
A script to extract landmarks from the sample yoga poses, then save into CSV file.
Everytime a new sample yoga pose is added, the CSV file has to be deleted and the script must be run.
"""

import cv2
import mediapipe as mp
import numpy as np
import os
import csv

mp_drawing = mp.solutions.drawing_utils
mp_drawing_styles = mp.solutions.drawing_styles
mp_pose = mp.solutions.pose
path = "yoga_poses_imitation_game_images"

# the features exclude the facial landmarks, becoz those are not helpful at determining yoga poses
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


# For checking whether landmarks can be detected on the collected images
# sample_yoga_pose_imgs = os.listdir(path)
# with mp_pose.Pose(static_image_mode=True, model_complexity=2, enable_segmentation=True,
#                   min_detection_confidence=0.5) as pose:
#     for idx, file in enumerate(sample_yoga_pose_imgs):
#
#         image = cv2.imread(os.path.join(path, file))
#         image_height, image_width, _ = image.shape
#         # Convert the BGR image to RGB before processing.
#         results = pose.process(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))
#
#         if not results.pose_landmarks:
#             print(f"For image {file}:")
#             print("Failed to detect landmarks!")
#             continue
#
#         # Draw pose landmarks on the image.
#         mp_drawing.draw_landmarks(image, results.pose_landmarks,
#                                   landmark_drawing_spec=mp_drawing_styles.get_default_pose_landmarks_style())
#         cv2.imshow("Annotated img", image)
#         cv2.waitKey(0)
#         cv2.destroyAllWindows()


# Extract body landmarks from the sample yoga poses, then save into CSV file
sample_yoga_pose_imgs = os.listdir(path)
filename = "yoga_poses_imitation_game_images/sample_yoga_poses_landmarks.csv"
with mp_pose.Pose(static_image_mode=True, model_complexity=2, enable_segmentation=True,
                  min_detection_confidence=0.5) as pose:
    print("Detecting landmarks on sample yoga pose images:")
    sample_yoga_pose_records = []
    for idx, file in enumerate(sample_yoga_pose_imgs):
        image = cv2.imread(os.path.join(path, file))
        image_height, image_width, _ = image.shape
        # Convert the BGR image to RGB before processing.
        results = pose.process(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))

        if not results.pose_landmarks:
            print(f"Failed to detect landmarks for file {file}...")
            continue

        # extract the x-, and y-coordinates of the 22 body landmarks as features
        record = []
        landmarks_dict = {}
        for index, ft in enumerate(features):
            landmark_coordinates = results.pose_landmarks.landmark[ft]
            landmarks_dict[feature_names[index]] = [landmark_coordinates.x, landmark_coordinates.y]
        landmarks_dict = normalize_pose_landmarks(landmarks_dict)

        for normalized_coordinates in landmarks_dict.values():
            for normalized_coor in normalized_coordinates:
                record.append(normalized_coor)

        sample_yoga_pose_records.append(record)
        record = []
        # print("results = ")
        # print(results.pose_landmarks)
    #         print("Right heel")
    #         print(f'coordinates: ({str(results.pose_landmarks.landmark[mp_pose.PoseLandmark.RIGHT_HEEL].x * image_width)}, {str(results.pose_landmarks.landmark[mp_pose.PoseLandmark.RIGHT_HEEL].y * image_height)})')
    #         print(f"visibility: {str(results.pose_landmarks.landmark[mp_pose.PoseLandmark.RIGHT_HEEL].visibility)}")

    # writing to csv file
    with open(filename, 'w', newline="") as csvfile:
        csvwriter = csv.writer(csvfile)
        # writing the records
        csvwriter.writerows(sample_yoga_pose_records)

        print(f"Successfully written {str(len(sample_yoga_pose_records))} records!")
