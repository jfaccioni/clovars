from __future__ import annotations

import os
import sys
from argparse import ArgumentParser
from pathlib import Path
from typing import Any

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
from scipy.stats import exponnorm, gamma, lognorm, norm

from clovars.utils import QuietPrinterMixin


class DataFitter(QuietPrinterMixin):
    """Class responsible for estimating the best-fit curve for a given dataset."""
    def __init__(
            self,
            input_file: str,
            sheet_name: str = '',
            division_times_column: str = '',
            death_times_column: str = '',
            verbose: bool = False,
    ) -> None:
        """Initializes a DataFitter instance."""
        super().__init__(verbose=verbose)
        self.file_path = Path(input_file)
        self.sheet_name = sheet_name
        self.division_times_column = division_times_column
        self.death_times_column = death_times_column
        self.validate_file_path()
        self.data = self.parse_input_data()
        self.validate_column_names()
        self.death_fit = None
        self.division_fit = None

    @staticmethod
    def parse_command_line_args() -> dict[str, Any]:
        """Parse the command-line arguments and returns them as a Namespace instance."""
        parser = ArgumentParser()
        parser.add_argument('file_path', help='Path to the file', default='.')
        parser.add_argument('-s', '--sheet-name', help='Sheet name (for Excel spreadsheets)', default=None)
        parser.add_argument('-d', '--death-label', help='Column name for death times', default=None)
        parser.add_argument('-m', '--division-label', help='Column name for division times', default=None)
        parser.add_argument('-v', '--verbose', help='Increases output verbosity', action='store_true')
        return vars(parser.parse_args(sys.argv[1:]))

    def validate_file_path(self) -> None:
        """Validates the file path argument, raising a ValueError if it does not exist."""
        if not os.path.exists(self.file_path):
            raise ValueError(f"File {self.file_path} does not exist!")

    def validate_column_names(self) -> None:
        """Validates the column names of the data."""
        if self.division_times_column is None:
            print('No division label added, skipping division times from analysis...')
        elif self.division_times_column not in self.data:
            print('Division label not found in data, skipping division times from analysis...')
            self.division_times_column = None
        elif self.data[self.division_times_column].isna().all():
            print('Skipping division times from analysis since it is empty...')
            self.division_times_column = None
        if self.death_times_column is None:
            print('No death label added, skipping death times from analysis...')
        elif self.death_times_column not in self.data:
            print('Death label not found in data, skipping death times from analysis...')
            self.death_times_column = None
        elif self.data[self.death_times_column].isna().all():
            print('Skipping death times from analysis since it is empty...')
            self.death_times_column = None

    def parse_input_data(self) -> pd.DataFrame:
        """Parses and returns the input data."""
        if (suffix := self.file_path.suffix) == '.csv':
            df = pd.read_csv(self.file_path, index_col=None)
        elif suffix == '.xlsx':
            if self.sheet_name is None:
                raise ValueError('Data from Excel requires a sheet name argument!')
            df = pd.read_excel(self.file_path, sheet_name=self.sheet_name, index_col=None)
        else:
            raise ValueError(f"Unsupported file type: {suffix}. Only .csv or .xlsx files are supported.")
        return df

    def fit(self) -> None:
        if self.division_times_column is not None:
            self.quiet_print(f'Calculating best fit for division...')
            division_data = self.data[self.division_times_column].dropna().values
            self.division_fit = self.calculate_best_fit(data=division_data)
        else:
            self.quiet_print(f'Skipped calculations for division column because it is None.')
        if self.death_times_column is not None:
            self.quiet_print(f'Calculating best fit for death...')
            death_data = self.data[self.death_times_column].dropna().values
            self.death_fit = self.calculate_best_fit(data=death_data)
        else:
            self.quiet_print(f'Skipped calculations for death column because it is None.')

    @staticmethod
    def calculate_best_fit(data: np.ndarray) -> dict[str, Any]:
        """Calculates the best fit data and saves it to the fit_data attribute."""
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

    def display(self) -> None:
        """Displays the previously calculated fit data."""
        if self.division_fit is None:
            self.quiet_print('Skipped displaying division fit data because it is None.')
        else:
            self.quiet_print('Displaying best fit for division times...')
            self.display_fit_by_rank(fit_data=self.division_fit)
        print('\n' + '-*' * 20 + '-\n\n')
        if self.death_fit is None:
            self.quiet_print('Skipped displaying death fit data because it is None.')
        else:
            self.quiet_print('Displaying best fit for death times...')
            self.display_fit_by_rank(fit_data=self.death_fit)

    def display_fit_by_rank(
            self,
            fit_data: dict[str, Any],
    ) -> None:
        """Prints the data fitted by its RMSE ranking."""
        for i, (fit_name, fit_values) in enumerate(sorted(fit_data.items(), key=lambda tup: tup[1]['RMSE']), 1):
            rank = self.to_ordinal(i)
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

    def plot(self) -> None:
        """Plots the previously calculated fit data."""
        if self.division_fit is None:
            self.quiet_print('Skipped plotting division fit data because it is None.')
        else:
            self.plot_fit(fit_data=self.division_fit, column_name=self.division_times_column, title_label='division')
        if self.death_fit is None:
            self.quiet_print('Skipped plotting death fit data because it is None.')
        else:
            self.plot_fit(fit_data=self.death_fit, column_name=self.death_times_column, title_label='death')

    def plot_fit(
            self,
            fit_data: dict[str, Any],
            column_name: str,
            title_label: str,
    ) -> None:
        """Plots the data fitted to different distributions."""
        original_data = self.data[column_name]
        fig, ax = plt.subplots()
        label = f'Data\n$N$={len(original_data)}'
        sns.kdeplot(original_data, ax=ax, label=label, color='.5', linestyle='--', linewidth=5)
        xs = np.linspace(np.amin(original_data), np.amax(original_data), 10_000)
        for fit_name, fit_values in fit_data.items():
            params_str = "\n".join([
                f'{label}={round(value, 2)}'
                for label, value in fit_values['named_params'].items()
            ])
            label = f'{fit_name}\n{params_str}'
            ys = fit_values['func'].pdf(xs, *fit_values['params'])
            sns.lineplot(x=xs, y=ys, ax=ax, label=label, linewidth=3, alpha=0.7)
        plt.ylim(top=0.05)
        fig.suptitle(f'Fit for {title_label}')

    @staticmethod
    def to_ordinal(n: int) -> str:
        """Convert an integer into its ordinal string representation."""
        # Source: https://stackoverflow.com/a/50992575/11161432
        if 11 <= (n % 100) <= 13:
            suffix = 'th'
        else:
            suffix = ['th', 'st', 'nd', 'rd', 'th'][min(n % 10, 4)]
        return str(n) + suffix
