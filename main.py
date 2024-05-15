import tkinter as tk
from tkinter import *
from tkinter import ttk, messagebox

from database_constants import HOST, DATABASE_NAME, USERS_COLLECTION_NAME
import pymongo
from PIL import Image, ImageTk
from pymongo import errors

path_to_bg_img = "./icons/login_background.png"


def logout(window):
    window.destroy()
    login_page()


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
    window.resizable(False, False)
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
    logout_button = tk.Button(window, text="Logout", command=lambda: logout(window))
    logout_button.place(x=WINDOW_WIDTH-100, y=WINDOW_HEIGHT-50)
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
            home_page(entered_uname)
        else:
            msg = messagebox.showinfo("Warning", "Incorrect password, try again.")
    else:
        msg = messagebox.showinfo("Warning", "Username does not exist, try again.")

    client.close()


def credentials_are_valid(entered_uname, entered_pwd):
    if len(entered_uname) == 0 or len(entered_pwd) == 0:
        msg = messagebox.showinfo("Warning", "Username or password can't be empty!")
        return False
    elif len(entered_uname) > 10:
        msg = messagebox.showinfo("Warning", "Username can't contain more than 10 characters!")
        return False
    elif len(entered_pwd) > 10:
        msg = messagebox.showinfo("Warning", "Password can't contain more than 10 characters!")
        return False
    else:
        return True


def validate_register_credentials(entered_uname, entered_pwd):
    if credentials_are_valid(entered_uname, entered_pwd):
        client = pymongo.MongoClient(HOST)
        db = client[DATABASE_NAME]
        users_col = db[USERS_COLLECTION_NAME]
        query = {"uname": entered_uname}
        found_doc = users_col.find_one(query)
        if found_doc is None:
            try:
                users_col.insert_one({
                    "uname": entered_uname,
                    "pwd": entered_pwd
                })
                msg = messagebox.showinfo("Information", "New account has been registered!")
            except errors.WriteConcernError as wce:
                print(wce)
                msg = messagebox.showinfo("Warning", "Failed to register new account, try again!")

            except errors.WriteError as we:
                print(we)
                msg = messagebox.showinfo("Warning", "Failed to register new account, try again!")

        else:
            msg = messagebox.showinfo("Warning", "Duplicate username, try again.")

        client.close()


def login_page():
    WINDOW_WIDTH = 700
    WINDOW_HEIGHT = 400
    window = tk.Tk()
    window.geometry(str(WINDOW_WIDTH) + "x" + str(WINDOW_HEIGHT))
    window.title("HealthCV")
    window.resizable(False, False)
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
    register_but = ttk.Button(tab2, text="Register", command=lambda: validate_register_credentials(new_uname_tf.get(), new_pwd_tf.get()))
    register_but.grid(row=2, column=0, pady=5, columnspan=2)
    notebook.add(tab2, text="Registration tab")
    notebook.pack()
    window.mainloop()


if __name__ == "__main__":
    login_page()
