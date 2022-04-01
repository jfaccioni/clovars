from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
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
OUTPUT_PATH = SCRIPTS_FOLDER_PATH / 'Video S1' / 'Supplementary Video S1.mp4'


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
        .groupby(['$f_m$', 'colony_name', 'simulation_hours'])['division_threshold']
        .mean()
        .reset_index()
    )
    grouped_data['colony_size'] = (
        data
        .groupby(['$f_m$', 'colony_name', 'simulation_hours'])['division_threshold']
        .count()
        .reset_index(drop=True)
    )
    max_hours = grouped_data["simulation_hours"].max()

    def update(hour: float) -> None:
        """Updates the plot."""
        print('\b' * 100, end='')
        print( f'Video is: {round(100 * (hour/max_hours), 1)}% done...', end='')
        hour_data = grouped_data.loc[grouped_data['simulation_hours'] == hour]
        palette = ['#029e73', '#de8f05']
        # TOP AX
        top_ax.clear()
        sns.violinplot(ax=top_ax, data=hour_data, x='colony_size', y='$f_m$', palette=palette)
        sns.stripplot(
            ax=top_ax,
            data=hour_data,
            x='colony_size',
            y='$f_m$',
            color='0.8',
            edgecolor='0.3',
            linewidth=1,
            size=5,
        )
        top_ax.set_title('Distribution of colony sizes (N=100 per $f_m$)')
        top_ax.set_xlabel('Colony size')
        top_ax.set_xticks([tick for tick in top_ax.get_xticks() if tick.is_integer()])
        # BOTTOM AX
        bottom_ax.clear()
        sns.kdeplot(
            ax=bottom_ax,
            data=hour_data,
            x='division_threshold',
            hue='$f_m$',
            palette=palette,
            linewidth=3,
            alpha=0.7,
        )
        sns.rugplot(ax=bottom_ax, data=hour_data, x='division_threshold', hue='$f_m$', palette=palette)
        bottom_ax.set_title('Distribution of mean colony $t_{div}$ (N=100 per $f_m$)')
        bottom_ax.set_xlabel('Mean colony $t_{div}$')
        bottom_ax.set_xlim(-0.1, 1.1)
        bottom_ax.set_ylim(0, 3)
        # FIG
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
