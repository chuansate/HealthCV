import tkinter as tk
from tkinter import filedialog
import cv2
from PIL import Image, ImageTk
import os


class YogaPoseImitationGameWindow:
    def __init__(self, window):
        self.window = window
        self.window.title("Yoga poses imitation game")

        self.video_capture = cv2.VideoCapture(0)  # Changed camera index to 0 for default camera
        self.canvas = tk.Canvas(window, width=screen_width, height=screen_height)
        self.canvas.pack()
        self.current_image = None
        self.photo = None  # Initialize PhotoImage as None
        self.update_webcam()

    def update_webcam(self):
        success, frame = self.video_capture.read()

        if success:
            frame = cv2.flip(frame, 1)
            frame = cv2.resize(frame, (screen_width, screen_height))
            self.current_image = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
            self.photo = ImageTk.PhotoImage(image=self.current_image)
            self.canvas.create_image(0, 0, image=self.photo, anchor=tk.NW)

        self.window.after(10, self.update_webcam)


root = tk.Tk()
screen_width = root.winfo_screenwidth()
screen_height = root.winfo_screenheight()
app = YogaPoseImitationGameWindow(root)
root.state("zoomed")

root.mainloop()
