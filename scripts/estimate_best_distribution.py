from __future__ import annotations

import os
from typing import Any

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy.stats import exponnorm, gamma, lognorm, norm
import seaborn as sns

sns.set()

SETTINGS = {
    'folder_path': '.',
    'file_name': 'data.csv',
    'sheet_name': 'data',
    'division_times_column': 'Division Times',
    'death_times_column': 'Death Times',
}


def main(
        folder_path: str,
        file_name: str,
        sheet_name: str,
        division_times_column: str | None,
        death_times_column: str | None,
) -> None:
    """Main function of this script."""
    file_path = os.path.join(folder_path, file_name)
    df = parse_input_data(file_path=file_path, sheet_name=sheet_name)
    for column_name, data_label in [(division_times_column, 'division'), (death_times_column, 'death')]:
        if column_name is None:  # User does not want to analyze this column
            continue
        print(f'Calculating best fit for {data_label} ----->')
        data = df[column_name].dropna().values
        fit_data = calculate_best_fit(data=data)
        plot_fit_data(data_label=data_label, original_data=data, fit_data=fit_data)
        display_fit_by_rank(fit_data=fit_data)
        print('\n' + '-*' * 20 + '-\n\n')
    print('Done')
    plt.show()


def to_ordinal(n: int) -> str:
    """Convert an integer into its ordinal representation."""
    # Source: https://stackoverflow.com/a/50992575/11161432
    if 11 <= (n % 100) <= 13:
        suffix = 'th'
    else:
        suffix = ['th', 'st', 'nd', 'rd', 'th'][min(n % 10, 4)]
    return str(n) + suffix


def parse_input_data(
        file_path: str,
        sheet_name: str,
) -> pd.DataFrame:
    """Parses and returns the input data."""
    if file_path.endswith('.csv'):
        df = pd.read_csv(file_path, index_col=None)
    elif file_path.endswith('.xlsx'):
        df = pd.read_excel(file_path, sheet_name=sheet_name, index_col=None)
    else:
        raise ValueError(f"Unsupported file type: .{file_path.split('.')[-1]}. Only .csv or .xlsx files are supported.")
    return df


def calculate_best_fit(data: np.ndarray) -> dict[str, Any]:
    """Prints the best fit for the input dataset."""
    # Sources:
    # https://stackoverflow.com/questions/6620471/fitting-empirical-distribution-to-theoretical-ones-with-scipy-python
    # https://en.wikipedia.org/wiki/Residual_sum_of_squares
    y, x = np.histogram(data, density=True)
    x = (x + np.roll(x, -1))[:-1] / 2.0
    fit_data = {}
    for label, func, param_labels in [
        ('Gaussian', norm, ('$\mu$', '$\sigma$')),
        ('EMGaussian', exponnorm, ('$K$', '$\mu$', '$\sigma$')),
        ('Gamma', gamma, ('$a$', '$\mu$', '$\sigma$')),
        ('Lognormal', lognorm, ('$s$', '$\mu$', '$\sigma$')),
    ]:
        param_values = func.fit(data)
        fit_data[label] = {
            'func': func,
            'params': param_values,
            'named_params': {label: value for label, value in zip(param_labels, param_values)},
            'RMSE': np.sum(np.power(y - func.pdf(x, *param_values), 2.0)).item(),
        }
    return fit_data


def plot_fit_data(
        data_label: str,
        original_data: np.array,
        fit_data: dict[str, Any],
) -> None:
    """Plots the data fitted to different distributions."""
    fig, ax = plt.subplots()
    label = f'Data\n$N$={len(original_data)}'
    sns.kdeplot(original_data, ax=ax, label=label, color='.5', linestyle='--', linewidth=5)
    xs = np.linspace(np.amin(original_data), np.amax(original_data), 10_000)
    for fit_name, fit_values in fit_data.items():
        params_str = "\n".join([f'{label}={round(value, 2)}' for label, value in fit_values['named_params'].items()])
        label = f'{fit_name}\n{params_str}'
        ys = fit_values['func'].pdf(xs, *fit_values['params'])
        sns.lineplot(x=xs, y=ys, ax=ax, label=label, linewidth=3, alpha=0.7)
    plt.ylim(top=0.05)
    fig.suptitle(f'Fit for {data_label}')


def display_fit_by_rank(fit_data: dict[str, Any]) -> None:
    """Prints the data fitted by its RMSE ranking."""
    for i, (fit_name, fit_values) in enumerate(sorted(fit_data.items(), key=lambda tup: tup[1]['RMSE']), 1):
        rank = to_ordinal(i)
        RMSE = fit_values['RMSE']
        params_str = '\n    '.join([
            k.replace('$', '').replace('\\', '') + f" = {v}"
            for k, v in fit_values['named_params'].items()
        ])
        print(
            f'{fit_name = !s} ',
            f'{rank     = !s} ',
            f'{RMSE     = !s} ',
            f'params:\n    {params_str}',
            '----------------',
            sep='\n',
        )


if __name__ == '__main__':
    main(
        folder_path=SETTINGS['folder_path'],
        file_name=SETTINGS['file_name'],
        sheet_name=SETTINGS['sheet_name'],
        division_times_column=SETTINGS['division_times_column'],
        death_times_column=SETTINGS['death_times_column'],
    )
