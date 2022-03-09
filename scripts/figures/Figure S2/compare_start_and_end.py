from __future__ import annotations

from collections import defaultdict
from pathlib import Path
from typing import Any

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns

sns.set()

pd.set_option('display.max_rows', None)
pd.set_option('display.max_columns', None)
pd.set_option('display.width', None)
pd.set_option('display.max_colwidth', None)

BASE_PATH = Path('scripts', 'figures', 'Figure S2', 'data')
INPUT_PATHS = [
    BASE_PATH / 'low_memory_control' / 'cell_output.csv',
    BASE_PATH / 'low_memory_tmz' / 'cell_output.csv',
    BASE_PATH / 'high_memory_control' / 'cell_output.csv',
    BASE_PATH / 'high_memory_tmz' / 'cell_output.csv',
]


def main(input_paths: list[Path]) -> None:
    """Main function of this script."""
    dfs = []
    for path in input_paths:
        df = pd.read_csv(path, index_col=0)
        df['memory'], df['treatment'] = get_info_from_path_name(path=path)
        dfs.append(df)
    data = pd.concat(dfs, ignore_index=True)
    grouped_data = data.groupby(['memory', 'treatment', 'colony_name', 'simulation_seconds']).mean().reset_index()
    grouped_data = pd.concat([
        grouped_data.loc[grouped_data['simulation_seconds'] == 0],
        grouped_data.loc[grouped_data['simulation_seconds'] == grouped_data['simulation_seconds'].max()],
    ], ignore_index=True)
    grouped_data['simulation_moment'] = grouped_data['simulation_seconds'].apply(lambda s: 'start' if s == 0 else 'end')
    grouped_data['memory'] = grouped_data['memory'].astype(str) + ' memory '
    grouped_data['category'] = grouped_data['memory'] + grouped_data['simulation_moment']
    g = sns.displot(
        data=grouped_data,
        kind='kde',
        x='division_threshold',
        hue='category',
        hue_order=['0.0 memory start', '0.0 memory end', '0.9 memory start', '0.9 memory end'],
        row='treatment',
        palette=['#993e50', '#50993e', '#cb7082', '#82cb70'],
        alpha=0.5,
        fill=True,
        rug=True,
    )
    g.figure.tight_layout()
    plt.show()


def get_info_from_path_name(path: Path) -> tuple[float, str]:
    """Returns the memory and treatment based on the Path's words."""
    memory = 0.0 if 'low' in path.as_posix().lower() else 0.9
    treatment = 'TMZ' if 'tmz' in path.as_posix().lower() else 'Control'
    return memory, treatment


if __name__ == '__main__':
    main(input_paths=INPUT_PATHS)
