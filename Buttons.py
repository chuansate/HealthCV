import numpy as np
import cv2
import cvzone


class Button:
    def __init__(self, img, coord_top_left_corner, width, height, colour, thickness, name):
        """
        :param img: ndarray, it is the frame of video stream
        :param coord_top_left_corner: tuple, the coordinates of the top left corner of the button
        :param width: int, the width of the button
        :param height: int, the height of the button
        :param colour: tuple, the colour of the button's borderline
        :param thickness: int, the thickness of the button's borderline
        """
        self.coord_top_left_corner = coord_top_left_corner
        self.width = width
        self.height = height
        self.colour = colour
        self.thickness = thickness
        self.name = name
        cv2.rectangle(img, coord_top_left_corner, (coord_top_left_corner[0] + width, coord_top_left_corner[1] + height),
                      colour, thickness)

    def isTapped(self, index_finger_tip_x, index_finger_tip_y):
        if (self.coord_top_left_corner[0] <= index_finger_tip_x <=
            self.coord_top_left_corner[0] + self.width) and (
                self.coord_top_left_corner[1] <= index_finger_tip_y <=
                self.coord_top_left_corner[1] + self.height):
            print(f"Button {self.name} is being tapped!")
            return True
        return False


class ButtonImage:
    def __init__(self, frame, button_img, coord_top_left_corner, name):
        """
        :param frame: ndarray, it is the frame of video stream
        :param button_img: ndarray, it is the image used for the button
        :param coord_top_left_corner: tuple, the coordinates of the top left corner of the button
        """
        if (not isinstance(button_img, np.ndarray)) or (not isinstance(frame, np.ndarray)):
            raise TypeError("The frame or the image used to create the button must be a ndarray!")

        if type(coord_top_left_corner) != tuple:
            raise TypeError("The coordinates for the top left corner of the button must be a tuple!")

        self.width = button_img.shape[1]
        self.height = button_img.shape[0]
        self.coord_top_left_corner = coord_top_left_corner
        # Put the overlay at the specified position
        alpha = 0  # alpha value to control the transparency of the overlay
        overlay_button_img = cv2.addWeighted(frame[coord_top_left_corner[1]: coord_top_left_corner[1]+self.height, coord_top_left_corner[0]:coord_top_left_corner[0]+self.width], alpha, button_img, 1-alpha, 0)
        frame[coord_top_left_corner[1]: coord_top_left_corner[1]+self.height, coord_top_left_corner[0]:coord_top_left_corner[0]+self.width] = overlay_button_img
        # cv2.imshow("button_img", button_img)
        # cv2.imshow("Hi", frame)
        # cv2.waitKey(0)
        self.name = name

    def isTapped(self, index_finger_tip_x, index_finger_tip_y):
        if (self.coord_top_left_corner[0] <= index_finger_tip_x <=
            self.coord_top_left_corner[0] + self.width) and (
                self.coord_top_left_corner[1] <= index_finger_tip_y <=
                self.coord_top_left_corner[1] + self.height):
            print(f"Button {self.name} is being tapped!")
            return True
        return False
