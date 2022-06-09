from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

import numpy as np
import pandas as pd
import plotly.express as px
from scipy.stats import norm, exponnorm

if TYPE_CHECKING:
    import plotly.graph_objs as go


@dataclass
class Param:
    name: str
    value: float
    min_: float
    max_: float
    step: float

    def to_dict(self) -> dict:
        return {
            'value': self.value,
            'min': self.min_,
            'max': self.max_,
            'step': self.step,
        }


@dataclass
class Signal:
    name: str
    params: list[Param]


def get_signals() -> list[Signal]:
    """Returns a list of Signal instances used when defining possible Cell Signals."""
    return [
        Signal(name='Gaussian', params=[
            Param('Mean', value=0,    min_=-10, max_=10, step=0.05),
            Param('Std',  value=0.05, min_=0,   max_=10, step=0.01),
        ]),
        Signal(name='EM Gaussian', params=[
            Param('Mean', value=0,    min_=-10, max_=10, step=0.05),
            Param('Std',  value=0.05, min_=0,   max_=10, step=0.01),
            Param('K',    value=0.1,  min_=0,   max_=10, step=0.01),
        ]),
        Signal(name='Sinusoidal', params=[
            Param('Period', value=3_600, min_=100, max_=1_000_000, step=100),
        ]),
        Signal(name='Stochastic', params=[
            Param('Noise', value=0.2, min_=0, max_=1, step=0.01),
        ]),
        Signal(name='Stochastic-Sinusoidal', params=[
            Param('Period',            value=3_600, min_=100, max_=1_000_000, step=100),
            Param('Noise',             value=0.2,   min_=0,   max_=1,         step=0.01),
            Param('Stochastic Weight', value=0.2,   min_=0,   max_=1,         step=0.01),
        ]),
    ]


def draw_signal(signal_params: dict[str, float]) -> go.Figure:
    size = 100
    repeats = 5
    xs = np.arange(size)
    dfs = []
    for r in range(repeats):
        if (signal_type := signal_params['type']) == 'Gaussian':
            ys = norm(loc=signal_params['mean'], scale=signal_params['std']).rvs(size).cumsum()
        elif signal_params['type'] == 'EM Gaussian':
            ys = exponnorm(loc=signal_params['mean'], scale=signal_params['std'], K=signal_params['k']).rvs(size).cumsum()
        else:
            raise ValueError(f"Bad curve type: {signal_type}")
        dfs.append(pd.DataFrame({
            'iteration': xs,
            'signal': ys,
            'repeat': r,
        }))
    data = pd.concat(dfs, ignore_index=True)
    data['signal'] = data['signal'].clip(lower=-1.0, upper=1.0)
    return px.line(data_frame=data, x='iteration', y='signal', color='repeat')
