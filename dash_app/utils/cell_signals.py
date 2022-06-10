from __future__ import annotations

from typing import TYPE_CHECKING

import numpy as np
import pandas as pd
import plotly.express as px

from clovars.scientific import get_cell_signal
from dash_app.classes import Param, Signal

if TYPE_CHECKING:
    import plotly.graph_objs as go


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


def draw_signal(signal_params: dict[str, str | float]) -> go.Figure:
    size = 100
    repeats = 5
    delta = 1800  # seconds
    xs = np.arange(size)
    dfs = []
    for r in range(repeats):
        signal = get_cell_signal(**signal_params)
        values = []
        for i in range(size):
            values.append(signal.value)
            signal.oscillate(current_seconds=i*delta)
        dfs.append(pd.DataFrame({
            'iteration': xs,
            'signal': values,
            'sample': r+1,
        }))
    data = pd.concat(dfs, ignore_index=True)
    data['signal'] = data['signal'].clip(lower=-1.0, upper=1.0)
    return px.line(
        data_frame=data,
        x='iteration',
        y='signal',
        color='sample',
        title=f'Sample signals<br><sup>Δt between iterations: {round(delta/60, 2)} min</sup>',
        range_x=[0, size],
        range_y=[-1, 1],
    )
