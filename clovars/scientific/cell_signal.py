from __future__ import annotations

from typing import Optional

import numpy as np
from matplotlib import pyplot as plt

from clovars.scientific import get_oscillator, Distribution, Wave, Oscillator


class CellSignal:
    """Class representing an abstract cell signal that fluctuates over time."""
    def __init__(
        self,
        oscillator_name: str = '',
        initial_value: float = 0.0,
        oscillator: Oscillator = None,
        *oscillator_args,
        **oscillator_kwargs,
    ) -> None:
        """Initializes a CellSignal instance."""
        self.value = initial_value
        self.oscillator = oscillator
        if oscillator is None:
            self.oscillator = get_oscillator(name=oscillator_name, *oscillator_args, **oscillator_kwargs)

    def oscillate(self) -> None:
        """Oscillates the CellSignal value based on its Oscillator."""
        self.value += self.oscillator.oscillate()

    def oscillate_and_get(self) -> float:
        """Oscillates the CellSignal and returns its value afterwards."""
        self.oscillate()
        return self.value

    def oscillate_for(
            self,
            n: int = 100,
    ) -> list[float]:
        """Oscillates the CellSignal n times, returning a list of the values after each oscillation."""
        return [self.oscillate_and_get() for _ in range(n)]

    def split(self) -> CellSignal:
        """Returns a new CellSignal instance with the same parameters as the current instance."""
        return CellSignal(initial_value=self.value, oscillator=self.oscillator.split())

    def bifurcate(self) -> tuple[CellSignal, CellSignal]:
        """Returns two new CellSignals, based on the desired correlation values between them."""
        if isinstance(self.oscillator, Wave):
            return self.split(), self.split()
        elif isinstance(self.oscillator, Distribution):
            return self.split(), self.split()
        elif isinstance(self.oscillator, Oscillator):  # MultivariateGaussianDistribution
            left_value, right_value = self.oscillator.bifurcate()
            return (
                CellSignal(initial_value=left_value, oscillator=self.oscillator.split()),
                CellSignal(initial_value=right_value, oscillator=self.oscillator.split()),
            )
        else:  # MultivariateGaussian
            raise ValueError('Bad dist type!')

    def mutate(
            self,
            oscillator_name: str = 'gaussian',
            *oscillator_args,
            **oscillator_kwargs,
    ) -> None:
        """Modifies the current Distribution of the CellSignal."""
        self.oscillator = get_oscillator(name=oscillator_name, *oscillator_args, **oscillator_kwargs)


def plot_cell_signal(
        signal: CellSignal,
        n_iters: int = 100,
) -> None:
    """Plots the distribution visually."""
    fig, ax = plt.subplots()
    xs = np.arange(n_iters)
    ys = signal.oscillate_for(n=n_iters)
    ax.plot(xs, ys)
    plt.show()


def get_cell_signal(
        name: str = '',
        initial_value: Optional[float] = None,
        *args,
        **kwargs,
) -> CellSignal:
    """Returns a CellSignal instance, according to the input parameters."""
    return CellSignal(oscillator_name=name, initial_value=initial_value, *args, **kwargs)


if __name__ == '__main__':
    signal = CellSignal(oscillator_name='gaussian', initial_value=1_000)
    plot_cell_signal(signal=signal, n_iters=100)
