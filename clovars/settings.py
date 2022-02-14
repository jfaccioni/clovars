from __future__ import annotations

import os
from typing import Any

BASE_FOLDER = os.path.join(
    'output',
    '2022-01-26_oxford_runs',
    'Control_95_memory',
)


def get_run_settings() -> dict[str, Any]:
    """Returns a collection of settings necessary for running the Simulation."""
    colony_data = [
        {
            'copies': 100,  # copies of this Colony to create
            'initial_size': 1,  # number of cell in the Colony
            'treatment_data': {
                0: {
                    'name': 'Control',
                    'division_curve': {
                        'name': 'Gamma',
                        'mean': 0.00,
                        'std': 0.90,
                        'a': 28.47,
                    },
                    'death_curve': {
                        'name': 'Gaussian',
                        'mean': 100.00,
                        'std': 1.00,
                    },
                    'signal_disturbance': None,
                    'fitness_memory_disturbance': None,
                },
                # 72: {
                #     'name': 'Temozolomide',
                #     'division_curve': {
                #         'name': 'EMGaussian',
                #         'mean': 13.09,
                #         'std': 7.17,
                #         'k': 3.54,
                #     },
                #     'death_curve': {
                #         'name': 'EMGaussian',
                #         'mean': 55.09,
                #         'std': 23.75,
                #         'k': 2.93,
                #     },
                #     'signal_disturbance': {
                #         'name': 'Gaussian',
                #         'mean': 0.00,
                #         'std': 0.15,
                #     },
                #     'fitness_memory_disturbance': None,
                # },
            },
            'cells': {
                'radius': 20,  # in µm
                'max_speed': 0.020351,  # in µm/seconds
                'fitness_memory': 0.50,  # between 0 and 1
                'signal': {
                    'name': 'Gaussian',
                    'initial_value': 0.0,
                    'std': 0.05,
                },
            },
        },
    ]
    well_settings = {
        'well_radius': 13351.624,  # in µm
    }
    simulation_writer_settings = {
        'output_folder': BASE_FOLDER,
        'parameters_file_name': 'params.json',
        'cell_csv_file_name': 'cell_output.csv',
        'colony_csv_file_name': 'colony_output.csv',
        'confirm_overwrite': False,
    }
    simulation_runner_settings = {
        'delta': 3600,  # int (in seconds)
        'stop_conditions': {
            'stop_at_frame': 24 * 7,  # int, can be None
            'stop_at_single_colony_size': None,  # int, can be None
            'stop_at_all_colonies_size': None,  # int, can be None
        },
    }
    verbose = True
    return {
        'colony_data': colony_data,
        'well_settings': well_settings,
        'simulation_writer_settings': simulation_writer_settings,
        'simulation_runner_settings': simulation_runner_settings,
        'verbose': verbose,
    }


def get_view_settings() -> dict[str, Any]:
    """Returns a collection of settings necessary for viewing a Simulation run."""
    output_folder = os.path.join(BASE_FOLDER, 'view')
    simulation_loader_settings = {
        'simulation_input_folder': BASE_FOLDER,
        'parameters_file_name': 'params.json',
        'cell_csv_file_name': 'cell_output.csv',
        'colony_csv_file_name': 'colony_output.csv',
    }
    view_settings = {
        # MAIN SETTINGS
        'colormap_name': 'viridis',
        'dpi': 320,
        # ete3
        'show_ete3': False,
        'render_ete3': False,
        'ete3_tree_layout': 'family',
        'ete3_file_name': 'tree',
        'ete3_file_extension': 'png',
        # matplotlib 3D
        'show_3D': False,
        'render_3D': True,
        'matplotlib3d_file_name': '3D',
        'matplotlib3d_file_extension': 'svg',
        # matplotlib gaussians
        'show_gaussians': False,
        'render_gaussians': True,
        'division_gaussian': True,
        'death_gaussian': True,
        'gaussians_file_name': 'gaussians',
        'gaussians_file_extension': 'svg',
    }
    verbose = True
    return {
        'output_folder': output_folder,
        'simulation_loader_settings': simulation_loader_settings,
        'view_settings': view_settings,
        'verbose': verbose,
    }


def get_analysis_settings() -> dict[str, Any]:
    """Returns a collection of settings necessary for analysing a Simulation run."""
    output_folder = os.path.join(BASE_FOLDER, 'analysis')
    simulation_loader_settings = {
        'simulation_input_folder': BASE_FOLDER,
        'parameters_file_name': 'params.json',
        'cell_csv_file_name': 'cell_output.csv',
        'colony_csv_file_name': 'colony_output.csv',
    }
    analysis_settings = {
        # treatment statistical analysis
        'compare_treatments': False,
        'treatments_bootstrap_n': 1000,
        # dynafit analysis
        'plot_dynafit': False,
        'dynafit_start_day': 4.0,
        'dynafit_end_day': 7.0,
        'cs_group_filter': 0,
        'cs_merge': False,
        'cs_bins': 10,
        'dynafit_bootstrap_n': 100,
        'use_log_colony_size': False,
        # cell fate distribution
        'show_cell_fate_distributions': False,
        'render_cell_fate_distributions': False,
        'join_treatments': False,
        'distributions_file_name': 'dist',
        'distributions_file_extension': 'png',
        # cell fitness distribution
        'show_cell_fitness_distributions': False,
        # colony division times CV
        'show_colony_division_times_cv': True,
        # videos
        'write_video_colony_signal_vs_size_over_time': False,
        'write_video_colony_fitness_over_time': False,
    }
    verbose = True
    return {
        'output_folder': output_folder,
        'simulation_loader_settings': simulation_loader_settings,
        'analysis_settings': analysis_settings,
        'verbose': verbose,
    }
