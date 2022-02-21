import os
from argparse import ArgumentParser, Namespace

import toml

from clovars import ANALYSE_SETTINGS_PATH, COLONY_DATA_PATH, RUN_SETTINGS_PATH, VIEW_SETTINGS_PATH
from clovars.simulation import analyse_simulation_function, run_simulation_function, view_simulation_function


def main() -> None:
    """Main function of CloVarS."""
    args = parse_command_line_arguments()
    if args.mode.lower() == 'run':
        toml_run_settings = toml.load(RUN_SETTINGS_PATH)
        toml_colony_data = toml.load(COLONY_DATA_PATH)
        run_settings = format_run_settings(run_settings=toml_run_settings, colony_data=toml_colony_data)  # noqa
        run_simulation_function(**run_settings)
    elif args.mode.lower() == 'view':
        toml_view_settings = toml.load(VIEW_SETTINGS_PATH)
        view_settings = format_view_settings(view_settings=toml_view_settings)  # noqa
        view_simulation_function(**view_settings)
    elif args.mode.lower() == 'analyse':
        toml_analyse_settings = toml.load(ANALYSE_SETTINGS_PATH)
        analyse_settings = format_analyse_settings(analyse_settings=toml_analyse_settings)  # noqa
        analyse_simulation_function(**analyse_settings)
    else:
        print(f'Invalid mode {args.mode}. Exiting...')


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
    view_3d_dict = view_settings.get('3D_view', {})
    view_treatment_dict = view_settings.get('treatment_curves', {})
    return {
        'output_folder': os.path.join(input_dict.get('simulation_input_folder', '.'), 'view'),
        'simulation_loader_settings': input_dict,
        'view_settings': {
            'colormap_name': view_dict.get('colormap', 'viridis'),
            'dpi': view_dict.get('figure_dpi', 320),
            'layout': view_dict.get('layout', 'family'),
            'display_2D': view_2d_dict.get('display', False),
            'render_2D': view_2d_dict.get('render', False),
            'file_name_2D': view_2d_dict.get('render_file_name', '2D'),
            'file_extension_2D': view_2d_dict.get('render_file_extension', 'png'),
            'display_3D': view_3d_dict.get('display', False),
            'render_3D': view_3d_dict.get('render', False),
            '3D_file_name': view_3d_dict.get('render_file_name', '3D'),
            '3D_file_extension': view_3d_dict.get('render_file_extension', 'png'),
            'show_gaussians': view_treatment_dict.get('display', False),
            'render_gaussians': view_treatment_dict.get('render', False),
            'division_gaussian': view_treatment_dict.get('show_division', False),
            'death_gaussian': view_treatment_dict.get('show_death', False),
            'gaussians_file_name': view_treatment_dict.get('render_file_name', 'curves'),
            'gaussians_file_extension': view_treatment_dict.get('render_file_extension', 'png'),
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


def parse_command_line_arguments() -> Namespace:
    parser = ArgumentParser(description='Execute CloVarS')
    parser.add_argument(
        'mode',
        nargs='?',
        help='Mode in which to run CloVarS (run/analyse/view)',
        default='run',
    )
    return parser.parse_args()


if __name__ == '__main__':
    main()
