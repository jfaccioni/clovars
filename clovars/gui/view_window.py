import tkinter as tk
from tkinter import ttk, filedialog

from clovars.simulation import view_simulation_function
from clovars.IO.parameter_validator import ViewParameterValidator
import toml

# ================ STYLE CONSTANTS ================
BG_COLOR = "#0D1117"
TAB_BG = "#0D1117"  # Background for notebook tabs
FRAME_BG = "#0D1117"  # Background for notebook frames
LABEL_FONT = ("Helvetica", 12)
ENTRY_FONT = ("Helvetica", 11)
BUTTON_FONT = ("Helvetica", 12, "bold")
TITLE_FONT = ("Helvetica", 14, "bold")
BUTTON_BG = "#21262D"
BUTTON_FG = "#C9D1D9"
BUTTON_ACTIVE_BG = "#30363D"
BUTTON_ACTIVE_FG = "#58A6FF"
ENTRY_BG = "#21262D"
ENTRY_FG = "#C9D1D9"
TEXT_COLOR = "#C9D1D9"
CHECKBOX_BG = BG_COLOR
CHECKBOX_FG = "#C9D1D9"
OPTIONMENU_BG = "#21262D"
OPTIONMENU_FG = "#C9D1D9"
FRAME_PADX = 20
FRAME_PADY = 10

# Global variables for entry fields
verbose_var = None
sim_folder_entry = None
params_entry = None
cell_entry = None
colony_entry = None
colormap_var = None
layout_var = None
dpi_entry = None
view_2d_display_var = None
view_2d_render_var = None
view_2d_file_entry = None
view_2d_ext_var = None
video_2d_render_var = None
video_2d_file_entry = None
video_2d_ext_var = None
view_3d_display_var = None
view_3d_render_var = None
view_3d_display_well_var = None
z_axis_ratio_entry = None
view_3d_file_entry = None
view_3d_ext_var = None
treat_display_var = None
treat_render_var = None
treat_div_var = None
treat_death_var = None
treat_file_entry = None
treat_ext_var = None

SETTINGS_PATH = "gui_settings/view_settings.toml"

def main():
    global verbose_var

    config = toml.load(SETTINGS_PATH)

    root = tk.Tk()
    root.title("CloVarS - View")
    root.geometry("700x700")
    root.configure(bg=BG_COLOR)

    # Configure notebook style - THIS IS THE FIXED VERSION
    style = ttk.Style()
    style.theme_use('alt')

    # Configure the notebook background
    style.configure('TNotebook', background=BG_COLOR, borderwidth=0)

    # Configure the tab appearance
    style.configure('TNotebook.Tab',
                    background="#21262D",
                    foreground="#C9D1D9",
                    padding=[10, 5],
                    font=LABEL_FONT)
    style.map('TNotebook.Tab',
              background=[('selected', '#30363D')],
              foreground=[('selected', '#58A6FF')])

    # Configure the frame that holds the tabs
    style.configure('TNotebook.PanedWindow', background=BG_COLOR)

    # Configure the content area of the notebook
    style.configure('TFrame', background=FRAME_BG)

    # Main title
    tk.Label(root,
             text="CloVarS - View",
             font=TITLE_FONT,
             bg=BG_COLOR,
             fg="#58A6FF").pack(pady=10)

    notebook = ttk.Notebook(root, style='TNotebook')

    # Create a custom style for the notebook that forces the background
    notebook_style = ttk.Style()
    notebook_style.configure('Custom.TNotebook', background=BG_COLOR)
    notebook_style.configure('Custom.TNotebook.Tab',
                             background="#21262D",
                             foreground="#C9D1D9",
                             padding=[10, 5])
    notebook_style.map('Custom.TNotebook.Tab',
                       background=[('selected', '#30363D')],
                       foreground=[('selected', '#58A6FF')])

    notebook = ttk.Notebook(root, style='Custom.TNotebook')
    notebook.pack(fill='both', expand=True, padx=10, pady=10)

    tabs = {}
    for section in config:
        # Create each tab with the proper background
        if section == "verbose": continue
        tab = ttk.Frame(notebook, style='Custom.TNotebook')
        notebook.add(tab, text=section.capitalize())
        tabs[section] = tab

        # Force the tab content background
        for child in tab.winfo_children():
            child.configure(background=FRAME_BG)

    # Build tabs
    build_input_tab(tabs["input"], config["input"])
    build_view_tab(tabs["view"], config["view"])
    build_2d_view_tab(tabs["2D_view"], config["2D_view"])
    build_2d_video_tab(tabs["2D_video"], config["2D_video"])
    build_3d_view_tab(tabs["3D_view"], config["3D_view"])
    build_treatment_tab(tabs["treatment_curves"], config["treatment_curves"])

    # View button
    tk.Button(root,
              text="View!",
              command=view_clovars,
              font=BUTTON_FONT,
              bg=BUTTON_BG,
              fg=BUTTON_FG,
              activebackground=BUTTON_ACTIVE_BG,
              activeforeground=BUTTON_ACTIVE_FG,
              bd=0,
              relief="flat",
              width=15).pack(pady=20)

    root.mainloop()


