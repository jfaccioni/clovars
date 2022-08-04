"""distribution.py - stores the base Oscillator class integrated in CellSignals and Curves."""
from __future__ import annotations

import abc

import numpy as np
from scipy.stats import exponnorm, gamma, lognorm, norm

from clovars.scientific import Numeric


# Oscillator -------------------------------------------------------------------

class Oscillator:
    """Class representing an entity capable of oscillating its value."""
    @abc.abstractmethod
    def _validate(self) -> float:
        """
        Abstract internal method that must be implemented by Oscillator subclasses.
        Validates the input parameters of the Oscillator.
        """
        pass

    @abc.abstractmethod
    def oscillate(self) -> float:
        """
        Abstract method that must be implemented by Oscillator subclasses.
        Returns a new value derived from the Oscillator.
        """
        pass

    @abc.abstractmethod
    def split(self) -> Oscillator:
        """
        Abstract method that must be implemented by Oscillator subclasses.
        Returns a new Oscillator instance, initially identical to the current Oscillator instance.
        """
        pass


# Distribution -----------------------------------------------------------------

class Distribution(Oscillator):
    """Class representing a distribution (gaussian, gamma, lognormal, ...) that is able to oscillate."""
    _dist_types = {
        'gaussian': norm,
        'emgaussian': exponnorm,
        'gamma': gamma,
        'lognormal': lognorm,
    }
    _valid_types = list(_dist_types)

    def __init__(
            self,
            dist_type: str = '',
            *args,  # Distribution-specific arguments
            **kwargs,  # Distribution-specific keyword arguments
    ) -> None:
        """Initializes a Distribution instance."""
        self._dist_type = dist_type
        self._args = args
        self._kwargs = kwargs
        self._validate()
        self._scipy_dist = self._dist_types[self._dist_type](*args, **kwargs)  # Should not raise KeyError

    @property
    def mean(self) -> float:
        """
        Returns the mean of the underlying scipy dist.
        Relies on the fact that the "loc" argument is passed as a keyword in the Distribution functions below!
        """
        return self._kwargs['loc']

    @property
    def std(self) -> float:
        """
        Returns the standard deviation of the underlying scipy dist.
        Relies on the fact that the "scale" argument is passed as a keyword in the Distribution functions below!
        """
        return self._kwargs['scale']

    def _validate(self) -> None:
        """Raises a ValueError if the type of the Distribution is invalid (i.e. not in the _dist_types dictionary)."""
        if not self._dist_type:
            raise ValueError(f"No dist_type provided, please provide a valid value: {self._valid_types}")
        if self._dist_type not in self._valid_types:
            raise ValueError(f"Invalid Distribution type: {self._dist_type}. Valid names are: {self._valid_types}")

    def oscillate(self) -> float:
        """Implements the oscillate method by returning a random value drawn from the distribution."""
        return self._scipy_dist.rvs()

    def split(self) -> Distribution:
        """Implements the split method by returning an identical, independent Distribution."""
        # we can return the same instance, since it does not depend on any internal state
        # (no problem if 2 or more cells share the reference to the same oscillator)
        return self

    def cdf(
            self,
            x: Numeric,
    ) -> Numeric:
        """Returns the Distribution's cumulative distribution function evaluated at x."""
        return self._scipy_dist.cdf(x)

    def pdf(
            self,
            x: Numeric,
    ) -> Numeric:
        """Returns the Distribution's probability density function evaluated at x."""
        return self._scipy_dist.pdf(x)


def GaussianDistribution(
        mean: float = 0.0,
        std: float = 1.0,
) -> Distribution:
    """Returns a gaussian distribution."""
    return Distribution(dist_type='gaussian', loc=mean, scale=std)


def EMGaussianDistribution(
        mean: float = 0.0,
        std: float = 1.0,
        k: float = 0.05,
) -> Distribution:
    """Returns an exponentially-modified gaussian distribution."""
    return Distribution(dist_type='emgaussian', loc=mean, scale=std, K=k)


def GammaDistribution(
        mean: float = 0.0,
        std: float = 1.0,
        a: float = 0.05,
) -> Distribution:
    """Returns a gamma distribution."""
    return Distribution(dist_type='gamma', loc=mean, scale=std, a=a)


def LognormalDistribution(
        mean: float = 0.0,
        std: float = 1.0,
        s: float = 0.05,
) -> Distribution:
    """Returns a lognormal distribution."""
    return Distribution(dist_type='lognormal', loc=mean, scale=std, s=s)


# Wave -------------------------------------------------------------------------

