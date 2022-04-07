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
