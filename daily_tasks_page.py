"""
Display daily tasks according to the fitness goal of the user
"""
import tkinter as tk
from tkinter import *
from tkinter import ttk, messagebox
from PIL import Image, ImageTk
from paths_to_images import PATH_TO_TICK_IMG


class DailyTasksPage:
    def __init__(self, root, WINDOW_WIDTH, WINDOW_HEIGHT):
        self.root = root
        # factors considered when recommending personalized daily tasks
        self.__factors = {
            "fitness_goals": ["Weight Loss", "Muscle Gain", "Endurance", "Flexibility"],
            "fitness_levels": ["Beginner", "Intermediate", "Advanced"]
        }

        self.root.title("Daily Tasks")
        self.root.geometry(str(WINDOW_WIDTH) + "x" + str(WINDOW_HEIGHT))
        self.root.configure(bg="#f5f5f5")
        self.tick_img = None
        self.create_widgets()

    def create_widgets(self):
        TICK_WIDTH = 50
        TICK_HEIGHT = 50

        self.tick_img = Image.open(PATH_TO_TICK_IMG)
        self.tick_img = self.tick_img.resize((TICK_WIDTH, TICK_HEIGHT))
        self.tick_img = ImageTk.PhotoImage(self.tick_img)
        # Main frame
        main_frame = tk.Frame(self.root, bg="#f5f5f5", padx=20, pady=20)
        main_frame.pack(expand=True, fill=tk.BOTH)

        # Title
        title_label = tk.Label(main_frame, text="Daily Tasks", font=("Helvetica", 15, "bold"), bg="#f5f5f5", fg="#333333")
        title_label.pack(pady=10)

        # User Info Frame
        user_info_frame = tk.Frame(main_frame, bg="#ffffff", padx=10, pady=10, bd=1, relief=tk.SOLID)
        user_info_frame.pack(fill=tk.X, pady=10)

        # Fitness Goal
        goal_label = tk.Label(user_info_frame, text="Fitness Goal: Weight Loss", font=("Helvetica", 14), bg="#ffffff", anchor="w")
        goal_label.pack(fill=tk.X)

        # Current Fitness Level
        level_label = tk.Label(user_info_frame, text="Current Fitness Level: Intermediate", font=("Helvetica", 14), bg="#ffffff", anchor="w")
        level_label.pack(fill=tk.X)

        # Task List Frame
        tasks_frame = tk.Frame(main_frame, bg="#f5f5f5")
        tasks_frame.pack(expand=True, fill=tk.BOTH, pady=10)

        # Tasks Title
        tasks_title_label = tk.Label(tasks_frame, text="Tasks", font=("Helvetica", 16, "bold"), bg="#f5f5f5", fg="#333333")
        tasks_title_label.pack(anchor="w")

        # Scrollable Tasks List
        tasks_canvas = tk.Canvas(tasks_frame, bg="#f5f5f5")
        scrollbar = ttk.Scrollbar(tasks_frame, orient="vertical", command=tasks_canvas.yview)
        scrollable_frame = ttk.Frame(tasks_canvas)
        scrollable_frame.bind(
            "<Configure>",
            lambda e: tasks_canvas.configure(
                scrollregion=tasks_canvas.bbox("all")
            )
        )

        tasks_canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        tasks_canvas.configure(yscrollcommand=scrollbar.set)

        tasks_canvas.pack(side="left", fill=tk.BOTH, expand=True)
        scrollbar.pack(side="right", fill=tk.Y)

        # generate these based on the fitness goal and fitness level of the users
        self.add_task(scrollable_frame, "Run 5 miles", "Run at a steady pace for 5 miles.", True)
        self.add_task(scrollable_frame, "Strength Training", "Complete a full body strength training workout.", True)
        self.add_task(scrollable_frame, "Yoga", "Attend a 1-hour yoga class.", False)
        self.add_task(scrollable_frame, "Cycling", "Cycle for 20 miles at a moderate pace.", False)
        self.add_task(scrollable_frame, "Swimming", "Swim for 30 minutes.", True)

    def add_task(self, parent, task_name, task_details, completed):
        task_frame = tk.Frame(parent, bg="#ffffff", padx=10, pady=10, bd=1, relief=tk.SOLID)
        task_frame.pack(fill=tk.X, pady=5)

        task_label = tk.Label(task_frame, text=task_name, font=("Helvetica", 14, "bold"), bg="#ffffff", anchor="w")
        task_label.pack(fill=tk.X)

        details_label = tk.Label(task_frame, text=task_details, font=("Helvetica", 12), bg="#ffffff", anchor="w")
        details_label.pack(fill=tk.X)

        if completed:
            img_frame = tk.Frame(task_frame, bg="#ffffff")
            img_frame.pack(fill=tk.X, expand=True)
            img_label = Label(img_frame, image=self.tick_img)
            img_label.pack(side=tk.RIGHT)

            rating_label = tk.Label(task_frame, text="How was the target?", font=("Helvetica", 12), bg="#f5f5f5")
            rating_label.pack()

            rating_var = tk.StringVar(value="Normal")

            rating_easy = tk.Radiobutton(task_frame, text="Easy", variable=rating_var, value="Easy",
                                         font=("Helvetica", 12), bg="#f5f5f5")
            rating_easy.pack(side=tk.LEFT, padx=10)
            rating_normal = tk.Radiobutton(task_frame, text="Normal", variable=rating_var, value="Normal",
                                           font=("Helvetica", 12), bg="#f5f5f5")
            rating_normal.pack(side=tk.LEFT, padx=10)
            rating_hard = tk.Radiobutton(task_frame, text="Hard", variable=rating_var, value="Hard",
                                         font=("Helvetica", 12), bg="#f5f5f5")
            rating_hard.pack(side=tk.LEFT, padx=10)

            save_button = tk.Button(task_frame, text="Save", command=lambda: self.save_rating(rating_var.get()), bg="#007bff", fg="#ffffff",
                                    font=("Helvetica", 12))
            save_button.pack(pady=20)

    def save_rating(self, rating_var):
        print(rating_var)
        msg = messagebox.showinfo("Information", "Updated the feedback!")


def go_back(uname, window):
    from home_page import home_page
    window.destroy()
    home_page(uname)


def daily_tasks_page(uname, home_window):
    if home_window is not None:
        # window could be None happen when the user is from push-up/biceps curl to fitness_games_page
        home_window.destroy()
    WINDOW_WIDTH = 600
    WINDOW_HEIGHT = 400
    window = tk.Tk()
    app = DailyTasksPage(window, WINDOW_WIDTH, WINDOW_HEIGHT)
    window.resizable(False, False)
    title_label = tk.Label(window, text="Daily Tasks", font=("Helvetica", 16, "bold"), bg='#f0f0f0')
    title_label.pack(pady=20)

    goback_button = tk.Button(window, text="Go back", command=lambda: go_back(uname, window))
    goback_button.place(x=WINDOW_WIDTH - 100, y=WINDOW_HEIGHT - 50)
    window.mainloop()
