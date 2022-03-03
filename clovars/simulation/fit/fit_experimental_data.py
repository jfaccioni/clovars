from __future__ import annotations

import matplotlib.pyplot as plt
from clovars.simulation import DataFitter


def fit_experimental_data_function(
        input_file: str,
        sheet_name: str,
        division_times_column: str,
        death_times_column: str,
        verbose: bool,
) -> None:
    """Fits the experimental data to the family of distributions and displays the results on screen."""
    de = DataFitter(
        input_file=input_file,
        sheet_name=sheet_name,
        division_times_column=division_times_column,
        death_times_column=death_times_column,
        verbose=verbose,
    )
    de.fit()
    de.display()
    de.plot()
    plt.show()
