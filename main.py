import tkinter as tk
from tkinter import *
from tkinter import ttk, messagebox

import pymongo
from PIL import Image, ImageTk

path_to_bg_img = "./icons/login_background.png"
HOST = "mongodb://localhost:27017/"
DATABASE_NAME = "HealthCV"
USERS_COLLECTION_NAME = "users"

def fitness_games_page():
    pass


def workout_plan_page():
    pass


def guides_page():
    pass


def home_page(uname):
    WINDOW_WIDTH = 700
    WINDOW_HEIGHT = 400
    window = tk.Tk()
    window.geometry(str(WINDOW_WIDTH) + "x" + str(WINDOW_HEIGHT))
    window.title("Home Page")
    bg_img = Image.open(path_to_bg_img)
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
                                     activebackground=button_active_bg, command=fitness_games_page)
    fitness_games_button.pack(pady=10, ipadx=20, ipady=10)

    guides_button = tk.Button(window, text="Guides", font=button_font, bg=button_bg, fg=button_fg,
                              activebackground=button_active_bg, command=guides_page)
    guides_button.pack(pady=10, ipadx=20, ipady=10)

    workout_plan_button = tk.Button(window, text="Workout Plan", font=button_font, bg=button_bg, fg=button_fg,
                                    activebackground=button_active_bg, command=workout_plan_page)
    workout_plan_button.pack(pady=10, ipadx=20, ipady=10)
    window.mainloop()


def validate_login_credentials(window, entered_uname, entered_pwd):
    client = pymongo.MongoClient(HOST)
    db = client[DATABASE_NAME]
    users_col = db[USERS_COLLECTION_NAME]
    query = {"uname": entered_uname}
    found_doc = users_col.find_one(query)
    if found_doc is not None:
        if found_doc["pwd"] == entered_pwd:
            window.destroy()
            home_page("Low")
        else:
            msg = messagebox.showinfo("Warning", "Incorrect password, try again.")
    else:
        msg = messagebox.showinfo("Warning", "Username does not exist, try again.")

    client.close()


def login_page():
    WINDOW_WIDTH = 700
    WINDOW_HEIGHT = 400
    window = tk.Tk()
    window.geometry(str(WINDOW_WIDTH) + "x" + str(WINDOW_HEIGHT))
    window.title("HealthCV")
    bg_img = Image.open(path_to_bg_img)
    bg_img = bg_img.resize((WINDOW_WIDTH, WINDOW_HEIGHT))
    bg_img = ImageTk.PhotoImage(bg_img, master=window)
    img_label = Label(window, image=bg_img)
    img_label.place(x=0, y=0)
    app_name_lb = Label(window, text="HealthCV")
    app_name_lb.place(x=20, y=20)
    app_name_lb.config(font=("Courier", 20))
    login_registration_frame = Frame(window)
    login_registration_frame.place(x=WINDOW_WIDTH - 300, y=100)
    notebook = ttk.Notebook(login_registration_frame)
    # Login tab
    tab1 = ttk.Frame(notebook)
    uname_label = ttk.Label(tab1, text="Username: ")
    uname_label.grid(row=0, column=0, pady=5)
    uname_tf = Entry(tab1)
    uname_tf.grid(row=0, column=1, pady=5)
    pwd_label = ttk.Label(tab1, text="Password: ")
    pwd_label.grid(row=1, column=0, pady=5)
    pwd_tf = Entry(tab1)
    pwd_tf.grid(row=1, column=1, pady=5)
    login_but = ttk.Button(tab1, text="Login",
                           command=lambda: validate_login_credentials(window, uname_tf.get(), pwd_tf.get()))
    login_but.grid(row=2, column=0, pady=5, columnspan=2)
    notebook.add(tab1, text="Login tab")
    # Registration tab
    tab2 = ttk.Frame(notebook)
    new_uname_label = ttk.Label(tab2, text="New Username: ")
    new_uname_label.grid(row=0, column=0, pady=5)
    new_uname_tf = Entry(tab2)
    new_uname_tf.grid(row=0, column=1, pady=5)
    new_pwd_label = ttk.Label(tab2, text="New Password: ")
    new_pwd_label.grid(row=1, column=0, pady=5)
    new_pwd_tf = Entry(tab2)
    new_pwd_tf.grid(row=1, column=1, pady=5)
    register_but = ttk.Button(tab2, text="Register")
    register_but.grid(row=2, column=0, pady=5, columnspan=2)
    notebook.add(tab2, text="Registration tab")
    notebook.pack()
    window.mainloop()


if __name__ == "__main__":
    login_page()
