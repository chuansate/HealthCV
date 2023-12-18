import cv2
import numpy as np

# Create a black image of size 350x600
image = np.zeros((600, 350, 3), dtype="uint8")

# modifying pixels from 0 to 100 vertically, then from 200:300 horizontally
image[0:100, 200:300] = (255, 255, 255)
# Display the image
cv2.imshow('Black Image', image)
cv2.waitKey(0)
cv2.destroyAllWindows()
