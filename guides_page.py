"""
Explain the guides for each type of exercise

"""
import tkinter as tk
from tkinter import *
from tkinter import ttk, messagebox
from PIL import Image, ImageTk
from paths_to_images import PATH_TO_BACKGROUND_IMG, PATH_TO_PUSH_UP_ICON, PATH_TO_BICEPS_CURL_ICON


def go_back(uname, window):
    from home_page import home_page
    window.destroy()
    home_page(uname)


def guides_page(uname, window):
    from guides_push_up import guides_push_up_page
    if window is not None:
        # window could be None happen when the user is from push-up/biceps curl to fitness_games_page
        window.destroy()
    WINDOW_WIDTH = 700
    WINDOW_HEIGHT = 400
    ICON_WIDTH = 30
    ICON_HEIGHT = 35
    window = tk.Tk()
    window.geometry(str(WINDOW_WIDTH) + "x" + str(WINDOW_HEIGHT))
    window.title("Guides page")
    window.resizable(False, False)
    bg_img = Image.open(PATH_TO_BACKGROUND_IMG)
    bg_img = bg_img.resize((WINDOW_WIDTH, WINDOW_HEIGHT))
    bg_img = ImageTk.PhotoImage(bg_img, master=window)
    img_label = Label(window, image=bg_img)
    img_label.place(x=0, y=0)
    title_label = tk.Label(window, text="Guides page", font=("Helvetica", 16, "bold"), bg='#f0f0f0')
    title_label.pack(pady=20)

    # Creating buttons with styling
    button_font = ("Helvetica", 12, "bold")
    button_bg = "#4CAF50"  # Green background
    button_fg = "#ffffff"  # White text
    button_active_bg = "#45a049"
    push_up_img = Image.open(PATH_TO_PUSH_UP_ICON)
    push_up_img = push_up_img.resize((ICON_WIDTH, ICON_HEIGHT))
    push_up_img = ImageTk.PhotoImage(push_up_img)
    push_up_button = tk.Button(window, text="Push-up", font=button_font, bg=button_bg, fg=button_fg,
                               activebackground=button_active_bg, image=push_up_img, compound=RIGHT,
                               command=lambda: guides_push_up_page(uname, window))
    push_up_button.pack(pady=10, ipadx=20, ipady=10)

    logout_button = tk.Button(window, text="Go back", command=lambda: go_back(uname, window))
    logout_button.place(x=WINDOW_WIDTH - 100, y=WINDOW_HEIGHT - 50)
    window.mainloop()
