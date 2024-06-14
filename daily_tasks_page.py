"""
Display daily tasks according to the fitness goal of the user
"""
import tkinter as tk
import datetime
from tkinter import *
from tkinter import ttk, messagebox
from PIL import Image, ImageTk

from data_models import User
from data_models.daily_tasks import DailyTasks
from paths_to_images import PATH_TO_TICK_IMG


class PersonalizedDailyTasks:
    def __init__(self):
        self.__personalized_daily_tasks = {
            "Weight Loss": {
                "Beginner": {
                    "Push-up": {"feedback": None, "done": False, "target_set": 3, "target_rep": 3, "current_set": 0, "current_rep": 0},
                    "Biceps curl": {"feedback": None, "done": False, "target_set": 3, "target_rep": 3, "current_set": 0, "current_rep": 0},
                    "Kick-And-Catch": {"feedback": None, "done": False, "target_score": 200, "current_score": 0},
                    "Yoga Imitation": {"feedback": None, "done": False, "target_score": 500, "current_score": 0}
                },
                "Intermediate": {
                    "Push-up": {"feedback": None, "done": False, "target_set": 4, "target_rep": 5, "current_set": 0, "current_rep": 0},
                    "Biceps curl": {"feedback": None, "done": False, "target_set": 4, "target_rep": 5, "current_set": 0, "current_rep": 0},
                    "Kick-And-Catch": {"feedback": None, "done": False, "target_score": 400, "current_score": 0},
                    "Yoga Imitation": {"feedback": None, "done": False, "target_score": 700, "current_score": 0}
                },
                "Advanced": {
                    "Push-up": {"feedback": None, "done": False, "target_set": 5, "target_rep": 8, "current_set": 0, "current_rep": 0},
                    "Biceps curl": {"feedback": None, "done": False, "target_set": 5, "target_rep": 8, "current_set": 0, "current_rep": 0},
                    "Kick-And-Catch": {"feedback": None, "done": False, "target_score": 600, "current_score": 0},
                    "Yoga Imitation": {"feedback": None, "done": False, "target_score": 900, "current_score": 0}
                },
            },
            "Muscle Gain": {
                "Beginner": {
                    "Push-up": {"feedback": None, "done": False, "target_set": 3, "target_rep": 6, "current_set": 0, "current_rep": 0},
                    "Biceps curl": {"feedback": None, "done": False, "target_set": 3, "target_rep": 10, "current_set": 0, "current_rep": 0},
                },
                "Intermediate": {
                    "Push-up": {"feedback": None, "done": False, "target_set": 4, "target_rep": 8, "current_set": 0, "current_rep": 0},
                    "Biceps curl": {"feedback": None, "done": False, "target_set": 4, "target_rep": 12, "current_set": 0, "current_rep": 0},
                },
                "Advanced": {
                    "Push-up": {"feedback": None, "done": False, "target_set": 5, "target_rep": 10, "current_set": 0, "current_rep": 0},
                    "Biceps curl": {"feedback": None, "done": False, "target_set": 5, "target_rep": 14, "current_set": 0, "current_rep": 0},
                },
            },
            "Endurance": {
                "Beginner": {
                    "Push-up": {"feedback": None, "done": False, "target_set": 2, "target_rep": 8, "current_set": 0, "current_rep": 0},
                    "Biceps curl": {"feedback": None, "done": False, "target_set": 2, "target_rep": 10, "current_set": 0, "current_rep": 0},
                    "Kick-And-Catch": {"feedback": None, "done": False, "num_match": 10, "each_game_target_score": 25, "num_match_done": 0},
                    "Yoga Imitation": {"feedback": None, "done": False, "target_score": 600, "current_score": 0}
                },
                "Intermediate": {
                    "Push-up": {"feedback": None, "done": False, "target_set": 3, "target_rep": 10, "current_set": 0, "current_rep": 0},
                    "Biceps curl": {"feedback": None, "done": False, "target_set": 3, "target_rep": 12, "current_set": 0, "current_rep": 0},
                    "Kick-And-Catch": {"feedback": None, "done": False, "num_match": 12, "each_game_target_score": 35, "num_match_done": 0},
                    "Yoga Imitation": {"feedback": None, "done": False, "target_score": 800, "current_score": 0}
                },
                "Advanced": {
                    "Push-up": {"feedback": None, "done": False, "target_set": 3, "target_rep": 10, "current_set": 0, "current_rep": 0},
                    "Biceps curl": {"feedback": None, "done": False, "target_set": 3, "target_rep": 12, "current_set": 0, "current_rep": 0},
                    "Kick-And-Catch": {"feedback": None, "done": False, "num_match": 14, "each_game_target_score": 40, "num_match_done": 0},
                    "Yoga Imitation": {"feedback": None, "done": False, "target_score": 800, "current_score": 0}
                },
            },
            "Flexibility": {
                "Beginner": {
                    "Kick-And-Catch": {"feedback": None, "done": False, "target_punch": 50, "target_kick": 50, "current_punch": 0, "current_kick": 0},
                    "Yoga Imitation": {"feedback": None, "done": False, "target_score": 1000, "current_score": 0}
                },
                "Intermediate": {
                    "Kick-And-Catch": {"feedback": None, "done": False, "target_punch": 80, "target_kick": 80, "current_punch": 0, "current_kick": 0},
                    "Yoga Imitation": {"feedback": None, "done": False, "target_score": 1300, "current_score": 0}
                },
                "Advanced": {
                    "Kick-And-Catch": {"feedback": None, "done": False, "target_punch": 110, "target_kick": 110, "current_punch": 0, "current_kick": 0},
                    "Yoga Imitation": {"feedback": None, "done": False, "target_score": 1600, "current_score": 0}
                }
            }
        }

    def get_daily_tasks(self, fitness_goal, fitness_level):
        try:
            return self.__personalized_daily_tasks[fitness_goal][fitness_level]
        except KeyError as e:
            msg = messagebox.showinfo("Warning", "Failed to retrieve personalized daily tasks, try again.")
            print(e)


