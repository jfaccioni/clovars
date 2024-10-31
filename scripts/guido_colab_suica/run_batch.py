from __future__ import annotations

from pathlib import Path

from clovars import ROOT_PATH
from clovars.IO import RunParameterValidator, ColonyDataFormatter
from clovars.simulation import run_simulation_function

SETTINGS = {
    'run_path': ROOT_PATH / 'scripts' / 'guido_colab_suica' / 'run.toml',
    'colonies_path': ROOT_PATH / 'scripts' / 'guido_colab_suica' / 'colonies.toml',
    'base_remote_folder': ROOT_PATH / 'data' / 'guido_colab_suica',
    'md_memory': [0.0, 0.1, 0.2, 0.3, 1.0],
    'ss_memory': [0.0, 0.3, 0.6, 0.9, 1.0],
}


def main(
        run_path: str | Path,
        colonies_path: str | Path,
        base_remote_folder: Path,
        md_memory: list[float],
        ss_memory: list[float],
) -> None:
    """Main function of this script."""
    run_validator = RunParameterValidator()
    run_validator.parse_toml(toml_path=run_path)
    run_validator.validate()
    run_params = run_validator.to_simulation()

    colony_formatter = ColonyDataFormatter()
    colony_formatter.parse_toml(toml_path=colonies_path)
    colonies = colony_formatter.to_simulation()

    for md_memory_value, ss_memory_value in zip(md_memory, ss_memory):
        prefix = f'MD{md_memory_value:.2f}_SS{ss_memory_value:.2f}'
        print(f'Running with {md_memory_value=}, {ss_memory_value=}')
        for colony in colonies:
            colony['cells']['mother_fitness_memory'] = md_memory_value
            colony['cells']['sister_fitness_memory'] = ss_memory_value

        run_params['simulation_writer_settings']['output_folder'] = str(base_remote_folder / prefix)
        run_params['simulation_writer_settings']['parameters_file_name'] = f'{prefix}_params.json'
        run_params['simulation_writer_settings']['cell_csv_file_name'] = f'{prefix}_cell_output.csv'
        run_params['simulation_writer_settings']['colony_csv_file_name'] = f'{prefix}_colony_output.csv'

        run_simulation_function(colony_data=colonies, **run_params)


if __name__ == '__main__':
    main(**SETTINGS)
