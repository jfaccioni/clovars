from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import dash_bootstrap_components as dbc
from dash import html, dcc, callback, Output, Input, State

from components import NumericInputGroup


def get_colonies_tab() -> html.Div:
    """Returns a html div representing the colonies tab."""
    colonies_card = dbc.Card([
        dbc.Label('Cell Parameters', size='lg'),
        html.Br(),
        html.Div([
            dbc.Label('Radius', size='md'),
            NumericInputGroup(name='radius', suffix='µm', value=20.0, min_=0.0, max_=1_000, step=0.5),
        ]),
        html.Div([
            dbc.Label('Max Speed', size='md'),
            NumericInputGroup(name='max-speed', suffix='µm/s', value=0.02, min_=0.0, max_=10.0, step=0.01),
        ]),
        html.Br(),
        dbc.Label('Cell Memory', size='lg'),
        # html.Br(),
        # html.Div([
        #     checkbox := dbc.Checkbox(label='Linked inheritance'),
        #     dbc.Row([
        #         dbc.Col([
        #             md_collapse := dbc.Collapse([
        #                 dbc.Label('mother-daughter'),
        #                 dbc.Input(type="number", placeholder='...', value=0.5, min=0.0, max=1.0, step=0.05),
        #             ], is_open=False),
        #         ]),
        #         dbc.Col([
        #             ss_collapse := dbc.Collapse([
        #                 dbc.Label('sister-sister'),
        #                 dbc.Input(type="number", placeholder='...', value=0.5, min=0.0, max=1.0, step=0.05),
        #             ], is_open=False),
        #         ]),
        #     ]),
        # ]),
        # html.Br(),
        # dbc.Label('Cell Signal', size='lg'),
        # html.Br(),
        # get_signal_controller(),
    ], body=True)

    # TODO: replace html.Br with actual CSS and classes for each html element

    # @dash.callback(
    #     Output(md_collapse, 'is_open'),
    #     Output(ss_collapse, 'is_open'),
    #     Input(checkbox, 'value'),
    # )
    # def open_collapsable_boxes(checkbox_is_checked: bool) -> tuple[bool, bool]:
    #     return checkbox_is_checked, checkbox_is_checked

    return html.Div([colonies_card, dcc.Store(id='colonies-store', data={})])


@callback(
    Output('colonies-store', 'data'),
    Input({'type': 'numeric-input-inputbox', 'name': 'radius'}, 'value'),  # radius input
    Input({'type': 'numeric-input-inputbox', 'name': 'max-speed'}, 'value'),  # max_speed input
    State('colonies-store', 'data'),
)
def update_globals_store_parameters(
        radius_value: float,
        max_speed_value: float,
        store_data: dict[str, Any],
) -> dict[str, Any]:
    """Updates the parameters in the globals store's storage."""
    store_data['radius'] = radius_value
    store_data['max_speed'] = max_speed_value
    return store_data


@dataclass
class Param:
    name: str
    value: float
    min_: float | None = None
    max_: float | None = None
    step_: float | None = None

    def __post_init__(self) -> None:
        if self.min_ is not None and self.value < self.min_:
            raise ValueError(f'Value {self.value} cannot be lower than minimal value ({self.min_})')
        elif self.max_ is not None and self.value > self.max_:
            raise ValueError(f'Value {self.value} cannot be higher than maximal value ({self.max_})')


@dataclass
class Signal:
    name: str
    initial_value: float
    params: list[Param]

    def __post_init__(self) -> None:
        if not 0.0 <= self.initial_value <= 1.0:
            raise ValueError(f'Initial value {self.initial_value} must be in the [0, 1] interval.')


_PARAMS = [
    _noise := Param('Noise', 0.2, min_=0.0, max_=1.0, step_=0.05),
    _period := Param('Period', 3600, min_=0.0, step_=3600),
    _stochastic_weight := Param('Stochastic Weight', 0.2, min_=0.0, max_=1.0, step_=0.05),
    _mean := Param('Mean', 0.0, step_=0.05),
    _std := Param('Standard Deviation', 0.05, min_=0.0, step_=0.05),
    _k := Param('K', 1.0, min_=0.0, step_=0.05),
]

_SIGNALS = {
    'Stochastic': Signal('Stochastic', 0.0, params=[_noise]),
    'Sinusoidal': Signal('Sinusoidal', 0.0, params=[_period]),
    'Stochastic-Sinusoidal': Signal('Stochastic-Sinusoidal', 0.0, params=[_noise, _period, _stochastic_weight]),
    'Gaussian': Signal('Gaussian', 0.0, params=[_mean, _std]),
    'EM Gaussian': Signal('EM Gaussian', 0.0, params=[_mean, _std, _k]),
}


def get_signal_controller() -> html.Div:
    component = html.Div([
        dcc.Dropdown([s.name for s in _SIGNALS.values()], className='dash-simplex'),
        dbc.Row([])
    ])

    # @dash.callback(
    #     Output(params, 'children'),
    #     Input(dropdown, 'value'),
    # )
    # def select_curve_params(dropdown_value: str | None) -> list[dbc.Col] | None:
    #     if (signal := _SIGNALS.get(dropdown_value)) is None:
    #         return None
    #     return [
    #         dbc.Col([
    #             dbc.Label(p.name),
    #             dbc.Input(type="number", placeholder='...', value=p.value, min=p.min_, max=p.max_, step=p.step_),
    #         ], md=6)
    #         for p in _PARAMS
    #         if p in signal.params
    #     ]

    return component
