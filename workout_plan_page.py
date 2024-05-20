"""
Setting sets and reps for each type of exercise
showing statistics over time
showing today's report
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


def validate_set_rep_counts(workout_plan_window, setting_set_rep_window, set_value, rep_value, uname):
    from counting_biceps_curl import render_counting_biceps_curl_UI
    invalid_inputs = False
    try:
        rep_count = int(rep_value)
        set_count = int(set_value)
        if 1 <= rep_count <= 20 and 1 <= set_count <= 6:
            invalid_inputs = False
        else:
            invalid_inputs = True
    except ValueError:
        invalid_inputs = True
    if invalid_inputs:
        msg = messagebox.showinfo("Warning", "Invalid inputs, try again.")
    else:
        workout_plan_window.destroy()
        render_counting_biceps_curl_UI(uname, setting_set_rep_window)


def setting_set_rep_counts_page(uname, workout_plan_window):
    root = Tk()
    root.title("Workout Set & Rep Counter")
    WINDOW_WIDTH = 250
    WINDOW_HEIGHT = 150
    root.geometry(str(WINDOW_WIDTH) + "x" + str(WINDOW_HEIGHT))
    root.resizable(False, False)
    # Labels
    set_label = Label(root, text="Sets (Max 6):")
    set_label.grid(row=0, column=0, pady=5)

    rep_label = Label(root, text="Reps (Max 20):")
    rep_label.grid(row=1, column=0, pady=5)

    # Entries with validation
    set_entry = Entry(root)
    set_entry.grid(row=0, column=1, pady=5)

    rep_entry = Entry(root)
    rep_entry.grid(row=1, column=1, pady=5)

    # Button
    start_button = Button(root, text="Start Workout", command=lambda: validate_set_rep_counts(workout_plan_window, root, set_entry.get(), rep_entry.get(), uname))
    start_button.grid(row=2, column=0, pady=5, columnspan=2)

    root.mainloop()


def workout_plan_page(uname, window):
    from counting_biceps_curl import render_counting_biceps_curl_UI
    if window is not None:
        # window could be None happen when the user is from push-up/biceps curl to fitness_games_page
        window.destroy()
    WINDOW_WIDTH = 700
    WINDOW_HEIGHT = 400
    ICON_WIDTH = 30
    ICON_HEIGHT = 35
    window = tk.Tk()
    window.geometry(str(WINDOW_WIDTH) + "x" + str(WINDOW_HEIGHT))
    window.title("Workout plan page")
    window.resizable(False, False)
    bg_img = Image.open(PATH_TO_BACKGROUND_IMG)
    bg_img = bg_img.resize((WINDOW_WIDTH, WINDOW_HEIGHT))
    bg_img = ImageTk.PhotoImage(bg_img, master=window)
    img_label = Label(window, image=bg_img)
    img_label.place(x=0, y=0)
    title_label = tk.Label(window, text="Workout plan", font=("Helvetica", 16, "bold"), bg='#f0f0f0')
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
                                  command=lambda: setting_set_rep_counts_page(uname, window))
    push_up_button.pack(pady=10, ipadx=20, ipady=10)

    biceps_curl_img = Image.open(PATH_TO_BICEPS_CURL_ICON)
    biceps_curl_img = biceps_curl_img.resize((ICON_WIDTH, ICON_HEIGHT))
    biceps_curl_img = ImageTk.PhotoImage(biceps_curl_img)
    biceps_curl_button = tk.Button(window, text="Biceps curl", font=button_font, bg=button_bg, fg=button_fg,
                                      activebackground=button_active_bg, image=biceps_curl_img, compound=RIGHT,
                                      command=lambda: render_counting_biceps_curl_UI(uname, window))
    biceps_curl_button.pack(pady=10, ipadx=20, ipady=10)

    logout_button = tk.Button(window, text="Go back", command=lambda: go_back(uname, window))
    logout_button.place(x=WINDOW_WIDTH - 100, y=WINDOW_HEIGHT - 50)
    window.mainloop()
