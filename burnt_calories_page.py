"""
Allows users to modify their details, such as fitness goal, current fitness level,
Displays current user level, joined date
"""
import tkinter as tk
from tkinter import *
from PIL import Image, ImageTk
from paths_to_images import PATH_TO_BURNED_CALORIES_IMG, PATH_TO_BACKGROUND_IMG
from tkcalendar import Calendar
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import random
import datetime
from tkinter import messagebox
from data_models import BurnedCalories


class BurntCaloriesPage:
    def __init__(self, root, WINDOW_WIDTH, WINDOW_HEIGHT, uname):
        self.root = root
        self.uname = uname
        self.root.title("Burnt calories page")
        self.root.configure(bg="#f5f5f5")
        self.root.geometry(str(WINDOW_WIDTH) + "x" + str(WINDOW_HEIGHT))
        self.bg_img = Image.open(PATH_TO_BACKGROUND_IMG)
        self.bg_img = self.bg_img.resize((WINDOW_WIDTH, WINDOW_HEIGHT))
        self.bg_img = ImageTk.PhotoImage(self.bg_img, master=self.root)
        self.create_widgets()

    # def create_widgets(self):
    #     img_label = Label(self.root, image=self.bg_img)
    #     img_label.place(x=0, y=0)
    #     # Main frame
    #     main_frame = tk.Frame(self.root, padx=20, pady=20)
    #     main_frame.pack(expand=True, fill=tk.BOTH)
    #     self.root.resizable(False, False)
    #
    #     # Title
    #     title_label = tk.Label(main_frame, text="Fitness Tracker", font=("Helvetica", 20, "bold"), bg="#f5f5f5", fg="#333333")
    #     title_label.pack(pady=10)
    #
    #     # Today's burned calories
    #     today_frame = tk.Frame(main_frame, bg="#ffffff", padx=10, pady=10, bd=1, relief=tk.SOLID)
    #     today_frame.pack(fill=tk.X, pady=10)
    #
    #     today_label = tk.Label(today_frame, text="Today's Burned Calories: 500", font=("Helvetica", 14), bg="#ffffff", anchor="w")
    #     today_label.pack(fill=tk.X)
    #
    #     # Calendar picker
    #     calendar_frame = tk.Frame(main_frame, bg="#f5f5f5")
    #     calendar_frame.pack(pady=10)
    #
    #     calendar_label = tk.Label(calendar_frame, text="Choose Month and Year", font=("Helvetica", 16, "bold"), bg="#f5f5f5", fg="#333333")
    #     calendar_label.pack(anchor="w")
    #
    #     self.calendar = Calendar(calendar_frame, selectmode='day', year=2023, month=6)
    #     self.calendar.pack(pady=10)
    #
    #     visualize_button = tk.Button(calendar_frame, text="Visualize", command=self.visualize_data, bg="#007bff", fg="#ffffff", font=("Helvetica", 12))
    #     visualize_button.pack(pady=10)
    def load_today_burned_calories(self):
        burned_calories_table = BurnedCalories()
        cur_datetime = datetime.datetime.now()
        cur_date = datetime.datetime(cur_datetime.year, cur_datetime.month, cur_datetime.day, cur_datetime.hour,
                            cur_datetime.minute)
        return burned_calories_table.get_burned_calories_by_date(self.uname, cur_date)

    def create_widgets(self):
        img_label = Label(self.root, image=self.bg_img)
        img_label.place(x=0, y=0)

        # Today's burned calories
        today_frame = tk.Frame(self.root, bg="#ffffff", padx=10, pady=10, bd=1, relief=tk.SOLID)
        today_frame.pack(fill=tk.X, pady=10)

        burned_calories = self.load_today_burned_calories()
        if burned_calories is not None:
            today_label = tk.Label(today_frame, text="Today's Burned Calories: " + str(burned_calories), font=("Helvetica", 14), bg="#ffffff", anchor="w")
            today_label.configure(anchor="center")
            today_label.pack(fill=tk.X)
        else:
            today_label = tk.Label(today_frame, text="Today's Burned Calories: DB wrong",
                                   font=("Helvetica", 14), bg="#ffffff", anchor="w")
            today_label.configure(anchor="center")
            today_label.pack(fill=tk.X)


        # Calendar picker
        calendar_frame = tk.Frame(self.root, bg="#f5f5f5")
        calendar_frame.pack(pady=10)

        calendar_label = tk.Label(calendar_frame, text="Pick any month for visualization", font=("Helvetica", 14, "bold"), bg="#f5f5f5", fg="#333333")
        calendar_label.pack(anchor="w")

        self.calendar = Calendar(calendar_frame, selectmode='day', year=2024, month=6)
        self.calendar.pack(pady=10)

        visualize_button = tk.Button(calendar_frame, text="Visualize", command=self.visualize_data, bg="#007bff", fg="#ffffff", font=("Helvetica", 12))
        visualize_button.pack(pady=10)

    def visualize_data(self):
        bc_table = BurnedCalories()
        # Get selected date
        selected_date = self.calendar.selection_get()
        if selected_date is not None:
            year = selected_date.year
            month = selected_date.month

            days_in_month = (datetime.date(year, month + 1, 1) - datetime.date(year, month, 1)).days if month < 12 else 31
            # daily_calories = [random.randint(200, 800) for _ in range(days_in_month)]

            daily_calories = [bc_table.get_burned_calories_by_date(self.uname, datetime.date(year, month, _ + 1)) for _ in range(days_in_month)]
            dates = [datetime.date(year, month, day + 1).day for day in range(days_in_month)]

            # Create the plot
            fig, ax = plt.subplots()
            plt.ylim(0, 1000)
            ax.plot(dates, daily_calories, marker='o', linestyle='-', color='b')
            ax.set_title(f"Daily Burned Calories for {selected_date.strftime('%B %Y')}")
            ax.set_xlabel("Day of Date")
            ax.set_ylabel("Calories Burned")
            ax.grid(True)

            # Show the plot in a new window
            plot_window = tk.Toplevel(self.root)
            plot_window.title("Calories Burned Over Time")
            plot_window.geometry("800x600")

            canvas = FigureCanvasTkAgg(fig, master=plot_window)
            canvas.draw()
            canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        else:
            msg = messagebox.showinfo("Warning", "Please simply choose a day in the desired year and month.")


def go_back(uname, window):
    from home_page import home_page
    window.destroy()
    home_page(uname)


def burnt_calories_page(uname, window):
    window.destroy()
    WINDOW_WIDTH = 700
    WINDOW_HEIGHT = 400
    ICON_WIDTH = 30
    ICON_HEIGHT = 35
    window = tk.Tk()

    app = BurntCaloriesPage(window, WINDOW_WIDTH, WINDOW_HEIGHT, uname)

    title_label = tk.Label(window, text="Burned calories page", font=("Helvetica", 16, "bold"), bg='#f0f0f0')
    title_label.pack(pady=20)

    goback_button = tk.Button(window, text="Go back", command=lambda: go_back(uname, window))
    goback_button.place(x=WINDOW_WIDTH - 100, y=WINDOW_HEIGHT - 50)
    window.mainloop()

