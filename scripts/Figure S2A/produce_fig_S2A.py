from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
from scipy.stats import gamma, exponnorm

sns.set()

BASE_PATH = Path('..', 'data', 'experimental')
INPUT_PATHS = [
    BASE_PATH / 'control.csv',
    BASE_PATH / 'tmz.csv',
]

CURVE_PARAMETERS = {  # estimated from running "clovars fit" on "control.csv" and "tmz.csv"
    'control_division_parameters': {
        'type': gamma,
        'loc': 16.23,
        'scale': 2.84,
        'a': 3.32,
    },
    'tmz_division_parameters': {
        'type': exponnorm,
        'loc': 12.72,
        'scale': 8.50,
        'K': 2.87,
    },
    'tmz_death_parameters': {
        'type': exponnorm,
        'loc': 55.09,
        'scale': 23.75,
        'K': 2.93,
    },
}


def main(
        input_paths: list[Path],
        curve_parameters: dict[str, dict[str, float]],
) -> None:
    """Main function of this script."""
    dfs = []
    for path in input_paths:
        df = pd.melt(pd.read_csv(path, index_col=None), var_name='type', value_name='hours')
        df['treatment'] = path.stem
        dfs.append(df)
    data = pd.concat(dfs, ignore_index=True).dropna()

    for (treatment_name, curve_type), grouped_data in data.groupby(['treatment', 'type']):
        try:
            params = curve_parameters[f'{treatment_name}_{curve_type}_parameters']
        except KeyError:
            continue
        fig, ax = plt.subplots()
        fig.suptitle(f'{treatment_name}, {curve_type} curve (N={len(grouped_data)})')

        sns.kdeplot(data=grouped_data, ax=ax, x='hours', legend=False, color='0.4', fill=True)
        sns.histplot(data=grouped_data, ax=ax, x='hours', legend=False, color='0.4', stat='density', bins=10)

        xs = np.linspace(grouped_data['hours'].min() - 10, grouped_data['hours'].max() + 10, 10_000)
        ys = params.pop('type').pdf(xs, **params)
        sns.lineplot(ax=ax, x=xs, y=ys, color='#50993E' if curve_type == 'division' else '#993E50')
    plt.show()


if __name__ == '__main__':
    main(input_paths=INPUT_PATHS, curve_parameters=CURVE_PARAMETERS)
