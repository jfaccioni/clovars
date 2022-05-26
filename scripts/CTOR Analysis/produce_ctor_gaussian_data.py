from __future__ import annotations

from pathlib import Path

from clovars import ROOT_PATH
from clovars.IO import RunParameterValidator, ColonyDataFormatter
from clovars.simulation import run_simulation_function

SETTINGS = {
    'settings_path': Path('./run.toml'),
    'colonies_path': Path('./colonies.toml'),
    'ctor_output_folder': ROOT_PATH / 'data' / 'ctor_analysis' / '2022-05-26 Gaussian Curves',
    'curve_shifts': [-9, -6, -3, 0, 3, 6, 9],
    'repeats': 25,
}


def main(
        settings_path: Path,
        colonies_path: Path,
        ctor_output_folder: Path,
        curve_shifts: list[int],
        repeats: int,
) -> None:
    """Main function of this script."""
    # RUN SETTINGS
    validator = RunParameterValidator()
    validator.parse_toml(settings_path)  # noqa
    validator.validate()
    params = validator.to_simulation()
    # COLONIES SETTINGS
    formatter = ColonyDataFormatter()
    formatter.parse_toml(colonies_path)  # noqa
    colony_data = formatter.to_simulation()
    params['colony_data'] = colony_data
    # KEEP ORIGINAL DIVISION/DEATH CURVES
    assert len(params['colony_data']) == 1, 'Do not execute multiple colonies in this script!'
    treatment_data = params['colony_data'][0]['treatment_data']  # only one colony
    original_division_curves = {
        frame: treatment['division_curve'].copy()
        for frame, treatment in treatment_data.items()
    }
    original_death_curves = {
        frame: treatment['death_curve'].copy()
        for frame, treatment in treatment_data.items()
    }
    # USE CTOR OUTPUT FOLDER
    params['simulation_writer_settings']['output_folder'] = str(ctor_output_folder)
    for curve_shift in curve_shifts:
        # INJECT CTOR SETTINGS INTO PARAMS DICT
        for curve_dict, curve_label in (
                (original_division_curves, 'division_curve'),
                (original_death_curves, 'death_curve'),
        ):
            for k in curve_dict.keys():
                new_curve_mean = curve_dict[k]['mean'] + curve_shift
                params['colony_data'][0]['treatment_data'][k][curve_label]['mean'] = new_curve_mean
        for repeat in range(1, repeats+1):
            # INJECT OUTPUT SETTINGS INTO PARAMS DICT
            suffix = f"_+{curve_shift}h_{repeat}" if curve_shift > 0 else f"_{curve_shift}h_{repeat}"
            params['simulation_writer_settings']['parameters_file_name'] = f'params{suffix}.json'
            params['simulation_writer_settings']['cell_csv_file_name'] = f'cell_output{suffix}.csv'
            params['simulation_writer_settings']['colony_csv_file_name'] = f'colony_output{suffix}.csv'
            # RUN
            run_simulation_function(**params)


if __name__ == '__main__':
    main(
        settings_path=SETTINGS['settings_path'],
        colonies_path=SETTINGS['colonies_path'],
        curve_shifts=SETTINGS['curve_shifts'],
        ctor_output_folder=SETTINGS['ctor_output_folder'],
        repeats=SETTINGS['repeats'],
    )
