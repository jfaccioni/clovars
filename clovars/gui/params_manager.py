from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Any

PARAMS_FILE_NAME = 'params.json'
CELL_CSV_FILE_NAME = 'cells.csv'
COLONY_CSV_FILE_NAME = 'colony.csv'
RUN_OUTPUT_FOLDER = "."
VIEW_INPUT_FOLDER = RUN_OUTPUT_FOLDER
VIEW_OUTPUT_FOLDER = os.path.join(RUN_OUTPUT_FOLDER, 'view')
ANALYSIS_INPUT_FOLDER = RUN_OUTPUT_FOLDER
ANALYSIS_OUTPUT_FOLDER = os.path.join(RUN_OUTPUT_FOLDER, 'analysis')


@dataclass
class ParamsManager:
    """DataClass responsible for managing all parameters that the user interacts with through the GUI."""
    _run_params: RunParams | None = None
    _view_params: ViewParams | None = None
    _analysis_params: AnalysisParams | None = None

    def __post_init__(self) -> None:
        if self._run_params is None:
            self._run_params = RunParams()
        if self._view_params is None:
            self._view_params = ViewParams()
        if self._analysis_params is None:
            self._analysis_params = AnalysisParams()

    def get_run_params(self) -> dict[str, Any]:
        """Returns the parameters currently stored in the RunSettings instance."""
        return self._run_params.to_simulation()

    def get_view_params(self) -> dict[str, Any]:
        """Returns the parameters currently stored in the ViewSettings instance."""
        return self._view_params.to_simulation()

    def get_analysis_params(self) -> dict[str, Any]:
        """Returns the parameters currently stored in the AnalysisSettings instance."""
        return self._analysis_params.to_simulation()


@dataclass
class RunParams:
    """DataClass holding the parameters needed to run a simulation."""
    colony_params_list: list[ColonyParams] | None = None
    well_radius: float = 13351.624  # in µm
    output_folder: str = RUN_OUTPUT_FOLDER
    params_file_name: str = PARAMS_FILE_NAME
    cell_csv_file_name: str = CELL_CSV_FILE_NAME
    colony_csv_file_name: str = COLONY_CSV_FILE_NAME
    warn_on_overwrite: bool = True
    stop_at_frame: int | None = 100
    stop_at_single_colony_size: int | None = None
    stop_at_all_colonies_size: int | None = None
    delta: int = 3600
    verbose: bool = True

    def __post_init__(self):
        """Sets default attributes if their value is None."""
        if self.colony_params_list is None:
            self.colony_params_list = []

    def to_simulation(self) -> dict[str, Any]:
        """Returns dictionary of run simulation parameters, as expected by the run simulation function."""
        if not (colony_data := [colony_params.to_simulation() for colony_params in self.colony_params_list]):
            colony_data = [{}]  # Creates at least one Colony
        return {
            'colony_data': colony_data,
            'well_settings': {
                'well_radius': self.well_radius,
            },
            'simulation_writer_settings': {
                'output_folder': self.output_folder,
                'parameters_file_name': self.params_file_name,
                'cell_csv_file_name': self.cell_csv_file_name,
                'colony_csv_file_name': self.colony_csv_file_name,
                'warn_on_overwrite': self.warn_on_overwrite,
            },
            'simulation_runner_settings': {
                'delta': self.delta,
                'stop_conditions': {
                    'stop_at_frame': self.stop_at_frame,
                    'stop_at_single_colony_size': self.stop_at_single_colony_size,
                    'stop_at_all_colonies_size': self.stop_at_all_colonies_size,
                },
            },
            'verbose': self.verbose,
        }


