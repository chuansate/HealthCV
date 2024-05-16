"""
Display leaderboard, display rules and guides before the player starts
"""
import pymongo
from pymongo import errors
import tkinter as tk
from tkinter import *
from tkinter import ttk, messagebox
from PIL import Image, ImageTk
from paths_to_images import PATH_TO_BACKGROUND_IMG

KICK_AND_CATCH_BG_IMG = ""
YOGA_IMITATION_BG_IMG = ""


def go_back(uname, window):
    from home_page import home_page
    window.destroy()
    home_page(uname)


def fitness_games_page(uname, window):
    window.destroy()
    WINDOW_WIDTH = 700
    WINDOW_HEIGHT = 400
    window = tk.Tk()
    window.geometry(str(WINDOW_WIDTH) + "x" + str(WINDOW_HEIGHT))
    window.title("Fitness games page")
    window.resizable(False, False)
    bg_img = Image.open(PATH_TO_BACKGROUND_IMG)
    bg_img = bg_img.resize((WINDOW_WIDTH, WINDOW_HEIGHT))
    bg_img = ImageTk.PhotoImage(bg_img, master=window)
    img_label = Label(window, image=bg_img)
    img_label.place(x=0, y=0)
    title_label = tk.Label(window, text="Fitness games", font=("Helvetica", 16, "bold"), bg='#f0f0f0')
    title_label.pack(pady=20)

    # Creating buttons with styling
    button_font = ("Helvetica", 12, "bold")
    button_bg = "#4CAF50"  # Green background
    button_fg = "#ffffff"  # White text
    button_active_bg = "#45a049"

    kick_catch_button = tk.Button(window, text="Kick-And-Catch", font=button_font, bg=button_bg, fg=button_fg,
                                     activebackground=button_active_bg)
    kick_catch_button.pack(pady=10, ipadx=20, ipady=10)

    yoga_imitation_button = tk.Button(window, text="Yoga Imitation", font=button_font, bg=button_bg, fg=button_fg,
                              activebackground=button_active_bg)
    yoga_imitation_button.pack(pady=10, ipadx=20, ipady=10)

    logout_button = tk.Button(window, text="Go back", command=lambda: go_back(uname, window))
    logout_button.place(x=WINDOW_WIDTH - 100, y=WINDOW_HEIGHT - 50)
    window.mainloop()
