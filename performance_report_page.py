"""
Performance about agility, flexibility, and other health metrics
Visualize training volume over time
Visualize game performance over time
"""
import tkinter as tk
from tkinter import *
from PIL import Image, ImageTk
from paths_to_images import PATH_TO_BACKGROUND_IMG


def go_back(uname, window):
    from home_page import home_page
    window.destroy()
    home_page(uname)


def performance_report_page(uname, window):
    if window is not None:
        # window could be None happen when the user is from push-up/biceps curl to fitness_games_page
        window.destroy()
    WINDOW_WIDTH = 700
    WINDOW_HEIGHT = 400
    ICON_WIDTH = 30
    ICON_HEIGHT = 35
    window = tk.Tk()
    window.geometry(str(WINDOW_WIDTH) + "x" + str(WINDOW_HEIGHT))
    window.title("Performance report page")
    window.resizable(False, False)
    bg_img = Image.open(PATH_TO_BACKGROUND_IMG)
    bg_img = bg_img.resize((WINDOW_WIDTH, WINDOW_HEIGHT))
    bg_img = ImageTk.PhotoImage(bg_img, master=window)
    img_label = Label(window, image=bg_img)
    img_label.place(x=0, y=0)
    title_label = tk.Label(window, text="Performance report page", font=("Helvetica", 16, "bold"), bg='#f0f0f0')
    title_label.pack(pady=20)

    goback_button = tk.Button(window, text="Go back", command=lambda: go_back(uname, window))
    goback_button.place(x=WINDOW_WIDTH - 100, y=WINDOW_HEIGHT - 50)
    window.mainloop()