def create_browse_button(parent, entry_var, is_file=True):
    def browse():
        if is_file:
            path = filedialog.askopenfilename()
        else:
            path = filedialog.askdirectory()
        if path:
            entry_var.delete(0, tk.END)
            entry_var.insert(0, path)

    return tk.Button(parent,
                     text="Browse",
                     command=browse,
                     font=BUTTON_FONT,
                     bg=BUTTON_BG,
                     fg=BUTTON_FG,
                     activebackground=BUTTON_ACTIVE_BG,
                     activeforeground=BUTTON_ACTIVE_FG,
                     bd=0,
                     relief="flat")


def build_input_tab(frame, data):
    global sim_folder_entry, params_entry, cell_entry, colony_entry

    frame.grid_columnconfigure(1, weight=1)

    # Simulation Folder
    tk.Label(frame, text="Simulation Folder:", bg=BG_COLOR, fg=TEXT_COLOR).grid(
        row=0, column=0, sticky='w', padx=FRAME_PADX, pady=(FRAME_PADY, 0))
    sim_folder_entry = tk.Entry(frame, font=ENTRY_FONT, bg=ENTRY_BG, fg=ENTRY_FG,
                                insertbackground=ENTRY_FG)
    sim_folder_entry.insert(0, data["simulation_input_folder"])
    sim_folder_entry.grid(row=1, column=0, columnspan=2, sticky='ew', padx=FRAME_PADX)
    create_browse_button(frame, sim_folder_entry, is_file=False).grid(
        row=1, column=2, padx=(0, FRAME_PADX))

    # Parameters File
    tk.Label(frame, text="Parameters File:", bg=BG_COLOR, fg=TEXT_COLOR).grid(
        row=2, column=0, sticky='w', padx=FRAME_PADX, pady=(FRAME_PADY, 0))
    params_entry = tk.Entry(frame, font=ENTRY_FONT, bg=ENTRY_BG, fg=ENTRY_FG,
                            insertbackground=ENTRY_FG)
    params_entry.insert(0, data["parameters_file_name"])
    params_entry.grid(row=3, column=0, columnspan=2, sticky='ew', padx=FRAME_PADX)
    #create_browse_button(frame, params_entry).grid(row=3, column=2, padx=(0, FRAME_PADX))

    # Cell CSV File
    tk.Label(frame, text="Cell CSV File:", bg=BG_COLOR, fg=TEXT_COLOR).grid(
        row=4, column=0, sticky='w', padx=FRAME_PADX, pady=(FRAME_PADY, 0))
    cell_entry = tk.Entry(frame, font=ENTRY_FONT, bg=ENTRY_BG, fg=ENTRY_FG,
                          insertbackground=ENTRY_FG)
    cell_entry.insert(0, data["cell_csv_file_name"])
    cell_entry.grid(row=5, column=0, columnspan=2, sticky='ew', padx=FRAME_PADX)
    #create_browse_button(frame, cell_entry).grid(row=5, column=2, padx=(0, FRAME_PADX))

    # Colony CSV File
    tk.Label(frame, text="Colony CSV File:", bg=BG_COLOR, fg=TEXT_COLOR).grid(
        row=6, column=0, sticky='w', padx=FRAME_PADX, pady=(FRAME_PADY, 0))
    colony_entry = tk.Entry(frame, font=ENTRY_FONT, bg=ENTRY_BG, fg=ENTRY_FG,
                            insertbackground=ENTRY_FG)
    colony_entry.insert(0, data["colony_csv_file_name"])
    colony_entry.grid(row=7, column=0, columnspan=2, sticky='ew', padx=FRAME_PADX)
    #create_browse_button(frame, colony_entry).grid(row=7, column=2, padx=(0, FRAME_PADX))


