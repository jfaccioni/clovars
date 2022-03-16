from __future__ import annotations

import sys
from abc import abstractmethod
from pathlib import Path
from typing import Any

import toml

NoneType = type(None)


class ParameterValidator:
    """Base class representing a parameter validator."""
    expected_params = {
        # key: (key_type, value_type, default)
    }

    def __init__(self) -> None:
        """Initializes a ParameterValidator instance."""
        self.params = {}

    def __str__(self) -> str:
        """Returns a string-version of ParameterValidator."""
        return f'ParameterValidator({self.params=})'

    @abstractmethod
    def to_simulation(self) -> dict[str, Any]:
        """Formats the params as expected by the simulation functions."""
        raise NotImplemented

    def parse_toml(
            self,
            toml_path: str,
    ) -> None:
        """Loads the data from the TOML file into the self.params."""
        for key, value in toml.load(toml_path).items():
            self.load_toml_data(key=key, value=value)

    def load_toml_data(
            self,
            key: str,
            value: Any,
            key_names: list[str] = None,
    ) -> None:
        """Recursively sets the data from the input dictionary into the self.params."""
        if key_names is None:
            key_names = [key]
        if not isinstance(value, dict):
            self.params[".".join(key_names)] = value
        else:
            for k, v in value.items():
                key_names.append(k)
                self.load_toml_data(key=k, value=v, key_names=key_names)
                key_names.pop()

    def validate(self) -> None:
        """Validate the params dict as expected."""
        self.validate_required_keys()
        self.validate_optional_keys()
        self.validate_value_types()

    def validate_required_keys(self) -> None:
        """Prompts the user to use a default value or quit the simulation if a required key isn't in the params."""
        for key, (key_type, _, default) in self.expected_params.items():
            if key_type == 'required' and key not in self.params:
                prompt_message = f'Key {key} not found in parameters. Use default value of {default}? (y/n)'
                self.prompt_default(key=key, default=default, prompt_message=prompt_message)

    def validate_optional_keys(self) -> None:
        """Sets the default values for optional keys."""
        for key, (key_type, _, default) in self.expected_params.items():
            if key_type == 'optional' and key not in self.params:
                self.params[key] = default

    def validate_value_types(self) -> None:
        """Prompts the user to use a default value if an expected value isn't the correct data type."""
        for key, (_, value_type, default) in self.expected_params.items():
            valid_types = (value_type,) if not isinstance(value_type, tuple) else value_type
            value = self.params[key]
            if not (
                    isinstance(value, valid_types) or
                    (isinstance(value, bool) and int in valid_types)  # bools are instances of integers
            ):
                prompt_message = (
                    f'Value {value} associated with {key} is not of the proper type {[t.__name__ for t in valid_types]}'
                    f'. Use default value of {default}? (y/n): '
                )
                self.prompt_default(key=key, default=default, prompt_message=prompt_message)

    def prompt_default(
            self,
            key: str,
            default: Any,
            prompt_message: str,
    ) -> None:
        """Prompts the user whether to use a default value for the value with incorrect data type or not."""
        while True:
            answer = input(prompt_message)
            if answer.lower() == 'y':
                self.params[key] = default
                break
            elif answer.lower() == 'n':
                self.exit()
            print('Please answer with "y" or "n" only.')

    @staticmethod
    def exit() -> None:
        """Prints the quit message and exits the simulation."""
        print("User chose to not use a default value. Exiting the simulation...")
        sys.exit(0)


