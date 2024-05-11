import cv2
import numpy as np


class PunchObject:
    def __init__(self, button_img, coord_top_left_corner, stay_duration):
        """
        :param frame: ndarray, it is the frame of video stream
        :param button_img: ndarray, it is the image used for the button
        :param coord_top_left_corner: tuple, the coordinates of the top left corner of the button
        :param stay_duration: how long the punch object stays on the screen
        """
        if not isinstance(button_img, np.ndarray):
            raise TypeError("The image used to create the punch object must be a ndarray!")

        if type(coord_top_left_corner) != tuple:
            raise TypeError("The coordinates for the top left corner of the button must be a tuple!")

        self.width = button_img.shape[1]
        self.height = button_img.shape[0]
        self.button_img = button_img
        self.coord_top_left_corner = coord_top_left_corner
        self.total_stay_duration = stay_duration
        self.stay_duration_elapsed = 0

    def isPunched(self, index_finger_tip_x, index_finger_tip_y):
        if (self.coord_top_left_corner[0] <= index_finger_tip_x <=
            self.coord_top_left_corner[0] + self.width) and (
                self.coord_top_left_corner[1] <= index_finger_tip_y <=
                self.coord_top_left_corner[1] + self.height):
            return True
        return False

    def isExpired(self, currentTime, previousTime):
        self.stay_duration_elapsed += (currentTime - previousTime)
        if self.stay_duration_elapsed > self.total_stay_duration:
            return True
        else:
            # cv2.putText(frame, str(
            #     int(round(self.__total_stay_duration - self.__stay_duration_elapsed, 0))),
            #             self.coord_top_left_corner,
            #             cv2.FONT_HERSHEY_PLAIN, 1, (255, 0, 255), 1)
            return False


class KickObject:
    def __init__(self, button_img, coord_top_left_corner, stay_duration):
        """
        :param frame: ndarray, it is the frame of video stream
        :param button_img: ndarray, it is the image used for the button
        :param coord_top_left_corner: tuple, the coordinates of the top left corner of the button
        :param stay_duration: how long the kick object stays on the screen
        """
        if not isinstance(button_img, np.ndarray):
            raise TypeError("The image used to create the kick object must be a ndarray!")

        if type(coord_top_left_corner) != tuple:
            raise TypeError("The coordinates for the top left corner of the button must be a tuple!")

        self.width = button_img.shape[1]
        self.height = button_img.shape[0]
        self.button_img = button_img
        self.coord_top_left_corner = coord_top_left_corner
        self.total_stay_duration = stay_duration
        self.stay_duration_elapsed = 0

    def isKicked(self, foot_index_x, foot_index_y):
        if (self.coord_top_left_corner[0] <= foot_index_x <=
            self.coord_top_left_corner[0] + self.width) and (
                self.coord_top_left_corner[1] <= foot_index_y <=
                self.coord_top_left_corner[1] + self.height):
            return True
        return False

    def isExpired(self, currentTime, previousTime):
        self.stay_duration_elapsed += (currentTime - previousTime)
        if self.stay_duration_elapsed > self.total_stay_duration:
            return True
        else:
            # cv2.putText(frame, str(
            #     int(round(self.__total_stay_duration - self.__stay_duration_elapsed, 0))),
            #             self.coord_top_left_corner,
            #             cv2.FONT_HERSHEY_PLAIN, 1, (255, 0, 255), 1)
            return False