@dataclass
class ColonyParams:
    """DataClass holding the parameters needed to instantiate a Colony."""
    copies: int = 1  # copies of this Colony to create
    initial_size: int = 1  # number of cell in the Colony
    radius: float = 20.0  # in µm
    max_speed: float = 0.020351  # in µm/seconds
    fitness_memory: float = 0.0  # between 0 and 1
    signal_params: CellSignalParams | None = None
    treatment_params_list: list[TreatmentParams] | None = None

    def __post_init__(self):
        """Sets the default attributes if their value is None."""
        if self.treatment_params_list is None:
            self.treatment_params_list = []

    def to_simulation(self) -> dict:
        """Returns a dictionary of Colony parameters, as expected by the run simulation function."""
        treatment_data = {
            treatment_params.frame_added: treatment_params.to_simulation()
            for treatment_params in self.treatment_params_list
        }
        if (signal_params := self.signal_params) is None:
            signal_params = CellSignalParams()
        signal = signal_params.to_simulation()
        return {
            'copies': self.copies,
            'initial_size': self.initial_size,
            'treatment_data': treatment_data,
            'cells': {
                'radius': self.radius,
                'max_speed': self.max_speed,
                'fitness_memory': self.fitness_memory,
                'signal': signal,
            },
        }


@dataclass
class TreatmentParams:
    """DataClass holding the parameters needed to instantiate a Treatment."""
    name: str
    frame_added: int
    division_curve_params: CurveParams | None = None
    death_curve_params: CurveParams | None = None
    signal_disturbance_params: CellSignalParams | None = None

    def to_simulation(self) -> dict:
        """Returns a dictionary of Treatment parameters, as expected by the run simulation function."""
        if (division_curve_params := self.division_curve_params) is not None:
            division_curve_params = CurveParams()
        division_curve = division_curve_params.to_simulation()
        if (death_curve_params := self.death_curve_params) is not None:
            death_curve_params = CurveParams()
        death_curve = death_curve_params.to_simulation()
        if (signal_disturbance_params := self.signal_disturbance_params) is not None:
            signal_disturbance_params = CellSignalParams()
        signal_disturbance = signal_disturbance_params.to_simulation()
        return {
            'name': self.name,
            'division_curve': division_curve,
            'death_curve': death_curve,
            'signal_disturbance': signal_disturbance,
        }


@dataclass
class CurveParams:
    """DataClass holding the parameters needed to instantiate a Curve."""
    name: str = 'Gaussian'
    mean: float = 0.0
    std: float = 1.0
    k: float = 1.0
    a: float = 1.0
    s: float = 1.0

    def to_simulation(self) -> dict:
        """Returns a dictionary of Curve parameters, as expected by the run simulation function."""
        return {
            'name': self.name,
            'mean': self.mean,
            'std': self.std,
            'k': self.k,
            'a': self.a,
            's': self.s,
        }


@dataclass
class CellSignalParams:
    """DataClass holding the parameters needed to instantiate a CellSignal."""
    name: str = 'Gaussian'
    initial_value: float = 0.0
    period: float = 0.05
    noise: float = 0.05
    stochastic_weight: float = 0.05
    mean: float = 0.05
    std: float = 0.05
    k: float = 0.05

    def to_simulation(self) -> dict:
        """Returns a dictionary of CellSignal parameters, as expected by the run simulation function."""
        return {
            'name': self.name,
            'initial_value': self.initial_value,
            'period': self.period,
            'noise': self.noise,
            'stochastic_weight': self.stochastic_weight,
            'mean': self.mean,
            'std': self.std,
            'k': self.k,
        }


