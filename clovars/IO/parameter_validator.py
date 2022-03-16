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
            toml_path: Path,
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
            self.prompt_default(key='stop_at_frame', default=120, prompt_message=prompt_message)
            self.params['stop_at_single_colony_size'] = None
            self.params['stop_at_all_colonies_size'] = None

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


if __name__ == '__main__':
    p = RunParameterValidator()
    print(p)
    p.parse_toml(toml_path=Path('../default_settings/default_run.toml'))
    print(p)
    p.validate()
    print(p)
    print(p.to_simulation())