class DailyTasksPage(tk.Tk):
    def __init__(self, WINDOW_WIDTH, WINDOW_HEIGHT, uname):
        super().__init__()
        self.resizable(False, False)

        # factors considered when recommending personalized daily tasks
        self.__factors = {
            "fitness_goals": ["Weight Loss", "Muscle Gain", "Endurance", "Flexibility"],
            "fitness_levels": ["Beginner", "Intermediate", "Advanced"]
        }
        self.WINDOW_WIDTH = WINDOW_WIDTH
        self.WINDOW_HEIGHT = WINDOW_HEIGHT
        self.__uname = uname
        self.title("Daily Tasks")
        self.geometry(str(WINDOW_WIDTH) + "x" + str(WINDOW_HEIGHT))
        self.configure(bg="#f5f5f5")
        self.tick_img = None
        self.create_widgets()
        self.goback_button = tk.Button(self, text="Go back", command=lambda: go_back(uname, self))
        self.goback_button.place(x=WINDOW_WIDTH - 100, y=WINDOW_HEIGHT - 50)

    def create_widgets(self):
        TICK_WIDTH = 50
        TICK_HEIGHT = 50

        self.tick_img = Image.open(PATH_TO_TICK_IMG)
        self.tick_img = self.tick_img.resize((TICK_WIDTH, TICK_HEIGHT))
        self.tick_img = ImageTk.PhotoImage(self.tick_img)
        # Main frame
        main_frame = tk.Frame(self, bg="#f5f5f5", padx=20, pady=5)
        main_frame.pack(expand=True, fill=tk.BOTH)
        user_table = User()
        user_doc = user_table.search_by_uname(self.__uname)
        ds_obj = PersonalizedDailyTasks()
        # After loading the daily_tasks, write them into the table `DailyTask` with additional info such as progress
        daily_tasks = ds_obj.get_daily_tasks(user_doc["fitness_goal"], user_doc["fitness_level"])
        # Title
        title_label = tk.Label(main_frame, text="Daily Tasks", font=("Helvetica", 12, "bold"), bg="#f5f5f5", fg="#333333")
        title_label.pack(pady=5)

        # User Info Frame
        user_info_frame = tk.Frame(main_frame, bg="#ffffff", padx=10, pady=10, bd=1, relief=tk.SOLID)
        user_info_frame.pack(fill=tk.X, pady=10)

        # Fitness Goal
        goal_label = tk.Label(user_info_frame, text="Fitness Goal: " + user_doc["fitness_goal"], font=("Helvetica", 12), bg="#ffffff", anchor="w")
        goal_label.pack(fill=tk.X)

        # Current Fitness Level
        level_label = tk.Label(user_info_frame, text="Fitness Level: " + user_doc["fitness_level"], font=("Helvetica", 12), bg="#ffffff", anchor="w")
        level_label.pack(fill=tk.X)

        # Task List Frame
        tasks_frame = tk.Frame(main_frame, bg="#f5f5f5")
        tasks_frame.pack(expand=True, fill=tk.BOTH, pady=5)

        # Tasks Title
        tasks_title_label = tk.Label(tasks_frame, text="Tasks", font=("Helvetica", 12, "bold"), bg="#f5f5f5", fg="#333333")
        tasks_title_label.pack(anchor="w")

        # Scrollable Tasks List
        self.tasks_canvas = tk.Canvas(tasks_frame, bg="#f5f5f5")
        self.scrollbar = ttk.Scrollbar(tasks_frame, orient="vertical", command=self.tasks_canvas.yview)
        self.scrollable_frame = ttk.Frame(self.tasks_canvas)
        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.tasks_canvas.configure(
                scrollregion=self.tasks_canvas.bbox("all")
            )
        )

        self.tasks_canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.tasks_canvas.configure(yscrollcommand=self.scrollbar.set)

        self.tasks_canvas.pack(side="left", fill=tk.BOTH, expand=True)
        self.scrollbar.pack(side="right", fill=tk.Y)

        dt_table = DailyTasks()
        cur_datetime = datetime.datetime.now()
        cur_date = datetime.datetime(cur_datetime.year, cur_datetime.month, cur_datetime.day, cur_datetime.hour,
                                     cur_datetime.minute)
        if dt_table.daily_tasks_exist_on_date(self.__uname, cur_date):
            print("Record of the daily tasks are already in the database!")
        else:
            dt_table.create_daily_tasks(self.__uname, cur_date, daily_tasks)

        daily_tasks_progresses = dt_table.get_daily_tasks_progresses(self.__uname, cur_date)
        if daily_tasks_progresses is not None:
            self.render_daily_tasks(daily_tasks_progresses["progresses"], user_doc["fitness_goal"])
        else:
            print("No daily tasks progresses!")

    def add_task(self, task_name, description, completed):
        task_frame = tk.Frame(self.scrollable_frame, bg="#ffffff", padx=10, pady=10, bd=1, relief=tk.SOLID)
        task_frame.pack(fill=tk.X, pady=5, expand=True)

        task_label = tk.Label(task_frame, text=task_name, font=("Helvetica", 12, "bold"), bg="#ffffff", anchor="w")
        task_label.pack(fill=tk.X, expand=True)

        details_label = tk.Label(task_frame, text=description, font=("Helvetica", 12), bg="#ffffff", anchor="w")
        details_label.pack(fill=tk.X, expand=True)

        if completed:
            img_frame = tk.Frame(task_frame, bg="#ffffff")
            img_frame.pack(fill=tk.X, expand=True)
            img_label = Label(img_frame, image=self.tick_img)
            img_label.pack(side=tk.RIGHT)

            rating_label = tk.Label(task_frame, text="How was the target?", font=("Helvetica", 12), bg="#f5f5f5")
            rating_label.pack(fill=tk.X)

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
        self.scrollable_frame.pack(fill=tk.X, expand=True)
        self.tasks_canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw", width=self.WINDOW_WIDTH-60)
        self.tasks_canvas.configure(yscrollcommand=self.scrollbar.set)

        self.tasks_canvas.pack(side="left", fill=tk.BOTH, expand=True)
        self.scrollbar.pack(side="right", fill=tk.Y)

    def render_daily_tasks(self, daily_tasks, fitness_goal):
        """after the user changes their fitness goal and fitness level at profile page, rmb to check the table daily_tasks and delete any existing record."""
        for task, info in daily_tasks.items():
            if fitness_goal == "Weight Loss":
                if task == "Push-up":
                    description = "Target: " + str(info["target_set"]) + " set(s) " + str(info["target_rep"]) + " rep(s); Best record: "+ str(info["current_set"]) + " set(s) " + str(info["current_rep"]) + " rep(s)"
                    self.add_task(task, description, info["done"])
                elif task == "Biceps curl":
                    description = "Target: " + str(info["target_set"]) + " set(s) " + str(info["target_rep"]) + " rep(s); Best record: "+ str(info["current_set"]) + " set(s) " + str(info["current_rep"]) + " rep(s)"
                    self.add_task(task, description, info["done"])
                elif task == "Kick-And-Catch":
                    description = "Progress of score: " + str(info["current_score"]) + "/" + str(info["target_score"])
                    self.add_task(task, description, info["done"])
                elif task == "Yoga Imitation":
                    description = "Progress of score: " + str(info["current_score"]) + "/" + str(info["target_score"])
                    self.add_task(task, description, info["done"])
            elif fitness_goal == "Muscle Gain":
                if task == "Push-up":
                    description = "Target: " + str(info["target_set"]) + " set(s) " + str(info["target_rep"]) + " rep(s); Best record: "+ str(info["current_set"]) + " set(s) " + str(info["current_rep"]) + " rep(s)"
                    self.add_task(task, description, info["done"])
                elif task == "Biceps curl":
                    description = "Target: " + str(info["target_set"]) + " set(s) " + str(info["target_rep"]) + " rep(s); Best record: "+ str(info["current_set"]) + " set(s) " + str(info["current_rep"]) + " rep(s)"
                    self.add_task(task, description, info["done"])
            elif fitness_goal == "Endurance":
                if task == "Push-up":
                    description = "Target: " + str(info["target_set"]) + " set(s) " + str(info["target_rep"]) + " rep(s); Best record: "+ str(info["current_set"]) + " set(s) " + str(info["current_rep"]) + " rep(s)"
                    self.add_task(task, description, info["done"])
                elif task == "Biceps curl":
                    description = "Target: " + str(info["target_set"]) + " set(s) " + str(info["target_rep"]) + " rep(s); Best record: "+ str(info["current_set"]) + " set(s) " + str(info["current_rep"]) + " rep(s)"
                    self.add_task(task, description, info["done"])
                elif task == "Kick-And-Catch":
                    description = "Play " + str(info["num_match"]) + " matches with at least " + str(info["each_game_target_score"]) + " scores each game. Progress: " + str(info["num_match_done"]) + "/" + str(info["num_match"])
                    self.add_task(task, description, info["done"])
                elif task == "Yoga Imitation":
                    description = "Progress of score: " + str(info["current_score"]) + "/" + str(info["target_score"])
                    self.add_task(task, description, info["done"])
            elif fitness_goal == "Flexibility":
                if task == "Kick-And-Catch":
                    description = "Make " + str(info["target_punch"]) + " punches, progress "+ str(info["current_punch"]) + "/" + str(info["target_punch"]) + " . Make " + str(info["target_kick"]) + " kicks, progress " + str(info["current_kick"]) + "/" + str(info["target_kick"])
                    self.add_task(task, description, info["done"])
                elif task == "Yoga Imitation":
                    description = "Progress of score: " + str(info["current_score"]) + "/" + str(info["target_score"])
                    self.add_task(task, description, info["done"])
            else:
                description = "ERROR! NO fitness goal!"
                self.add_task(task, description, info["done"])


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
    window = DailyTasksPage(WINDOW_WIDTH, WINDOW_HEIGHT, uname)

    window.mainloop()
