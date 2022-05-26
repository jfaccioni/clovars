from __future__ import annotations

import shutil
from pathlib import Path

from clovars import ROOT_PATH

SETTINGS = {
    'ctor_output_folder': ROOT_PATH / 'data' / 'ctor_analysis' / '2022-05-26 Gaussian Curves',
}


def main(ctor_output_folder: Path) -> None:
    """Main function of this script."""
    # DATA FILES
    for prefix in ('cell', 'colony', 'params'):
        for suffix in ('.csv', '.json'):
            for data_file in ctor_output_folder.glob(fr"{prefix}*{suffix}"):
                *_, shift, colony_number, = data_file.stem.split("_")
                out_dir = ctor_output_folder / f'CTOR_{shift}' / 'data' / f'Colony_{int(colony_number):02d}'
                out_dir.mkdir(parents=True, exist_ok=True)
                out_file = f'{prefix}{data_file.suffix}'
                shutil.move(data_file, out_dir / out_file)
    # FIGURES
    ctor_figures_folder = ctor_output_folder / 'figures'
    # Treatment figures
    treatment_figures = list(ctor_figures_folder.glob(r"CTOR_treatments*.png"))
    for treatment_figure in treatment_figures:
        _, _, shift, _, _, _ = treatment_figure.stem.split("_")
        out_dir = ctor_output_folder / f'CTOR_{shift}' / 'figures'
        out_dir.mkdir(parents=True, exist_ok=True)
        out_file = f'Treatment.png'
        shutil.move(treatment_figure, out_dir / out_file)
    # Branch figures
    branch_figures = [figure for figure in ctor_figures_folder.glob(r"CTOR_*.png") if figure not in treatment_figures]
    for branch_figure in branch_figures:
        _, shift, colony_number, branch_name = branch_figure.stem.split("_")
        branch_number = branch_name.split('-')[-1]
        out_dir = ctor_output_folder / f'CTOR_{shift}' / 'figures' / f'Colony_{int(colony_number):02d}'
        out_dir.mkdir(parents=True, exist_ok=True)
        out_file = f'Branch_{int(branch_number):02d}.png'
        shutil.move(branch_figure, out_dir / out_file)
    # Remove figure folder, if empty
    try:
        ctor_figures_folder.rmdir()
    except OSError:
        print('Did not remove figures directory (not empty)')


if __name__ == '__main__':
    main(
        ctor_output_folder=SETTINGS['ctor_output_folder'],
    )
