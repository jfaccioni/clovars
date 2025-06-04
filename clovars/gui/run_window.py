import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import toml
from pathlib import Path
from clovars.IO.parameter_validator import RunParameterValidator, ColonyDataFormatter
from clovars.simulation import run_simulation_function

# ================ STYLE CONSTANTS ================
BG_COLOR = "#0D1117"
TAB_BG = "#0D1117"
FRAME_BG = "#0D1117"
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
LISTBOX_BG = "#21262D"
LISTBOX_FG = "#C9D1D9"
LISTBOX_SELECT_BG = "#30363D"
LISTBOX_SELECT_FG = "#58A6FF"
FRAME_PADX = 10
FRAME_PADY = 5


class StyledTreatmentEditor(tk.Toplevel):
    def __init__(self, parent, treatment=None, callback=None):
        super().__init__(parent)
        self.title("Treatment Editor")
        self.geometry("800x600")
        self.configure(bg=BG_COLOR)
        self.callback = callback

        # Treatment data or new template
        self.treatment = treatment if treatment else {
            'name': "New Treatment",
            'added_on_frame': 0,
            'division_curve': {
                'name': 'Gamma',
                'mean': 16.23,
                'std': 2.84,
                'a': 3.32,
                'k': None,
                's': None
            },
            'death_curve': {
                'name': 'Gaussian',
                'mean': 100.0,
                'std': 1.0,
                'a': None,
                'k': None,
                's': None
            }
        }

        self.style = ttk.Style()
        self.configure_styles()
        self.create_widgets()

    def configure_styles(self):
        self.style.theme_use('alt')

        # Notebook styling
        self.style.configure('TNotebook', background=BG_COLOR)
        self.style.configure('TNotebook.Tab',
                             background="#21262D",
                             foreground="#C9D1D9",
                             padding=[10, 5],
                             font=LABEL_FONT)
        self.style.map('TNotebook.Tab',
                       background=[('selected', '#30363D')],
                       foreground=[('selected', '#58A6FF')])

        # Entry styling
        self.style.configure('TEntry',
                             fieldbackground=ENTRY_BG,
                             foreground=ENTRY_FG,
                             insertcolor=ENTRY_FG,
                             bordercolor=BG_COLOR,
                             lightcolor=BG_COLOR,
                             darkcolor=BG_COLOR)

        # Combobox styling - Updated with more complete configuration
        self.style.configure('TCombobox',
                             fieldbackground=ENTRY_BG,
                             foreground=ENTRY_FG,
                             background=OPTIONMENU_BG,
                             selectbackground=LISTBOX_SELECT_BG,
                             selectforeground=LISTBOX_SELECT_FG,
                             arrowcolor=ENTRY_FG,
                             bordercolor=BG_COLOR,
                             lightcolor=BG_COLOR,
                             darkcolor=BG_COLOR)

        self.style.map('TCombobox',
                       fieldbackground=[('readonly', ENTRY_BG)],
                       foreground=[('readonly', ENTRY_FG)],
                       background=[('readonly', OPTIONMENU_BG)],
                       selectbackground=[('readonly', LISTBOX_SELECT_BG)],
                       selectforeground=[('readonly', LISTBOX_SELECT_FG)])

        # Button styling
        self.style.configure('TButton',
                             background=BUTTON_BG,
                             foreground=BUTTON_FG,
                             bordercolor=BG_COLOR,
                             font=BUTTON_FONT)
        self.style.map('TButton',
                       background=[('active', BUTTON_ACTIVE_BG)],
                       foreground=[('active', BUTTON_ACTIVE_FG)])

        # Label styling
        self.style.configure('TLabel',
                             background=FRAME_BG,
                             foreground=TEXT_COLOR,
                             font=LABEL_FONT)

        # Frame styling
        self.style.configure('TFrame',
                             background=FRAME_BG)

    def create_widgets(self):
        notebook = ttk.Notebook(self)
        notebook.pack(fill=tk.BOTH, expand=True)

        # General Settings Tab
        general_tab = ttk.Frame(notebook)
        notebook.add(general_tab, text="General")

        self.create_label(general_tab, "Treatment Name:", 0, 0)
        self.name_var = tk.StringVar(value=self.treatment['name'])
        self.create_entry(general_tab, self.name_var, 0, 1)

        self.create_label(general_tab, "Added on Frame:", 1, 0)
        self.frame_var = tk.IntVar(value=self.treatment['added_on_frame'])
        self.create_entry(general_tab, self.frame_var, 1, 1)

        # Division Curve Tab
        div_tab = ttk.Frame(notebook)
        notebook.add(div_tab, text="Division Curve")
        self.create_curve_widgets(div_tab, self.treatment['division_curve'], "division")

        # Death Curve Tab
        death_tab = ttk.Frame(notebook)
        notebook.add(death_tab, text="Death Curve")
        self.create_curve_widgets(death_tab, self.treatment['death_curve'], "death")

        # Buttons
        btn_frame = ttk.Frame(self)
        btn_frame.pack(fill=tk.X, pady=10)

        save_btn = ttk.Button(btn_frame, text="Save", command=self.save)
        save_btn.pack(side=tk.RIGHT, padx=5)

        cancel_btn = ttk.Button(btn_frame, text="Cancel", command=self.destroy)
        cancel_btn.pack(side=tk.RIGHT, padx=5)

    def create_label(self, parent, text, row, column):
        label = ttk.Label(parent, text=text)
        label.grid(row=row, column=column, sticky="e", padx=FRAME_PADX, pady=FRAME_PADY)
        return label

    def create_entry(self, parent, var, row, column):
        entry = ttk.Entry(parent, textvariable=var)
        entry.grid(row=row, column=column, sticky="ew", padx=FRAME_PADX, pady=FRAME_PADY)
        return entry

    def create_curve_widgets(self, parent, curve, prefix):
        self.create_label(parent, "Curve Type:", 0, 0)
        # Use prefix-specific variable for curve type
        setattr(self, f"{prefix}_curve_type_var", tk.StringVar(value=curve['name']))
        curve_types = ['Gaussian', 'Gamma', 'EMGaussian', 'Lognormal']

        cb = ttk.Combobox(parent, textvariable=getattr(self, f"{prefix}_curve_type_var"),
                          values=curve_types, state="readonly")
        cb.grid(row=0, column=1, sticky="ew", padx=FRAME_PADX, pady=FRAME_PADY)
        # Update the correct curve fields when selection changes
        cb.bind("<<ComboboxSelected>>", lambda e: self.update_curve_fields(parent, prefix))

        # Common parameters - use prefix-specific variables
        self.create_label(parent, "Mean:", 1, 0)
        setattr(self, f"{prefix}_mean_var", tk.DoubleVar(value=curve['mean']))
        self.create_entry(parent, getattr(self, f"{prefix}_mean_var"), 1, 1)

        self.create_label(parent, "Standard Deviation:", 2, 0)
        setattr(self, f"{prefix}_std_var", tk.DoubleVar(value=curve['std']))
        self.create_entry(parent, getattr(self, f"{prefix}_std_var"), 2, 1)

        # Dynamic parameter frame
        setattr(self, f"{prefix}_param_frame", ttk.Frame(parent))
        getattr(self, f"{prefix}_param_frame").grid(row=3, column=0, columnspan=2,
                                                    sticky="ew", padx=FRAME_PADX, pady=FRAME_PADY)
        self.update_curve_fields(parent, prefix)

    def update_curve_fields(self, parent, prefix):
        # Clear existing parameter fields
        for widget in getattr(self, f"{prefix}_param_frame").winfo_children():
            widget.destroy()

        # Get the current curve type for this section
        curve_type = getattr(self, f"{prefix}_curve_type_var").get()

        # Add specific parameters based on curve type
        row = 0
        if curve_type == 'Gamma':
            ttk.Label(getattr(self, f"{prefix}_param_frame"), text="Shape (a):").grid(
                row=row, column=0, sticky="e", padx=5, pady=2)
            setattr(self, f"{prefix}_a_var", tk.DoubleVar(
                value=self.treatment[f"{prefix}_curve"].get('a', 3.32)))
            ttk.Entry(getattr(self, f"{prefix}_param_frame"),
                      textvariable=getattr(self, f"{prefix}_a_var")).grid(
                row=row, column=1, sticky="ew", padx=5, pady=2)
            row += 1
        elif curve_type == 'EMGaussian':
            ttk.Label(getattr(self, f"{prefix}_param_frame"), text="Exponential (k):").grid(
                row=row, column=0, sticky="e", padx=5, pady=2)
            setattr(self, f"{prefix}_k_var", tk.DoubleVar(
                value=self.treatment[f"{prefix}_curve"].get('k', 1.0)))
            ttk.Entry(getattr(self, f"{prefix}_param_frame"),
                      textvariable=getattr(self, f"{prefix}_k_var")).grid(
                row=row, column=1, sticky="ew", padx=5, pady=2)
            row += 1
        elif curve_type == 'Lognormal':
            ttk.Label(getattr(self, f"{prefix}_param_frame"), text="Shape (s):").grid(
                row=row, column=0, sticky="e", padx=5, pady=2)
            setattr(self, f"{prefix}_s_var", tk.DoubleVar(
                value=self.treatment[f"{prefix}_curve"].get('s', 1.0)))
            ttk.Entry(getattr(self, f"{prefix}_param_frame"),
                      textvariable=getattr(self, f"{prefix}_s_var")).grid(
                row=row, column=1, sticky="ew", padx=5, pady=2)
            row += 1

    def save(self):
        try:
            # Update treatment data
            self.treatment = {
                'name': self.name_var.get(),
                'added_on_frame': self.frame_var.get(),
                'division_curve': self.get_curve_params("division"),
                'death_curve': self.get_curve_params("death")
            }

            if self.callback:
                self.callback(self.treatment)

            self.destroy()
        except Exception as e:
            messagebox.showerror("Error", f"Invalid parameters: {str(e)}")

    def get_curve_params(self, prefix):
        curve_type = getattr(self, f"{prefix}_curve_type_var").get()
        params = {
            'name': curve_type,
            'mean': getattr(self, f"{prefix}_mean_var").get(),
            'std': getattr(self, f"{prefix}_std_var").get()
        }

        # Add the specific parameter based on curve type
        if curve_type == 'Gamma' and hasattr(self, f"{prefix}_a_var"):
            params['a'] = getattr(self, f"{prefix}_a_var").get()
        elif curve_type == 'EMGaussian' and hasattr(self, f"{prefix}_k_var"):
            params['k'] = getattr(self, f"{prefix}_k_var").get()
        elif curve_type == 'Lognormal' and hasattr(self, f"{prefix}_s_var"):
            params['s'] = getattr(self, f"{prefix}_s_var").get()

        return params


class StyledCloVarSGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("CloVarS Configuration Editor")
        self.root.geometry("1200x800")
        self.root.configure(bg=BG_COLOR)

        # Configure styles
        self.configure_styles()

        # Create settings directory if it doesn't exist
        self.settings_dir = Path("gui_settings")
        self.settings_dir.mkdir(exist_ok=True)

        # Paths to TOML files
        self.run_settings_path = self.settings_dir / "run_settings.toml"
        self.colonies_settings_path = self.settings_dir / "colonies_settings.toml"

        # Load or initialize default settings
        self.run_settings = self.load_or_create_settings(self.run_settings_path, RUN_SETTINGS_DEFAULT)
        self.colonies_settings = self.load_or_create_settings(self.colonies_settings_path, COLONIES_SETTINGS_DEFAULT)

        # Create notebook (tabs)
        self.notebook = ttk.Notebook(self.root, style='Custom.TNotebook')
        self.notebook.pack(fill='both', expand=True)

        # Create tabs
        self.create_run_settings_tab()
        self.create_colonies_settings_tab()

        # Add save button at bottom
        self.save_button = tk.Button(self.root, text="Run!", command=self.run_button_function,
                                     bg=BUTTON_BG, fg=BUTTON_FG, activebackground=BUTTON_ACTIVE_BG,
                                     activeforeground=BUTTON_ACTIVE_FG, font=BUTTON_FONT, bd=0)
        self.save_button.pack(side='bottom', pady=10)

    def configure_styles(self):
        style = ttk.Style()
        style.theme_use('alt')

        # Main notebook style
        style.configure('Custom.TNotebook', background=BG_COLOR)
        style.configure('Custom.TNotebook.Tab',
                        background="#21262D",
                        foreground="#C9D1D9",
                        padding=[10, 5],
                        font=LABEL_FONT)
        style.map('Custom.TNotebook.Tab',
                  background=[('selected', '#30363D')],
                  foreground=[('selected', '#58A6FF')])

        # Frame style
        style.configure('TFrame', background=FRAME_BG)

        # Label style
        style.configure('TLabel', background=FRAME_BG, foreground=TEXT_COLOR, font=LABEL_FONT)

        # LabelFrame style
        style.configure('TLabelframe', background=FRAME_BG, foreground=TEXT_COLOR)
        style.configure('TLabelframe.Label', background=FRAME_BG, foreground="#58A6FF", font=('Helvetica', 12, 'bold'))

        # Entry style
        style.configure('TEntry',
                        fieldbackground=ENTRY_BG,
                        foreground=ENTRY_FG,
                        insertcolor=ENTRY_FG,
                        bordercolor=BG_COLOR,
                        lightcolor=BG_COLOR,
                        darkcolor=BG_COLOR)

        # Combobox style
        style.configure('TCombobox',
                        fieldbackground=ENTRY_BG,
                        foreground=ENTRY_FG,
                        background=OPTIONMENU_BG,
                        arrowcolor=ENTRY_FG)

        # Button style
        style.configure('TButton',
                        background=BUTTON_BG,
                        foreground=BUTTON_FG,
                        bordercolor=BG_COLOR,
                        font=BUTTON_FONT)
        style.map('TButton',
                  background=[('active', BUTTON_ACTIVE_BG)],
                  foreground=[('active', BUTTON_ACTIVE_FG)])

        style.configure('TCheckbutton',
                        background=FRAME_BG,
                        foreground=BUTTON_ACTIVE_FG,
                        indicatorbackground= BG_COLOR,  # Background of the checkbox
                        indicatorcolour="#58A6FF",  # Color when checked
                        indicatordepth=0,
                        indicatorsize=30,
                        font=LABEL_FONT)
        style.map('TCheckbutton',
                  background=[('active', FRAME_BG)],
                  foreground=[('active', TEXT_COLOR)],
                  indicatorcolor=[  # Correct property name
                      ('selected', BG_COLOR),  # Color when checked
                      ('!selected', BG_COLOR),  # Color when unchecked
                      ('disabled', BG_COLOR)  # Color when disabled
                  ])

        # Scrollbar style
        style.configure('Vertical.TScrollbar',
                        background=BG_COLOR,
                        troughcolor=BG_COLOR,
                        arrowcolor=ENTRY_FG,
                        bordercolor=BG_COLOR)
        style.map('Vertical.TScrollbar',
                  background=[('active', BUTTON_ACTIVE_BG)])

        style.configure('TPanedwindow', background=BG_COLOR)
        style.map('TPanedwindow',
                  background=[('active', BG_COLOR)],
                  bordercolor=[('active', BG_COLOR)],
                  lightcolor=[('active', BG_COLOR)],
                  darkcolor=[('active', BG_COLOR)])

        # Right panel notebook style (different from main notebook)
        style.configure('Right.TNotebook', background=BG_COLOR)
        style.configure('Right.TNotebook.Tab',
                        background="#21262D",
                        foreground="#C9D1D9",
                        padding=[10, 5],
                        font=LABEL_FONT)
        style.map('Right.TNotebook.Tab',
                  background=[('selected', '#30363D')],
                  foreground=[('selected', '#58A6FF')])

    def load_or_create_settings(self, path, default_settings):
        """Load settings from TOML or create with defaults if file doesn't exist"""
        try:
            if path.exists():
                return toml.load(path)
            else:
                with open(path, 'w') as f:
                    toml.dump(default_settings, f)
                return default_settings
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load {path}: {str(e)}")
            return default_settings

    def create_run_settings_tab(self):
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="Run Settings")

        canvas = tk.Canvas(tab, bg=BG_COLOR, highlightthickness=0)
        scrollbar = ttk.Scrollbar(tab, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)

        scrollable_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        self.run_settings_widgets = {}
        row = 0

        # Geral
        frame = ttk.LabelFrame(scrollable_frame, text="Geral")
        frame.grid(row=row, column=0, padx=10, pady=5, sticky="ew")
        row += 1

        self.run_settings_widgets['verbose'] = tk.BooleanVar(value=self.run_settings.get('verbose', True))
        ttk.Checkbutton(frame, text="Verbose", variable=self.run_settings_widgets['verbose'],
                        style="TCheckbutton").grid(row=0, column=0, sticky="w", padx=5, pady=2)

        ttk.Label(frame, text="Delta (segundos):").grid(row=1, column=0, sticky="e", padx=5, pady=2)
        self.run_settings_widgets['delta'] = tk.IntVar(value=self.run_settings.get('delta', 3600))
        ttk.Entry(frame, textvariable=self.run_settings_widgets['delta']).grid(row=1, column=1, sticky="w", padx=5,
                                                                               pady=2)

        # Well
        frame = ttk.LabelFrame(scrollable_frame, text="Well")
        frame.grid(row=row, column=0, padx=10, pady=5, sticky="ew")
        row += 1

        ttk.Label(frame, text="Well Radius (µm):").grid(row=0, column=0, sticky="e", padx=5, pady=2)
        self.run_settings_widgets['well.well_radius'] = tk.DoubleVar(
            value=self.run_settings['well'].get('well_radius', 0.0))
        ttk.Entry(frame, textvariable=self.run_settings_widgets['well.well_radius']).grid(row=0, column=1, sticky="w",
                                                                                          padx=5, pady=2)

        # Output
        frame = ttk.LabelFrame(scrollable_frame, text="Output")
        frame.grid(row=row, column=0, padx=10, pady=5, sticky="ew")
        row += 1

        output_fields = [
            ('output.output_folder', 'Output Folder'),
            ('output.parameters_file_name', 'Parameters File Name'),
            ('output.cell_csv_file_name', 'Cell CSV File Name'),
            ('output.colony_csv_file_name', 'Colony CSV File Name'),
        ]

        for i, (key, label) in enumerate(output_fields):
            ttk.Label(frame, text=label + ":").grid(row=i, column=0, sticky="e", padx=5, pady=2)
            val = self.run_settings['output'].get(key.split('.')[-1], '')
            self.run_settings_widgets[key] = tk.StringVar(value=val)
            ttk.Entry(frame, textvariable=self.run_settings_widgets[key]).grid(row=i, column=1, sticky="ew", padx=5,
                                                                               pady=2)

        ttk.Label(frame, text="Confirm Overwrite:").grid(row=4, column=0, sticky="e", padx=5, pady=2)
        self.run_settings_widgets['output.confirm_overwrite'] = tk.BooleanVar(
            value=self.run_settings['output'].get('confirm_overwrite', True))
        ttk.Checkbutton(frame, variable=self.run_settings_widgets['output.confirm_overwrite'],
                        style="TCheckbutton").grid(row=4, column=1, sticky="w", padx=5, pady=2)

        # Stop Conditions
        frame = ttk.LabelFrame(scrollable_frame, text="Stop Conditions")
        frame.grid(row=row, column=0, padx=10, pady=5, sticky="ew")
        row += 1

        stop_fields = [
            ('stop_conditions.stop_at_frame', 'Stop at Frame', 'int'),
            ('stop_conditions.stop_at_single_colony_size', 'Stop at Single Colony Size', 'int'),
            ('stop_conditions.stop_at_all_colonies_size', 'Stop at All Colonies Size', 'int'),
        ]

        for i, (key, label, typ) in enumerate(stop_fields):
            ttk.Label(frame, text=label + ":").grid(row=i, column=0, sticky="e", padx=5, pady=2)
            val = self.run_settings['stop_conditions'].get(key.split('.')[-1])
            val = "" if val is None else val
            var = tk.StringVar(value=str(val))
            ttk.Entry(frame, textvariable=var).grid(row=i, column=1, sticky="ew", padx=5, pady=2)
            self.run_settings_widgets[key] = var

    def create_colonies_settings_tab(self):
        """Create the Colonies Settings tab with colony and treatment management"""
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="Colonies Settings")

        # Create a paned window for colony list and details
        paned = ttk.PanedWindow(tab, orient=tk.HORIZONTAL, style='TPanedwindow')
        paned.pack(fill=tk.BOTH, expand=True)

        # Left panel - colony list
        left_panel = ttk.Frame(paned, style = "TFrame")
        paned.add(left_panel, weight=1)

        # Colony list controls
        ttk.Label(left_panel, text="Colonies", font=('Arial', 12, 'bold')).pack(pady=5)

        # Create styled listbox
        self.colony_listbox = tk.Listbox(left_panel,
                                         bg=LISTBOX_BG,
                                         fg=LISTBOX_FG,
                                         selectbackground=LISTBOX_SELECT_BG,
                                         selectforeground=LISTBOX_SELECT_FG,
                                         font=LABEL_FONT)
        self.colony_listbox.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        btn_frame = ttk.Frame(left_panel)
        btn_frame.pack(pady=5)

        ttk.Button(btn_frame, text="Add Colony", command=self.add_colony).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Remove Colony", command=self.remove_colony).pack(side=tk.LEFT, padx=5)

        # Right panel - colony details
        right_panel = ttk.Frame(paned, style = "TFrame")
        paned.add(right_panel, weight=3)

        # Notebook for colony settings and treatments
        self.colony_notebook = ttk.Notebook(right_panel, style='Right.TNotebook')
        self.colony_notebook.pack(fill=tk.BOTH, expand=True)

        # Initialize with first colony
        self.current_colony_index = 0 if self.colonies_settings['colony'] else None
        self.update_colony_display()

        # Bind listbox selection
        self.colony_listbox.bind('<<ListboxSelect>>', self.on_colony_select)

    def update_colony_display(self):
        """Update the colony list and details display"""
        self.colony_listbox.delete(0, tk.END)

        for i, colony in enumerate(self.colonies_settings['colony']):
            name = f"Colony {i + 1}"
            if 'treatment' in colony and colony['treatment']:
                treatments = ", ".join(t['name'] for t in colony['treatment'])
                name += f" ({treatments})"
            self.colony_listbox.insert(tk.END, name)

        if self.colonies_settings['colony']:
            self.colony_listbox.selection_set(self.current_colony_index)
            self.show_colony_details(self.current_colony_index)

    def show_colony_details(self, colony_index):
        """Show details for the selected colony"""
        for tab in self.colony_notebook.tabs():
            self.colony_notebook.forget(tab)

        if colony_index is None or colony_index >= len(self.colonies_settings['colony']):
            return

        colony = self.colonies_settings['colony'][colony_index]

        # Colony settings tab
        colony_tab = ttk.Frame(self.colony_notebook)
        self.colony_notebook.add(colony_tab, text="Colony Settings")

        # General colony settings
        general_frame = ttk.LabelFrame(colony_tab, text="General Settings")
        general_frame.pack(fill=tk.X, padx=5, pady=5)

        ttk.Label(general_frame, text="Copies:").grid(row=0, column=0, sticky="e", padx=5, pady=2)
        copies_var = tk.IntVar(value=colony.get('copies', 1))
        ttk.Entry(general_frame, textvariable=copies_var).grid(row=0, column=1, sticky="ew", padx=5, pady=2)

        ttk.Label(general_frame, text="Initial Size:").grid(row=1, column=0, sticky="e", padx=5, pady=2)
        initial_size_var = tk.IntVar(value=colony.get('initial_size', 1))
        ttk.Entry(general_frame, textvariable=initial_size_var).grid(row=1, column=1, sticky="ew", padx=5, pady=2)

        # Cells settings
        cells_frame = ttk.LabelFrame(colony_tab, text="Cells Settings")
        cells_frame.pack(fill=tk.X, padx=5, pady=5)

        cells = colony.get('cells', {})

        ttk.Label(cells_frame, text="Radius (µm):").grid(row=0, column=0, sticky="e", padx=5, pady=2)
        radius_var = tk.DoubleVar(value=cells.get('radius', 20.0))
        ttk.Entry(cells_frame, textvariable=radius_var).grid(row=0, column=1, sticky="ew", padx=5, pady=2)

        ttk.Label(cells_frame, text="Max Speed (µm/s):").grid(row=1, column=0, sticky="e", padx=5, pady=2)
        max_speed_var = tk.DoubleVar(value=cells.get('max_speed', 0.020351))
        ttk.Entry(cells_frame, textvariable=max_speed_var).grid(row=1, column=1, sticky="ew", padx=5, pady=2)

        linked_var = tk.BooleanVar(value=cells.get('linked_sister_inheritance', True))
        ttk.Checkbutton(cells_frame, text="Linked sister inheritance", variable=linked_var,style = "TCheckbutton").grid(row=2, column=0,
                                                                                                 columnspan=2,
                                                                                                 sticky="w", padx=5,
                                                                                                 pady=2)

        ttk.Label(cells_frame, text="Mother Fitness Memory:").grid(row=3, column=0, sticky="e", padx=5, pady=2)
        mother_mem_var = tk.DoubleVar(value=cells.get('mother_fitness_memory', 0.0))
        ttk.Entry(cells_frame, textvariable=mother_mem_var).grid(row=3, column=1, sticky="ew", padx=5, pady=2)

        ttk.Label(cells_frame, text="Sister Fitness Memory:").grid(row=4, column=0, sticky="e", padx=5, pady=2)
        sister_mem_var = tk.DoubleVar(value=cells.get('sister_fitness_memory', 0.0))
        ttk.Entry(cells_frame, textvariable=sister_mem_var).grid(row=4, column=1, sticky="ew", padx=5, pady=2)

        # Signal settings
        signal_frame = ttk.LabelFrame(cells_frame, text="Signal Settings")
        signal_frame.grid(row=5, column=0, columnspan=2, sticky="ew", padx=5, pady=5)

        signal = cells.get('signal', {})

        ttk.Label(signal_frame, text="Signal Name:").grid(row=0, column=0, sticky="e", padx=5, pady=2)
        signal_name_var = tk.StringVar(value=signal.get('name', 'Gaussian'))
        ttk.Combobox(signal_frame, textvariable=signal_name_var,
                     values=['Gaussian', 'Uniform', 'Constant']).grid(row=0, column=1, sticky="ew", padx=5, pady=2)

        ttk.Label(signal_frame, text="Initial Value:").grid(row=1, column=0, sticky="e", padx=5, pady=2)
        signal_init_var = tk.DoubleVar(value=signal.get('initial_value', 0.0))
        ttk.Entry(signal_frame, textvariable=signal_init_var).grid(row=1, column=1, sticky="ew", padx=5, pady=2)

        ttk.Label(signal_frame, text="Standard Deviation:").grid(row=2, column=0, sticky="e", padx=5, pady=2)
        signal_std_var = tk.DoubleVar(value=signal.get('std', 0.05))
        ttk.Entry(signal_frame, textvariable=signal_std_var).grid(row=2, column=1, sticky="ew", padx=5, pady=2)

        # Store references to variables
        self.current_colony_vars = {
            'copies': copies_var,
            'initial_size': initial_size_var,
            'cells': {
                'radius': radius_var,
                'max_speed': max_speed_var,
                'linked_sister_inheritance': linked_var,
                'mother_fitness_memory': mother_mem_var,
                'sister_fitness_memory': sister_mem_var,
                'signal': {
                    'name': signal_name_var,
                    'initial_value': signal_init_var,
                    'std': signal_std_var
                }
            }
        }

        # Treatments tab
        treatments_tab = ttk.Frame(self.colony_notebook)
        self.colony_notebook.add(treatments_tab, text="Treatments")

        # Treatment list
        treatment_frame = ttk.Frame(treatments_tab)
        treatment_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        ttk.Label(treatment_frame, text="Treatments", font=('Arial', 12, 'bold')).pack(pady=5)

        self.treatment_listbox = tk.Listbox(treatment_frame,
                                            bg=LISTBOX_BG,
                                            fg=LISTBOX_FG,
                                            selectbackground=LISTBOX_SELECT_BG,
                                            selectforeground=LISTBOX_SELECT_FG,
                                            font=LABEL_FONT)
        self.treatment_listbox.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        btn_frame = ttk.Frame(treatment_frame)
        btn_frame.pack(pady=5)

        ttk.Button(btn_frame, text="Add Treatment",
                   command=lambda: self.add_treatment(colony_index)).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Edit Treatment",
                   command=lambda: self.edit_treatment(colony_index)).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Remove Treatment",
                   command=lambda: self.remove_treatment(colony_index)).pack(side=tk.LEFT, padx=5)

        self.update_treatment_list(colony_index)

    def edit_treatment(self, colony_index):
        """Open treatment editor for selected treatment"""
        selection = self.treatment_listbox.curselection()
        if not selection:
            return

        treatment_idx = selection[0]
        colony = self.colonies_settings['colony'][colony_index]
        treatment = colony['treatment'][treatment_idx]

        def update_treatment(updated_treatment):
            colony['treatment'][treatment_idx] = updated_treatment
            self.update_treatment_list(colony_index)
            self.update_colony_display()

        editor = StyledTreatmentEditor(self.root, treatment, update_treatment)
        editor.grab_set()

    def update_treatment_list(self, colony_index):
        """Update the treatment list for a colony"""
        self.treatment_listbox.delete(0, tk.END)
        if colony_index < len(self.colonies_settings['colony']):
            colony = self.colonies_settings['colony'][colony_index]
            if 'treatment' in colony:
                for treatment in colony['treatment']:
                    self.treatment_listbox.insert(tk.END, treatment['name'])

    def on_colony_select(self, event):
        """Handle colony selection change"""
        selection = self.colony_listbox.curselection()
        if selection:
            self.current_colony_index = selection[0]
            self.show_colony_details(self.current_colony_index)

    def add_colony(self):
        """Add a new colony with default settings"""
        new_colony = {
            'copies': 1,
            'initial_size': 1,
            'cells': {
                'radius': 20.0,
                'max_speed': 0.020351,
                'linked_sister_inheritance': True,
                'mother_fitness_memory': 0.0,
                'sister_fitness_memory': 0.0,
                'signal': {
                    'name': 'Gaussian',
                    'initial_value': 0.0,
                    'std': 0.05
                }
            },
            'treatment': []
        }
        self.colonies_settings['colony'].append(new_colony)
        self.current_colony_index = len(self.colonies_settings['colony']) - 1
        self.update_colony_display()

    def remove_colony(self):
        """Remove the selected colony"""
        if len(self.colonies_settings['colony']) > 0 and self.current_colony_index is not None:
            del self.colonies_settings['colony'][self.current_colony_index]
            if self.current_colony_index >= len(self.colonies_settings['colony']):
                self.current_colony_index = max(0, len(self.colonies_settings['colony']) - 1)
            self.update_colony_display()

    def add_treatment(self, colony_index):
        """Add a new treatment to the specified colony"""
        if colony_index < len(self.colonies_settings['colony']):
            new_treatment = {
                'name': f"Treatment {len(self.colonies_settings['colony'][colony_index].get('treatment', [])) + 1}",
                'added_on_frame': 0,
                'division_curve': {
                    'name': 'Gamma',
                    'mean': 16.23,
                    'std': 2.84,
                    'a': 3.32
                },
                'death_curve': {
                    'name': 'Gaussian',
                    'mean': 100.0,
                    'std': 1.0
                }
            }

            if 'treatment' not in self.colonies_settings['colony'][colony_index]:
                self.colonies_settings['colony'][colony_index]['treatment'] = []

            self.colonies_settings['colony'][colony_index]['treatment'].append(new_treatment)
            self.update_treatment_list(colony_index)
            self.update_colony_display()

    def remove_treatment(self, colony_index):
        """Remove the selected treatment from the specified colony"""
        if (colony_index < len(self.colonies_settings['colony']) and
                'treatment' in self.colonies_settings['colony'][colony_index]):
            selection = self.treatment_listbox.curselection()
            if selection:
                del self.colonies_settings['colony'][colony_index]['treatment'][selection[0]]
                self.update_treatment_list(colony_index)
                self.update_colony_display()

    def browse_folder(self, var):
        """Open folder browser dialog"""
        folder = filedialog.askdirectory()
        if folder:
            var.set(folder)

    def save_all_settings(self):
        """Save all settings to TOML files"""
        self.save_run_settings()

        # Save colonies settings
        self.save_colonies_settings()

    def run_clovars(self):
        # load run params
        run_validator = RunParameterValidator()
        run_validator.parse_toml(toml_path=self.run_settings_path)
        run_validator.validate()
        run_params = run_validator.to_simulation()

        colony_formatter = ColonyDataFormatter()
        colony_formatter.parse_toml(toml_path=self.colonies_settings_path)
        colonies = colony_formatter.to_simulation()

        run_simulation_function(colony_data=colonies, **run_params)

    def run_button_function(self):
        try:
            self.save_all_settings()

            ## RODAR SIMULACAO
            self.run_clovars()

            messagebox.showinfo("Success", "Simulation runned successfully!")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to run simulation: {str(e)}")

    def save_run_settings(self):
        self.run_settings['verbose'] = self.run_settings_widgets['verbose'].get()
        self.run_settings['delta'] = self.run_settings_widgets['delta'].get()

        self.run_settings['well']['well_radius'] = self.run_settings_widgets['well.well_radius'].get()

        for key in ['output_folder', 'parameters_file_name', 'cell_csv_file_name', 'colony_csv_file_name']:
            self.run_settings['output'][key] = self.run_settings_widgets[f'output.{key}'].get()

        self.run_settings['output']['confirm_overwrite'] = self.run_settings_widgets['output.confirm_overwrite'].get()

        for key in ['stop_at_frame', 'stop_at_single_colony_size', 'stop_at_all_colonies_size']:
            val = self.run_settings_widgets[f'stop_conditions.{key}'].get()
            self.run_settings['stop_conditions'][key] = int(val) if val.strip().isdigit() else None

        with open(self.run_settings_path, 'w') as f:
            toml.dump(self.run_settings, f)

    def save_colonies_settings(self):
        """Save colonies settings to TOML"""
        # Update current colony settings if any are being edited
        if hasattr(self, 'current_colony_vars') and self.current_colony_index is not None:
            colony = self.colonies_settings['colony'][self.current_colony_index]

            # Update general colony settings
            colony['copies'] = self.current_colony_vars['copies'].get()
            colony['initial_size'] = self.current_colony_vars['initial_size'].get()

            # Update cells settings
            colony['cells']['radius'] = self.current_colony_vars['cells']['radius'].get()
            colony['cells']['max_speed'] = self.current_colony_vars['cells']['max_speed'].get()
            colony['cells']['linked_sister_inheritance'] = self.current_colony_vars['cells'][
                'linked_sister_inheritance'].get()
            colony['cells']['mother_fitness_memory'] = self.current_colony_vars['cells']['mother_fitness_memory'].get()
            colony['cells']['sister_fitness_memory'] = self.current_colony_vars['cells']['sister_fitness_memory'].get()

            # Update signal settings
            colony['cells']['signal']['name'] = self.current_colony_vars['cells']['signal']['name'].get()
            colony['cells']['signal']['initial_value'] = self.current_colony_vars['cells']['signal'][
                'initial_value'].get()
            colony['cells']['signal']['std'] = self.current_colony_vars['cells']['signal']['std'].get()

        # Save to file
        with open(self.colonies_settings_path, 'w') as f:
            toml.dump(self.colonies_settings, f)