class RunParameterValidator(ParameterValidator):
    """Class representing a validator of the simulation's run parameters."""
    expected_params = {
        'well.well_radius': ('required', (int, float), 13_351.624),
        'output.output_folder': ('required', str, 'output'),
        'output.parameters_file_name': ('required', str, 'params.json'),
        'output.cell_csv_file_name': ('required', str, 'cell_output.csv'),
        'output.colony_csv_file_name': ('required', str, 'colony_output.csv'),
        'output.confirm_overwrite': ('optional', bool, True),
        'delta': ('required', int, 3600),
        'stop_conditions.stop_at_frame': ('optional', (int, NoneType), None),
        'stop_conditions.stop_at_single_colony_size': ('optional', (int, NoneType), None),
        'stop_conditions.stop_at_all_colonies_size': ('optional', (int, NoneType), None),
        'verbose': ('optional', bool, True),
    }

    def validate(self) -> None:
        """Validates the stop conditions before following onwards with base validation."""
        self.validate_stop_conditions()
        super().validate()

    def validate_stop_conditions(self) -> None:
        """Checks if at least one stop condition is present in the simulation."""
        stop_condition_keys = [
            'stop_conditions.stop_at_frame',
            'stop_conditions.stop_at_single_colony_size',
            'stop_conditions.stop_at_all_colonies_size',
        ]
        if not any(stop_condition_key in self.params for stop_condition_key in stop_condition_keys):
            prompt_message = 'No stop condition detected. Use default of stop at frame = 120? (y/n)'
            self.prompt_default(key='stop_conditions.stop_at_frame', default=120, prompt_message=prompt_message)
            self.params['stop_conditions.stop_at_single_colony_size'] = None
            self.params['stop_conditions.stop_at_all_colonies_size'] = None

    @property
    def well_settings(self) -> dict[str, Any]:
        """Returns the well settings dictionary."""
        return {
            'well_radius': self.params['well.well_radius']
        }

    @property
    def simulation_writer_settings(self) -> dict[str, Any]:
        """Returns the simulation writer settings dictionary."""
        return {
            'output_folder': self.params['output.output_folder'],
            'parameters_file_name': self.params['output.parameters_file_name'],
            'cell_csv_file_name': self.params['output.cell_csv_file_name'],
            'colony_csv_file_name': self.params['output.colony_csv_file_name'],
            'confirm_overwrite': self.params['output.confirm_overwrite'],
        }

    @property
    def simulation_runner_settings(self) -> dict[str, Any]:
        """Returns the simulation runner settings dictionary."""
        return {
            'delta': self.params['delta'],
            'stop_conditions': self.stop_conditions,
        }

    @property
    def stop_conditions(self) -> dict[str, Any]:
        """Returns the stop conditions dictionary."""
        return {
            'stop_at_frame': self.params['stop_conditions.stop_at_frame'],
            'stop_at_single_colony_size': self.params['stop_conditions.stop_at_single_colony_size'],
            'stop_at_all_colonies_size': self.params['stop_conditions.stop_at_all_colonies_size'],
        }

    @property
    def verbose(self) -> bool:
        """Returns the verbose flag."""
        return self.params['verbose']

    def to_simulation(self) -> dict[str, Any]:
        """Returns a dictionary as expected by the run_simulation_function."""
        return {
            'well_settings': self.well_settings,
            'simulation_writer_settings': self.simulation_writer_settings,
            'simulation_runner_settings': self.simulation_runner_settings,
            'verbose': self.verbose,
        }


class ViewParameterValidator(ParameterValidator):
    """Class representing a validator of the simulation's view parameters."""
    expected_params = {
        'input.simulation_input_folder': ('required', str, 'output'),
        'input.parameters_file_name': ('required', str, 'params.json'),
        'input.cell_csv_file_name': ('required', str, 'cell_output.csv'),
        'input.colony_csv_file_name': ('required', str, 'colony_output.csv'),
        'view.colormap_name': ('required', str, 'viridis'),
        'view.layout': ('required', str, 'family'),
        'view.figure_dpi': ('optional', int, 320),
        '2D_view.display': ('optional', bool, False),
        '2D_view.render': ('optional', bool, False),
        '2D_view.render_file_name': ('optional', str, '2D'),
        '2D_view.render_file_extension': ('optional', str, 'png'),
        '2D_video.render': ('optional', bool, False),
        '2D_video.render_file_name': ('optional', str, '2D'),
        '2D_video.render_file_extension': ('optional', str, 'mp4'),
        '3D_view.display': ('optional', bool, False),
        '3D_view.render': ('optional', bool, False),
        '3D_view.display_well': ('optional', bool, False),
        '3D_view.z_axis_ratio': ('optional', float, 1.2),
        '3D_view.render_file_name': ('optional', str, '3D'),
        '3D_view.render_file_extension': ('optional', str, 'png'),
        'treatment_curves.display': ('optional', bool, False),
        'treatment_curves.render': ('optional', bool, False),
        'treatment_curves.show_division': ('optional', bool, False),
        'treatment_curves.show_death': ('optional', bool, False),
        'treatment_curves.render_file_name': ('optional', str, 'treatments'),
        'treatment_curves.render_file_extension': ('optional', str, 'png'),
        'verbose': ('optional', bool, True),
    }

    @property
    def output_folder(self) -> str:
        """Returns the path to the view output folder."""
        return str(Path(self.params.get('input.simulation_input_folder', '.'), 'view'))

    @property
    def simulation_loader_settings(self) -> dict[str, Any]:
        """Returns the simulation loader settings dictionary."""
        return {
            'simulation_input_folder': self.params['input.simulation_input_folder'],
            'parameters_file_name': self.params['input.parameters_file_name'],
            'cell_csv_file_name': self.params['input.cell_csv_file_name'],
            'colony_csv_file_name': self.params['input.colony_csv_file_name'],
        }

    @property
    def view_settings(self) -> dict[str, Any]:
        """Returns the view settings dictionary."""
        return {
            'colormap_name': self.params['view.colormap_name'],
            'layout': self.params['view.layout'],
            'dpi': self.params['view.figure_dpi'],
            'display_2D': self.params['2D_view.display'],
            'render_2D': self.params['2D_view.render'],
            'file_name_2D': self.params['2D_view.render_file_name'],
            'file_extension_2D': self.params['2D_view.render_file_extension'],
            'render_video_2D': self.params['2D_video.render'],
            'file_name_video_2D': self.params['2D_video.render_file_name'],
            'file_extension_video_2D': self.params['2D_video.render_file_extension'],
            'display_3D': self.params['3D_view.display'],
            'render_3D': self.params['3D_view.render'],
            'display_well': self.params['3D_view.display_well'],
            'z_axis_ratio': self.params['3D_view.z_axis_ratio'],
            'file_name_3D': self.params['3D_view.render_file_name'],
            'file_extension_3D': self.params['3D_view.render_file_extension'],
            'display_treatments': self.params['treatment_curves.display'],
            'render_treatments': self.params['treatment_curves.render'],
            'show_division': self.params['treatment_curves.show_division'],
            'show_death': self.params['treatment_curves.show_death'],
            'file_name_treatments': self.params['treatment_curves.render_file_name'],
            'file_extension_treatments': self.params['treatment_curves.render_file_extension'],
        }

    @property
    def verbose(self) -> bool:
        """Returns the verbose flag."""
        return self.params['verbose']

    def to_simulation(self) -> dict[str, Any]:
        """Returns a dictionary as expected by the view_simulation_function."""
        return {
            'output_folder': self.output_folder,
            'simulation_loader_settings': self.simulation_loader_settings,
            'view_settings': self.view_settings,
            'verbose': self.verbose,
        }


