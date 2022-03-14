from pathlib import Path
import random
import sys

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

from clovars.main import main as clovars_main

sns.set()
RANDOMNESS_SEED = 42


def main():
    """Main function of this script."""
    random.seed(RANDOMNESS_SEED)
    np.random.seed(RANDOMNESS_SEED)
    dfs = []
    for treatment_name in ['control', 'tmz']:
        sys.argv = ['', 'run', f'Fig_2D_run_{treatment_name}.toml', f'Fig_2D_colonies_{treatment_name}.toml']
        clovars_main()
        path = Path('output')
        data = pd.read_csv(path / f'colony_output_{treatment_name}.csv', index_col=None)
        data['run_name'] = treatment_name
        dfs.append(data)
        remove_tree(path=path)
    df = pd.concat(dfs, ignore_index=True)
    fig, ax = plt.subplots()
    palette = ['#50993e', '#993e50']
    sns.lineplot(
        data=df,
        ax=ax,
        x='simulation_days',
        y='size',
        hue='run_name',
        palette=palette,
        linestyle='dashed',
        linewidth=5,
        zorder=2,
    )
    sns.lineplot(
        data=df,
        ax=ax,
        x='simulation_days',
        y='size',
        hue='run_name',
        palette=palette,
        linestyle='solid',
        linewidth=2,
        zorder=1,
        alpha=0.7,
        units='name',
        estimator=None,
        legend=False,
    )
    plt.show()


def remove_tree(path: Path):
    """Recursively deletes files and folders starting from path."""
    # Source: https://stackoverflow.com/a/57892171/11161432
    for child in path.iterdir():
        if child.is_file():
            child.unlink()
        else:
            remove_tree(child)
    path.rmdir()


if __name__ == '__main__':
    main()