def build_view_tab(frame, data):
    global colormap_var, layout_var, dpi_entry

    frame.grid_columnconfigure(1, weight=1)

    # Colormap
    tk.Label(frame, text="Colormap:", bg=BG_COLOR, fg=TEXT_COLOR).grid(
        row=0, column=0, sticky='w', padx=FRAME_PADX, pady=(FRAME_PADY, 0))
    colormap_var = tk.StringVar(value=data["colormap_name"])
    opt_menu = tk.OptionMenu(frame, colormap_var, "plasma", "viridis", "inferno", "magma")
    opt_menu.config(bg=OPTIONMENU_BG, fg=OPTIONMENU_FG,
                    activebackground=BUTTON_ACTIVE_BG,
                    activeforeground=BUTTON_ACTIVE_FG,
                    highlightthickness=0)
    opt_menu['menu'].config(bg=OPTIONMENU_BG, fg=OPTIONMENU_FG,
                            activebackground=BUTTON_ACTIVE_BG,
                            activeforeground=BUTTON_ACTIVE_FG)
    opt_menu.grid(row=1, column=0, sticky='ew', padx=FRAME_PADX)

    # Layout
    tk.Label(frame, text="Layout:", bg=BG_COLOR, fg=TEXT_COLOR).grid(
        row=2, column=0, sticky='w', padx=FRAME_PADX, pady=(FRAME_PADY, 0))
    layout_var = tk.StringVar(value=data["layout"])
    opt_menu = tk.OptionMenu(frame, layout_var, "family", "time", "age",
                             "generation", "division", "death", "signal")
    opt_menu.config(bg=OPTIONMENU_BG, fg=OPTIONMENU_FG,
                    activebackground=BUTTON_ACTIVE_BG,
                    activeforeground=BUTTON_ACTIVE_FG,
                    highlightthickness=0)
    opt_menu['menu'].config(bg=OPTIONMENU_BG, fg=OPTIONMENU_FG,
                            activebackground=BUTTON_ACTIVE_BG,
                            activeforeground=BUTTON_ACTIVE_FG)
    opt_menu.grid(row=3, column=0, sticky='ew', padx=FRAME_PADX)

    # DPI
    tk.Label(frame, text="DPI:", bg=BG_COLOR, fg=TEXT_COLOR).grid(
        row=4, column=0, sticky='w', padx=FRAME_PADX, pady=(FRAME_PADY, 0))
    dpi_entry = tk.Entry(frame, font=ENTRY_FONT, bg=ENTRY_BG, fg=ENTRY_FG,
                         insertbackground=ENTRY_FG)
    dpi_entry.insert(0, str(data["figure_dpi"]))
    dpi_entry.grid(row=5, column=0, sticky='ew', padx=FRAME_PADX)


def build_2d_view_tab(frame, data):
    global view_2d_display_var, view_2d_render_var, view_2d_file_entry, view_2d_ext_var

    frame.grid_columnconfigure(1, weight=1)

    # Display
    view_2d_display_var = tk.BooleanVar(value=data["display"])
    tk.Checkbutton(frame, text="Display", variable=view_2d_display_var,
                   bg=BG_COLOR, fg=TEXT_COLOR, selectcolor=BG_COLOR,
                   activebackground=BG_COLOR, activeforeground="#58A6FF").grid(
        row=0, column=0, sticky='w', padx=FRAME_PADX, pady=(FRAME_PADY, 0))

    # Render
    view_2d_render_var = tk.BooleanVar(value=data["render"])
    tk.Checkbutton(frame, text="Render", variable=view_2d_render_var,
                   bg=BG_COLOR, fg=TEXT_COLOR, selectcolor=BG_COLOR,
                   activebackground=BG_COLOR, activeforeground="#58A6FF").grid(
        row=1, column=0, sticky='w', padx=FRAME_PADX, pady=(FRAME_PADY, 0))

    # Render File Name
    tk.Label(frame, text="Render File Name:", bg=BG_COLOR, fg=TEXT_COLOR).grid(
        row=2, column=0, sticky='w', padx=FRAME_PADX, pady=(FRAME_PADY, 0))
    view_2d_file_entry = tk.Entry(frame, font=ENTRY_FONT, bg=ENTRY_BG, fg=ENTRY_FG,
                                  insertbackground=ENTRY_FG)
    view_2d_file_entry.insert(0, data["render_file_name"])
    view_2d_file_entry.grid(row=3, column=0, columnspan=2, sticky='ew', padx=FRAME_PADX)

    # Extension
    tk.Label(frame, text="Extension:", bg=BG_COLOR, fg=TEXT_COLOR).grid(
        row=4, column=0, sticky='w', padx=FRAME_PADX, pady=(FRAME_PADY, 0))
    view_2d_ext_var = tk.StringVar(value=data["render_file_extension"])
    opt_menu = tk.OptionMenu(frame, view_2d_ext_var, "png", "svg")
    opt_menu.config(bg=OPTIONMENU_BG, fg=OPTIONMENU_FG,
                    activebackground=BUTTON_ACTIVE_BG,
                    activeforeground=BUTTON_ACTIVE_FG,
                    highlightthickness=0)
    opt_menu['menu'].config(bg=OPTIONMENU_BG, fg=OPTIONMENU_FG,
                            activebackground=BUTTON_ACTIVE_BG,
                            activeforeground=BUTTON_ACTIVE_FG)
    opt_menu.grid(row=5, column=0, sticky='ew', padx=FRAME_PADX)


