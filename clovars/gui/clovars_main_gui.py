import tkinter as tk
import subprocess
import sys

# Define functions
def open_window(script_name: str):
    subprocess.Popen([sys.executable, script_name])

def run_clicked(): open_window("clovars/gui/run_window.py")
def view_clicked(): open_window("clovars/gui/view_window.py")
def analyse_clicked(): open_window("clovars/gui/analyse_window.py")
def fit_clicked(): open_window("clovars/gui/fit_window.py")

# Create Window
root = tk.Tk()
root.title("CloVarS - Clonal Variability Simulator")
root.geometry("600x400")  # Make window bigger
root.configure(bg="#0D1117")  # Dark azure background

# Style configurations
TITLE_FONT = ("Helvetica", 32, "bold")
BUTTON_FONT = ("Helvetica", 14)
BUTTON_WIDTH = 20
BUTTON_HEIGHT = 2
BUTTON_BG = "#21262D"  # Darker button
BUTTON_FG = "#C9D1D9"  # Light text
BUTTON_ACTIVE_BG = "#30363D"  # Button color when pressed
BUTTON_ACTIVE_FG = "#58A6FF"  # Light blue text when pressed

# Create features
main_title = tk.Label(
    root,
    text="CloVarS",
    font=TITLE_FONT,
    bg="#0D1117",
    fg="#58A6FF",  # Azure blue title
    pady=20
)

btn_run = tk.Button(
    root, text="Run", command=run_clicked,
    font=BUTTON_FONT, width=BUTTON_WIDTH, height=BUTTON_HEIGHT,
    bg=BUTTON_BG, fg=BUTTON_FG,
    activebackground=BUTTON_ACTIVE_BG,
    activeforeground=BUTTON_ACTIVE_FG,
    bd=0, relief="flat"
)

btn_view = tk.Button(
    root, text="View", command=view_clicked,
    font=BUTTON_FONT, width=BUTTON_WIDTH, height=BUTTON_HEIGHT,
    bg=BUTTON_BG, fg=BUTTON_FG,
    activebackground=BUTTON_ACTIVE_BG,
    activeforeground=BUTTON_ACTIVE_FG,
    bd=0, relief="flat"
)

btn_analyse = tk.Button(
    root, text="Analyse", command=analyse_clicked,
    font=BUTTON_FONT, width=BUTTON_WIDTH, height=BUTTON_HEIGHT,
    bg=BUTTON_BG, fg=BUTTON_FG,
    activebackground=BUTTON_ACTIVE_BG,
    activeforeground=BUTTON_ACTIVE_FG,
    bd=0, relief="flat"
)

btn_fit = tk.Button(
    root, text="Fit", command=fit_clicked,
    font=BUTTON_FONT, width=BUTTON_WIDTH, height=BUTTON_HEIGHT,
    bg=BUTTON_BG, fg=BUTTON_FG,
    activebackground=BUTTON_ACTIVE_BG,
    activeforeground=BUTTON_ACTIVE_FG,
    bd=0, relief="flat"
)

# Add features to window
main_title.pack()

btn_run.pack(pady=10)
btn_view.pack(pady=10)
btn_analyse.pack(pady=10)
btn_fit.pack(pady=10)

# Run window
root.mainloop()
