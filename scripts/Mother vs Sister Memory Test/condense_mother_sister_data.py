from __future__ import annotations

from pathlib import Path

import pandas as pd

from utils import DATA_SYMLINK_PATH

SETTINGS = {
    'input_path': str(DATA_SYMLINK_PATH / 'output'),
    'output_path': str(DATA_SYMLINK_PATH / 'condensed_data.csv'),
}


def main(
        input_path: str,
        output_path: str,
) -> None:
    """Main function of this script."""
    dfs = []
    paths = [path for path in Path(input_path).iterdir() if is_cell_csv(path=path)]
    n_paths = len(paths)
    for i, path in enumerate(paths, 1):
        print(f'Adding data ({i:03}/{n_paths}) from file: {path}')
        df = load_data(path=path)
        dfs.append(df)
    data = pd.concat(dfs, ignore_index=True)
    data.to_csv(output_path)


def is_cell_csv(path: Path) -> bool:
    """Returns whether the given path points to a clovars cell csv file."""
    return path.stem.startswith('cell') and path.suffix == '.csv'


def load_data(path: Path) -> pd.DataFrame:
    """Loads the data from the given path and returns it as a DataFrame."""
    sister_memory = float(path.stem.split('_')[-1][1:]) / 10
    mother_memory = float(path.stem.split('_')[-2][1:]) / 10
    df = pd.read_csv(str(path))
    df['mother_memory'] = mother_memory
    df['sister_memory'] = sister_memory
    return df


if __name__ == '__main__':
    main(
        input_path=SETTINGS['input_path'],
        output_path=SETTINGS['output_path'],
    )
