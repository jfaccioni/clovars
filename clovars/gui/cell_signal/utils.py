from __future__ import annotations

from clovars.gui.cell_signal import ParamModel

_VALID_SIGNAL_NAMES = ['Sinusoidal', 'Stochastic', 'SinusoidalStochastic', 'Gaussian', 'EMGaussian', 'Constant']


def _get_params(signal_name: str) -> list[ParamModel] | None:
    """Returns a list of ParamModel instances, given the signal name (returns None if the name is invalid)."""
    if signal_name not in _VALID_SIGNAL_NAMES:
        return None
    return {
        'Sinusoidal': [
            ParamModel(name='Initial value', value=0.0, minimum=-1.0, maximum=1.0, step=0.05),
            ParamModel(name='Period', value=3600.0, minimum=1.0, maximum=1_000_000.0, step=300),
        ],
        'Stochastic': [
            ParamModel(name='Initial value', value=0.0, minimum=-1.0, maximum=1.0, step=0.05),
            ParamModel(name='Noise', value=0.2, minimum=0.0, maximum=1.0, step=0.05),
        ],
        'SinusoidalStochastic': [
            ParamModel(name='Initial value', value=0.0, minimum=-1.0, maximum=1.0, step=0.05),
            ParamModel(name='Period', value=3600.0, minimum=1.0, maximum=1_000_000.0, step=300),
            ParamModel(name='Noise', value=0.2, minimum=0.0, maximum=1.0, step=0.05),
        ],
        'Gaussian': [
            ParamModel(name='Initial value', value=0.0, minimum=-1.0, maximum=1.0, step=0.05),
            ParamModel(name='Mean', value=0.0, minimum=-100.0, maximum=100.0, step=0.05),
            ParamModel(name='Std. dev.', value=0.05, minimum=0.0, maximum=100.0, step=0.05),
        ],
        'EMGaussian': [
            ParamModel(name='Initial value', value=0.0, minimum=-1.0, maximum=1.0, step=0.05),
            ParamModel(name='Mean', value=0.0, minimum=-100.0, maximum=100.0, step=0.05),
            ParamModel(name='Std. dev.', value=0.05, minimum=0.0, maximum=100.0, step=0.05),
            ParamModel(name='K', value=0.01, minimum=0.0, maximum=100.0, step=0.05),
        ],
        'Constant': [
            ParamModel(name='Initial value', value=0.0, minimum=-1.0, maximum=1.0, step=0.05),
        ],
    }[signal_name]
