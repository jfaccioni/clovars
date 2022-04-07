from __future__ import annotations

from scipy.stats import norm

from clovars.scientific import reflect_around_interval


def brownian_motion(
        current_value: float,
        scale: float,
) -> float:
    """Simulates a brownian motion of the current value, scaled by a given factor."""
    fluctuation = norm.rvs(loc=0, scale=(1 - scale) ** 2)
    return current_value + fluctuation


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
