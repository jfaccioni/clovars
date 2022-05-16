from __future__ import annotations

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns

from utils import DATA_SYMLINK_PATH

sns.set()

SETTINGS = {
    'input_path': str(DATA_SYMLINK_PATH / 'condensed_data.csv'),
    'cache_path': str(DATA_SYMLINK_PATH / 'cliche_cached_data.csv'),
    'log2_colony_size': True,
    'split_lines': True,
    'refresh_cache': False,
}


def main(
        input_path: str,
        cache_path: str,
        log2_colony_size: bool,
        split_lines: bool,
        refresh_cache: bool,
) -> None:
    """Main function of this script."""
    # Loads data
    if refresh_cache is True:  # Load the data and cache it
        data = load_and_cache_data(input_path=input_path, cache_path=cache_path)
    else:
        try:
            data = load_cache(cache_path=cache_path)
        except FileNotFoundError:  # Cache does not exist yet - load the data and cache it
            data = load_and_cache_data(input_path=input_path, cache_path=cache_path)
    # Calculates colony size and signal mean of each colony
    data = (
        data
        .groupby(['memory_label', 'simulation_hours', 'colony_name'])
        .agg(
            mother_memory=('mother_memory', 'first'),  # keep this column
            sister_memory=('sister_memory', 'first'),  # keep this column
            colony_size=('Unnamed: 0', 'count'),
            mean_colony_signal=('signal_value', 'mean'),
        )
        .reset_index()
    )
    # Calculates colony size mean and signal CV across colonies
    data = (
        data
        .groupby(['memory_label', 'simulation_hours'])
        .agg(
            mother_memory=('mother_memory', 'first'),  # keep this column
            sister_memory=('sister_memory', 'first'),  # keep this column
            mean_colony_size=('colony_size', 'mean'),
            log2_mean_colony_size=('colony_size', lambda group: np.log2(group.mean())),
            CV_mean_colony_signal=('mean_colony_signal', lambda group: group.var() / group.mean()),
        )
        .reset_index()
    )
    # Plots data
    if split_lines:
        sns.relplot(
            data=data,
            kind='line',
            x='mean_colony_size' if not log2_colony_size else 'log2_mean_colony_size',
            y='CV_mean_colony_signal',
            row='mother_memory',
            col='sister_memory',
        )
        plt.savefig('plot_split.png')
    else:
        sns.lineplot(
            data=data,
            x='mean_colony_size' if not log2_colony_size else 'log2_mean_colony_size',
            y='CV_mean_colony_signal',
            hue='memory_label',
        )
        plt.savefig('plot_merge.png')
    plt.show()


def load_and_cache_data(
        input_path: str,
        cache_path: str,
) -> pd.DataFrame:
    """Loads the data and caches it."""
    data = load_and_preprocess_data(input_path)
    write_cache(data_to_cache=data, path=cache_path)
    return data


def load_and_preprocess_data(path: str) -> pd.DataFrame:
    """Loads the data and performs the necessary preprocessing steps."""
    data = pd.read_csv(path)
    return preprocess_data(data=data)


def write_cache(
        data_to_cache: pd.DataFrame,
        path: str,
) -> None:
    """Writes the preprocessed data to a cache."""
    data_to_cache.to_csv(path, index=False)


def preprocess_data(data: pd.DataFrame) -> pd.DataFrame:
    """Performs the necessary preprocessing steps with the data."""
    data = filter_multiple_of(data=data, column_label='simulation_hours', multiple=24.0)
    data['memory_label'] = concatenate_series(left=data['mother_memory'], right=data['sister_memory'], sep=':')
    data['signal_value'] = scale_series(series=data['signal_value'], new_min=40, new_max=400)
    return data


def load_cache(cache_path: str) -> pd.DataFrame:
    """Loads the preprocessed data from a cache."""
    return pd.read_csv(cache_path, index_col=None)


def filter_multiple_of(
        data: pd.DataFrame,
        column_label: str,
        multiple: float,
) -> pd.DataFrame:
    """Filters the input data's column for rows that are multiples of the given value."""
    return data.loc[data[column_label] % multiple == 0.0]


def concatenate_series(
        left: pd.Series,
        right: pd.Series,
        sep: str,
) -> pd.DataFrame:
    """Concatenates two pandas Series as strings, including a separator between them, and returns the result."""
    return left.astype(str) + sep + right.astype(str)


def scale_series(
        series: pd.Series,
        new_min: float,
        new_max: float,
) -> pd.DataFrame:
    """Scales a pandas Series between new min and new_max and returns it."""
    # Source: https://androidkt.com/how-to-scale-data-to-range-using-minmax-normalization/
    above = (series - series.min()) * (new_max - new_min)
    below = series.max() - series.min()
    return new_min + (above/below)


if __name__ == '__main__':
    main(
        input_path=SETTINGS['input_path'],
        cache_path=SETTINGS['cache_path'],
        log2_colony_size=SETTINGS['log2_colony_size'],
        split_lines=SETTINGS['split_lines'],
        refresh_cache=SETTINGS['refresh_cache'],
    )
