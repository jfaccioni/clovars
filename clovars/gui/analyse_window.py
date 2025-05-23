import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import toml
import os
from clovars.IO.parameter_validator import AnalysisParameterValidator
from clovars.simulation import analyse_simulation_function

SETTINGS_PATH = "gui_settings/analyse_settings.toml"

# Load settings from TOML
def load_settings():
    if os.path.exists(SETTINGS_PATH):
        with open(SETTINGS_PATH, "r") as f:
            return toml.load(f)
    else:
        return {
            "verbose": True,
            "input": {},
            "dynafit": {},
            "tree_stats": {},
            "cell_fate_distribution": {},
            "cell_fitness_distribution": {},
            "colony_division_times": {},
            "videos": {}
        }

# Save settings to TOML
def save_settings():
    new_data = {
        "verbose": True,
        "input": {
            "simulation_input_folder": simulation_input_entry.get(),
            "parameters_file_name": parameters_file_entry.get(),
            "cell_csv_file_name": cell_csv_entry.get(),
            "colony_csv_file_name": colony_csv_entry.get()
        },
        "tree_stats": {
            "perform": tree_stats_perform_var.get(),
            "bootstrap_n": int(tree_stats_bootstrap_entry.get())
        },
        "dynafit": {
            "perform": dynafit_perform_var.get(),
            "start_day": float(start_day_entry.get()),
            "end_day": float(end_day_entry.get()),
            "filter_colonies_smaller_than": int(filter_colonies_entry.get()),
            "merge_colonies_of_different_sizes": merge_sizes_var.get(),
            "number_of_bins_to_merge_on": int(bins_to_merge_entry.get()),
            "bootstrap_n": int(dynafit_bootstrap_entry.get()),
            "use_log2_colony_size": use_log2_var.get()
        },
        "cell_fate_distribution": {
            "display": cell_fate_display_var.get(),
            "render": cell_fate_render_var.get(),
            "join_treatments": cell_fate_join_var.get(),
            "render_file_name": cell_fate_filename_entry.get(),
            "render_file_extension": cell_fate_extension_entry.get()
        },
        "cell_fitness_distribution": {
            "perform": cell_fitness_perform_var.get()
        },
        "colony_division_times": {
            "perform": division_times_perform_var.get()
        },
        "videos": {
            "render_colony_signal_vs_size": video_signal_size_var.get(),
            "render_colony_fitness_distribution": video_fitness_var.get()
        }
    }
    os.makedirs(os.path.dirname(SETTINGS_PATH), exist_ok=True)
    with open(SETTINGS_PATH, "w") as f:
        toml.dump(new_data, f)

def analyse_clovars():
    save_settings()

    validator = AnalysisParameterValidator()
    validator.parse_toml(SETTINGS_PATH)
    validator.validate()
    analysis_params = validator.to_simulation()

    analyse_simulation_function(**analysis_params)

    messagebox.showinfo("Success", "Analysis runned successfully!")


def browse_folder():
    folder = filedialog.askdirectory()
    if folder:
        simulation_input_entry.delete(0, tk.END)
        simulation_input_entry.insert(0, folder)

# Load current settings
settings = load_settings()
input_settings = settings.get("input", {})
dynafit_settings = settings.get("dynafit", {})
tree_stats_settings = settings.get("tree_stats", {})
cell_fate_settings = settings.get("cell_fate_distribution", {})
cell_fitness_settings = settings.get("cell_fitness_distribution", {})
division_times_settings = settings.get("colony_division_times", {})
videos_settings = settings.get("videos", {})

# Create window
root = tk.Tk()
root.title("CloVarS - Analyse")
root.geometry("700x700")
root.configure(bg="#0D1117")

# Style configurations
LABEL_FONT = ("Helvetica", 12)
ENTRY_FONT = ("Helvetica", 11)
BUTTON_FONT = ("Helvetica", 14, "bold")
BUTTON_BG = "#21262D"
BUTTON_FG = "#C9D1D9"
BUTTON_ACTIVE_BG = "#30363D"
BUTTON_ACTIVE_FG = "#58A6FF"

