from __future__ import annotations

from typing import TYPE_CHECKING

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
from sklearn.decomposition import PCA
from sklearn.manifold import TSNE
from sklearn.preprocessing import StandardScaler

from clovars import ROOT_PATH

if TYPE_CHECKING:
    from pathlib import Path

sns.set()
sns.set_context('paper')

SETTINGS = {
    'input_folder': ROOT_PATH / 'scripts' / 'ML Tree Test' / 'results',
    'output_folder': ROOT_PATH / 'scripts' / 'ML Tree Test' / 'results',
    'palette': 'rocket',
    'pca_params': {
        'n_components': 2,
    },
    'tsne_params': {
        'init': 'pca',
        'learning_rate': 'auto',
    },
}


def main(
        input_folder: Path,
        output_folder: Path,
        palette: str | None = None,
        pca_params: dict | None = None,
        tsne_params: dict | None = None,
) -> None:
    """Main function of this script."""
    pca_params = pca_params or {}
    tsne_params = tsne_params or {}
    # Loads the data
    path = str(input_folder / 'tree_stats.csv')
    data = pd.read_csv(path, index_col=0)
    # Preprocesses the data
    labels, values = preprocess_data(data=data)
    # Plots the data
    fig, axes = plt.subplots(nrows=2, ncols=2, figsize=(16, 16))
    hue_labels = ['treatment', 'memory_label']
    for ax_row, hue in zip(axes, hue_labels):
        left_ax, right_ax = ax_row
        plot_pca(labels=labels, values=values, hue=hue, palette=palette, pca_params=pca_params, ax=left_ax)
        plot_tsne(labels=labels, values=values, hue=hue, palette=palette, tsne_params=tsne_params, ax=right_ax)
    plt.tight_layout()
    # Display the plots
    path = str(output_folder / 'results.png')
    plt.savefig(path)
    plt.show()


def preprocess_data(data: pd.DataFrame) -> tuple[pd.DataFrame, np.ndarray]:
    """Preprocesses the data for subsequent plotting."""
    # Splits the labels and the values
    labels = data.iloc[:, :2]
    values = data.iloc[:, 2:]
    # Fills NaNs and standardizes values
    values = values.fillna(0).values
    values = StandardScaler().fit_transform(values)
    return labels, values


def plot_pca(
        labels: pd.DataFrame,
        values: np.ndarray,
        hue: str,
        palette: str,
        pca_params: dict,
        ax: plt.Axes = None,
) -> plt.Axes:
    """Plots the data in a PCA plot. Returns the Axes instance where the PCA is plotted."""
    # Gets the Axes instance, if needed
    if ax is None:
        _, ax = plt.subplots()
    # Performs PCA
    pca = PCA(**pca_params)
    pca_values = pca.fit_transform(values)
    pca_results = pd.DataFrame(pca_values[:, :2], columns=['PCA1', 'PCA2'])
    # Merges PCA data with labels
    data = pd.concat([labels, pca_results], axis=1)
    # Plots the data
    hue_order = get_hue_order(hue=hue)
    sns.scatterplot(ax=ax, data=data, x='PCA1', y='PCA2', hue=hue, hue_order=hue_order, palette=palette)
    ax.set_title('PCA')
    return ax


def plot_tsne(
        labels: pd.DataFrame,
        values: np.ndarray,
        hue: str,
        palette: str,
        tsne_params: dict,
        ax: plt.Axes = None
) -> plt.Axes:
    """Plots the data in a t-SNE plot. Returns the Axes instance where the t-SNE is plotted."""
    # Gets the Axes instance, if needed
    if ax is None:
        _, ax = plt.subplots()
    # Performs t-SNE
    tsne = TSNE(**tsne_params)
    tsne_values = tsne.fit_transform(values)
    tsne_results = pd.DataFrame(tsne_values[:, :2], columns=['t-SNE1', 't-SNE2'])
    # Merges t-SNE data with labels
    data = pd.concat([labels, tsne_results], axis=1)
    # Plots the data
    hue_order = get_hue_order(hue=hue)
    sns.scatterplot(ax=ax, data=data, x='t-SNE1', y='t-SNE2', hue=hue, hue_order=hue_order, palette=palette)
    ax.set_title('t-SNE')
    return ax


def get_hue_order(hue: str) -> list[str]:
    """Returns the proper hue order, given the hue string."""
    if hue == 'treatment':
        return ['Control', 'ControlTMZ', 'TMZ']
    elif hue == 'memory_label':
        return ['No Memory', 'Almost No Memory', 'Half Memory', 'Almost Full Memory', 'Full Memory']
    else:
        raise ValueError(f'Invalid "hue" value: "{hue}". Valid values are: "treatment", "memory_label".')


if __name__ == '__main__':
    main(
        input_folder=SETTINGS['input_folder'],
        output_folder=SETTINGS['output_folder'],
        palette=SETTINGS['palette'],
        pca_params=SETTINGS['pca_params'],
        tsne_params=SETTINGS['tsne_params'],
    )
