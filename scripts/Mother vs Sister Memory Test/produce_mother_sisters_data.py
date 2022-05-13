from __future__ import annotations

from itertools import product

from clovars.IO.parameter_validator import RunParameterValidator, ColonyDataFormatter
from clovars.simulation import run_simulation_function
from utils import DATA_SYMLINK_PATH

SETTINGS = {
    'mother_memories': [0.0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0],
    'sister_memories': [0.0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0],
}


def main(
        mother_memories: list[float],
        sister_memories: list[float],
) -> None:
    """Main function of this script."""
    n_runs = len(mother_memories) * len(sister_memories)
    for i, (mother_memory, sister_memory) in enumerate(product(mother_memories, sister_memories), 1):
        print(f"Running simulation {i:03}/{n_runs} with: | {mother_memory=} | {sister_memory=}", )
        # Validates and gets the run settings
        validator = RunParameterValidator()
        validator.parse_toml('run.toml')
        validator.validate()
        params = validator.to_simulation()
        # Formats and gets the colony data
        formatter = ColonyDataFormatter()
        formatter.parse_toml('colonies.toml')
        params['colony_data'] = formatter.to_simulation()
        # Injects script variables into parameters
        file_suffix = f'm{mother_memory}_s{sister_memory}'.replace('.', '')
        params['simulation_writer_settings']['confirm_overwrite'] = False
        params['simulation_writer_settings']['output_folder'] = str(DATA_SYMLINK_PATH / 'output')
        params['simulation_writer_settings']['parameters_file_name'] = f'params_{file_suffix}.json'
        params['simulation_writer_settings']['cell_csv_file_name'] = f'cell_output_{file_suffix}.csv'
        params['simulation_writer_settings']['colony_csv_file_name'] = f'colony_output_{file_suffix}.csv'
        for colony in params['colony_data']:
            colony['cells']['linked_sister_inheritance'] = True
            colony['cells']['mother_fitness_memory'] = mother_memory
            colony['cells']['sister_fitness_memory'] = sister_memory
        # Runs the simulation
        run_simulation_function(**params)


if __name__ == '__main__':
    main(
        mother_memories=SETTINGS['mother_memories'],
        sister_memories=SETTINGS['sister_memories'],
    )
