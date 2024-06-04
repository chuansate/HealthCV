import tkinter as tk
from tkinter import *
from tkinter import ttk, messagebox
from PIL import Image, ImageTk
from paths_to_images import PATH_TO_SCORE_IMG
from data_models import Game
from data_models import User

# leaderboard_data = {
#     "Kick & Catch": [
#         ("Alice", 1000),
#         ("Bob", 850),
#         ("Charlie", 700),
#     ],
#     "Yoga Imitation": [
#         ("David", 98),
#         ("Eve", 95),
#         ("Frank", 90),
#     ],
# }

# the keys are game names, and the values are lists of tuples (player_name, score)
leaderboard_data = {}


def return_score_only(tup):
    return tup[1]


def go_back(uname, window):
    from fitness_games_page import fitness_games_page
    window.destroy()
    fitness_games_page(uname, None)


def load_leaderboard_data(top_number):
    g = Game()
    games_ids_names_list = g.get_all_games_ids_names()
    best_records_by_each_user = g.get_best_records_by_each_user()
    for row in games_ids_names_list:
        best_records_by_each_user[str(row["_id"])].sort(key=return_score_only, reverse=True)

    for row in games_ids_names_list:
        leaderboard_data[row["game_name"]] = best_records_by_each_user[str(row["_id"])][:top_number]


# Function to update leaderboard display
def update_leaderboard(frame, game, rec_width):
    tk.Label(frame, text=game + " Leaderboard").pack(pady=10)
    # DK WHY ISNT IT SHOWING THE TROPHY ICON??
    score_img = Image.open(PATH_TO_SCORE_IMG)
    score_img = ImageTk.PhotoImage(score_img)
    for i, (player, score) in enumerate(leaderboard_data[game]):
        rec = tk.Frame(frame, bg="gray", height=35, width=rec_width)
        rec.pack(pady=5, side=TOP)
        index_label = tk.Label(rec, text=f"{i+1}. ", fg="white", bg="gray", font=("Arial", 14))
        index_label.place(x=20, y=3)
        name_label = tk.Label(rec, text=f"{player}", fg="white", bg="gray", font=("Arial", 14))
        name_label.place(x=50, y=3)
        img_label = Label(rec, image=score_img, bg="gray")
        img_label.place(x=rec_width-130, y=0)
        img_label.image = score_img
        score_label = tk.Label(rec, text=f"{str(score)}", fg="white", bg="gray", font=("Arial", 14))
        score_label.place(x=rec_width-80, y=3)


def leaderboard_page(uname, window):
    if window is not None:
        # window could be None happen when the user is from kick_and_catch_game/yoga_poses_imitation_game to fitness_games_page
        window.destroy()

    # displaying top 3 players only in each game
    load_leaderboard_data(top_number=3)
    WINDOW_WIDTH = 700
    WINDOW_HEIGHT = 400
    window = tk.Tk()
    window.geometry(str(WINDOW_WIDTH) + "x" + str(WINDOW_HEIGHT))
    window.resizable(False, False)
    window.title("Leaderboard page")
    # Create notebook with tabs for each game
    notebook = ttk.Notebook(window)
    notebook.pack(fill=tk.BOTH, expand=True)

    # Add tabs for each game
    kick_and_catch_frame = ttk.Frame(notebook)
    yoga_imitation_frame = ttk.Frame(notebook)
    # Update initial leaderboard display
    update_leaderboard(kick_and_catch_frame, "Kick-And-Catch", WINDOW_WIDTH-100)
    update_leaderboard(yoga_imitation_frame, "Yoga Imitation", WINDOW_WIDTH-100)
    notebook.add(kick_and_catch_frame, text="Kick-And-Catch")
    notebook.add(yoga_imitation_frame, text="Yoga Imitation")

    logout_button = tk.Button(window, text="Go back", command=lambda: go_back(uname, window))
    logout_button.place(x=WINDOW_WIDTH - 100, y=WINDOW_HEIGHT - 50)
    window.mainloop()