def build_2d_video_tab(frame, data):
    global video_2d_render_var, video_2d_file_entry, video_2d_ext_var

    frame.grid_columnconfigure(1, weight=1)

    # Render
    video_2d_render_var = tk.BooleanVar(value=data["render"])
    tk.Checkbutton(frame, text="Render", variable=video_2d_render_var,
                   bg=BG_COLOR, fg=TEXT_COLOR, selectcolor=BG_COLOR,
                   activebackground=BG_COLOR, activeforeground="#58A6FF").grid(
        row=0, column=0, sticky='w', padx=FRAME_PADX, pady=(FRAME_PADY, 0))

    # Render File Name
    tk.Label(frame, text="Render File Name:", bg=BG_COLOR, fg=TEXT_COLOR).grid(
        row=1, column=0, sticky='w', padx=FRAME_PADX, pady=(FRAME_PADY, 0))
    video_2d_file_entry = tk.Entry(frame, font=ENTRY_FONT, bg=ENTRY_BG, fg=ENTRY_FG,
                                   insertbackground=ENTRY_FG)
    video_2d_file_entry.insert(0, data["render_file_name"])
    video_2d_file_entry.grid(row=2, column=0, columnspan=2, sticky='ew', padx=FRAME_PADX)

    # Extension
    tk.Label(frame, text="Extension:", bg=BG_COLOR, fg=TEXT_COLOR).grid(
        row=3, column=0, sticky='w', padx=FRAME_PADX, pady=(FRAME_PADY, 0))
    video_2d_ext_var = tk.StringVar(value=data["render_file_extension"])
    opt_menu = tk.OptionMenu(frame, video_2d_ext_var, "mp4")
    opt_menu.config(bg=OPTIONMENU_BG, fg=OPTIONMENU_FG,
                    activebackground=BUTTON_ACTIVE_BG,
                    activeforeground=BUTTON_ACTIVE_FG,
                    highlightthickness=0)
    opt_menu['menu'].config(bg=OPTIONMENU_BG, fg=OPTIONMENU_FG,
                            activebackground=BUTTON_ACTIVE_BG,
                            activeforeground=BUTTON_ACTIVE_FG)
    opt_menu.grid(row=4, column=0, sticky='ew', padx=FRAME_PADX)


