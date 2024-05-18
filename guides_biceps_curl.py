import cv2
import time
from tkinter import messagebox


def guides_biceps_curl_page(uname, window):
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

