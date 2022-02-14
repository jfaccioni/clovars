from __future__ import annotations

from dataclasses import dataclass
from typing import Iterator, Dict, Any

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy.stats import norm, exponnorm, gamma, lognorm

from clovars.scientific import Curve


@dataclass
class _CurveData:
    """Dataclass storing a Curve's name, initialization parameters and root sum of squares (RSS)."""
    name: str
    rss: float
    params: dict


class CurveEstimator:
    """Estimates the best-fit curve for the input data."""
    curves_dict = {
            "Gaussian": norm,
            "EMGaussian": exponnorm,
            "Gamma": gamma,
            "Lognormal": lognorm,
    }

    def __init__(
            self,
            data: pd.Series,
    ) -> None:
        """Initializes a CurveEstimator instance."""
        self.data = data
        self.curves = []
        self.fit_data()

    def __str__(self) -> str:
        """Returns a user-friendly text of the CurveEstimator instance."""
        text = f"CurveEstimator\nData={list(self.data)}\n-----"
        for curve in self:
            text += f'\n{curve.name} fit\nRSS = {curve.rss}\nParameters = {curve.params}\n-----'
        return text

    def __repr__(self) -> str:
        """Returns a string representation of the CurveEstimator instance."""
        values = ', '.join(self.data.astype(str))
        return f"CurveEstimator(data=pd.Series([{values}])"

    def __iter__(self) -> Iterator:
        """Iterates over the Curves, starting from the one with the smallest RSS."""
        return iter(sorted(self.curves, key=lambda c: c.rss))

    def __getitem__(
            self,
            i: int,
    ) -> _CurveData:
        """Gets the i-th best fit Curve."""
        return list(self)[i]

    def fit_data(self) -> None:
        """Writes the Curves fitted to the data to the estimations dictionary."""
        # Sources:
        # https://stackoverflow.com/questions/6620471/fitting-empirical-distribution-to-theoretical-ones-with-scipy-python
        # https://en.wikipedia.org/wiki/Residual_sum_of_squares
        y, x = np.histogram(self.data, density=True)
        x = (x + np.roll(x, -1))[:-1] / 2.0
        for curve_name, curve_type in self.curves_dict.items():
            params = self.get_curve_params(curve_type=curve_type)
            y_fit = curve_type.pdf(x, **params)
            rss = np.sum(np.power(y - y_fit, 2.0)).item()
            curve = _CurveData(name=curve_name, rss=rss, params=params)
            self.curves.append(curve)

    def get_curve_params(self, curve_type: Curve) -> Dict:
        """Returns a dictionary of the Curves parameters names and values."""
        param_values = curve_type.fit(self.data)
        if (param_names := curve_type.shapes) is None:  # this curve type has no additional parameters
            return {'loc': param_values[0], 'scale': param_values[1]}
        params = {}
        for param_name, param_value in zip(param_names, param_values):
            params[param_name] = param_value
        return params | {'loc': param_values[-2], 'scale': param_values[-1]}

    def to_simulation(self) -> Dict[str, Any]:
        """Returns a properly formatted dictionary to be used in conjunction with the Simulation."""
        best_fit_curve = self[0]
        simulation_params = {'name': best_fit_curve.name, **best_fit_curve.params}
        if 'K' in simulation_params:  # capitalized in scipy.stats.exponnorm but not on the simulation
            simulation_params['k'] = simulation_params['K']
        return simulation_params


def demo(data):
    """Short demo of the curve_estimator script."""
    ce = CurveEstimator(data=data)
    print(ce)
    print(ce.to_simulation())

    def plot_curve_estimator(curve_estimator: CurveEstimator) -> None:
        """Plots the CE."""
        fig, ax = plt.subplots()
        ax.hist(data, color='gray', alpha=0.3)
        xs = np.linspace(min(data) - 1, max(data) + 1, len(data))
        for curve in curve_estimator:
            ys = CurveEstimator.curves_dict[curve.name].pdf(xs, **curve.params)
            ax.plot(xs, ys * len(data), label=f"{curve.name} (RSS={round(curve.rss, 4)})")
        plt.legend()
        plt.show()

    plot_curve_estimator(curve_estimator=ce)


if __name__ == '__main__':
    DATA = np.array([*np.random.normal(loc=32, scale=2, size=1000), *np.random.normal(loc=24, scale=2, size=1000)])
    demo(data=DATA)
