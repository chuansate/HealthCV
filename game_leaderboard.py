import tkinter as tk
from tkinter import *
from tkinter import ttk, messagebox

# Sample leaderboard data
leaderboard_data = {
    "Kick & Catch": [
        ("Alice", 1000),
        ("Bob", 850),
        ("Charlie", 700),
    ],
    "Yoga Imitation": [
        ("David", 98),
        ("Eve", 95),
        ("Frank", 90),
    ],
}


def go_back(uname, window):
    from fitness_games_page import fitness_games_page
    window.destroy()
    fitness_games_page(uname, None)


# Function to update leaderboard display
def update_leaderboard(frame, game):
    ttk.Label(frame, text=game + " Leaderboard", style="SubHeader.TLabel").pack(pady=10)
    for i, (player, score) in enumerate(leaderboard_data[game][:3]):
        label = ttk.Label(frame, text=f"{i+1}. {player} - {score}", font=("Arial", 14), style="List.TLabel")
        label.pack(pady=5)


def leaderboard_page(uname, window):
    if window is not None:
        # window could be None happen when the user is from kick_and_catch_game/yoga_poses_imitation_game to fitness_games_page
        window.destroy()
    WINDOW_WIDTH = 700
    WINDOW_HEIGHT = 400
    window = tk.Tk()
    window.geometry(str(WINDOW_WIDTH) + "x" + str(WINDOW_HEIGHT))
    window.title("Leaderboard page")
    # Create notebook with tabs for each game
    notebook = ttk.Notebook(window)
    notebook.pack(fill=tk.BOTH, expand=True)

    # Add tabs for each game
    kick_and_catch_frame = ttk.Frame(notebook)
    yoga_imitation_frame = ttk.Frame(notebook)
    # Update initial leaderboard display
    update_leaderboard(kick_and_catch_frame, "Kick & Catch")
    update_leaderboard(yoga_imitation_frame, "Yoga Imitation")
    notebook.add(kick_and_catch_frame, text="Kick & Catch")
    notebook.add(yoga_imitation_frame, text="Yoga Imitation")

    logout_button = tk.Button(window, text="Go back", command=lambda: go_back(uname, window))
    logout_button.place(x=WINDOW_WIDTH - 100, y=WINDOW_HEIGHT - 50)
    window.mainloop()