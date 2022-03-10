from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
from matplotlib.animation import FuncAnimation

sns.set(font_scale=2)

BASE_PATH = Path('scripts')
INPUT_PATHS = [
    BASE_PATH / 'data' / 'low_memory_control' / 'cell_output.csv',
    BASE_PATH / 'data' / 'high_memory_control' / 'cell_output.csv',
]
OUTPUT_PATH = BASE_PATH / 'Video S1' / 'Supplementary Video S1.mp4'


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
    data['memory'] = data['memory'].astype(str)
    fig, (top_ax, bottom_ax) = plt.subplots(figsize=(16, 16), nrows=2)
    grouped_data = (
        data
        .groupby(['memory', 'colony_name', 'simulation_hours'])['division_threshold']
        .mean()
        .reset_index()
    )
    grouped_data['colony_size'] = (
        data
        .groupby(['memory', 'colony_name', 'simulation_hours'])['division_threshold']
        .count()
        .reset_index(drop=True)
    )
    max_hours = grouped_data["simulation_hours"].max()

    def update(hour: float) -> None:
        """Updates the plot."""
        print('\b' * 100, end='')
        print( f'Video is: {round(100 * (hour/max_hours), 1)}% done...', end='')
        hour_data = grouped_data.loc[grouped_data['simulation_hours'] == hour]
        palette = ['#82cb70', '#cb7082']
        top_ax.clear()
        top_ax.set_title(f'Simulation time: {round(hour, 1)} hours')
        top_ax.set_xlim(-0.1, 1.1)
        top_ax.set_ylim(0, 3)
        sns.kdeplot(
            ax=top_ax,
            data=hour_data,
            x='division_threshold',
            hue='memory',
            palette=palette,
            linewidth=3,
            alpha=0.7,
        )
        sns.rugplot(ax=top_ax, data=hour_data, x='division_threshold', hue='memory', palette=palette)
        bottom_ax.clear()
        bottom_ax.set_title('Colony size distribution')
        sns.violinplot(ax=bottom_ax, data=hour_data, x='memory', y='colony_size', palette=palette)
        sns.stripplot(
            ax=bottom_ax,
            data=hour_data,
            x='memory',
            y='colony_size',
            color='0.8',
            edgecolor='0.3',
            linewidth=1,
            size=5,
        )
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
