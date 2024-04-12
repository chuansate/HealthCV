import mediapipe as mp
import cv2
from mediapipe.tasks import python
from mediapipe import solutions
from mediapipe.framework.formats import landmark_pb2
import numpy as np
from mediapipe.tasks.python import vision

MODEL_PATH = 'hand_landmarker.task'
MARGIN = 10  # pixels
FONT_SIZE = 1
FONT_THICKNESS = 1
HANDEDNESS_TEXT_COLOR = (88, 205, 54)  # vibrant green

#
# def draw_landmarks_on_image(rgb_image, detection_result):
#     hand_landmarks_list = detection_result.hand_landmarks
#     handedness_list = detection_result.handedness
#     annotated_image = np.copy(rgb_image)
#     # Loop through the detected hands to visualize.
#     print("len = ", len(hand_landmarks_list))
#     for idx in range(len(hand_landmarks_list)):
#         hand_landmarks = hand_landmarks_list[idx]
#         handedness = handedness_list[idx]
#         # Draw the hand landmarks.
#         hand_landmarks_proto = landmark_pb2.NormalizedLandmarkList()
#         hand_landmarks_proto.landmark.extend([
#           landmark_pb2.NormalizedLandmark(x=landmark.x, y=landmark.y, z=landmark.z) for landmark in hand_landmarks
#         ])
#         solutions.drawing_utils.draw_landmarks(
#             annotated_image,
#             hand_landmarks_proto,
#             solutions.hands.HAND_CONNECTIONS,
#             solutions.drawing_styles.get_default_hand_landmarks_style(),
#             solutions.drawing_styles.get_default_hand_connections_style()
#         )
#         # Get the top left corner of the detected hand's bounding box.
#         height, width, _ = annotated_image.shape
#         x_coordinates = [landmark.x for landmark in hand_landmarks]
#         y_coordinates = [landmark.y for landmark in hand_landmarks]
#         text_x = int(min(x_coordinates) * width)
#         text_y = int(min(y_coordinates) * height) - MARGIN
#         # Draw handedness (left or right hand) on the image.
#         cv2.putText(annotated_image, f"{handedness[0].category_name}",
#                     (text_x, text_y), cv2.FONT_HERSHEY_DUPLEX,
#                     FONT_SIZE, HANDEDNESS_TEXT_COLOR, FONT_THICKNESS, cv2.LINE_AA)
#     return annotated_image


HandLandmarker = mp.tasks.vision.HandLandmarker
HandLandmarkerOptions = mp.tasks.vision.HandLandmarkerOptions
HandLandmarkerResult = mp.tasks.vision.HandLandmarkerResult


# Create a hand landmarker instance with the live stream mode:
def draw_landmarks(detection_result: HandLandmarkerResult, rgb_image: mp.Image, timestamp_ms: int):
    # print('hand landmarker result: {}'.format(result))
    hand_landmarks_list = detection_result.hand_landmarks
    handedness_list = detection_result.handedness
    if detection_result.handedness == "Left" or detection_result.handedness == "Right":
        print("detection_result = ", detection_result)

    # Loop through the detected hands to visualize.
    for idx in range(len(hand_landmarks_list)):
        hand_landmarks = hand_landmarks_list[idx]
        handedness = handedness_list[idx]
        # Draw the hand landmarks.
        hand_landmarks_proto = landmark_pb2.NormalizedLandmarkList()

        hand_landmarks_proto.landmark.extend([
            landmark_pb2.NormalizedLandmark(x=landmark.x, y=landmark.y, z=landmark.z) for landmark in hand_landmarks
        ])

        print("Before")
        # HERE GOT PROBLEMS!! ONCE THE HAND LANDMARKS ARE DETECTED, HERE CRASHED THE ENTIRE PROGRAM!
        solutions.drawing_utils.draw_landmarks(
            rgb_image.numpy_view(),
            hand_landmarks_proto,
            solutions.hands.HAND_CONNECTIONS,
            solutions.drawing_styles.get_default_hand_landmarks_style(),
            solutions.drawing_styles.get_default_hand_connections_style()
        )
        # Get the top left corner of the detected hand's bounding box.
        height = rgb_image.height
        width = rgb_image.width
        # height, width, _ = annotated_img.shape
        x_coordinates = [landmark.x for landmark in hand_landmarks]
        y_coordinates = [landmark.y for landmark in hand_landmarks]
        text_x = int(min(x_coordinates) * width)
        text_y = int(min(y_coordinates) * height) - MARGIN
        # Draw handedness (left or right hand) on the image.
        print(handedness[0].category_name)
        print("text_x_y = ", (text_x, text_y))
        cv2.putText(rgb_image.numpy_view(), f"{handedness[0].category_name}",
                    (text_x, text_y), cv2.FONT_HERSHEY_DUPLEX,
                    FONT_SIZE, HANDEDNESS_TEXT_COLOR, FONT_THICKNESS, cv2.LINE_AA)


# Setup options
base_options = python.BaseOptions(model_asset_path=MODEL_PATH)
options = vision.HandLandmarkerOptions(
    running_mode=mp.tasks.vision.RunningMode.LIVE_STREAM,
    base_options=base_options,
    num_hands=2,
    min_hand_detection_confidence=0.3,
    min_hand_presence_confidence=0.3,
    min_tracking_confidence=0.3,
    result_callback=draw_landmarks
)
detector = vision.HandLandmarker.create_from_options(options)

cap = cv2.VideoCapture(0)
frame_timestamp_ms = 0
while True:
    # capture image
    ret, frame = cap.read()

    if ret:
        frame = cv2.flip(frame, 1)
        frame_height = frame.shape[0]
        frame_width = frame.shape[1]
        frame_SRGB = mp.Image(image_format=mp.ImageFormat.SRGB, data=frame)
        detector.detect_async(frame_SRGB, frame_timestamp_ms)

        cv2.imshow('Hand landmarks detection', frame_SRGB.numpy_view())
        frame_timestamp_ms += 1
    else:
        print("! No frame")

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# After the loop release the cap object
cap.release()

# Destroy all the windows
cv2.destroyAllWindows()
