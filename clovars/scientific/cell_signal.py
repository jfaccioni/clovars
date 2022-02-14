from __future__ import annotations

import copy
import random
from functools import partial
from typing import Optional

import numpy as np
from scipy.stats import norm, exponnorm


class CellSignal:
    """Represents an abstract Feature that can fluctuate over time."""
    def __init__(
            self,
            initial_value: float = 0.0,
    ) -> None:
        """Initializes a CellSignal instance."""
        self.initial_value = initial_value
        if not (-1.0 <= self.initial_value <= 1.0):
            raise ValueError(f"{self.__class__.__name__} initial value must be in the interval [-1, 1]")
        self.value = self.initial_value

    def split(self) -> CellSignal:
        """Copies the values from the CellSignal and returns a new CellSignal instance."""
        return copy.copy(self)

    def oscillate(
            self,
            *args,
            **kwargs,
    ) -> None:
        """Oscillates the current Feature value, adding it to the list of values."""
        self.value = self.get_new_value(*args, **kwargs)

    def get_new_value(
            self,
            *args,
            **kwargs,
    ) -> float:
        """Abstract method meant to be implemented by subclasses of CellSignal."""
        raise NotImplementedError  # using @abstractmethod here makes testing harder


class SinusoidalCellSignal(CellSignal):
    """Represents a sinusoidal feature."""
    def __init__(
            self,
            initial_value: float = 0.0,
            period: int = 3600,
    ) -> None:
        """Initializes a SinusoidalCellSignal instance."""
        super().__init__(initial_value=initial_value)
        self.period = period
        if self.period <= 0:
            raise ValueError(f"{self.__class__.__name__} period cannot be <= zero")

    def get_new_value(
            self,
            current_seconds: int,
            *args,
            **kwargs,
    ) -> float:
        """Implements the abstract method responsible for getting a new Signal value."""
        return self.sine(current_seconds=current_seconds)

    def sine(
            self,
            current_seconds: int,
    ) -> float:
        """Returns the sine wave evaluated at a specific point in time."""
        amplitude = 1.0
        vertical_shift = 0.0
        period_in_radians = (2 * np.pi / self.period)
        # The line below took me way longer to get right than I want to admit, but it actually works now
        horizontal_shift = np.arcsin((self.initial_value - vertical_shift) / amplitude) / period_in_radians
        return amplitude * np.sin(period_in_radians * (current_seconds + horizontal_shift)) + vertical_shift


class StochasticCellSignal(CellSignal):
    """Represents a stochastic feature."""
    def __init__(
            self,
            initial_value: float = 0.0,
            noise: float = 0.2,
    ) -> None:
        """Initializes a StochasticCellSignal instance."""
        super().__init__(initial_value=initial_value)
        self.noise = noise
        if not (0 <= self.noise <= 1):
            raise ValueError(f"{self.__class__.__name__} noise must be in the interval [0, 1]")

    def get_new_value(
            self,
            *args,
            **kwargs,
    ) -> float:
        """Implements the abstract method responsible for getting a new Signal value."""
        return self.stochastic()

    def stochastic(self) -> float:
        """Returns a random noise signal."""
        noise = self.noise * random.uniform(-1, 1)
        if (new_value := noise + self.value) > 1.0:
            return 1.0
        elif new_value < -1.0:
            return -1.0
        else:
            return new_value


class StochasticSinusoidalCellSignal(SinusoidalCellSignal, StochasticCellSignal):
    """Represents a feature with sinusoidal and stochastic components."""
    def __init__(
            self,
            initial_value: float = 0.0,
            period: int = 3600,
            noise: float = 0.2,
            stochastic_weight: float = 0.5,
    ) -> None:
        """Initializes a StochasticSinusoidalCellSignal instance."""
        SinusoidalCellSignal.__init__(self, initial_value=initial_value, period=period)
        StochasticCellSignal.__init__(self, initial_value=initial_value, noise=noise)
        self.stochastic_weight = stochastic_weight
        if not 0 <= self.stochastic_weight <= 1:
            raise ValueError("StochasticSinusoidalCellSignal stochastic weight must be in the interval [0, 1]")
        self.sine_weight = 1.0 - self.stochastic_weight

    def get_new_value(
            self,
            current_seconds: int,
            *args,
            **kwargs,
    ) -> float:
        """Implements the abstract method responsible for getting a new Signal value."""
        sine_component = self.sine(current_seconds=current_seconds) * self.sine_weight
        stochastic_component = self.stochastic() * self.stochastic_weight
        return sine_component + stochastic_component


