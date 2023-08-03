from __future__ import annotations

from pathlib import Path

import numpy as np

from clovars import ROOT_PATH
from clovars.IO import RunParameterValidator, ColonyDataFormatter
from clovars.simulation import run_simulation_function

SETTINGS = {
    'run_path': ROOT_PATH / 'scripts' / 'batch_run_analysis' / 'run.toml',
    'colonies_path': ROOT_PATH / 'scripts' / 'batch_run_analysis' / 'colonies.toml',
    'batch_fitness_memory': np.linspace(0.0, 1.0, 11).tolist(),
}


def main(
        run_path: str | Path,
        colonies_path: str | Path,
        batch_fitness_memory: list[float],
) -> None:
    """Main function of this script."""
    run_validator = RunParameterValidator()
    run_validator.parse_toml(toml_path=run_path)
    run_validator.validate()
    run_params = run_validator.to_simulation()
    print(run_params)

    colony_formatter = ColonyDataFormatter()
    colony_formatter.parse_toml(toml_path=colonies_path)
    colonies = colony_formatter.to_simulation()

    for fitness_memory in batch_fitness_memory:
        for colony in colonies:
            colony['cells']['mother_fitness_memory'] = fitness_memory
        run_params['simulation_writer_settings']['parameters_file_name'] = f'params_{fitness_memory:.2f}.json'
        run_params['simulation_writer_settings']['cell_csv_file_name'] = f'cell_output_{fitness_memory:.2f}.csv'
        run_params['simulation_writer_settings']['colony_csv_file_name'] = f'colony_output_{fitness_memory:.2f}.csv'
        run_simulation_function(colony_data=colonies, **run_params)


if __name__ == '__main__':
    main(**SETTINGS)
