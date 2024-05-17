"""
Display leaderboard, display rules and guides before the player starts
"""
import tkinter as tk
from tkinter import *
from tkinter import ttk, messagebox
from PIL import Image, ImageTk
from paths_to_images import PATH_TO_BACKGROUND_IMG, PATH_TO_KICK_AND_CATCH_BG_IMG, PATH_TO_YOGA_IMITATION_BG_IMG


def go_back(uname, window):
    from home_page import home_page
    window.destroy()
    home_page(uname)


def fitness_games_page(uname, window):
    from kick_and_catch_game import render_kick_and_catch_game_UI
    from yoga_poses_imitation_game_opencv import render_yoga_poses_imitation_game_UI
    if window is not None:
        # window could be None happen when the user is from kick_and_catch_game/yoga_poses_imitation_game to fitness_games_page
        window.destroy()
    WINDOW_WIDTH = 700
    WINDOW_HEIGHT = 400
    ICON_WIDTH = 30
    ICON_HEIGHT = 35
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
    k_a_c_img = Image.open(PATH_TO_KICK_AND_CATCH_BG_IMG)
    k_a_c_img = k_a_c_img.resize((ICON_WIDTH, ICON_HEIGHT))
    k_a_c_img = ImageTk.PhotoImage(k_a_c_img)
    kick_catch_button = tk.Button(window, text="Kick-And-Catch", font=button_font, bg=button_bg, fg=button_fg,
                                     activebackground=button_active_bg, image=k_a_c_img, compound=RIGHT, command=lambda: render_kick_and_catch_game_UI(uname, window))
    kick_catch_button.pack(pady=10, ipadx=20, ipady=10)

    yoga_img = Image.open(PATH_TO_YOGA_IMITATION_BG_IMG)
    yoga_img = yoga_img.resize((ICON_WIDTH, ICON_HEIGHT))
    yoga_img = ImageTk.PhotoImage(yoga_img)
    yoga_imitation_button = tk.Button(window, text="Yoga Imitation", font=button_font, bg=button_bg, fg=button_fg,
                              activebackground=button_active_bg, image=yoga_img, compound=RIGHT, command=lambda: render_yoga_poses_imitation_game_UI(uname, window))
    yoga_imitation_button.pack(pady=10, ipadx=20, ipady=10)

    logout_button = tk.Button(window, text="Go back", command=lambda: go_back(uname, window))
    logout_button.place(x=WINDOW_WIDTH - 100, y=WINDOW_HEIGHT - 50)
    window.mainloop()