class GaussianCellSignal(CellSignal):
    """Represents a feature which oscillates around a mean."""
    def __init__(
            self,
            initial_value: float = 0.0,
            mean: float = 0.0,
            std: float = 0.05,
    ) -> None:
        """Initializes a GaussianCellSignal instance."""
        super().__init__(initial_value=initial_value)
        self.mean = mean
        self.std = std
        if self.std <= 0:
            raise ValueError(f"{self.__class__.__name__} std must be > 0.")

    def get_new_value(
            self,
            *args,
            **kwargs,
    ) -> float:
        """Implements the abstract method responsible for getting a new Signal value."""
        return self.normal()

    def normal(self) -> float:
        """Returns a Gaussian value floating around the GaussianCellSignal's current value."""
        if (new_value := self.value + norm.rvs(loc=self.mean, scale=self.std)) > 1.0:
            return 1.0
        elif new_value < -1.0:
            return -1.0
        else:
            return new_value


class EMGaussianCellSignal(CellSignal):
    """Represents a feature which oscillates around a mean, tailed towards the positive end."""
    def __init__(
            self,
            initial_value: float = 0.0,
            mean: float = 0.0,
            std: float = 0.05,
            k: float = 1.0,
    ) -> None:
        """Initializes a GaussianCellSignal instance."""
        super().__init__(initial_value=initial_value)
        self.mean = mean
        self.std = std
        self.k = k

    def get_new_value(
            self,
            *args,
            **kwargs,
    ) -> float:
        """Implements the abstract method responsible for getting a new Signal value."""
        return self.em_normal()

    def em_normal(self) -> float:
        """Returns an exponentially-modified Gaussian value floating around the EMGaussianCellSignal's current value."""
        if (new_value := self.value + exponnorm.rvs(loc=self.mean, scale=self.std, K=self.k)) > 1.0:
            return 1.0
        elif new_value < -1.0:
            return -1.0
        else:
            return new_value


class ConstantCellSignal(CellSignal):
    """Represents a constant feature."""
    def get_new_value(
            self,
            *args,
            **kwargs,
    ) -> float:
        """Implements the abstract method responsible for getting a new Signal value."""
        return self.constant()

    def constant(self) -> float:
        """Returns the constant signal."""
        return self.value


def get_cell_signal(
        name: str = '',
        initial_value: Optional[float] = None,
        period: Optional[float] = None,
        noise: Optional[float] = None,
        stochastic_weight: Optional[float] = None,
        mean: Optional[float] = None,
        std: Optional[float] = None,
        k: Optional[float] = None,
) -> CellSignal:
    """Returns a CellSignal instance, according to the input parameters."""
    name = name or "Gaussian"
    initial_value = initial_value if initial_value is not None else 0.0
    period = period if period is not None else 3600
    noise = noise if noise is not None else 0.2
    stochastic_weight = stochastic_weight if stochastic_weight is not None else 0.5
    mean = mean if mean is not None else 0.0
    std = std if std is not None else 1.0
    k = k if k is not None else 1.0
    signals = {
        'Stochastic': partial(StochasticCellSignal, initial_value=initial_value, noise=noise),
        'Sinusoidal': partial(SinusoidalCellSignal, initial_value=initial_value, period=period),
        'StochasticSinusoidal': partial(
            StochasticSinusoidalCellSignal,
            initial_value=initial_value,
            period=period,
            noise=noise,
            stochastic_weight=stochastic_weight
        ),
        'Gaussian': partial(GaussianCellSignal, initial_value=initial_value, mean=mean, std=std),
        'EMGaussian': partial(EMGaussianCellSignal, initial_value=initial_value, mean=mean, std=std, k=k),
        'Constant': partial(ConstantCellSignal, initial_value=initial_value),
    }
    if name == 'Random':
        name = random.choice(list(signals.keys()))
    if (signal := signals.get(name)) is None:
        raise ValueError(f"Invalid signal type: {name}")
    return signal()
