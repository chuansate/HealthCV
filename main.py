import tkinter as tk
from tkinter import *
from tkinter import ttk, messagebox
from PIL import Image, ImageTk


def home_page():
    WINDOW_WIDTH = 700
    WINDOW_HEIGHT = 400
    window = tk.Tk()
    window.geometry(str(WINDOW_WIDTH) + "x" + str(WINDOW_HEIGHT))
    window.title("Home Page")
    app_name_lb = Label(window, text="Home Page")
    # Three buttons: Fitness games, Guides, Workout plan (setting sets and reps, then record the data on everyday)

    app_name_lb.place(x=20, y=20)
    window.mainloop()


def validate_login_credentials(window, entered_uname, entered_pwd):
    if entered_uname == "Low" and entered_pwd == "Low123":
        window.destroy()
        home_page()
    else:
        msg = messagebox.showinfo("Warning", "Invalid credentials, try again.")


def login_page():
    WINDOW_WIDTH = 700
    WINDOW_HEIGHT = 400
    window = tk.Tk()
    window.geometry(str(WINDOW_WIDTH) + "x" + str(WINDOW_HEIGHT))
    window.title("HealthCV")
    bg_img = Image.open("./icons/login_background.png")
    bg_img = bg_img.resize((WINDOW_WIDTH, WINDOW_HEIGHT))
    bg_img = ImageTk.PhotoImage(bg_img, master=window)
    img_label = Label(window, image=bg_img)
    img_label.place(x=0, y=0)
    app_name_lb = Label(window, text="HealthCV")
    app_name_lb.place(x=20, y=20)
    app_name_lb.config(font=("Courier", 20))
    login_registration_frame = Frame(window)
    login_registration_frame.place(x=WINDOW_WIDTH-300, y=100)
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
    login_but = ttk.Button(tab1, text="Login", command=lambda: validate_login_credentials(window, uname_tf.get(), pwd_tf.get()))
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

