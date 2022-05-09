from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Type

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
from sklearn.decomposition import PCA
from sklearn.manifold import TSNE
from sklearn.preprocessing import StandardScaler
from umap import UMAP

from clovars import ROOT_PATH

if TYPE_CHECKING:
    from pathlib import Path

sns.set()
sns.set_context('paper')

SETTINGS = {
    'input_folder': ROOT_PATH / 'scripts' / 'ML Tree Test' / 'results',
    'output_folder': ROOT_PATH / 'scripts' / 'ML Tree Test' / 'results',
    'save_figure': False,
    'palette': None,
    'pca_params': {
        'n_components': 2,
    },
    'tsne_params': {
        'init': 'pca',
        'learning_rate': 'auto',
    },
    'umap_params': {
    }
}


@dataclass
class Model:
    name: str
    reducer: Type[PCA] | Type[TSNE] | Type[UMAP]
    params: dict

    def create(self) -> PCA | TSNE | UMAP:
        """Returns and instance of the reducer inside the Model."""
        return self.reducer(**self.params)

    @property
    def xlabel(self) -> str:
        """Returns the label of the X dimension of the model."""
        return self.name + '_1'

    @property
    def ylabel(self) -> str:
        """Returns the label of the Y dimension of the model."""
        return self.name + '_2'

    @property
    def labels(self) -> list[str, str]:
        """Returns a list of the labels of the X and Y dimensions of the model."""
        return [self.xlabel, self.ylabel]


def main(
        input_folder: Path,
        output_folder: Path,
        save_figure: bool = False,
        palette: str | None = None,
        pca_params: dict | None = None,
        tsne_params: dict | None = None,
        umap_params: dict | None = None,
) -> None:
    """Main function of this script."""
    # Defines the models
    models = [
        Model('PCA', PCA, pca_params or {}),
        Model('t-SNE', TSNE, tsne_params or {}),
        Model('UMAP', UMAP, umap_params or {}),
    ]
    hue_labels = ['treatment', 'memory']
    # Loads the data
    path = str(input_folder / 'tree_stats.csv')
    data = pd.read_csv(path, index_col=0)
    # Preprocesses the data
    labels, values = preprocess_data(data=data)
    # Plots the data
    fig, axes = plt.subplots(nrows=len(hue_labels), ncols=len(models), figsize=(24, 16))
    for ax_row, hue in zip(axes, hue_labels):
        for ax, model in zip(ax_row, models):
            fit_data = fit_to_model(model=model, labels=labels, values=values)
            hue_order = get_hue_order(hue=hue)
            sns.scatterplot(
                ax=ax,
                data=fit_data,
                x=model.xlabel,
                y=model.ylabel,
                hue=hue,
                hue_order=hue_order,
                palette=palette,
            )
            ax.set_title(f'{model.name}: color by {hue}')
    plt.tight_layout()
    # Display the plots
    if save_figure is True:
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


def fit_to_model(
        model: Model,
        labels: pd.DataFrame,
        values: np.ndarray,
) -> pd.DataFrame:
    """Fits the data to the model plot and returns it."""
    model_values = model.create().fit_transform(values)
    model_results = pd.DataFrame(model_values[:, :2], columns=model.labels)
    return pd.concat([labels, model_results], axis=1)


def get_hue_order(hue: str) -> list[str]:
    """Returns the proper hue order, given the hue string."""
    if hue == 'treatment':
        return ['Control', 'ControlTMZ', 'TMZ']
    elif hue == 'memory':
        return ['No Memory', 'Almost No Memory', 'Half Memory', 'Almost Full Memory', 'Full Memory']
    else:
        raise ValueError(f'Invalid "hue" value: "{hue}". Valid values are: "treatment", "memory_label".')


if __name__ == '__main__':
    main(
        input_folder=SETTINGS['input_folder'],
        output_folder=SETTINGS['output_folder'],
        save_figure=SETTINGS['save_figure'],
        palette=SETTINGS['palette'],
        pca_params=SETTINGS['pca_params'],
        tsne_params=SETTINGS['tsne_params'],
    )
