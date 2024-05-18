import cv2
import time
from tkinter import messagebox
import mediapipe as mp
cap = cv2.VideoCapture(0)
mp_pose = mp.solutions.pose
pose = mp_pose.Pose()
mp_drawing = mp.solutions.drawing_utils


def guides_push_up_page(uname, window):
    """It will fail to count, becoz teh position was initialized to None
    There is no conditional statement to handle the None case
    Hence, there is a need to detect whether the user is in ready pose of push-up!!
    """
    from guides_page import guides_page
    window.destroy()

    cap = cv2.VideoCapture(0)
    cv2.namedWindow("Guides Push-up", cv2.WINDOW_NORMAL)
    cv2.setWindowProperty("Guides Push-up", cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)
    prevTime = 0
    curTime = 0
    FONT_SCALE = 1.2
    # Flags
    failed_to_turn_on_webcam = False

    pushup_counter = 0
    position = None  # 'down' or 'up'

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
        cv2.putText(frame, "Press E to end", (frame_width - 150, 25),
                    cv2.FONT_HERSHEY_PLAIN, 1,
                    (255, 0, 255), 1)

        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        result = pose.process(rgb_frame)
        if result.pose_landmarks:
            landmarks = result.pose_landmarks.landmark

            shoulder = landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER.value]
            hip = landmarks[mp_pose.PoseLandmark.LEFT_HIP.value]

            # Calculate the vertical distance between shoulder and hip
            shoulder_y = shoulder.y
            hip_y = hip.y

            if position == 'down' and shoulder_y < hip_y:
                pushup_counter += 1
                position = 'up'
            elif position == 'up' and shoulder_y >= hip_y:
                position = 'down'

            mp_drawing.draw_landmarks(frame, result.pose_landmarks, mp_pose.POSE_CONNECTIONS)
        else:


        cv2.putText(frame, f'Push-ups: {pushup_counter}', (10, 60), cv2.FONT_HERSHEY_PLAIN, 1.2, (255, 0, 255), 1,
                    cv2.LINE_AA)
        cv2.putText(frame, f'Position: {position}', (10, 85), cv2.FONT_HERSHEY_PLAIN, 1.2, (255, 0, 255), 1,
                    cv2.LINE_AA)


        prevTime = curTime
        cv2.imshow('Guides Push-up', frame)
        if cv2.waitKey(1) & 0xFF == ord('e'):
            msg = messagebox.showinfo("Warning", "The progress in this session has been lost.")
            break
    if failed_to_turn_on_webcam:
        msg = messagebox.showinfo("Warning", "Failed to turn on the webcam.")
    cap.release()
    cv2.destroyAllWindows()
    from guides_page import guides_page
    guides_page(uname, None)
