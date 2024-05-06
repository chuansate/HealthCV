"""
for the imitation game, use mediapipe to extract body landmarks from the sample image and users. Then, normalize the coordinates with the middle of the hip (middle of the hip is the new center).
but the distance of the user from camera might vary. If the user is close to camera, the new coordinates are larger; If the user is far away from camera, the new coordinates are smaller.
The new coordinates of the user can be broken down into x-components and y-components, they can be further normalized based on the x range and y range (refer to normalization in structured dataset).
Link to common yoga poses: https://greatist.com/move/common-yoga-poses
"""
import tkinter as tk
import cv2
from PIL import Image, ImageTk


class YogaPoseImitationGameWindow:
    def __init__(self, window):
        self.window = window
        self.window.title("Yoga poses imitation game")

        self.video_capture = cv2.VideoCapture(0)  # Changed camera index to 0 for default camera
        self.canvas = tk.Canvas(self.window, width=screen_width, height=screen_height)
        self.canvas.pack()
        self.current_image = None
        self.photo = None  # Initialize PhotoImage as None
        self.ufo_image = ImageTk.PhotoImage(file='ufo2.png')
        self.ufo_image_width = self.ufo_image.width()
        self.ufo_image_height = self.ufo_image.height()
        self.xVelocity = 10
        self.yVelocity = 10
        self.created_ufo_image = False
        self.ufo_image_id = None
        self.update_webcam()

    def update_webcam(self):
        success, frame = self.video_capture.read()

        if success:
            frame = cv2.flip(frame, 1)
            frame = cv2.resize(frame, (screen_width, screen_height))
            self.current_image = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
            self.photo = ImageTk.PhotoImage(image=self.current_image)
            self.canvas.create_image(0, 0, image=self.photo, anchor=tk.NW)
            print(list(self.canvas.find_all()))    # to retrieve ID of all objects on canvas
            if not self.created_ufo_image:
                self.ufo_image_id = self.canvas.create_image(0, 0, image=self.ufo_image, anchor=tk.NW)
                print("id of the ufo = ", self.ufo_image_id)
                self.created_ufo_image = True

            self.spawning_ufo()
            #self.canvas.delete("all")
            # print("image names = ", self.canvas.image_names())
            self.canvas.delete("all")
        self.window.after(10, self.update_webcam)

    def spawning_ufo(self):
        coordinates = self.canvas.coords(self.ufo_image_id)
        if coordinates[0] >= (screen_width - self.ufo_image_width) or coordinates[0] < 0:
            self.xVelocity = -self.xVelocity
        if coordinates[1] >= (screen_height - self.ufo_image_height) or coordinates[1] < 0:
            self.yVelocity = -self.yVelocity
        self.canvas.move(self.ufo_image_id, self.xVelocity, self.yVelocity)
        self.window.update()



root = tk.Tk()
screen_width = root.winfo_screenwidth()
screen_height = root.winfo_screenheight()
app = YogaPoseImitationGameWindow(root)
root.state("zoomed")

root.mainloop()