class AnalysisParameterValidator(ParameterValidator):
    """Class representing a validator of the simulation's analysis parameters."""
    expected_params = {
        'input.simulation_input_folder': ('required', str, 'output'),
        'input.parameters_file_name': ('required', str, 'params.json'),
        'input.cell_csv_file_name': ('required', str, 'cell_output.csv'),
        'input.colony_csv_file_name': ('required', str, 'colony_output.csv'),
        'tree_stats.perform': ('optional', bool, False),
        'tree_stats.bootstrap_n': ('optional', int, 1000),
        'dynafit.perform': ('optional', bool, False),
        'dynafit.start_day': ('optional', float, 4.0),
        'dynafit.end_day': ('optional', float, 7.0),
        'dynafit.filter_colonies_smaller_than': ('optional', int, 0),
        'dynafit.merge_colonies_of_different_sizes': ('optional', bool, False),
        'dynafit.number_of_bins_to_merge_on': ('optional', int, 10),
        'dynafit.bootstrap_n': ('optional', int, 1000),
        'dynafit.use_log2_colony_size': ('optional', bool, False),
        'cell_fate_distribution.display': ('optional', bool, False),
        'cell_fate_distribution.render': ('optional', bool, False),
        'cell_fate_distribution.join_treatments': ('optional', bool, False),
        'cell_fate_distribution.render_file_name': ('optional', str, 'cell_fate_distribution'),
        'cell_fate_distribution.render_file_extension': ('optional', str, 'png'),
        'cell_fitness_distribution.perform': ('optional', bool, False),
        'colony_division_times.perform': ('optional', bool, False),
        'videos.render_colony_signal_vs_size': ('optional', bool, False),
        'videos.render_colony_fitness_distribution': ('optional', bool, False),
        'verbose': ('optional', bool, True),
    }

    @property
    def output_folder(self) -> str:
        """Returns the path to the view output folder."""
        return str(Path(self.params.get('input.simulation_input_folder', '.'), 'analysis'))

    @property
    def simulation_loader_settings(self) -> dict[str, Any]:
        """Returns the simulation loader settings dictionary."""
        return {
            'simulation_input_folder': self.params['input.simulation_input_folder'],
            'parameters_file_name': self.params['input.parameters_file_name'],
            'cell_csv_file_name': self.params['input.cell_csv_file_name'],
            'colony_csv_file_name': self.params['input.colony_csv_file_name'],
        }

    @property
    def analysis_settings(self) -> dict[str, Any]:
        """Returns the analysis settings dictionary."""
        return {
            'compare_treatments': self.params['tree_stats.perform'],
            'treatments_bootstrap_n': self.params['tree_stats.bootstrap_n'],
            'plot_dynafit': self.params['dynafit.perform'],
            'dynafit_start_day': self.params['dynafit.start_day'],
            'dynafit_end_day': self.params['dynafit.end_day'],
            'cs_group_filter': self.params['dynafit.filter_colonies_smaller_than'],
            'cs_merge': self.params['dynafit.merge_colonies_of_different_sizes'],
            'cs_bins': self.params['dynafit.number_of_bins_to_merge_on'],
            'dynafit_bootstrap_n': self.params['dynafit.bootstrap_n'],
            'use_log_colony_size': self.params['dynafit.use_log2_colony_size'],
            'show_cell_fate_distributions': self.params['cell_fate_distribution.display'],
            'render_cell_fate_distributions': self.params['cell_fate_distribution.render'],
            'join_treatments': self.params['cell_fate_distribution.join_treatments'],
            'distributions_file_name': self.params['cell_fate_distribution.render_file_name'],
            'distributions_file_extension': self.params['cell_fate_distribution.render_file_extension'],
            'show_cell_fitness_distributions': self.params['cell_fitness_distribution.perform'],
            'show_colony_division_times_cv': self.params['colony_division_times.perform'],
            'write_video_colony_signal_vs_size_over_time': self.params['videos.render_colony_signal_vs_size'],
            'write_video_colony_fitness_over_time': self.params['videos.render_colony_fitness_distribution'],
        }

    @property
    def verbose(self) -> bool:
        """Returns the verbose flag."""
        return self.params['verbose']

    def to_simulation(self) -> dict[str, Any]:
        """Returns a dictionary as expected by the view_simulation_function."""
        return {
            'output_folder': self.output_folder,
            'simulation_loader_settings': self.simulation_loader_settings,
            'analysis_settings': self.analysis_settings,
            'verbose': self.verbose,
        }


