from __future__ import annotations

from collections import defaultdict
from pathlib import Path
from typing import Any

import pandas as pd

BASE_PATH = Path('scripts', 'data')
INPUT_PATHS = [
    BASE_PATH / 'low_memory_control' / 'cell_output.csv',
    BASE_PATH / 'low_memory_tmz' / 'cell_output.csv',
    BASE_PATH / 'high_memory_control' / 'cell_output.csv',
    BASE_PATH / 'high_memory_tmz' / 'cell_output.csv',
]
OUTPUT_PATH = BASE_PATH / 'sister_fate_data.csv'


def main(
        input_paths: list[Path],
        output_path: Path,
) -> None:
    """Main function of this script."""
    dfs = []
    for path in input_paths:
        memory, treatment = get_info_from_path_name(path=path)
        df = get_sister_deltas(data=pd.read_csv(path, index_col=0))
        df['memory'] = memory
        df['treatment'] = treatment
        dfs.append(df)
    data = pd.concat(dfs, ignore_index=True)
    data.to_csv(output_path)


def get_info_from_path_name(path: Path) -> tuple[float, str]:
    """Returns the memory and treatment based on the Path's words."""
    memory = 0.0 if 'low' in path.as_posix().lower() else 0.9
    treatment = 'TMZ' if 'tmz' in path.as_posix().lower() else 'Control'
    return memory, treatment


def get_sister_deltas(
        data: pd.DataFrame,
) -> pd.DataFrame:
    """Returns a DataFrame of the age difference between sisters."""
    ddict = defaultdict(list)
    for cell_name, cell_data in data.groupby('name'):
        if (sister_name := get_sister_name(cell_name=cell_name)) is None:  # cell_name does not end in "... .1"  # noqa
            continue
        sister_data = data.loc[data['name'] == sister_name]
        for prefix, name, df in (
                ['cell_', cell_name, cell_data],
                ['sister_', sister_name, sister_data],
        ):
            ddict[prefix + 'name'].append(name)
            ddict[prefix + 'fate'].append(get_last_value(df=df, column='fate_at_next_frame'))
            ddict[prefix + 'hours_at_fate'].append(get_last_value(df=df, column='seconds_since_birth') / 3600)
    df = pd.DataFrame(ddict)
    df['coinciding_fate'] = df['cell_fate'] == df['sister_fate']
    df['hours_difference_to_fate'] = abs(df['cell_hours_at_fate'] - df['sister_hours_at_fate'])
    return df


def get_sister_name(cell_name: str) -> str | None:
    """Returns the sister name from a cell's name (return None if the cell is a root cell or the sister cell itself)."""
    if '.' not in cell_name:  # cell_name is root
        return None
    if cell_name.endswith('2'):  # is sister cell itself
        return None
    return cell_name[:-1] + '2'


def get_last_value(
        df: pd.DataFrame,
        column: str,
) -> Any:
    """Returns the last value from the DataFrame's column."""
    return df.tail(1)[column].item()


if __name__ == '__main__':
    main(input_paths=INPUT_PATHS, output_path=OUTPUT_PATH)
