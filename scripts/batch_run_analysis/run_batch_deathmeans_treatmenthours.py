from __future__ import annotations

import itertools
from pathlib import Path

from clovars import ROOT_PATH
from clovars.IO import RunParameterValidator, ColonyDataFormatter
from clovars.simulation import run_simulation_function

SETTINGS = {
    'run_path': ROOT_PATH / 'scripts' / 'batch_run_analysis' / 'run.toml',
    'colonies_path': ROOT_PATH / 'scripts' / 'batch_run_analysis' / 'colonies.toml',
    'death_curve_means': [45.09, 55.09, 65.09],
    'hours_to_tmz': [24.0, 48.0, 72.0],
}


def main(
        run_path: str | Path,
        colonies_path: str | Path,
        death_curve_means: list[float],
        hours_to_tmz: list[float],
) -> None:
    """Main function of this script."""
    run_validator = RunParameterValidator()
    run_validator.parse_toml(toml_path=run_path)
    run_validator.validate()
    run_params = run_validator.to_simulation()

    colony_formatter = ColonyDataFormatter()
    colony_formatter.parse_toml(toml_path=colonies_path)
    colonies = colony_formatter.to_simulation()

    original_treatments = colonies[0]['treatment_data']  # Parte do princípio de que só tem 1 colônia
    original_ctr = original_treatments[0]
    original_tmz = original_treatments[72]
    for death_curve_mean, hours_to_tmz in itertools.product(death_curve_means, hours_to_tmz):
        print(f'Running with {death_curve_mean=}, {hours_to_tmz=}')
        for colony in colonies:
            tmz = original_tmz.copy()
            tmz['death_curve']['mean'] = death_curve_mean
            colony['treatment_data'] = {0: original_ctr.copy(), hours_to_tmz: tmz}
        prefix = f'{hours_to_tmz}tt_{death_curve_mean}mean'
        run_params['simulation_writer_settings']['parameters_file_name'] = f'{prefix}_params.json'
        run_params['simulation_writer_settings']['cell_csv_file_name'] = f'{prefix}_cell_output.csv'
        run_params['simulation_writer_settings']['colony_csv_file_name'] = f'{prefix}_colony_output.csv'
        run_simulation_function(colony_data=colonies, **run_params)


if __name__ == '__main__':
    main(**SETTINGS)
