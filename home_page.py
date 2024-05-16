import tkinter as tk
from tkinter import *
from PIL import Image, ImageTk
from paths_to_images import PATH_TO_BACKGROUND_IMG


def logout(window):
    from main import login_page
    window.destroy()
    login_page()


def home_page(uname):
    from fitness_games_page import fitness_games_page
    from guides_page import guides_page
    from workout_plan_page import workout_plan_page
    WINDOW_WIDTH = 700
    WINDOW_HEIGHT = 400
    window = tk.Tk()
    window.geometry(str(WINDOW_WIDTH) + "x" + str(WINDOW_HEIGHT))
    window.title("Home Page")
    window.resizable(False, False)
    bg_img = Image.open(PATH_TO_BACKGROUND_IMG)
    bg_img = bg_img.resize((WINDOW_WIDTH, WINDOW_HEIGHT))
    bg_img = ImageTk.PhotoImage(bg_img, master=window)
    img_label = Label(window, image=bg_img)
    img_label.place(x=0, y=0)
    # Three buttons: Fitness games, Guides, Workout plan (setting sets and reps, then record the data on everyday)
    # Adding a title label
    title_label = tk.Label(window, text="Welcome back, " + uname + "!", font=("Helvetica", 16, "bold"), bg='#f0f0f0')
    title_label.pack(pady=20)

    # Creating buttons with styling
    button_font = ("Helvetica", 12, "bold")
    button_bg = "#4CAF50"  # Green background
    button_fg = "#ffffff"  # White text
    button_active_bg = "#45a049"

    fitness_games_button = tk.Button(window, text="Fitness Games", font=button_font, bg=button_bg, fg=button_fg,
                                     activebackground=button_active_bg, command=lambda: fitness_games_page(uname, window))
    fitness_games_button.pack(pady=10, ipadx=20, ipady=10)

    guides_button = tk.Button(window, text="Guides", font=button_font, bg=button_bg, fg=button_fg,
                              activebackground=button_active_bg, command=lambda: guides_page(uname))
    guides_button.pack(pady=10, ipadx=20, ipady=10)

    workout_plan_button = tk.Button(window, text="Workout Plan", font=button_font, bg=button_bg, fg=button_fg,
                                    activebackground=button_active_bg, command=lambda: workout_plan_page(uname))
    workout_plan_button.pack(pady=10, ipadx=20, ipady=10)
    logout_button = tk.Button(window, text="Logout", command=lambda: logout(window))
    logout_button.place(x=WINDOW_WIDTH-100, y=WINDOW_HEIGHT-50)
    window.mainloop()