def build_3d_view_tab(frame, data):
    global view_3d_display_var, view_3d_render_var, view_3d_display_well_var, z_axis_ratio_entry, view_3d_file_entry, view_3d_ext_var

    frame.grid_columnconfigure(1, weight=1)

    # Display
    view_3d_display_var = tk.BooleanVar(value=data["display"])
    tk.Checkbutton(frame, text="Display", variable=view_3d_display_var,
                   bg=BG_COLOR, fg=TEXT_COLOR, selectcolor=BG_COLOR,
                   activebackground=BG_COLOR, activeforeground="#58A6FF").grid(
        row=0, column=0, sticky='w', padx=FRAME_PADX, pady=(FRAME_PADY, 0))

    # Render
    view_3d_render_var = tk.BooleanVar(value=data["render"])
    tk.Checkbutton(frame, text="Render", variable=view_3d_render_var,
                   bg=BG_COLOR, fg=TEXT_COLOR, selectcolor=BG_COLOR,
                   activebackground=BG_COLOR, activeforeground="#58A6FF").grid(
        row=1, column=0, sticky='w', padx=FRAME_PADX, pady=(FRAME_PADY, 0))

    # Display Well
    view_3d_display_well_var = tk.BooleanVar(value=data["display_well"])
    tk.Checkbutton(frame, text="Display Well", variable=view_3d_display_well_var,
                   bg=BG_COLOR, fg=TEXT_COLOR, selectcolor=BG_COLOR,
                   activebackground=BG_COLOR, activeforeground="#58A6FF").grid(
        row=2, column=0, sticky='w', padx=FRAME_PADX, pady=(FRAME_PADY, 0))

    # Z Axis Ratio
    tk.Label(frame, text="Z Axis Ratio:", bg=BG_COLOR, fg=TEXT_COLOR).grid(
        row=3, column=0, sticky='w', padx=FRAME_PADX, pady=(FRAME_PADY, 0))
    z_axis_ratio_entry = tk.Entry(frame, font=ENTRY_FONT, bg=ENTRY_BG, fg=ENTRY_FG,
                                  insertbackground=ENTRY_FG)
    z_axis_ratio_entry.insert(0, str(data["z_axis_ratio"]))
    z_axis_ratio_entry.grid(row=4, column=0, sticky='ew', padx=FRAME_PADX)

    # Render File Name
    tk.Label(frame, text="Render File Name:", bg=BG_COLOR, fg=TEXT_COLOR).grid(
        row=5, column=0, sticky='w', padx=FRAME_PADX, pady=(FRAME_PADY, 0))
    view_3d_file_entry = tk.Entry(frame, font=ENTRY_FONT, bg=ENTRY_BG, fg=ENTRY_FG,
                                  insertbackground=ENTRY_FG)
    view_3d_file_entry.insert(0, data["render_file_name"])
    view_3d_file_entry.grid(row=6, column=0, columnspan=2, sticky='ew', padx=FRAME_PADX)

    # Extension
    tk.Label(frame, text="Extension:", bg=BG_COLOR, fg=TEXT_COLOR).grid(
        row=7, column=0, sticky='w', padx=FRAME_PADX, pady=(FRAME_PADY, 0))
    view_3d_ext_var = tk.StringVar(value=data["render_file_extension"])
    opt_menu = tk.OptionMenu(frame, view_3d_ext_var, "png", "svg")
    opt_menu.config(bg=OPTIONMENU_BG, fg=OPTIONMENU_FG,
                    activebackground=BUTTON_ACTIVE_BG,
                    activeforeground=BUTTON_ACTIVE_FG,
                    highlightthickness=0)
    opt_menu['menu'].config(bg=OPTIONMENU_BG, fg=OPTIONMENU_FG,
                            activebackground=BUTTON_ACTIVE_BG,
                            activeforeground=BUTTON_ACTIVE_FG)
    opt_menu.grid(row=8, column=0, sticky='ew', padx=FRAME_PADX)


