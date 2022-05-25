from __future__ import annotations

from typing import TYPE_CHECKING

import matplotlib.pyplot as plt
import pandas as pd
import scipy.stats
import seaborn as sns

from utils import DATA_SYMLINK_PATH, SCRIPTS_PATH

if TYPE_CHECKING:
    from pathlib import Path

sns.set()

SETTINGS = {
    'input_path': str(DATA_SYMLINK_PATH / 'condensed_data.csv'),
    'cache_path': str(DATA_SYMLINK_PATH / 'correlations_cached_data.csv'),
    'output_path': SCRIPTS_PATH / 'results',
    'refresh_cache': False,
}


def main(
        input_path: str,
        cache_path: str,
        output_path: Path,
        refresh_cache: bool,
) -> None:
    """Main function of this script."""
    output_path.mkdir(parents=True, exist_ok=True)
    # Loads data
    if refresh_cache is True:  # Load the data and cache it
        data = load_and_cache_data(input_path=input_path, cache_path=cache_path)
    else:
        try:
            data = load_cache(cache_path=cache_path)
        except FileNotFoundError:  # Cache does not exist yet - load the data and cache it
            data = load_and_cache_data(input_path=input_path, cache_path=cache_path)
    # Plot data
    for memory_label, memory_group in data.groupby('memory_label'):
        mother_memory, sister_memory = str(memory_label).split(":")
        output_file_name = str(
            output_path /
            f'correlations_md{mother_memory.replace(".", "_")}:sis{sister_memory.replace(".", "_")}.png'
        )
        dfs = [calculate_division_times(data=colony_group) for _, colony_group in memory_group.groupby('colony_name')]
        correlation_data = pd.concat(dfs, ignore_index=True)
        g = sns.relplot(
            data=correlation_data,
            kind='scatter',
            x='value01',
            y='value02',
            col='pair',
            color='black',
            alpha=0.5,
            facet_kws={'sharey': False}
        )
        for row in g.axes:
            mother_sister01_ax, mother_sister02_ax, sister01_sister02_ax = row
            # LEFT AX (Mother vs. Sister01)
            mother_sister01_ax.set_xlabel('Mother time to mitosis (h)')
            mother_sister01_ax.set_ylabel('Sister01 time to mitosis (h)')
            add_linear_regression(
                ax=mother_sister01_ax,
                correlation_data=correlation_data,
                pair_label='Mother-Sister01',
            )
            # MIDDLE AX (Mother vs. Sister02)
            mother_sister02_ax.set_xlabel('Mother time to mitosis (h)')
            mother_sister02_ax.set_ylabel('Sister02 time to mitosis (h)')
            add_linear_regression(
                ax=mother_sister02_ax,
                correlation_data=correlation_data,
                pair_label='Mother-Sister02',
            )
            # BOTTOM AX (Sister01 vs. Sister02)
            sister01_sister02_ax.set_xlabel('Sister01 time to mitosis (h)')
            sister01_sister02_ax.set_ylabel('Sister02 time to mitosis (h)')
            add_linear_regression(
                ax=sister01_sister02_ax,
                correlation_data=correlation_data,
                pair_label='Sister01-Sister02',
            )
            for ax in row:
                ax.set_xlim(0, 100)
                ax.set_ylim(0, 100)
        g.figure.suptitle(f'Mother-Daughter Memory: {mother_memory}\nSister-Sister Memory: {sister_memory}')
        plt.tight_layout()
        print(f"Writing figure: {output_file_name}")
        plt.savefig(output_file_name)
        plt.close()


def calculate_division_times(
        data: pd.DataFrame,
) -> pd.DataFrame | None:
    """Populates the division_times_dict with the division times of daughter, mother and sister cells."""
    dfs = []
    last_frame = data['simulation_frames'].max()
    for mother_name in data['name'].unique():
        child_cells = data.loc[
            (data['name'].isin([mother_name + '.1', mother_name + '.2'])) &  # Find Daughters by name
            (data['simulation_frames'] < last_frame)  # Skip end leaves
        ]
        if len(child_cells) > 1:  # Only analyse if two child cells with division time were found
            mother_value = data.loc[data['name'] == mother_name].iloc[0, :].seconds_since_birth / (60 * 60)
            sister_01_value = child_cells.iloc[0, :].seconds_since_birth / (60 * 60)
            sister_02_value = child_cells.iloc[1, :].seconds_since_birth / (60 * 60)
            df = pd.DataFrame({
                'value01': [mother_value, mother_value, sister_01_value],
                'value02': [sister_01_value, sister_02_value, sister_02_value],
                'pair': ['Mother-Sister01', 'Mother-Sister02', 'Sister01-Sister02'],
            })
            dfs.append(df)
    if dfs:
        return pd.concat(dfs, ignore_index=True)
    return None


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
    data['memory_label'] = concatenate_series(left=data['mother_memory'], right=data['sister_memory'], sep=':')
    data = filter_last(data=data, group_columns=['memory_label', 'name'], sort_columns=['simulation_seconds'])
    return data


def load_cache(cache_path: str) -> pd.DataFrame:
    """Loads the preprocessed data from a cache."""
    return pd.read_csv(cache_path, index_col=None)


def filter_last(
        data: pd.DataFrame,
        group_columns: list[str],
        sort_columns: list[str],
) -> pd.DataFrame:
    """Returns the last row after sorting the values by sort_columns and grouping by group_columns."""
    return data.sort_values(by=sort_columns, ascending=True).groupby(group_columns).last().reset_index()


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


def add_linear_regression(
        ax: plt.Axes,
        correlation_data: pd.DataFrame,
        pair_label: str,
) -> None:
    """Adds a linear regression to the given Axes and data."""
    data = correlation_data.loc[correlation_data['pair'] == pair_label]
    linear_regression = scipy.stats.linregress(data['value01'], data['value02'])
    slope, intercept, r = linear_regression.slope, linear_regression.intercept, linear_regression.rvalue
    spearman, p_value = scipy.stats.spearmanr(data['value01'], data['value02'])
    x = data['value01'].sort_values()
    ax.plot(x, intercept + (slope * x), color='#e24320', linestyle='--', linewidth=3)
    sign_text = "+" if slope >= 0 else "-"
    slope_text = f"{slope:.2f}" if slope >= 0 else f"{slope:.2f}"[1:]
    text = (
        f'$y = {intercept:.2f} {sign_text} {slope_text}x$\n'
        f'$r :{r:.2f}$, $r^2 :{r * r:.2f}$\n'
        rf'$\rho :{spearman:.2f}$ ($p = {p_value:.4f}$)'
    )
    ax.set_title(ax.get_title() + '\n' + text)


if __name__ == '__main__':
    main(
        input_path=SETTINGS['input_path'],
        cache_path=SETTINGS['cache_path'],
        output_path=SETTINGS['output_path'],
        refresh_cache=SETTINGS['refresh_cache'],
    )
