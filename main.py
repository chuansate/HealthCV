import tkinter as tk
from tkinter import *
from tkinter import ttk, messagebox
from fitness_games_page import fitness_games_page
from guides_page import guides_page
from workout_plan_page import workout_plan_page
import pymongo
from PIL import Image, ImageTk
from pymongo import errors
from data_models import User

from paths_to_images import PATH_TO_BACKGROUND_IMG


def validate_login_credentials(window, entered_uname, entered_pwd):
    user = User(entered_uname, entered_pwd)
    found = user.search_by_uname()
    if found is not None:
        if found["pwd"] == entered_pwd:
            from home_page import home_page
            window.destroy()
            home_page(entered_uname)
        else:
            msg = messagebox.showinfo("Warning", "Incorrect password, try again.")
    else:
        msg = messagebox.showinfo("Warning", "Username does not exist, try again.")


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
        new_user = User(entered_uname, entered_pwd)
        found = new_user.search_by_uname()
        if found is None:
            try:
                new_user.create_new_user()
                msg = messagebox.showinfo("Information", "New account has been registered!")
            except errors.WriteConcernError as wce:
                print(wce)
                msg = messagebox.showinfo("Warning", "Failed to register new account, try again!")

            except errors.WriteError as we:
                print(we)
                msg = messagebox.showinfo("Warning", "Failed to register new account, try again!")

        else:
            msg = messagebox.showinfo("Warning", "Duplicate username, try again.")


def login_page():
    WINDOW_WIDTH = 700
    WINDOW_HEIGHT = 400
    window = tk.Tk()
    window.geometry(str(WINDOW_WIDTH) + "x" + str(WINDOW_HEIGHT))
    window.title("HealthCV")
    window.resizable(False, False)
    bg_img = Image.open(PATH_TO_BACKGROUND_IMG)
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
    notebook.add(tab1, text="Login")
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
    notebook.add(tab2, text="Registration")
    notebook.pack()
    window.mainloop()


if __name__ == "__main__":
    login_page()