# Notebook
style = ttk.Style()
style.theme_use('default')
style.configure('TNotebook', background="#0D1117", borderwidth=0)
style.configure('TNotebook.Tab', background="#21262D", foreground="#C9D1D9", padding=[10, 5])
style.map('TNotebook.Tab', background=[('selected', '#30363D')], foreground=[('selected', '#58A6FF')])

notebook = ttk.Notebook(root)

# 1. INPUT TAB
input_tab = tk.Frame(notebook, bg="#0D1117")
notebook.add(input_tab, text="Input")

def create_label(tab, text):
    return tk.Label(tab, text=text, bg="#0D1117", fg="#C9D1D9", font=LABEL_FONT, anchor="w")

simulation_input_label = create_label(input_tab, "Simulation Input Folder:")
simulation_input_entry = tk.Entry(input_tab, width=50, font=ENTRY_FONT, bg="#21262D", fg="#C9D1D9", insertbackground="#C9D1D9")
simulation_input_entry.insert(0, input_settings.get("simulation_input_folder", ""))
browse_button = tk.Button(input_tab, text="Browse", command=browse_folder,
                           font=BUTTON_FONT, bg=BUTTON_BG, fg=BUTTON_FG,
                           activebackground=BUTTON_ACTIVE_BG, activeforeground=BUTTON_ACTIVE_FG, bd=0, relief="flat")

parameters_file_label = create_label(input_tab, "Parameters File Name:")
parameters_file_entry = tk.Entry(input_tab, width=50, font=ENTRY_FONT, bg="#21262D", fg="#C9D1D9", insertbackground="#C9D1D9")
parameters_file_entry.insert(0, input_settings.get("parameters_file_name", ""))

cell_csv_label = create_label(input_tab, "Cell CSV File Name:")
cell_csv_entry = tk.Entry(input_tab, width=50, font=ENTRY_FONT, bg="#21262D", fg="#C9D1D9", insertbackground="#C9D1D9")
cell_csv_entry.insert(0, input_settings.get("cell_csv_file_name", ""))

colony_csv_label = create_label(input_tab, "Colony CSV File Name:")
colony_csv_entry = tk.Entry(input_tab, width=50, font=ENTRY_FONT, bg="#21262D", fg="#C9D1D9", insertbackground="#C9D1D9")
colony_csv_entry.insert(0, input_settings.get("colony_csv_file_name", ""))

# Layout Input Tab
for widget in [simulation_input_label, simulation_input_entry, browse_button,
               parameters_file_label, parameters_file_entry,
               cell_csv_label, cell_csv_entry,
               colony_csv_label, colony_csv_entry]:
    widget.pack(fill="x", padx=10, pady=5)

# 2. DYNafit TAB
dynafit_tab = tk.Frame(notebook, bg="#0D1117")
notebook.add(dynafit_tab, text="Dynafit")

dynafit_perform_var = tk.BooleanVar(value=dynafit_settings.get("perform", False))
tk.Checkbutton(dynafit_tab, text="Perform Dynafit", variable=dynafit_perform_var,
               bg="#0D1117", fg="#C9D1D9", selectcolor="#0D1117", font=LABEL_FONT, activebackground="#0D1117",  activeforeground="#58A6FF").pack(anchor="w", padx=10, pady=5)

start_day_entry = tk.Entry(dynafit_tab, width=20, font=ENTRY_FONT, bg="#21262D", fg="#C9D1D9", insertbackground="#C9D1D9")
start_day_entry.insert(0, dynafit_settings.get("start_day", 4.0))
create_label(dynafit_tab, "Start Day:").pack(anchor="w", padx=10)
start_day_entry.pack(padx=10, pady=2)

end_day_entry = tk.Entry(dynafit_tab, width=20, font=ENTRY_FONT, bg="#21262D", fg="#C9D1D9", insertbackground="#C9D1D9")
end_day_entry.insert(0, dynafit_settings.get("end_day", 7.0))
create_label(dynafit_tab, "End Day:").pack(anchor="w", padx=10)
end_day_entry.pack(padx=10, pady=2)

filter_colonies_entry = tk.Entry(dynafit_tab, width=20, font=ENTRY_FONT, bg="#21262D", fg="#C9D1D9", insertbackground="#C9D1D9")
filter_colonies_entry.insert(0, dynafit_settings.get("filter_colonies_smaller_than", 0))
create_label(dynafit_tab, "Filter Colonies Smaller Than:").pack(anchor="w", padx=10)
filter_colonies_entry.pack(padx=10, pady=2)

