from __future__ import annotations

import os
import sys
from argparse import ArgumentParser

import toml

from clovars import DEFAULT_ANALYSIS_PATH, DEFAULT_COLONIES_PATH, DEFAULT_RUN_PATH, DEFAULT_VIEW_PATH, ROOT_PATH
from clovars.simulation import analyse_simulation_function, run_simulation_function, view_simulation_function


def main() -> None:
    """Main function of CloVarS."""
    args = parse_command_line_arguments()
    mode = args['mode'].lower()
    toml_settings = toml.load(args['settings-path'])
    if mode == 'run':
        toml_colony_data = toml.load(args['colonies-path'])
        run_settings = format_run_settings(run_settings=toml_settings, colony_data=toml_colony_data)  # noqa
        run_simulation_function(**run_settings)
    elif mode == 'view':
        view_settings = format_view_settings(view_settings=toml_settings)  # noqa
        view_simulation_function(**view_settings)
    elif mode == 'analyse':
        analyse_settings = format_analyse_settings(analyse_settings=toml_settings)  # noqa
        analyse_simulation_function(**analyse_settings)
    else:
        print(f'Something went wrong, got -> invalid mode {mode}. Exiting...')


def parse_command_line_arguments() -> dict[str, str]:
    parser = ArgumentParser(description='Execute CloVarS')
    parser.add_argument('mode', nargs='?', help='CloVarS execution mode (run/analyse/view)', default='run')
    parser.add_argument('settings-path', nargs='?', help='Path to the settings file', default='')
    parser.add_argument('colonies-path', nargs='?', help='Path to the colonies file (for run mode)', default='')
    args_dict = vars(parser.parse_args())
    mode = args_dict['mode']
    # SETTINGS CHECK
    if not args_dict['settings-path']:  # no settings path was given
        try:
            default_settings_path = {
                'run': DEFAULT_RUN_PATH,
                'view': DEFAULT_VIEW_PATH,
                'analyse': DEFAULT_ANALYSIS_PATH,
                }[mode]
        except KeyError:
            raise ValueError(f'Invalid mode {mode}')
        if input(
            f'WARNING: no settings path provided for {mode} mode. Use default settings?\n'
            f'Default {mode} settings are located at: \n\n{ROOT_PATH / default_settings_path}\n\n'
            '(y/n): '
        ).lower() != 'y':
            print('User chose not to use default settings.')
            sys.exit(0)
        args_dict['settings-path'] = default_settings_path
    # COLONY CHECK
    if mode == 'run' and not args_dict['colonies-path']:  # user wants to run clovars but no colonies path was given
        if input(
                'WARNING: no colonies path provided. Use default colonies?\n'
                f'Default colonies are located at: \n\n{ROOT_PATH / DEFAULT_COLONIES_PATH}\n\n'
                '(y/n): '
        ).lower() != 'y':
            print('User chose not to use default colonies.')
            sys.exit(0)
    args_dict['colonies-path'] = DEFAULT_COLONIES_PATH
    return args_dict


def format_run_settings(
        run_settings: dict,
        colony_data: dict,
) -> dict:
    """Formats the run settings parsed from the TOML file, as expected by CloVarS."""
    return {
        'colony_data': format_colony_data(colony_data),  # noqa
        'well_settings': run_settings['well'],
        'simulation_writer_settings': run_settings['output'],
        'simulation_runner_settings': {
            'delta': run_settings['delta'],
            'stop_conditions': run_settings['stop_conditions'],
        },
        'verbose': run_settings['verbose']
    }


def format_colony_data(input_colony_data: dict) -> list:
    """Formats the colony data parsed from the TOML file, as expected by CloVarS."""
    parsed_colony_data = []
    for colony_data in input_colony_data.get('colony', {}):
        parsed_treatment_data = {}
        for treatment_data in colony_data.get('treatment', {}):
            try:
                start_treatment_frame = treatment_data.pop('added_on_frame')
            except KeyError:  # ignore this treatment since we don't know when to add it
                continue
            parsed_treatment_data[start_treatment_frame] = treatment_data
        parsed_colony_data.append({
            'treatment_data': parsed_treatment_data,
            'copies': colony_data.get('copies', 1),
            'initial_size': colony_data.get('initial_size', 1),
            'cells': colony_data.get('cells', {}),
        })
    return parsed_colony_data


