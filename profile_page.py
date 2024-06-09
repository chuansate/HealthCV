"""
Allows users to modify their details, such as fitness goal, current fitness level,
Displays current user level, joined date
"""
import tkinter as tk
from tkinter import *
from tkinter import ttk, messagebox
from PIL import Image, ImageTk
from paths_to_images import PATH_TO_BACKGROUND_IMG, PATH_TO_PUSH_UP_ICON, PATH_TO_BICEPS_CURL_ICON
from data_models import User
# Define options for dropdown menus
fitness_goals = ["Weight Loss", "Muscle Gain", "Endurance", "Flexibility"]
fitness_levels = ["Beginner", "Intermediate", "Advanced"]


class ProfilePage:
    def __init__(self, master, WINDOW_HEIGHT, WINDOW_WIDTH, uname):
        self.master = master
        self.master.geometry(str(WINDOW_WIDTH) + "x" + str(WINDOW_HEIGHT))
        self.master.title("Profile page")
        self.master.resizable(False, False)
        # display username, joined date, user level, current fitness level, and fitness goal
        self.bg_img = Image.open(PATH_TO_BACKGROUND_IMG)
        self.bg_img = self.bg_img.resize((WINDOW_WIDTH, WINDOW_HEIGHT))
        self.bg_img = ImageTk.PhotoImage(self.bg_img, master=self.master)
        self.img_label = Label(self.master, image=self.bg_img)
        self.img_label.place(x=0, y=0)
        u_table = User()
        user_details = u_table.search_by_uname(uname)
        # Create labels and entry fields for username and joined date
        self.username_label = Label(master, text="Username:")
        self.username_label.grid(row=0, column=0, padx=5, pady=5)
        self.username_label2 = Label(master, text=user_details["uname"])
        self.username_label2.grid(row=0, column=1, padx=5, pady=5)

        self.joined_date_label = Label(master, text="Joined Date:")
        self.joined_date_label.grid(row=1, column=0, padx=5, pady=5)
        self.joined_date_label2 = Label(master, text=user_details["created_time"].strftime("%Y-%m-%d"))
        self.joined_date_label2.grid(row=1, column=1, padx=5, pady=5)

        # Create labels and dropdown menus for fitness goal and level
        self.fitness_goal_label = Label(master, text="Fitness Goal:")
        self.fitness_goal_label.grid(row=2, column=0, padx=5, pady=5)
        self.fitness_goal_var = StringVar(master)
        self.fitness_goal_var.set(user_details["fitness_goal"])  # Set default goal
        self.fitness_goal_menu = ttk.Combobox(master, values=fitness_goals, textvariable=self.fitness_goal_var, state="readonly")
        self.fitness_goal_menu.grid(row=2, column=1, padx=5, pady=5)

        self.fitness_level_label = Label(master, text="Fitness Level:")
        self.fitness_level_label.grid(row=3, column=0, padx=5, pady=5)
        self.fitness_level_var = StringVar(master)
        self.fitness_level_var.set(user_details["fitness_level"])  # Set default level
        self.fitness_level_menu = ttk.Combobox(master, values=fitness_levels, textvariable=self.fitness_level_var, state="readonly")
        self.fitness_level_menu.grid(row=3, column=1, padx=5, pady=5)

        # Create a button to save changes
        self.save_button = Button(master, text="Save Changes", command=lambda: self.save_profile(uname))
        self.save_button.grid(row=4, columnspan=2, padx=5, pady=5)
        self.goback_button = tk.Button(master, text="Go back", command=lambda: go_back(uname, self.master))
        self.goback_button.place(x=WINDOW_WIDTH - 100, y=WINDOW_HEIGHT - 50)

    # Function to save the edited profile information
    def save_profile(self, uname):
        u_table = User()
        fitness_goal = self.fitness_goal_var.get()
        fitness_level = self.fitness_level_var.get()

        # You can use the retrieved information here to update a database or perform other actions
        print(f"Username: {uname}, Fitness Goal: {fitness_goal}, Fitness Level: {fitness_level}")
        try:
            u_table.save_profile_page(uname, fitness_goal, fitness_level)
            msg = messagebox.showinfo("Information", "Updated the profile page successfully!")
        except UserWarning:
            msg = messagebox.showinfo("Warning", "Failed to update the profile page, try again.")


def go_back(uname, window):
    from home_page import home_page
    window.destroy()
    home_page(uname)


def profile_page(uname, window):
    if window is not None:
        # window could be None happen when the user is from push-up/biceps curl to fitness_games_page
        window.destroy()
    WINDOW_WIDTH = 700
    WINDOW_HEIGHT = 400
    ICON_WIDTH = 30
    ICON_HEIGHT = 35
    window = tk.Tk()

    profile_page = ProfilePage(window, WINDOW_HEIGHT, WINDOW_WIDTH, uname)

    window.mainloop()