merge_sizes_var = tk.BooleanVar(value=dynafit_settings.get("merge_colonies_of_different_sizes", False))
tk.Checkbutton(dynafit_tab, text="Merge Colonies of Different Sizes", variable=merge_sizes_var,
               bg="#0D1117", fg="#C9D1D9", selectcolor="#0D1117", font=LABEL_FONT, activebackground="#0D1117", activeforeground="#58A6FF").pack(anchor="w", padx=10, pady=5)

bins_to_merge_entry = tk.Entry(dynafit_tab, width=20, font=ENTRY_FONT, bg="#21262D", fg="#C9D1D9", insertbackground="#C9D1D9")
bins_to_merge_entry.insert(0, dynafit_settings.get("number_of_bins_to_merge_on", 10))
create_label(dynafit_tab, "Number of Bins to Merge On:").pack(anchor="w", padx=10)
bins_to_merge_entry.pack(padx=10, pady=2)

dynafit_bootstrap_entry = tk.Entry(dynafit_tab, width=20, font=ENTRY_FONT, bg="#21262D", fg="#C9D1D9", insertbackground="#C9D1D9")
dynafit_bootstrap_entry.insert(0, dynafit_settings.get("bootstrap_n", 100))
create_label(dynafit_tab, "Bootstrap N:").pack(anchor="w", padx=10)
dynafit_bootstrap_entry.pack(padx=10, pady=2)

use_log2_var = tk.BooleanVar(value=dynafit_settings.get("use_log2_colony_size", False))
tk.Checkbutton(dynafit_tab, text="Use log2(Colony Size)", variable=use_log2_var,
               bg="#0D1117", fg="#C9D1D9", selectcolor="#0D1117", font=LABEL_FONT, activebackground="#0D1117", activeforeground="#58A6FF").pack(anchor="w", padx=10, pady=5)

# 3. TREE STATS TAB
tree_stats_tab = tk.Frame(notebook, bg="#0D1117")
notebook.add(tree_stats_tab, text="Tree Stats")

tree_stats_perform_var = tk.BooleanVar(value=tree_stats_settings.get("perform", False))
tk.Checkbutton(tree_stats_tab, text="Perform Tree Stats", variable=tree_stats_perform_var,
               bg="#0D1117", fg="#C9D1D9", selectcolor="#0D1117", font=LABEL_FONT, activebackground="#0D1117",  activeforeground="#58A6FF").pack(anchor="w", padx=10, pady=5)

tree_stats_bootstrap_entry = tk.Entry(tree_stats_tab, width=20, font=ENTRY_FONT, bg="#21262D", fg="#C9D1D9", insertbackground="#C9D1D9")
tree_stats_bootstrap_entry.insert(0, tree_stats_settings.get("bootstrap_n", 1000))
create_label(tree_stats_tab, "Bootstrap N:").pack(anchor="w", padx=10)
tree_stats_bootstrap_entry.pack(padx=10, pady=2)

# 4. CELL FATE DISTRIBUTION TAB
cell_fate_tab = tk.Frame(notebook, bg="#0D1117")
notebook.add(cell_fate_tab, text="Cell Fate")

cell_fate_display_var = tk.BooleanVar(value=cell_fate_settings.get("display", True))
tk.Checkbutton(cell_fate_tab, text="Display Cell Fate Distribution", variable=cell_fate_display_var,
               bg="#0D1117", fg="#C9D1D9", selectcolor="#0D1117", font=LABEL_FONT, activebackground="#0D1117", activeforeground="#58A6FF").pack(anchor="w", padx=10, pady=5)

cell_fate_render_var = tk.BooleanVar(value=cell_fate_settings.get("render", False))
tk.Checkbutton(cell_fate_tab, text="Render Cell Fate Distribution", variable=cell_fate_render_var,
               bg="#0D1117", fg="#C9D1D9", selectcolor="#0D1117", font=LABEL_FONT, activebackground="#0D1117", activeforeground="#58A6FF").pack(anchor="w", padx=10, pady=5)

