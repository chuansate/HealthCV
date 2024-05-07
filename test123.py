import numpy as np
import cv2

x = 100
width = 900
y = 0
height = 100
background = np.zeros((255, 255, 3))
background[y:y+height, x:x+width] = (255, 0, 0)

cv2.imshow("hi", background)
cv2.waitKey(0)
