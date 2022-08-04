import numpy as np
from scipy.stats import multivariate_normal


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


def get_correlated_values(
        x: float,
        x_mean: float,
        x_std: float,
        y_mean: float,
        y_std: float,
        z_mean: float,
        z_std: float,
        x_y_corr: float,
        x_z_corr: float,
        y_z_corr: float,
) -> tuple[float, float]:
    """
    Given a value x and three correlation values, returns two new values (y and z)
    that have a specific correlation among themselves.
    """
    # SOURCE: https://stats.stackexchange.com/a/437682/325570
    x_var, y_var, z_var = x_std**2, y_std**2, z_std**2
    x_y_covar = x_y_corr * (x_std * y_std)
    x_z_covar = x_z_corr * (x_std * z_std)
    y_z_covar = y_z_corr * (y_std * z_std)
    covariance_matrix = np.array([
        [y_var,     y_z_covar],
        [y_z_covar,     z_var]
    ]) - np.array([
        [x_y_covar**2,          x_y_covar * x_z_covar],
        [x_z_covar * x_y_covar,          x_z_covar**2]
    ]) / x_var
    # Avoid scipy positive-semi-definite warnings (false positives):
    # Source: https://stackoverflow.com/a/41518536/11161432
    if (min_eig := np.min(np.real(np.linalg.eigvals(covariance_matrix)))) < 0:
        covariance_matrix -= 10 * min_eig * np.eye(*covariance_matrix.shape)
    mean_vector = np.array([
        [y_mean],
        [z_mean]
    ]) + np.array([
        [x_y_covar],
        [x_z_covar]
    ]) * (x - x_mean) / x_var
    return multivariate_normal.rvs(mean=mean_vector.ravel(), cov=covariance_matrix)
