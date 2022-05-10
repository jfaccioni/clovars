from __future__ import annotations

from typing import TYPE_CHECKING

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
from sklearn.preprocessing import StandardScaler

from clovars import ROOT_PATH

if TYPE_CHECKING:
    from pathlib import Path

sns.set()
sns.set_context('paper')

SETTINGS = {
    'input_folder': ROOT_PATH / 'scripts' / 'ML Tree Test' / 'results',
    'output_folder': ROOT_PATH / 'scripts' / 'ML Tree Test' / 'results',
    'save_figure': True,
    'palette': None,
    'hue': None,
}


def main(
        input_folder: Path,
        output_folder: Path,
        save_figure: bool = False,
        hue: str | None = None,
        palette: str | None = None,
) -> None:
    """Main function of this script."""
    # Loads the data
    path = str(input_folder / 'tree_stats.csv')
    data = pd.read_csv(path, index_col=0)
    # Plots the data
    processed_data = preprocess_data(data=data)
    # Displays the plot
    sns.pairplot(data=processed_data, hue=hue, palette=palette)
    if save_figure is True:
        suffix = "" if palette is None else f"_{palette}"
        path = str(output_folder / f'pair_plot{suffix}.png')
        plt.savefig(path)
    plt.show()


def preprocess_data(data: pd.DataFrame) -> pd.DataFrame:
    """Preprocesses the data for subsequent plotting."""
    # Splits the labels and the values
    labels = data.iloc[:, :2]
    values = data.iloc[:, 2:]
    # Fills NaNs and standardizes values
    values = values.fillna(0).values
    values = StandardScaler().fit_transform(values)
    return pd.concat([labels, pd.DataFrame(values, columns=data.columns[2:], index=data.index)])


if __name__ == '__main__':
    main(
        input_folder=SETTINGS['input_folder'],
        output_folder=SETTINGS['output_folder'],
        save_figure=SETTINGS['save_figure'],
        palette=SETTINGS['palette'],
        hue=SETTINGS['hue'],
    )
