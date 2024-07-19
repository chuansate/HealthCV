import tkinter as tk
from tkinter import *
from PIL import Image, ImageTk

from paths_to_images import PATH_TO_BACKGROUND_IMG, PATH_TO_PROFILE_IMG, PATH_TO_TASKS_IMG, PATH_TO_BURNED_CALORIES_IMG
from tkinter import ttk, messagebox


def logout(window):
    from main import login_page
    window.destroy()
    login_page()


def submit(uname, first_time_login_window, goal_var, level_var):
    from data_models import User
    goal = goal_var.get()
    level = level_var.get()

    if goal != "" and level != "":
        print(f"Fitness Goal: {goal}")
        print(f"Current Fitness Level: {level}")
        # write into database
        try:
            User().filling_in_fitness_goal_and_level(uname, goal, level)
            first_time_login_window.destroy()
            home_page(uname)
        except Exception:
            msg = messagebox.showinfo("Warning", "Failed to access the database, please try again.")
    else:
        msg = messagebox.showinfo("Warning", "Please select your fitness goal and fitness level.")


def home_page(uname):
    from burnt_calories_page import burnt_calories_page
    from fitness_games_page import fitness_games_page
    from guides_page import guides_page
    from workout_plan_page import workout_plan_page
    from profile_page import profile_page
    from data_models import User
    from daily_tasks_page import daily_tasks_page
    if User().user_hasnt_filled_in_details(uname):
        # ask them to fill in some details about them
        # Create the main window
        root = tk.Tk()
        root.title("First time login")
        root.geometry("300x200")
        root.resizable(False, False)
        # Fitness goals options
        goals = ["Weight Loss", "Muscle Gain", "Endurance", "Flexibility"]

        # Current fitness levels options
        levels = ["Beginner", "Intermediate", "Advanced"]

        # StringVars to hold the values
        goal_var = tk.StringVar()
        level_var = tk.StringVar()

        # Labels
        tk.Label(root, text="Select Your Fitness Goal:").pack(pady=5)

        # Combobox for fitness goals
        goal_combobox = ttk.Combobox(root, textvariable=goal_var, values=goals, state="readonly")
        goal_combobox.pack(pady=5)

        tk.Label(root, text="Select Your Current Fitness Level:").pack(pady=5)

        # Combobox for fitness levels
        level_combobox = ttk.Combobox(root, textvariable=level_var, values=levels, state="readonly")
        level_combobox.pack(pady=5)

        # Submit button
        submit_button = tk.Button(root, text="Submit", command=lambda: submit(uname, root, goal_var, level_var))
        submit_button.pack(pady=10)

        # Start the main event loop
        root.mainloop()
    else:
        WINDOW_WIDTH = 700
        WINDOW_HEIGHT = 400
        PROFILE_ICON_WIDTH = 40
        PROFILE_ICON_HEIGHT = 40
        window = tk.Tk()
        window.geometry(str(WINDOW_WIDTH) + "x" + str(WINDOW_HEIGHT))
        window.title("Home Page")
        window.resizable(False, False)
        bg_img = Image.open(PATH_TO_BACKGROUND_IMG)
        bg_img = bg_img.resize((WINDOW_WIDTH, WINDOW_HEIGHT))
        bg_img = ImageTk.PhotoImage(bg_img, master=window)
        img_label = Label(window, image=bg_img)
        img_label.place(x=0, y=0)

        profile_img = Image.open(PATH_TO_PROFILE_IMG)
        profile_img = profile_img.resize((PROFILE_ICON_WIDTH, PROFILE_ICON_HEIGHT))
        profile_img = ImageTk.PhotoImage(profile_img, master=window)
        profile_button = tk.Button(window, image=profile_img,
                                   command=lambda: profile_page(uname, window))
        profile_button.place(x=30, y=30)

        tasks_img = Image.open(PATH_TO_TASKS_IMG)
        tasks_img = tasks_img.resize((PROFILE_ICON_WIDTH, PROFILE_ICON_HEIGHT))
        tasks_img = ImageTk.PhotoImage(tasks_img, master=window)
        tasks_button = tk.Button(window, image=tasks_img,
                                   command=lambda: daily_tasks_page(uname, window))
        tasks_button.place(x=30, y=80)

        calories_img = Image.open(PATH_TO_BURNED_CALORIES_IMG)
        calories_img = calories_img.resize((PROFILE_ICON_WIDTH, PROFILE_ICON_HEIGHT))
        calories_img = ImageTk.PhotoImage(calories_img, master=window)
        calories_button = tk.Button(window, image=calories_img,
                                 command=lambda: burnt_calories_page(uname, window))
        calories_button.place(x=30, y=130)

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
                                  activebackground=button_active_bg, command=lambda: guides_page(uname, window))
        guides_button.pack(pady=10, ipadx=20, ipady=10)

        workout_plan_button = tk.Button(window, text="Workout Plan", font=button_font, bg=button_bg, fg=button_fg,
                                        activebackground=button_active_bg, command=lambda: workout_plan_page(uname, window))
        workout_plan_button.pack(pady=10, ipadx=20, ipady=10)
        logout_button = tk.Button(window, text="Logout", command=lambda: logout(window))
        logout_button.place(x=WINDOW_WIDTH-100, y=WINDOW_HEIGHT-50)
        window.mainloop()