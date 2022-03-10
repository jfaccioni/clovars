from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns

sns.set()

BASE_PATH = Path('scripts', 'data')
INPUT_PATHS = [
    BASE_PATH / 'low_memory_control' / 'cell_output.csv',
    BASE_PATH / 'high_memory_control' / 'cell_output.csv',
]


def main(input_paths: list[Path]) -> None:
    """Main function of this script."""
    dfs = []
    for path in input_paths:
        df = pd.read_csv(path, index_col=0)
        df['memory'], df['treatment'] = get_info_from_path_name(path=path)
        dfs.append(df)
    data = pd.concat(dfs, ignore_index=True)
    data['memory'] = data['memory'].apply({0.0: 'low', 0.9: 'high'}.get)
    data['colony_size'] = data.groupby(['memory', 'colony_name', 'simulation_days']).transform('count').iloc[:, 0]
    grouped_data = data.groupby(['memory', 'colony_name', 'simulation_days']).mean().reset_index()
    # FIG 1
    start_day, end_day = grouped_data['simulation_days'].min(), grouped_data['simulation_days'].max()
    fig1_data = grouped_data.loc[grouped_data['simulation_days'].isin([start_day, end_day])]
    fig1_data['moment'] = fig1_data.loc[:, 'simulation_days'].apply({start_day: 'start', end_day: 'end'}.get)
    sns.displot(
        data=fig1_data,
        kind='kde',
        x='division_threshold',
        col='moment',
        hue='memory',
        hue_order=['low', 'high'],
        palette=['#993e50', '#50993e'],
        alpha=0.5,
        linewidth=3,
    )
    # FIG 2
    fig, ax = plt.subplots()
    sns.lineplot(
        ax=ax,
        data=grouped_data,
        x='simulation_days',
        y='colony_size',
        hue='memory',
        hue_order=['low', 'high'],
        palette=['#993e50', '#50993e'],
        zorder=1,
        linewidth=0.5,
        linestyle='solid',
        estimator=None,
        units='colony_name',
        alpha=0.5,
    )
    sns.lineplot(
        ax=ax,
        data=grouped_data,
        x='simulation_days',
        y='colony_size',
        hue='memory',
        hue_order=['low', 'high'],
        palette=['#993e50', '#50993e'],
        zorder=2,
        linewidth=5,
        linestyle='dashed',
        ci=None,
        alpha=0.5
    )
    ax.set_yscale('log')
    plt.show()


def get_info_from_path_name(path: Path) -> tuple[float, str]:
    """Returns the memory and treatment based on the Path's words."""
    memory = 0.0 if 'low' in path.as_posix().lower() else 0.9
    treatment = 'TMZ' if 'tmz' in path.as_posix().lower() else 'Control'
    return memory, treatment


if __name__ == '__main__':
    main(input_paths=INPUT_PATHS)
