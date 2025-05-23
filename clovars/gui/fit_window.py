import tkinter as tk
from tkinter import filedialog
import toml
import os
from clovars.IO.parameter_validator import FitParameterValidator
from clovars.simulation import fit_experimental_data_function

SETTINGS_PATH = "gui_settings/fit_settings.toml"

# ================ STYLE CONSTANTS ================
BG_COLOR = "#0D1117"
LABEL_FONT = ("Helvetica", 12)
ENTRY_FONT = ("Helvetica", 11)
BUTTON_FONT = ("Helvetica", 14, "bold")
TITLE_FONT = ("Helvetica", 14, "bold")
SECTION_FONT = ("Helvetica", 12)
BUTTON_BG = "#21262D"
BUTTON_FG = "#C9D1D9"
BUTTON_ACTIVE_BG = "#30363D"
BUTTON_ACTIVE_FG = "#58A6FF"
ENTRY_BG = "#21262D"
ENTRY_FG = "#C9D1D9"
TEXT_COLOR = "#C9D1D9"

# Load settings from TOML
def load_settings():
    if os.path.exists(SETTINGS_PATH):
        with open(SETTINGS_PATH, "r") as f:
            return toml.load(f)
    else:
        return {
            "verbose": False,
            "input": {
                "input_file": "",
                "sheet_name": "",
                "division_hours_column_name": "",
                "death_hours_column_name": ""
            }
        }

# Save settings to TOML
def save_settings():
    new_data = {
        "verbose": False,
        "input": {
            "input_file": input_file_entry.get(),
            "sheet_name": sheet_name_entry.get(),
            "division_hours_column_name": division_column_entry.get(),
            "death_hours_column_name": death_column_entry.get()
        }
    }
    os.makedirs(os.path.dirname(SETTINGS_PATH), exist_ok=True)
    with open(SETTINGS_PATH, "w") as f:
        toml.dump(new_data, f)

def view_clovars():

    save_settings()

    validator = FitParameterValidator()
    validator.parse_toml(SETTINGS_PATH)
    validator.validate()
    fit_params = validator.to_simulation()

    fit_experimental_data_function(**fit_params)

def browse_file():
    filename = filedialog.askopenfilename()
    if filename:
        input_file_entry.delete(0, tk.END)
        input_file_entry.insert(0, filename)

# Load current settings
settings = load_settings()
input_settings = settings.get("input", {})

# Create window
root = tk.Tk()
root.title("CloVarS - Fit")
root.geometry("400x500")
root.configure(bg=BG_COLOR)

# Create widgets with consistent styling
main_title = tk.Label(root,
                     text="CloVarS - Fit",
                     font=TITLE_FONT,
                     bg=BG_COLOR,
                     fg="#58A6FF")
run_settings_title = tk.Label(root,
                            text="Fit Settings",
                            font=SECTION_FONT,
                            bg=BG_COLOR,
                            fg=TEXT_COLOR)

def create_label(text):
    return tk.Label(root,
                   text=text,
                   font=LABEL_FONT,
                   bg=BG_COLOR,
                   fg=TEXT_COLOR,
                   anchor="w")

def create_entry():
    return tk.Entry(root,
                  width=40,
                  font=ENTRY_FONT,
                  bg=ENTRY_BG,
                  fg=ENTRY_FG,
                  insertbackground=ENTRY_FG)

# Input File Section
input_file_label = create_label("Input File:")
input_file_entry = create_entry()
input_file_entry.insert(0, input_settings.get("input_file", ""))
input_file_button = tk.Button(root,
                            text="Browse",
                            command=browse_file,
                            font=BUTTON_FONT,
                            bg=BUTTON_BG,
                            fg=BUTTON_FG,
                            activebackground=BUTTON_ACTIVE_BG,
                            activeforeground=BUTTON_ACTIVE_FG,
                            bd=0,
                            relief="flat")

# Sheet Name Section
sheet_name_label = create_label("Sheet Name:")
sheet_name_entry = create_entry()
sheet_name_entry.insert(0, input_settings.get("sheet_name", ""))

# Division Column Section
division_column_label = create_label("Division Column Name:")
division_column_entry = create_entry()
division_column_entry.insert(0, input_settings.get("division_hours_column_name", ""))

# Death Column Section
death_column_label = create_label("Death Column Name:")
death_column_entry = create_entry()
death_column_entry.insert(0, input_settings.get("death_hours_column_name", ""))

# Fit Button
view_btn = tk.Button(root,
                    text="Fit!",
                    command=view_clovars,
                    font=BUTTON_FONT,
                    bg=BUTTON_BG,
                    fg=BUTTON_FG,
                    activebackground=BUTTON_ACTIVE_BG,
                    activeforeground=BUTTON_ACTIVE_FG,
                    bd=0,
                    relief="flat",
                    width=15)

# Layout with consistent padding
main_title.pack(pady=(20, 10))
run_settings_title.pack(pady=(0, 15))

input_file_label.pack(fill="x", padx=20, pady=(5, 0))
input_file_entry.pack(fill="x", padx=20, pady=(0, 5))
input_file_button.pack(pady=(0, 15), padx=20)

sheet_name_label.pack(fill="x", padx=20, pady=(5, 0))
sheet_name_entry.pack(fill="x", padx=20, pady=(0, 15))

division_column_label.pack(fill="x", padx=20, pady=(5, 0))
division_column_entry.pack(fill="x", padx=20, pady=(0, 15))

death_column_label.pack(fill="x", padx=20, pady=(5, 0))
death_column_entry.pack(fill="x", padx=20, pady=(0, 20))

view_btn.pack(pady=20)

# Initialize window
root.mainloop()