@dataclass
class ViewParams:
    """DataClass holding the parameters needed to view a simulation."""
    output_folder: str = VIEW_OUTPUT_FOLDER
    simulation_input_folder: str = VIEW_INPUT_FOLDER
    parameters_file_name: str = PARAMS_FILE_NAME
    cell_csv_file_name: str = CELL_CSV_FILE_NAME
    colony_csv_file_name: str = COLONY_CSV_FILE_NAME
    colormap_name: str = 'plasma'
    dpi: int = 120
    show_ete3: bool = False
    render_ete3: bool = False
    ete3_tree_layout: str = 'signal'
    ete3_file_name: str = 'tree'
    ete3_file_extension: str = 'png'
    show_3D: bool = True
    render_3D: bool = False
    matplotlib3d_file_name: str = '3D'
    matplotlib3d_file_extension: str = 'png'
    show_gaussians: bool = False
    render_gaussians: bool = False
    division_gaussian: bool = False
    death_gaussian: bool = False
    gaussians_file_name: str = 'gaussians'
    gaussians_file_extension: str = 'png'
    verbose: bool = True

    def to_simulation(self) -> dict[str, Any]:
        """Returns dictionary of view simulation parameters, as expected by the view simulation function."""
        return {
            'output_folder': self.output_folder,
            'simulation_loader_settings': {
                'simulation_input_folder': self.simulation_input_folder,
                'parameters_file_name': self.parameters_file_name,
                'cell_csv_file_name': self.cell_csv_file_name,
                'colony_csv_file_name': self.colony_csv_file_name,
            },
            'view_settings': {
                'colormap_name': self.colormap_name,
                'dpi': self.dpi,
                'show_ete3': self.show_ete3,
                'render_ete3': self.render_ete3,
                'ete3_tree_layout': self.ete3_tree_layout,
                'ete3_file_name': self.ete3_file_name,
                'ete3_file_extension': self.ete3_file_extension,
                'show_3D': self.show_3D,
                'render_3D': self.render_3D,
                'matplotlib3d_file_name': self.matplotlib3d_file_name,
                'matplotlib3d_file_extension': self.matplotlib3d_file_extension,
                'show_gaussians': self.show_gaussians,
                'render_gaussians': self.render_gaussians,
                'division_gaussian': self.division_gaussian,
                'death_gaussian': self.death_gaussian,
                'gaussians_file_name': self.gaussians_file_name,
                'gaussians_file_extension': self.gaussians_file_extension,
            },
            'verbose': self.verbose,
        }


@dataclass
class AnalysisParams:
    """DataClass holding the parameters needed to view a simulation."""
    output_folder: str = ANALYSIS_OUTPUT_FOLDER
    simulation_input_folder: str = ANALYSIS_INPUT_FOLDER
    parameters_file_name: str = PARAMS_FILE_NAME
    cell_csv_file_name: str = CELL_CSV_FILE_NAME
    colony_csv_file_name: str = COLONY_CSV_FILE_NAME
    compare_treatments: bool = False
    treatments_bootstrap_n: int = 1000
    plot_dynafit: bool = False
    dynafit_start_day: float = 6.0
    dynafit_end_day: float = 9.0
    cs_group_size_filter: int = 5
    cs_merge: bool = False
    cs_bins: int = 10
    dynafit_bootstrap_n: int = 100
    use_log_colony_size: bool = False
    show_cell_fate_distributions: bool = False
    render_cell_fate_distributions: bool = False
    join_treatments: bool = False
    distributions_file_name: str = 'dist'
    distributions_file_extension: str = 'png'
    show_cell_fitness_distributions: bool = False
    verbose: bool = True

    def to_simulation(self) -> dict[str, Any]:
        """Returns dictionary of analyse simulation parameters, as expected by the analyse_simulation function."""
        return {
            'output_folder': self.output_folder,
            'simulation_loader_settings': {
                'simulation_input_folder': self.simulation_input_folder,
                'parameters_file_name': self.parameters_file_name,
                'cell_csv_file_name': self.cell_csv_file_name,
                'colony_csv_file_name': self.colony_csv_file_name,
            },
            'analysis_settings': {
                'compare_treatments': self.compare_treatments,
                'treatments_bootstrap_n': self.treatments_bootstrap_n,
                'plot_dynafit': self.plot_dynafit,
                'dynafit_start_day': self.dynafit_start_day,
                'dynafit_end_day': self.dynafit_end_day,
                'cs_group_size_filter': self.cs_group_size_filter,
                'cs_merge': self.cs_merge,
                'cs_bins': self.cs_bins,
                'dynafit_bootstrap_n': self.dynafit_bootstrap_n,
                'use_log_colony_size': self.use_log_colony_size,
                'show_cell_fate_distributions': self.show_cell_fate_distributions,
                'render_cell_fate_distributions': self.render_cell_fate_distributions,
                'join_treatments': self.join_treatments,
                'distributions_file_name': self.distributions_file_name,
                'distributions_file_extension': self.distributions_file_extension,
                'show_cell_fitness_distributions': self.show_cell_fitness_distributions,
            },
            'verbose': self.verbose,
        }