cell_fate_join_var = tk.BooleanVar(value=cell_fate_settings.get("join_treatments", False))
tk.Checkbutton(cell_fate_tab, text="Join Treatments", variable=cell_fate_join_var,
               bg="#0D1117", fg="#C9D1D9", selectcolor="#0D1117", font=LABEL_FONT, activebackground="#0D1117", activeforeground="#58A6FF").pack(anchor="w", padx=10, pady=5)

cell_fate_filename_entry = tk.Entry(cell_fate_tab, width=30, font=ENTRY_FONT, bg="#21262D", fg="#C9D1D9", insertbackground="#C9D1D9")
cell_fate_filename_entry.insert(0, cell_fate_settings.get("render_file_name", "cell_fate_distribution"))
create_label(cell_fate_tab, "Render File Name:").pack(anchor="w", padx=10)
cell_fate_filename_entry.pack(padx=10, pady=2)

cell_fate_extension_entry = tk.Entry(cell_fate_tab, width=10, font=ENTRY_FONT, bg="#21262D", fg="#C9D1D9", insertbackground="#C9D1D9")
cell_fate_extension_entry.insert(0, cell_fate_settings.get("render_file_extension", "png"))
create_label(cell_fate_tab, "Render File Extension (png/svg):").pack(anchor="w", padx=10)
cell_fate_extension_entry.pack(padx=10, pady=2)

# 5. CELL FITNESS DISTRIBUTION TAB
cell_fitness_tab = tk.Frame(notebook, bg="#0D1117")
notebook.add(cell_fitness_tab, text="Cell Fitness")

cell_fitness_perform_var = tk.BooleanVar(value=cell_fitness_settings.get("perform", False))
tk.Checkbutton(cell_fitness_tab, text="Perform Cell Fitness Distribution Analysis", variable=cell_fitness_perform_var,
               bg="#0D1117", fg="#C9D1D9", selectcolor="#0D1117", font=LABEL_FONT, activebackground="#0D1117", activeforeground="#58A6FF").pack(anchor="w", padx=10, pady=5)

# 6. COLONY DIVISION TIMES TAB
division_times_tab = tk.Frame(notebook, bg="#0D1117")
notebook.add(division_times_tab, text="Division Times")

division_times_perform_var = tk.BooleanVar(value=division_times_settings.get("perform", False))
tk.Checkbutton(division_times_tab, text="Perform Colony Division Times Analysis", variable=division_times_perform_var,
               bg="#0D1117", fg="#C9D1D9", selectcolor="#0D1117", font=LABEL_FONT, activebackground="#0D1117", activeforeground="#58A6FF").pack(anchor="w", padx=10, pady=5)

# 7. VIDEOS TAB
videos_tab = tk.Frame(notebook, bg="#0D1117")
notebook.add(videos_tab, text="Videos")

video_signal_size_var = tk.BooleanVar(value=videos_settings.get("render_colony_signal_vs_size", False))
tk.Checkbutton(videos_tab, text="Render Colony Signal vs Size Video", variable=video_signal_size_var,
               bg="#0D1117", fg="#C9D1D9", selectcolor="#0D1117", font=LABEL_FONT, activebackground="#0D1117", activeforeground="#58A6FF").pack(anchor="w", padx=10, pady=5)

video_fitness_var = tk.BooleanVar(value=videos_settings.get("render_colony_fitness_distribution", False))
tk.Checkbutton(videos_tab, text="Render Colony Fitness Distribution Video", variable=video_fitness_var,
               bg="#0D1117", fg="#C9D1D9", selectcolor="#0D1117", font=LABEL_FONT, activebackground="#0D1117", activeforeground="#58A6FF").pack(anchor="w", padx=10, pady=5)

# Pack notebook
notebook.pack(expand=True, fill="both", padx=10, pady=10)

# Analyse Button
analyse_btn = tk.Button(root, text="Analyse!", command=analyse_clovars,
                        font=BUTTON_FONT, width=20,
                        bg=BUTTON_BG, fg=BUTTON_FG,
                        activebackground=BUTTON_ACTIVE_BG, activeforeground=BUTTON_ACTIVE_FG,
                        bd=0, relief="flat")
analyse_btn.pack(pady=20)

# Run GUI
root.mainloop()