def build_treatment_tab(frame, data):
    global treat_display_var, treat_render_var, treat_div_var, treat_death_var, treat_file_entry, treat_ext_var

    frame.grid_columnconfigure(1, weight=1)

    # Display
    treat_display_var = tk.BooleanVar(value=data["display"])
    tk.Checkbutton(frame, text="Display", variable=treat_display_var,
                   bg=BG_COLOR, fg=TEXT_COLOR, selectcolor=BG_COLOR,
                   activebackground=BG_COLOR, activeforeground="#58A6FF").grid(
        row=0, column=0, sticky='w', padx=FRAME_PADX, pady=(FRAME_PADY, 0))

    # Render
    treat_render_var = tk.BooleanVar(value=data["render"])
    tk.Checkbutton(frame, text="Render", variable=treat_render_var,
                   bg=BG_COLOR, fg=TEXT_COLOR, selectcolor=BG_COLOR,
                   activebackground=BG_COLOR, activeforeground="#58A6FF").grid(
        row=1, column=0, sticky='w', padx=FRAME_PADX, pady=(FRAME_PADY, 0))

    # Show Division
    treat_div_var = tk.BooleanVar(value=data["show_division"])
    tk.Checkbutton(frame, text="Show Division", variable=treat_div_var,
                   bg=BG_COLOR, fg=TEXT_COLOR, selectcolor=BG_COLOR,
                   activebackground=BG_COLOR, activeforeground="#58A6FF").grid(
        row=2, column=0, sticky='w', padx=FRAME_PADX, pady=(FRAME_PADY, 0))

    # Show Death
    treat_death_var = tk.BooleanVar(value=data["show_death"])
    tk.Checkbutton(frame, text="Show Death", variable=treat_death_var,
                   bg=BG_COLOR, fg=TEXT_COLOR, selectcolor=BG_COLOR,
                   activebackground=BG_COLOR, activeforeground="#58A6FF").grid(
        row=3, column=0, sticky='w', padx=FRAME_PADX, pady=(FRAME_PADY, 0))

    # Render File Name
    tk.Label(frame, text="Render File Name:", bg=BG_COLOR, fg=TEXT_COLOR).grid(
        row=4, column=0, sticky='w', padx=FRAME_PADX, pady=(FRAME_PADY, 0))
    treat_file_entry = tk.Entry(frame, font=ENTRY_FONT, bg=ENTRY_BG, fg=ENTRY_FG,
                                insertbackground=ENTRY_FG)
    treat_file_entry.insert(0, data["render_file_name"])
    treat_file_entry.grid(row=5, column=0, columnspan=2, sticky='ew', padx=FRAME_PADX)

    # Extension
    tk.Label(frame, text="Extension:", bg=BG_COLOR, fg=TEXT_COLOR).grid(
        row=6, column=0, sticky='w', padx=FRAME_PADX, pady=(FRAME_PADY, 0))
    treat_ext_var = tk.StringVar(value=data["render_file_extension"])
    opt_menu = tk.OptionMenu(frame, treat_ext_var, "png", "svg")
    opt_menu.config(bg=OPTIONMENU_BG, fg=OPTIONMENU_FG,
                    activebackground=BUTTON_ACTIVE_BG,
                    activeforeground=BUTTON_ACTIVE_FG,
                    highlightthickness=0)
    opt_menu['menu'].config(bg=OPTIONMENU_BG, fg=OPTIONMENU_FG,
                            activebackground=BUTTON_ACTIVE_BG,
                            activeforeground=BUTTON_ACTIVE_FG)
    opt_menu.grid(row=7, column=0, sticky='ew', padx=FRAME_PADX)


def view_clovars():
    view_data = {
        "input": {
            "simulation_input_folder": sim_folder_entry.get(),
            "parameters_file_name": params_entry.get(),
            "cell_csv_file_name": cell_entry.get(),
            "colony_csv_file_name": colony_entry.get()
        },
        "view": {
            "colormap_name": colormap_var.get(),
            "layout": layout_var.get(),
            "figure_dpi": int(dpi_entry.get())
        },
        "2D_view": {
            "display": view_2d_display_var.get(),
            "render": view_2d_render_var.get(),
            "render_file_name": view_2d_file_entry.get(),
            "render_file_extension": view_2d_ext_var.get()
        },
        "2D_video": {
            "render": video_2d_render_var.get(),
            "render_file_name": video_2d_file_entry.get(),
            "render_file_extension": video_2d_ext_var.get()
        },
        "3D_view": {
            "display": view_3d_display_var.get(),
            "render": view_3d_render_var.get(),
            "display_well": view_3d_display_well_var.get(),
            "z_axis_ratio": float(z_axis_ratio_entry.get()),
            "render_file_name": view_3d_file_entry.get(),
            "render_file_extension": view_3d_ext_var.get()
        },
        "treatment_curves": {
            "display": treat_display_var.get(),
            "render": treat_render_var.get(),
            "show_division": treat_div_var.get(),
            "show_death": treat_death_var.get(),
            "render_file_name": treat_file_entry.get(),
            "render_file_extension": treat_ext_var.get()
        }
    }

    with open("gui_settings/view_settings.toml", "w") as f:
        toml.dump(view_data, f)

    validator = ViewParameterValidator()
    validator.parse_toml(SETTINGS_PATH)
    validator.validate()
    view_params = validator.to_simulation()

    view_simulation_function(**view_params)


if __name__ == "__main__":
    main()