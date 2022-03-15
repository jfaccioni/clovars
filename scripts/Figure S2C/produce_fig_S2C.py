import random
import sys
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
from matplotlib.lines import Line2D

from clovars.main import main as clovars_main

sns.set()

EXPERIMENTAL_PATH = Path('..', 'data', 'experimental', 'control.csv')
RANDOMNESS_SEED = 42


def main() -> None:
    """Main function of this script."""
    random.seed(RANDOMNESS_SEED)
    np.random.seed(RANDOMNESS_SEED)
    path = Path('output')
    # Simulation
    sys.argv = ['', 'run', 'Fig_S2C_run.toml', f'Fig_S2C_colonies.toml']
    clovars_main()
    simulation_df = process_simulation_data(pd.read_csv(path / 'cell_output.csv'))
    # Experimental
    experimental_data = pd.read_csv(EXPERIMENTAL_PATH)
    experimental_df = pd.concat(
        [process_experimental_data(value=value, repeat=i) for i, value in enumerate(experimental_data['division'])],
        ignore_index=True,
    )
    # Plots
    fig, ax = plt.subplots()
    for i, (data, color) in enumerate([
            (simulation_df, '#983e50'),
            (experimental_df, '#50983e'),
    ]):
        sns.lineplot(
            data=data,
            ax=ax,
            x='simulation_days',
            y='count',
            units='colony_name',
            estimator=None,
            alpha=0.2,
            linewidth=1,
            color=color,
        )
        if i == 1:  # data is experimental data, needs smoothing first
            data = get_mean_experimental_data(experimental_data=data)
        sns.lineplot(
            data=data,
            ax=ax,
            x='simulation_days',
            y='count',
            linestyle='dashed',
            linewidth=3,
            color=color,
        )
    ax.legend(handles=[
        Line2D([0], [0], label='Simulation runs ($n=100$)', linewidth=2, color='#983e50'),
        Line2D([0], [0], label='Experimental bootstraps ($n=100$)', linewidth=2, color='#50983e'),
    ])
    plt.show()
    remove_tree(path=Path('output'))


def remove_tree(path: Path) -> None:
    """Recursively deletes files and folders starting from path."""
    # Source: https://stackoverflow.com/a/57892171/11161432
    for child in path.iterdir():
        if child.is_file():
            child.unlink()
        else:
            remove_tree(child)
    path.rmdir()


def process_simulation_data(data: pd.DataFrame) -> pd.DataFrame:
    """Processes and returns the simulation data."""
    data = data.groupby(['simulation_days', 'colony_name']).count().iloc[:, 0].reset_index()
    data = data.rename(columns={'index': 'count'})
    return data


def process_experimental_data(
        value: float,
        repeat: int,
) -> pd.DataFrame:
    """Processes and returns the experimental data."""
    division_hours = []
    while sum(division_hours) <= (24 * 7):
        division_hours.append(value)
    return pd.DataFrame({
        'simulation_days': np.cumsum(division_hours) / 24,
        'count': [2 ** n for n, _ in enumerate(division_hours)],
        'colony_name': repeat,
    })


def get_mean_experimental_data(experimental_data: pd.DataFrame) -> pd.DataFrame:
    """Returns a dataframe of the experimental data mean interpolation."""
    # Source: https://stackoverflow.com/a/63250438/11161432
    xs = [[*group['simulation_days'].values] for _, group in experimental_data.groupby('colony_name')]
    ys = [[*group['count'].values] for _, group in experimental_data.groupby('colony_name')]
    all_xs = [xx for x in xs for xx in x]
    mean_x = np.linspace(0, max(all_xs), len(all_xs))
    mean_y = np.mean([np.interp(mean_x, xs[i], ys[i]) for i in range(len(xs))], axis=0)
    return pd.DataFrame({'simulation_days': mean_x, 'count': mean_y})


if __name__ == '__main__':
    main()
