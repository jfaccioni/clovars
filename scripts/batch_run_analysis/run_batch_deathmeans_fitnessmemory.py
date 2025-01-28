from __future__ import annotations

import itertools
from pathlib import Path

from clovars import ROOT_PATH
from clovars.IO import RunParameterValidator, ColonyDataFormatter
from clovars.simulation import run_simulation_function

SETTINGS = {
    'run_path': ROOT_PATH / 'scripts' / 'batch_run_analysis' / 'run.toml',
    'colonies_path': ROOT_PATH / 'scripts' / 'batch_run_analysis' / 'colonies.toml',
    'base_remote_folder': ROOT_PATH / 'data' / 'clovars_output',
    'death_curve_means': [35.09, 55.09, 75.09],
    'fitness_memory': [0.1, 0.3, 0.5, 0.7, 0.9],
}


def main(
        run_path: str | Path,
        colonies_path: str | Path,
        base_remote_folder: Path,
        death_curve_means: list[float],
        fitness_memory: list[float],
) -> None:
    """Main function of this script."""
    run_validator = RunParameterValidator()
    run_validator.parse_toml(toml_path=run_path)
    run_validator.validate()
    run_params = run_validator.to_simulation()

    # Monkey patch output folder to save in remote folder
    output_folder = run_params['simulation_writer_settings']['output_folder']
    run_params['simulation_writer_settings']['output_folder'] = str(base_remote_folder / output_folder)

    colony_formatter = ColonyDataFormatter()
    colony_formatter.parse_toml(toml_path=colonies_path)
    colonies = colony_formatter.to_simulation()

    original_treatments = colonies[0]['treatment_data']  # Assumes a single colony
    original_ctr = original_treatments[0]
    original_tmz = original_treatments[72]
    for death_curve_mean, fitness_memory in itertools.product(death_curve_means, fitness_memory):
        print(f'Running with {death_curve_mean=}, {fitness_memory=}')
        for colony in colonies:
            tmz = original_tmz.copy()
            tmz['death_curve']['mean'] = death_curve_mean
            colony['treatment_data'] = {0: original_ctr.copy(), 72: tmz}
            colony['cells']['mother_fitness_memory'] = fitness_memory
        prefix = f'{fitness_memory}mem_{death_curve_mean}mean'
        run_params['simulation_writer_settings']['parameters_file_name'] = f'{prefix}_params.json'
        run_params['simulation_writer_settings']['cell_csv_file_name'] = f'{prefix}_cell_output.csv'
        run_params['simulation_writer_settings']['colony_csv_file_name'] = f'{prefix}_colony_output.csv'
        run_simulation_function(colony_data=colonies, **run_params)


if __name__ == '__main__':
    main(**SETTINGS)
