from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns

from clovars import ROOT_PATH


sns.set()

SETTINGS = {
    'ctor_output_folder': ROOT_PATH / 'data' / 'ctor_analysis' / '2022-05-26 Gaussian Curves',
    'use_cached_raw_data': True,
    'use_cached_processed_data': True,
    'filter_dead_colonies': True,
    'color_colonies': True,
}


def main(
        ctor_output_folder: Path,
        use_cached_raw_data: bool,
        use_cached_processed_data: bool,
        filter_dead_colonies: bool,
        color_colonies: bool,

) -> None:
    """Main function of this script."""
    raw_data_path = ctor_output_folder / 'all_cell_data_raw.csv'
    processed_data_path = ctor_output_folder / 'all_cell_data_processed.csv'
    if use_cached_processed_data is True:
        processed_data = pd.read_csv(processed_data_path)
    elif use_cached_raw_data is True:
        raw_data = pd.read_csv(raw_data_path, index_col=None)
        processed_data = process_raw_data(raw_data=raw_data)
        processed_data.to_csv(processed_data_path, index=False)
    else:
        raw_data = load_ctor_dataset(ctor_output_folder=ctor_output_folder)
        raw_data.to_csv(raw_data_path, index=False)
        processed_data = process_raw_data(raw_data=raw_data)
        processed_data.to_csv(processed_data_path, index=False)
    if filter_dead_colonies is True:
        processed_data = processed_data.loc[processed_data['colony_size'] > 1]
    final_data = (
        processed_data.
        groupby(['CTOR_shift', 'colony_num']).
        agg(colony_size_variance=('colony_size', 'var')).
        reset_index()
    )
    fig, (top_ax, bottom_ax) = plt.subplots(figsize=(16, 12), nrows=2, sharex='all')
    # TOP AX
    if color_colonies is True:
        sns.boxplot(ax=top_ax, data=processed_data, x='CTOR_shift', y='colony_size', showfliers=False, color='.75')
        sns.stripplot(ax=top_ax, data=processed_data, x='CTOR_shift', y='colony_size', hue='colony_num')
        top_ax.legend().remove()
    else:
        sns.boxplot(ax=top_ax, data=processed_data, x='CTOR_shift', y='colony_size', showfliers=False)
        sns.stripplot(ax=top_ax, data=processed_data, x='CTOR_shift', y='colony_size', color='.25')
    top_ax.set_title('Final size each colony branch')
    top_ax.set_xlabel('CTOR Shifts (hours)')
    top_ax.set_ylabel('Branch size (all colonies mixed)')
    # BOTTOM AX
    sns.boxplot(ax=bottom_ax, data=final_data, x='CTOR_shift', y='colony_size_variance', showfliers=False)
    sns.stripplot(ax=bottom_ax, data=final_data, x='CTOR_shift', y='colony_size_variance', color='.25')
    bottom_ax.set_title('Size variance in each colony branch')
    bottom_ax.set_xlabel('CTOR Shifts (hours)')
    bottom_ax.set_ylabel('Branch variance')
    # FIGURE
    fig.tight_layout()
    plt.show()


def load_ctor_dataset(ctor_output_folder: Path) -> pd.DataFrame:
    """Loads each CTOR data from the CTOR output folder, concatenates it into a single dataset and returns it."""
    dfs = []
    for ctor_folder in (p for p in ctor_output_folder.iterdir() if p.is_dir()):
        print(f'reading from CTOR folder:\n{ctor_folder}\n')
        _, shift_str = ctor_folder.stem.split('_')
        shift = int(shift_str.replace('h', ''))
        for colony_folder in (ctor_folder / 'data').iterdir():
            print(f'parsing data from colony folder:\n{colony_folder}\n')
            _, colony_num_str = colony_folder.stem.split('_')
            colony_num = int(colony_num_str)
            df = pd.read_csv(colony_folder / 'cell.csv', index_col=None)
            df['CTOR_shift'] = shift
            df['colony_num'] = colony_num
            dfs.append(df)
    data = pd.concat(dfs, ignore_index=True)
    return data


def process_raw_data(raw_data: pd.DataFrame) -> pd.DataFrame:
    """Processes the raw data and returns it."""
    print('Processing raw data...')
    raw_data['branch_num'] = raw_data['branch_name'].str.replace('1a-', '').astype(int)
    max_indices = (
            raw_data.
            groupby(['CTOR_shift', 'colony_num', 'branch_num'])['simulation_days'].
            transform('max') == raw_data['simulation_days']
    )
    filtered_data = raw_data.loc[max_indices, :]
    processed_data = (
        filtered_data.
        sort_values(by=['colony_num', 'branch_num']).
        groupby(['CTOR_shift', 'colony_num', 'branch_num']).
        agg(colony_size=('id', 'count')).
        reset_index()
    )
    return processed_data


if __name__ == '__main__':
    main(
        ctor_output_folder=SETTINGS['ctor_output_folder'],
        use_cached_raw_data=SETTINGS['use_cached_raw_data'],
        use_cached_processed_data=SETTINGS['use_cached_processed_data'],
        filter_dead_colonies=SETTINGS['filter_dead_colonies'],
        color_colonies=SETTINGS['color_colonies'],
    )
