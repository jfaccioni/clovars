from __future__ import annotations

from pathlib import Path

from clovars import ROOT_PATH
from clovars.IO import ViewParameterValidator
from clovars.simulation import view_simulation_function

SETTINGS = {
    'settings_path': Path('./view.toml'),
    'ctor_output_folder': ROOT_PATH / 'data' / 'ctor_analysis' / '2022-05-26 Gaussian Curves',
}


def main(
        settings_path: Path,
        ctor_output_folder: Path,
) -> None:
    """Main function of this script."""
    # RUN SETTINGS
    validator = ViewParameterValidator()
    validator.parse_toml(settings_path)  # noqa
    validator.validate()
    params = validator.to_simulation()
    params['output_folder'] = str(ctor_output_folder / 'figures')
    params['simulation_loader_settings']['simulation_input_folder'] = str(ctor_output_folder)
    for cell_csv_file in ctor_output_folder.glob(r"cell*.csv"):
        suffix = "_" + "_".join(cell_csv_file.stem.split('_')[-2:])
        params['view_settings']['file_name_2D'] = f"CTOR{suffix}"
        params['view_settings']['file_name_treatments'] = f"CTOR_treatments{suffix}"
        # INJECT LOADER SETTINGS INTO PARAMS DICT
        params['simulation_loader_settings']['parameters_file_name'] = f'params{suffix}.json'
        params['simulation_loader_settings']['cell_csv_file_name'] = f'cell_output{suffix}.csv'
        params['simulation_loader_settings']['colony_csv_file_name'] = f'colony_output{suffix}.csv'
        # VIEW
        view_simulation_function(**params)


if __name__ == '__main__':
    main(
        settings_path=SETTINGS['settings_path'],
        ctor_output_folder=SETTINGS['ctor_output_folder'],
    )
