"""distribution.py - stores the base Distribution class used for CellSignals and Curves."""
from __future__ import annotations

import numpy as np
import scipy.stats
from matplotlib import pyplot as plt


class Oscillator:
    """Class representing an entity capable of oscillating its value."""
    def oscillate(self) -> float:
        """
        Abstract method that must be implemented by Oscillator subclasses.
        Returns a new value derived from the Oscillator.
        """
        raise NotImplementedError

    def split(self) -> Oscillator:
        """
        Abstract method that must be implemented by Oscillator subclasses.
        Returns a new Oscillator instance, initially identical to the current Oscillator instance.
        """
        raise NotImplementedError


class Distribution(Oscillator):
    """Class representing a distribution (gaussian, gamma, lognormal, ...) that is able to oscillate."""
    _dist_types = {
        'gaussian': scipy.stats.norm,
        'emgaussian': scipy.stats.exponnorm,
        'gamma': scipy.stats.gamma,
        'lognormal': scipy.stats.lognorm,
    }

    def __init__(
            self,
            dist_type: str = '',
            scipy_dist: scipy.stats.rv_frozen = None,  # Frozen distribution
            *args,  # Distribution-specific arguments
            **kwargs,  # Distribution-specific keyword arguments
    ) -> None:
        """Initializes a Distribution instance."""
        self.dist_type = dist_type
        if scipy_dist is None:
            self.validate_dist_type(dist_type=self.dist_type)
            scipy_dist = self._dist_types[self.dist_type](*args, **kwargs)  # Should not raise KeyError
        self._scipy_dist = scipy_dist

    def validate_dist_type(
            self,
            dist_type: str,
    ) -> None:
        """Raises a ValueError if the type of the Distribution is invalid (i.e. not in the _dist_types dictionary)."""
        valid_types = list(self._dist_types)
        if not dist_type:
            raise ValueError(f"No dist_type provided, please provide a valid value: {valid_types}")
        if dist_type not in self._dist_types:
            raise ValueError(f"Invalid Distribution type: {dist_type}. Valid names are: {valid_types}")

    def oscillate(self) -> float:
        """Implements the oscillate method by returning a random value drawn from the distribution."""
        return self._scipy_dist.rvs()

    def split(self) -> Distribution:
        """Implements the split method by returning an identical Distribution."""
        return Distribution(dist_type=self.dist_type, scipy_dist=self._scipy_dist)

    # def cdf(
    #         self,
    #         x: float | np.ndarray,
    # ) -> float:
    #     """Returns the Distribution's cumulative distribution function evaluated at x."""
    #     return self._scipy_dist.cdf(x)
    #
    # def pdf(
    #         self,
    #         x: float | np.ndarray,
    # ) -> float:
    #     """Returns the Distribution's probability density function evaluated at x."""
    #     return self._scipy_dist.pdf(x)


class Wave(Oscillator):
    """Class representing a wave function that is able to oscillate."""
    _noise_min = 0.0
    _noise_max = 1.0

    def __init__(
            self,
            period: int = 3600,
            amplitude: int = 1,
            vertical_shift: int = 0,
            current_time: int = 0,
            noise: float = 0.0,
    ) -> None:
        """Initializes a Wave instance."""
        self.period = period
        self.amplitude = amplitude
        self.vertical_shift = vertical_shift
        self.current_time = current_time
        self.validate_noise(noise=noise)
        self.noise = noise
        self._period_in_radians = (2 * np.pi / self.period)
        self._horizontal_shift = np.arcsin((-self.vertical_shift) / self.amplitude) / self._period_in_radians

    def validate_noise(
            self,
            noise: float,
    ) -> None:
        """Raises a ValueError if the noise value is outside the valid range."""
        if not self._noise_min <= noise <= self._noise_max:
            raise ValueError(f"Noise value must be in the [{self._noise_min}, {self._noise_max}] interval.")

    def oscillate(self) -> float:
        """Implements the oscillate method by returning a random value drawn from the distribution."""
        self.current_time += 1
        sine_value = self._sine(x=self.current_time)
        noise_value = self._noise()
        return (sine_value * (1 - self.noise)) + (noise_value * self.noise)

    def _sine(
            self,
            x: int,
    ) -> float:
        """Returns a sine wave evaluated at x."""
        # The line below took me way longer to get right than I want to admit, but it actually works now
        return self.amplitude * np.sin(self._period_in_radians * (x + self._horizontal_shift)) + self.vertical_shift

    def _noise(self) -> float:
        """Returns a uniform value between inside the Wave's amplitude."""
        return np.random.uniform(low=-self.amplitude*3, high=self.amplitude*3)

    def split(self) -> Wave:
        """Implements the split method by returning an identical Distribution."""
        return Wave(
            period=self.period,
            amplitude=self.amplitude,
            vertical_shift=self.vertical_shift,
            current_time=self.current_time,
            noise=self.noise,
        )


def get_distribution(
        distribution: Distribution = None,
        distribution_name: str = '',
        *distribution_args,
        ** distribution_kwargs,
) -> Distribution:
    """Returns a Distribution instance, based on the input parameters."""
    if distribution is None:
        if not distribution_name:
            raise ValueError("Must provide either a Distribution instance or its name.")
        else:
            distribution = Distribution(name=distribution_name, *distribution_args, **distribution_kwargs)
    return distribution


if __name__ == '__main__':
    d = Distribution(dist_type='gaussian')
    w = Wave(period=5_000, noise=0.6)

    xs = np.linspace(-10, 10, 10_000)
    ys_dist = [0]
    ys_wave = [0]
    for _ in xs[1:]:
        ys_dist.append(ys_dist[-1] + d.oscillate())
        ys_wave.append(ys_wave[-1] + w.oscillate())

    fig, (left_ax, right_ax) = plt.subplots(ncols=2)
    left_ax.plot(xs, ys_dist)
    left_ax.set_title('Gaussian Distribution')
    right_ax.plot(xs, ys_wave)
    right_ax.set_title('Sinusoidal Wave')

    plt.show()
