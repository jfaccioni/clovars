from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
from matplotlib.animation import FuncAnimation

sns.set(font_scale=2)

SCRIPTS_FOLDER_PATH = Path('..')
DATA_PATH = SCRIPTS_FOLDER_PATH / 'data' / 'memory_demo'
INPUT_PATHS = [
    DATA_PATH / 'low_memory_control' / 'cell_output.csv',
    DATA_PATH / 'high_memory_control' / 'cell_output.csv',
]
OUTPUT_PATH = SCRIPTS_FOLDER_PATH / 'Video S2' / 'Supplementary Video S2.mp4'


def main(
        input_paths: list[Path],
        output_path: Path,
) -> None:
    """Main function of this script."""
    dfs = []
    for path in input_paths:
        df = pd.read_csv(path, index_col=0)
        df['memory'], df['treatment'] = get_info_from_path_name(path=path)
        dfs.append(df)
    data = pd.concat(dfs, ignore_index=True)
    data['$f_m$'] = data['memory'].astype(str)
    fig, (top_ax, bottom_ax) = plt.subplots(figsize=(16, 16), nrows=2)
    grouped_data = (
        data
        .groupby(['$f_m$', 'colony_name', 'simulation_hours'])['signal_value']
        .mean()
        .reset_index()
        .rename(columns={'signal_value': 'colony_signal_mean'})
    )
    grouped_data['colony_signal_variance'] = (
        data
        .groupby(['$f_m$', 'colony_name', 'simulation_hours'])['signal_value']
        .var()
        .reset_index(drop=True)
    )
    grouped_data['colony_size'] = (
        data
        .groupby(['$f_m$', 'colony_name', 'simulation_hours'])['signal_value']
        .count()
        .reset_index(drop=True)
    )
    grouped_data['colony_size_jitter'] = grouped_data['colony_size'] + grouped_data['$f_m$'].apply(
        lambda value: np.random.normal(loc={'0.0': -0.2, '0.9': +0.2}.get(value), scale=0.05)
    )
    max_hours = grouped_data["simulation_hours"].max()

    def update(hour: float) -> None:
        """Updates the plot."""
        print('\b' * 100, end='')
        print( f'Video is: {round(100 * (hour/max_hours), 1)}% done...', end='')
        hour_data = grouped_data.loc[grouped_data['simulation_hours'] == hour]
        for ax, label in (
                (top_ax, 'mean'),
                (bottom_ax, 'variance')
        ):
            ax.clear()
            sns.scatterplot(
                ax=ax,
                data=hour_data,
                x='colony_size_jitter',
                y=f'colony_signal_{label}',
                hue='$f_m$',
                palette=['#029e73', '#de8f05'],
            )
            ax.set_title(f'Distribution of signal {label} in colonies (N=100 per $f_m$)')
            ax.set_xlabel('Colony size')
            ax.set_xticks([tick for tick in ax.get_xticks() if tick.is_integer()])
            if ax.get_xlim()[-1] < 5:
                ax.set_xlim(right=5)
            ax.set_ylabel(f'Signal {label} in colonies')
        top_ax.set_ylim(-1, 1)
        top_ax.set_yticks([-1, 0, 1])
        bottom_ax.set_ylim(0, 0.7)
        if bottom_ax.get_yticks()[-1] == 0:
            bottom_ax.set_yticks([])
        fig.suptitle(f'Simulation time: {round(hour, 1)} hours')
        fig.tight_layout()

    ani = FuncAnimation(fig, update, frames=grouped_data['simulation_hours'].unique())
    ani.save(str(output_path))


def get_info_from_path_name(path: Path) -> tuple[float, str]:
    """Returns the memory and treatment based on the Path's words."""
    memory = 0.0 if 'low' in path.as_posix().lower() else 0.9
    treatment = 'TMZ' if 'tmz' in path.as_posix().lower() else 'Control'
    return memory, treatment


if __name__ == '__main__':
    main(input_paths=INPUT_PATHS, output_path=OUTPUT_PATH)
