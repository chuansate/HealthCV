import tkinter as tk
from tkinter import *
from tkinter import ttk, messagebox


def go_back(uname, window):
    from fitness_games_page import fitness_games_page
    window.destroy()
    fitness_games_page(uname, None)


def leaderboard_page(uname, window):
    if window is not None:
        # window could be None happen when the user is from kick_and_catch_game/yoga_poses_imitation_game to fitness_games_page
        window.destroy()
    WINDOW_WIDTH = 700
    WINDOW_HEIGHT = 400
    ICON_WIDTH = 30
    ICON_HEIGHT = 35
    window = tk.Tk()
    window.geometry(str(WINDOW_WIDTH) + "x" + str(WINDOW_HEIGHT))
    window.title("Leaderboard page")

    goback_button = tk.Button(window, text="Go back", command=lambda: go_back(uname, window))
    goback_button.place(x=WINDOW_WIDTH - 100, y=WINDOW_HEIGHT - 50)

    window.mainloop()