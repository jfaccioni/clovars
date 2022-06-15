from __future__ import annotations

from collections import defaultdict
from typing import TYPE_CHECKING

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns

from clovars import ROOT_PATH

if TYPE_CHECKING:
    from pathlib import Path

sns.set()

SETTINGS = {
    'input_folder': ROOT_PATH / 'data' / 'esicancer_output' / 'trees',
}


def main(input_folder: Path) -> None:
    """Main function of this script."""
    runs = defaultdict(dict)
    for csv_file_path in input_folder.glob("*.csv"):
        fitness_impact, _, result_type = csv_file_path.stem.split('_')
        runs[fitness_impact][result_type] = csv_file_path
    fig, axes = plt.subplots(figsize=(12, 24), ncols=len(runs), sharey='all')
    for (run_label, run_data), ax in zip(runs.items(), axes):
        colony_data = (
            pd
            .read_csv(run_data['ancestralResults'], sep=';', index_col=None)
            .iloc[:, :-1]
            .drop(columns='Population')
            .melt(id_vars='Generation', var_name='Colony ID', value_name='Colony Size')
        )
        sns.lineplot(
            ax=ax,
            data=colony_data,
            x='Generation',
            y='Colony Size',
            units='Colony ID',
            estimator=None,
            legend=None,
        )
        ax.set_title(run_label)
    plt.show()


if __name__ == '__main__':
    main(**SETTINGS)
