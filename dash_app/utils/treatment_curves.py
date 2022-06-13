from __future__ import annotations

import numpy as np
import plotly.graph_objs as go

from clovars.scientific import get_curve
from dash_app.classes import Param, Curve


def get_treatment_curves() -> list[Curve]:
    """Returns a list of Curve instances used when defining possible Treatment Curves."""
    return [
        Curve(name='Gaussian', params=[
            Param('Mean', value=36, min_=0, max_=200, step=0.25),
            Param('Std',  value=12, min_=0, max_=200, step=0.01),
        ]),
        Curve(name='EM Gaussian', params=[
            Param('Mean', value=12.75, min_=0, max_=200, step=0.25),
            Param('Std',  value=8.50, min_=0, max_=200, step=0.01),
            Param('K',    value=2.87, min_=0, max_=10,  step=0.01),
        ]),
        Curve(name='Gamma', params=[
            Param('Mean', value=16.25, min_=0, max_=200, step=0.25),
            Param('Std',  value=2.84,  min_=0, max_=200, step=0.01),
            Param('a',    value=3.82,  min_=0, max_=10,  step=0.01),
        ]),
        Curve(name='Lognormal', params=[
            Param('Mean', value=21,  min_=0, max_=200, step=0.25),
            Param('Std',  value=5.5, min_=0, max_=200, step=0.01),
            Param('s',    value=1,   min_=0, max_=10,  step=0.01),
        ]),
    ]


def draw_treatment_curve(
        curve_type: str,
        curve_params: dict[str, str | float],
) -> go.Figure:
    """Draws the Curve onto a plotly plot using CloVarS Curve objects."""
    color = {
        "division": "#029E73",
        "death": '#DE8F05',
    }[curve_type.lower()]
    fillcolor = {
        "division": "#52EEC3",
        "death": '#FFDF55',
    }[curve_type.lower()]
    xlim = 200
    curve = get_curve(**curve_params)
    x = np.linspace(0, xlim, 1_000)
    y = curve.pdf(x)
    fig = go.Figure(
        data=go.Scatter(
            x=x,
            y=y,
            mode='lines',
            line={'color': color, 'width': 5},
            fill='tozeroy',
            fillcolor=fillcolor,
            name=f'{curve_type.capitalize()} curve',
        ),
        layout={
            'xaxis': {'range': [0, xlim]},
            'legend': {'title': 'Curves'}
        },
    )
    return fig
