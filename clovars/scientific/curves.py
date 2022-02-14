from __future__ import annotations

import random
from functools import partial
from typing import Optional, TYPE_CHECKING

import matplotlib.pyplot as plt
import numpy as np
from scipy.stats import exponnorm, norm, gamma, lognorm

if TYPE_CHECKING:
    from .sctypes import Curve, Numeric


class AbstractCurve:
    """Class representing a gaussian curve."""
    def __init__(self) -> None:
        """Initializes a Gaussian instance."""
        self.curve: Curve = norm()  # placeholder

    def __call__(self, x: Optional[Numeric]) -> float:
        """
        Implements the call interface for AbstractCurve instances by returning the CDF of the underlying curve
        (i.e. allows for the syntax "curve(x)" to be used).
        """
        return self.cdf(x)

    def draw_many(
            self,
            size: int = 1
    ) -> np.ndarray:
        """Draws multiple random numbers from the AbstractCurve's PDF and returns them as a numpy array."""
        return self.curve.rvs(size=size)

    def draw(self) -> float:
        """Draws a single random number from the AbstractCurve's PDF and returns it."""
        return self.draw_many(size=1).item()

    def cdf(self, x: Optional[Numeric]) -> float:
        """Returns the cumulative density function of the AbstractCurve evaluated at the given point X."""
        return self.curve.cdf(x)

    def pdf(self, x: Optional[Numeric]) -> float:
        """Returns the point density function of the AbstractCurve evaluated at the given point X."""
        return self.curve.pdf(x)

    def plot_cdf(
            self,
            x_min: int = -25,
            x_max: int = 200,
            x_steps: int = 1000,
            ax: plt.Axes = None,
            *args,
            **kwargs,
    ) -> plt.Axes:
        """
        Returns an ax with the AbstractCurve plotted in it. Any additional arguments and keyword arguments
        are passed onto matplotlib.pyplot.plot.
        """
        if ax is None:
            ax = plt.gca()
        xs = np.linspace(x_min, x_max, x_steps)
        ys = self(xs)
        ax.plot(xs, ys, *args, **kwargs)
        return ax

    def plot_pdf(
            self,
            x_min: int = -25,
            x_max: int = 200,
            x_steps: int = 1000,
            ax: plt.Axes = None,
            *args,
            **kwargs,
    ) -> plt.Axes:
        """
        Returns an ax with the AbstractCurve plotted in it. Any additional arguments and keyword arguments
        are passed onto matplotlib.pyplot.plot.
        """
        if ax is None:
            ax = plt.gca()
        xs = np.linspace(x_min, x_max, x_steps)
        ys = self.curve.pdf(xs)
        ax.plot(xs, ys, *args, **kwargs)
        return ax


class Gaussian(AbstractCurve):
    """Class representing a gaussian curve."""
    def __init__(
            self,
            loc: float = 0.0,
            scale: float = 1.0,
    ) -> None:
        """Initializes a Gaussian instance."""
        super().__init__()
        self.curve = norm(loc=loc, scale=scale)


class EMGaussian(AbstractCurve):
    """
    Class representing an exponentially-modified gaussian curve
    (more info: https://en.wikipedia.org/wiki/Exponentially_modified_Gaussian_distribution).
    """
    def __init__(
            self,
            k: float = 1.0,
            loc: float = 0.0,
            scale: float = 1.0,
    ) -> None:
        """Initializes an EMGaussian instance."""
        super().__init__()
        self.curve = exponnorm(K=k, loc=loc, scale=scale)


class Gamma(AbstractCurve):
    """
    Class representing a gamma curve
    (more info: https://en.wikipedia.org/wiki/Gamma_distribution).
    """
    def __init__(
            self,
            a: float = 1.0,
            loc: float = 0.0,
            scale: float = 1.0,
    ) -> None:
        """Initializes a Gamma instance."""
        super().__init__()
        self.curve = gamma(a=a, loc=loc, scale=scale)


class Lognormal(AbstractCurve):
    """
    Class representing a lognormal curve
    (more info: https://en.wikipedia.org/wiki/Gamma_distribution).
    """
    def __init__(
            self,
            s: float = 1.0,
            loc: float = 0.0,
            scale: float = 1.0,
    ) -> None:
        """Initializes a Gamma instance."""
        super().__init__()
        self.curve = lognorm(s=s, loc=loc, scale=scale)


def get_curve(
        name: str = '',
        mean: Optional[float] = None,
        std: Optional[float] = None,
        k: Optional[float] = None,
        a: Optional[float] = None,
        s: Optional[float] = None,
) -> Curve:
    """Returns a Curve instance, according to the input parameters."""
    name = name or "Gaussian"
    mean = mean if mean is not None else 0.0
    std = std if std is not None else 1.0
    k = k if k is not None else 1.0
    a = a if a is not None else 1.0
    s = s if s is not None else 1.0
    curves = {
        'Gaussian': partial(Gaussian, loc=mean, scale=std),
        'EMGaussian': partial(EMGaussian, loc=mean, scale=std, k=k),
        'Gamma': partial(Gamma, loc=mean, scale=std, a=a),
        'Lognormal': partial(Lognormal, loc=mean, scale=std, s=s),
    }
    if name == 'Random':
        name = random.choice(list(curves.keys()))
    if (curve := curves.get(name)) is None:
        raise ValueError(f"Invalid curve type: {name}")
    return curve()
