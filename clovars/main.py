from __future__ import annotations

import sys
from argparse import ArgumentParser
from typing import Any, Callable, TYPE_CHECKING

from clovars import (
    DEFAULT_ANALYSIS_PATH,
    DEFAULT_COLONIES_PATH,
    DEFAULT_FIT_PATH,
    DEFAULT_RUN_PATH,
    DEFAULT_VIEW_PATH,
    ROOT_PATH,
)
from clovars.IO.parameter_validator import (
    AnalysisParameterValidator,
    FitParameterValidator,
    ColonyDataFormatter,
    RunParameterValidator,
    ViewParameterValidator,
)
from clovars.simulation import (
    analyse_simulation_function,
    fit_experimental_data_function,
    run_simulation_function,
    view_simulation_function,
)

if TYPE_CHECKING:
    from clovars.IO.parameter_validator import ParameterValidator


def main() -> None:
    """Main function of CloVarS."""
    mode, settings_path, colonies_path = parse_command_line_arguments()
    validator, simulation_function = get_validator_and_function(mode=mode)
    validator.parse_toml(settings_path)
    validator.validate()
    params = validator.to_simulation()
    print(f'Executing CloVarS in mode {mode}\n--- Parameters:\n{params}')
    if mode == 'run':  # need to format the colony data
        formatter = ColonyDataFormatter()
        formatter.parse_toml(colonies_path)
        colony_data = formatter.to_simulation()
        print(f'--- Colony data:\n{colony_data}')
        simulation_function(colony_data=colony_data, **params)
    else:
        simulation_function(**params)


def get_validator_and_function(mode: str) -> tuple[ParameterValidator, Callable]:
    """Given the simulation execution mode, returns the corresponding parameter validator and execution function."""
    try:
        return {
            'run': (RunParameterValidator(), run_simulation_function),
            'view': (ViewParameterValidator(), view_simulation_function),
            'analyse': (AnalysisParameterValidator(), analyse_simulation_function),
            'fit': (FitParameterValidator(), fit_experimental_data_function),
        }[mode]
    except KeyError:
        raise ValueError(f'Something went wrong, got invalid mode {mode}. Exiting...')


def parse_command_line_arguments() -> tuple[str, str, str]:
    parser = ArgumentParser(description='Execute CloVarS')
    parser.add_argument('mode', nargs='?', help='CloVarS execution mode (run/analyse/view)', default='')
    parser.add_argument('settings-path', nargs='?', help='Path to the settings file', default='')
    parser.add_argument('colonies-path', nargs='?', help='Path to the colonies file (for run mode)', default='')
    args_dict = vars(parser.parse_args())
    mode = get_mode(args_dict=args_dict)
    settings_path = get_settings_path(args_dict=args_dict, mode=mode)
    colonies_path = get_colonies_path(args_dict=args_dict) if mode == 'run' else ''
    return mode, settings_path, colonies_path


def get_mode(args_dict: dict[str, Any]) -> str:
    """Returns the execution mode from the command line args dict."""
    if not (mode := args_dict['mode']):  # no execution mode was given
        print('WARNING: no execution mode provided, defaulting to run mode.')
        return 'run'
    return mode.lower()


def get_settings_path(
        args_dict: dict[str, Any],
        mode: str,
) -> str:
    """Returns the settings path from the command line args dict."""
    if not (settings_path := args_dict['settings-path']):  # no settings path was given
        default_settings_path = get_default_settings_path(mode=mode)
        prompt_use_default_settings(mode=mode, default_settings_path=default_settings_path)
        return default_settings_path
    return settings_path


def get_default_settings_path(mode: str) -> str:
    """Returns the default settings path for the given mode."""
    try:
        return {
            'run': DEFAULT_RUN_PATH,
            'view': DEFAULT_VIEW_PATH,
            'analyse': DEFAULT_ANALYSIS_PATH,
            'fit': DEFAULT_FIT_PATH,
        }[mode]
    except KeyError:
        raise ValueError(f'Invalid mode {mode}')


def prompt_use_default_settings(
        mode: str,
        default_settings_path: str,
) -> None:
    """Prompts the user whether to use the default settings path or exit the simulation."""
    while True:
        answer = input(
            f'WARNING: no settings path provided for {mode} mode. Use default settings?\n'
            f'Default {mode} settings are located at: \n\n{ROOT_PATH / default_settings_path}\n\n'
            '(y/n): '
        ).lower()
        if answer == 'y':
            return
        elif answer == 'n':
            print('User chose not to use default settings.')
            sys.exit(0)
        else:
            print('Please answer with "y" or "n" only.')


def get_colonies_path(args_dict: dict[str, Any]) -> str:
    if not (colonies_path := args_dict['colonies-path']):  # user wants to run clovars but no colonies path was given
        prompt_use_default_colonies()
        return DEFAULT_COLONIES_PATH
    return colonies_path


def prompt_use_default_colonies() -> None:
    """Prompts the user whether to use the default colonies path or exit the simulation."""
    while True:
        answer = input(
            'WARNING: no colonies path provided. Use default colonies?\n'
            f'Default colonies are located at: \n\n{ROOT_PATH / DEFAULT_COLONIES_PATH}\n\n'
            '(y/n): '
        ).lower()
        if answer == 'y':
            return
        elif answer == 'n':
            print('User chose not to use default colonies.')
            sys.exit(0)
        else:
            print('Please answer with "y" or "n" only.')


if __name__ == '__main__':
    main()
