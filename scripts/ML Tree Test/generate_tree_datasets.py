from __future__ import annotations

import random
from typing import TYPE_CHECKING

import numpy as np

from clovars import ROOT_PATH
from clovars.IO.parameter_validator import ColonyDataFormatter, RunParameterValidator
from clovars.simulation import run_simulation_function

if TYPE_CHECKING:
    from pathlib import Path

SETTINGS = {
    'input_folder': ROOT_PATH / 'scripts' / 'ML Tree Test' / 'input',
    'output_folder': ROOT_PATH / 'output' / 'ML Tree Test',
    'python_random_seed': 42,
    'numpy_random_seed': 42,
}


def main(
        input_folder: Path,
        output_folder: Path,
        python_random_seed: int | None,
        numpy_random_seed: int | None,
) -> None:
    """Main function of this script."""
    # Sets the random seeds for reproducibility
    random.seed(python_random_seed)
    np.random.seed(numpy_random_seed)

    # Creates the output directory
    output_folder.mkdir(parents=True, exist_ok=True)

    # Iterates over input folders and run each as a separate simulation
    folders = list(input_folder.iterdir())
    n_folders = len(folders)
    for i, folder in enumerate(folders, 1):
        print(f'Running simulation {i}/{n_folders}, current folder: {folder.stem}')
        # Validates and gets the run settings
        validator = RunParameterValidator()
        validator.parse_toml(str(folder / 'run.toml'))
        validator.validate()
        params = validator.to_simulation()
        # Formats and gets the colony data
        formatter = ColonyDataFormatter()
        formatter.parse_toml(str(folder / 'colonies.toml'))
        params['colony_data'] = formatter.to_simulation()
        # Injects script variables into parameters
        params['simulation_writer_settings']['output_folder'] = str(output_folder / folder.stem)
        # Runs the simulation
        run_simulation_function(**params)


if __name__ == '__main__':
    main(
        input_folder=SETTINGS['input_folder'],
        output_folder=SETTINGS['output_folder'],
        python_random_seed=SETTINGS['python_random_seed'],
        numpy_random_seed=SETTINGS['numpy_random_seed'],
    )