class Wave(Oscillator):
    """Class representing a wave function that is able to oscillate."""
    # These values should NOT chane
    _noise_min = 0.0
    _noise_max = 1.0

    def __init__(
            self,
            period: int = 3600,  # in seconds
            delta: int = 360,  # in seconds
            current_time: int = 0,  # in seconds
            amplitude: int | float = 1.0,
            vertical_shift: int | float = 0.0,
            noise: float = 0.0,
    ) -> None:
        """Initializes a Wave instance."""
        self.period = period
        self.delta = delta
        self.current_time = current_time
        self.amplitude = amplitude
        self.vertical_shift = vertical_shift
        self.noise = noise
        self._validate()
        # Derived parameters
        self._period_in_radians = (2 * np.pi / self.period)
        self._horizontal_shift = np.arcsin((-self.vertical_shift) / self.amplitude) / self._period_in_radians

    def _validate(self) -> None:
        """Raises a ValueError if the noise value is outside the valid range."""
        if not self._noise_min <= self.noise <= self._noise_max:
            raise ValueError(f"Noise value must be in the [{self._noise_min}, {self._noise_max}] interval.")

    def oscillate(self) -> float:
        """Implements the oscillate method by returning a random value drawn from the distribution."""
        sine_value = self._sine(x=self.current_time)
        noise_value = self._noise()
        self.current_time += self.delta  # Wave "moves" self.delta seconds into the future
        return (sine_value * (1 - self.noise)) + (noise_value * self.noise)

    def split(self) -> Wave:
        """Implements the split method by returning an identical Distribution."""
        # Here we have to actually return a separate instance, since there is internal state in the
        # Oscillator (self.current time is updated internally with every self.oscillate() call)
        return Wave(
            period=self.period,
            delta=self.delta,
            current_time=self.current_time,
            amplitude=self.amplitude,
            vertical_shift=self.vertical_shift,
            noise=self.noise,
        )

    def _sine(
            self,
            x: Numeric,
    ) -> Numeric:
        """Returns a sine wave evaluated at x."""
        # The line below took me way longer to get right than I want to admit, but it actually works now
        return self.amplitude * np.sin(self._period_in_radians * (x + self._horizontal_shift)) + self.vertical_shift

    def _noise(self) -> float:
        """Returns a uniform value between inside the Wave's amplitude."""
        return np.random.uniform(low=-self.amplitude*3, high=self.amplitude*3)


def StochasticWave(
        *args,
        **kwargs,
) -> Wave:
    """Returns a purely stochastic wave."""
    return Wave(noise=1.0, *args, *kwargs)


def SinusoidalWave(
        *args,
        **kwargs,
) -> Wave:
    """Returns a purely sinusoidal wave."""
    return Wave(noise=0.0, *args, *kwargs)


def StochasticSinusoidalWave(
        noise: float = None,
        *args,
        **kwargs,
) -> Wave:
    """Returns a mixed stochastic / sinusoidal wave."""
    if noise is None:
        noise = np.random.uniform(0.2, 0.8)
    return Wave(noise=noise, *args, *kwargs)


# get Oscillator / Distribution / Wave functions -------------------------------

_VALID_DIST_NAMES = ['gaussian', 'emgaussian', 'gamma', 'lognormal']
_VALID_WAVE_NAMES = ['sinusoidal', 'stochastic', ['stochasticsinusoidal', 'stochsin', 'stochastic-sinusoidal'], 'wave']
_VALID_NAMES = _VALID_DIST_NAMES + _VALID_WAVE_NAMES


def get_oscillator(
        name: str,
        *args,
        **kwargs,
) -> Oscillator:
    """Returns an Oscillator, given its name."""
    try:
        return get_distribution(name=name, *args, **kwargs)
    except ValueError:
        try:
            return get_wave(name=name, *args, **kwargs)
        except ValueError as e:
            raise ValueError(f'Invalid Oscillator name: {name}. Valid names are:\n  {_VALID_NAMES}') from e


def get_distribution(
        name: str,
        *args,
        **kwargs,
) -> Distribution:
    """Returns a distribution, given its name."""
    match name.lower():
        case 'gaussian':
            return GaussianDistribution(*args, **kwargs)
        case 'emgaussian':
            return EMGaussianDistribution(*args, **kwargs)
        case 'gamma':
            return GammaDistribution(*args, **kwargs)
        case 'lognormal':
            return LognormalDistribution(*args, **kwargs)
        case _:
            raise ValueError(f"Invalid distribution name: {name}. Valid names are: {_VALID_DIST_NAMES}")


def get_wave(
        name: str,
        *args,
        **kwargs,
) -> Wave:
    """Returns a wave, given its name."""
    match name.lower():
        case 'sinusoidal':
            return SinusoidalWave(*args, **kwargs)
        case 'stochastic':
            return StochasticWave(*args, **kwargs)
        case 'stochasticsinusoidal' | 'stochsin' | 'stochastic-sinusoidal':
            return StochasticSinusoidalWave(*args, **kwargs)
        case 'wave':
            return Wave(*args, **kwargs)
        case _:
            raise ValueError(f"Invalid wave name: {name}. Valid names are: {_VALID_WAVE_NAMES}")