# Default settings
RUN_SETTINGS_DEFAULT = {
    'verbose': True,
    'delta': 3600,
    'well': {
        'well_radius': 13351.624
    },
    'output': {
        'output_folder': 'output',
        'parameters_file_name': 'params.json',
        'cell_csv_file_name': 'cell_output.csv',
        'colony_csv_file_name': 'colony_output.csv',
        'confirm_overwrite': True
    },
    'stop_conditions': {
        'stop_at_frame': 144,
        'stop_at_single_colony_size': None,
        'stop_at_all_colonies_size': None
    }
}


COLONIES_SETTINGS_DEFAULT = {
    'colony': [
        {
            'copies': 1,
            'initial_size': 1,
            'cells': {
                'radius': 20.0,
                'max_speed': 0.020351,
                'linked_sister_inheritance': True,
                'mother_fitness_memory': 0.0,
                'sister_fitness_memory': 0.0,
                'signal': {
                    'name': 'Gaussian',
                    'initial_value': 0.0,
                    'std': 0.05
                }
            },
            'treatment': [
                {
                    'name': 'Control',
                    'added_on_frame': 0,
                    'division_curve': {
                        'name': 'Gamma',
                        'mean': 16.23,
                        'std': 2.84,
                        'a': 3.32
                    },
                    'death_curve': {
                        'name': 'Gaussian',
                        'mean': 100.0,
                        'std': 1.0
                    }
                },
                {
                    'name': 'Temozolomide',
                    'added_on_frame': 72,
                    'division_curve': {
                        'name': 'EMGaussian',
                        'mean': 12.72,
                        'std': 8.50,
                        'k': 2.87
                    },
                    'death_curve': {
                        'name': 'EMGaussian',
                        'mean': 55.09,
                        'std': 23.75,
                        'k': 2.93
                    }
                }
            ]
        }
    ]
}

root = tk.Tk()
app = StyledCloVarSGUI(root)
root.mainloop()