class FitParameterValidator(ParameterValidator):
    """Class representing a validator of the simulation's fit parameters."""
    expected_params = {
        'input.input_file': ('required', str, 'data.csv'),
        'input.sheet_name': ('optional', str, 'Sheet1'),
        'input.division_hours_column_name': ('required', str, 'Division Times'),
        'input.death_hours_column_name': ('required', str, 'Death Times'),
        'verbose': ('optional', bool, True),
    }

    def validate(self) -> None:
        """Validates the file type and change the required arguments accordingly before resuming standard validation."""
        if self.input_file.endswith('.xlsx'):
            self.expected_params['input.input_sheet_name'] = ('required', str, 'Sheet1')
        super().validate()

    @property
    def input_file(self) -> str:
        """Returns the path to the fit input file."""
        return self.params['input.input_file']

    @property
    def sheet_name(self) -> str:
        """Returns the sheet name parameter."""
        return self.params['input.sheet_name']

    @property
    def division_times_column(self) -> str:
        """Returns the division times column name."""
        return self.params['input.division_hours_column_name']

    @property
    def death_times_column(self) -> str:
        """Returns the death times column name."""
        return self.params['input.death_hours_column_name']

    @property
    def verbose(self) -> bool:
        """Returns the verbose flag."""
        return self.params['verbose']

    def to_simulation(self) -> dict[str, Any]:
        """Returns a dictionary as expected by the fit_experimental_data_function."""
        return {
            'input_file': self.input_file,
            'sheet_name': self.sheet_name,
            'division_times_column': self.division_times_column,
            'death_times_column': self.death_times_column,
            'verbose': self.verbose,
        }


class ColonyDataFormatter:
    """Class representing a formatter of the simulation's colony data (does not perform actual validation)."""

    def __init__(self) -> None:
        """Initializes a ColonyDataFormatter instance."""
        self.data = []

    def __str__(self) -> str:
        """Returns a string-version of ColonyDataFormatter."""
        return f'ColonyDataFormatter({self.data=})'

    def parse_toml(
            self,
            toml_path: str,
    ) -> None:
        """Parses the data from the TOML file and sets it to the self.data attribute."""
        for colony_data in toml.load(toml_path).get('colony', {}):
            parsed_treatment_data = {}
            for treatment_data in colony_data.get('treatment', {}):
                try:
                    start_treatment_frame = treatment_data.pop('added_on_frame')
                except KeyError:  # ignore this treatment since we don't know when to add it
                    continue
                parsed_treatment_data[start_treatment_frame] = treatment_data
            self.data.append({
                'treatment_data': parsed_treatment_data,
                'copies': colony_data.get('copies', 1),
                'initial_size': colony_data.get('initial_size', 1),
                'cells': colony_data.get('cells', {}),
            })

    def to_simulation(self) -> list[dict[str, Any]]:
        """Returns the colony data as expected by the run_simulation_function."""
        return self.data
