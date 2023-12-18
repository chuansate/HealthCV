import cv2
import numpy as np
"""
This script is for making the ball flying towards the player, the ball will get smaller over time
but this is by loading image, and the image might contain some unwanted elements
Try using cv2.circle() to draw it.
"""
# Load the ball image (ensure it's in the same directory as your script)
ball = cv2.imread('ball250.png')
resized_ball = ball.copy()
# Specify the initial size of the ball
scale_percent = 100  # percent of original size

cap = cv2.VideoCapture(0)
WIDTH = 300
HEIGHT = 300
PAUSE_BUTTON_SIDE_LENGTH = 45
RESUME_BUTTON_SIDE_LENGTH = 45
cv2.namedWindow("Frame", cv2.WINDOW_NORMAL)
cv2.setWindowProperty("Frame", cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)
spawning_loc_ball = (100, 100) # (x, y) in a frame during webcam stream

while True:
    width_ball = int(ball.shape[1] * scale_percent / 100)
    height_ball = int(ball.shape[0] * scale_percent / 100)
    dim_ball = (width_ball, height_ball)
    if resized_ball.shape[0] > 50 and resized_ball.shape[1] > 50:
        resized_ball = cv2.resize(resized_ball, dim_ball, interpolation=cv2.INTER_AREA)
    else:
        scale_percent = 100
        resized_ball = ball.copy()
    success, frame = cap.read()
    # Flip the frame horizontally
    frame = cv2.flip(frame, 1)
    frame[spawning_loc_ball[1]: spawning_loc_ball[1] + resized_ball.shape[0], spawning_loc_ball[0]:spawning_loc_ball[0] + resized_ball.shape[1]] = resized_ball
    cv2.imshow('Frame', frame)
    scale_percent -= 1
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break


cv2.destroyAllWindows()
