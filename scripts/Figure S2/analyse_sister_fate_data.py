from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns

sns.set()

BASE_PATH = Path('scripts', 'data')
INPUT_PATH = BASE_PATH / 'sister_fate_data.csv'


def main(input_path: Path) -> None:
    """Main function of this script."""
    data = pd.read_csv(input_path, index_col=0)
    data['memory'] = data['memory'].astype(str)
    data['generation'] = data['cell_name'].str.count('.')
    sns.violinplot(data=data, x='generation', y='hours_difference_to_fate', hue='memory', fill=True, alpha=0.7)
    plt.show()


if __name__ == '__main__':
    main(input_path=INPUT_PATH)