def format_view_settings(view_settings: dict) -> dict:
    """Formats the view settings parsed from the TOML file, as expected by CloVarS."""
    input_dict = view_settings.get('input', {})
    view_dict = view_settings.get('view', {})
    view_2d_dict = view_settings.get('2D_view', {})
    video_2d_dict = view_settings.get('2D_video', {})
    view_3d_dict = view_settings.get('3D_view', {})
    view_treatment_dict = view_settings.get('treatment_curves', {})
    return {
        'output_folder': os.path.join(input_dict.get('simulation_input_folder', '.'), 'view'),
        'simulation_loader_settings': input_dict,
        'view_settings': {
            'colormap_name': view_dict.get('colormap_name', 'viridis'),
            'dpi': view_dict.get('figure_dpi', 320),
            'layout': view_dict.get('layout', 'family'),
            'display_2D': view_2d_dict.get('display', False),
            'render_2D': view_2d_dict.get('render', False),
            'file_name_2D': view_2d_dict.get('render_file_name', '2D'),
            'file_extension_2D': view_2d_dict.get('render_file_extension', 'png'),
            'render_video_2D': video_2d_dict.get('render', False),
            'file_name_video_2D': video_2d_dict.get('render_file_name', '2D'),
            'file_extension_video_2D': video_2d_dict.get('render_file_extension', 'mp4'),
            'display_3D': view_3d_dict.get('display', False),
            'render_3D': view_3d_dict.get('render', False),
            'display_well': view_3d_dict.get('display_well', False),
            'z_axis_ratio': view_3d_dict.get('z_axis_ratio', 1.0),
            'file_name_3D': view_3d_dict.get('render_file_name', '3D'),
            'file_extension_3D': view_3d_dict.get('render_file_extension', 'png'),
            'display_treatments': view_treatment_dict.get('display', False),
            'render_treatments': view_treatment_dict.get('render', False),
            'show_division': view_treatment_dict.get('show_division', False),
            'show_death': view_treatment_dict.get('show_death', False),
            'file_name_treatments': view_treatment_dict.get('render_file_name', 'curves'),
            'file_extension_treatments': view_treatment_dict.get('render_file_extension', 'png'),
        },
        'verbose': view_settings.get('verbose', False)
    }


def format_analyse_settings(analyse_settings: dict) -> dict:
    """Formats the analyse settings parsed from the TOML file, as expected by CloVarS."""
    input_dict = analyse_settings.get('input', {})
    tree_stats_dict = analyse_settings.get('tree_stats', {})
    dynafit_dict = analyse_settings.get('dynafit', {})
    cell_fate_dict = analyse_settings.get('cell_fate_distribution', {})
    cell_fitness_dict = analyse_settings.get('cell_fitness_distribution', {})
    colony_division_times_dict = analyse_settings.get('colony_division_times', {})
    videos_dict = analyse_settings.get('videos', {})
    return {
        'output_folder': os.path.join(input_dict.get('simulation_input_folder', '.'), 'analysis'),
        'simulation_loader_settings': input_dict,
        'analysis_settings': {
            'compare_treatments': tree_stats_dict.get('perform', False),
            'treatments_bootstrap_n': tree_stats_dict.get('bootstrap_n', 100),
            'plot_dynafit': dynafit_dict.get('perform', False),
            'dynafit_start_day': dynafit_dict.get('start_day', 3),
            'dynafit_end_day': dynafit_dict.get('end_day', 6),
            'cs_group_filter': dynafit_dict.get('filter_colonies_smaller_than', 0),
            'cs_merge': dynafit_dict.get('merge_colonies_of_different_sizes', False),
            'cs_bins': dynafit_dict.get('number_of_bins_to_merge_on', 10),
            'dynafit_bootstrap_n': dynafit_dict.get('bootstrap_n', 100),
            'use_log_colony_size': dynafit_dict.get('use_log2_colony_size', False),
            'show_cell_fate_distributions': cell_fate_dict.get('display', False),
            'render_cell_fate_distributions': cell_fate_dict.get('render', False),
            'join_treatments': cell_fate_dict.get('join_treatments', False),
            'distributions_file_name': cell_fate_dict.get('render_file_name', 'cell_fate_distributions'),
            'distributions_file_extension': cell_fate_dict.get('render_file_extension', 'png'),
            'show_cell_fitness_distributions': cell_fitness_dict.get('perform', False),
            'show_colony_division_times_cv': colony_division_times_dict.get('perform', False),
            'write_video_colony_signal_vs_size_over_time': videos_dict.get('render_colony_signal_vs_size', False),
            'write_video_colony_fitness_over_time': videos_dict.get('render_colony_fitness_distribution', False),
        },
        'verbose': analyse_settings.get('verbose', False)
    }


if __name__ == '__main__':
    main()
