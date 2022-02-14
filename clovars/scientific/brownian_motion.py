from __future__ import annotations

from scipy.stats import norm


def bounded_brownian_motion(
        current_value: float,
        scale: float,
        lower_bound: float = 0.0,
        upper_bound: float = 1.0,
) -> float:
    """Bounds the result of a brownian motion by reflecting it back into the interval bounds."""
    new_value = brownian_motion(current_value=current_value, scale=scale)
    bounded_new_value = reflect_around_interval(x=new_value, lower_bound=lower_bound, upper_bound=upper_bound)
    return bounded_new_value


def brownian_motion(
        current_value: float,
        scale: float,
) -> float:
    """Simulates a brownian motion of the current value, scaled by a given factor."""
    fluctuation = norm.rvs(loc=0, scale=(1 - scale) ** 2)
    return current_value + fluctuation


def reflect_around_interval(
        x: float,
        lower_bound: float,
        upper_bound: float,
) -> float:
    """Reflects the value x around an interval delimited by [lower_bound, upper_bound]."""
    interval = (upper_bound - lower_bound)
    period = 2 * interval
    amplitude = interval / 2
    shift = lower_bound + amplitude
    return triangular_wave(x=x-shift, period=period, amplitude=amplitude) + shift


def triangular_wave(x, period, amplitude):
    """
    Returns a triangular wave evaluated at x, given its period and amplitude.
    Equation source: https://en.wikipedia.org/wiki/Triangle_wave
    """
    return (4*amplitude/period) * abs(((x - period/4) % period) - period/2) - amplitude
