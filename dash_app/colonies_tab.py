from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import dash_bootstrap_components as dbc
from dash import html, dcc, callback, Output, Input, State, MATCH, ALL

from components import NumericInputGroup, CollapsableDiv, DivSelectorDropdown
from dash_app.utils import get_dropdown_label_from_index


def get_colonies_tab() -> html.Div:
    """Returns a html div representing the colonies tab."""
    radius_params = {
        'value': 20.0,
        'min_': 0.0,
        'max_': 1_000,
        'step': 0.5,
    }
    max_speed_params = {
        'value': 0.02,
        'min_': 0.0,
        'max_': 10.0,
        'step': 0.01,
    }
    memory_params = {
        'value': 0.2,
        'min_': 0.0,
        'max_': 1.0,
        'step': 0.05,
    }
    colonies_card = dbc.Card([
        dbc.Label('Cell Parameters', size='lg'),
        html.Br(),
        html.Div([NumericInputGroup(name='radius', prefix='Radius:', suffix='µm', **radius_params)]),
        html.Br(),
        html.Div([NumericInputGroup(name='max-speed', prefix='Max Speed:', suffix='µm/s', **max_speed_params)]),
        html.Br(),
        dbc.Label('Cell Memory', size='lg'),
        html.Br(),
        CollapsableDiv([
                NumericInputGroup(name='mother-daughter-memory', prefix='Mother/Daughter memory:', **memory_params),
                html.Br(),
                NumericInputGroup(name='sister-sister-memory', prefix='Sister/Sister memory:', **memory_params),
        ], name='memory', label='Link inheritance', checked=False),
        html.Br(),
        dbc.Label('Cell Signal', size='lg'),
        html.Br(),
        # get_signal_controller(),
        DivSelectorDropdown({
            'Stochastic': html.Div('Stochastic Data'),
            'Sinusoidal': html.Div('Sinusoidal Data'),
            'Stochastic-Sinusoidal': html.Div('Stochastic-Sinusoidal Data'),
            'Gaussian': html.Div('Gaussian Data'),
            'EM Gaussian': html.Div('EM Gaussian Data'),
        }, name='signal'),
    ], body=True)
    return html.Div([colonies_card, dcc.Store(id='colonies-store', data={})])


# ### CALLBACKS

@callback(
    Output({'type': 'collapsable-div-collapse', 'name': MATCH}, 'is_open'),
    Input({'type': 'collapsable-div-checkbox', 'name': MATCH}, 'value'),
)
def toggle_collapsable_div(checkbox_checked: bool) -> bool:
    """Opens the collapsable div whenever its checkbox is checked."""
    return checkbox_checked


@callback(
    Output('colonies-store', 'data'),
    Input({'type': 'numeric-input-inputbox', 'name': 'radius'}, 'value'),  # radius input
    Input({'type': 'numeric-input-inputbox', 'name': 'max-speed'}, 'value'),  # max_speed input
    Input({'type': 'collapsable-div-checkbox', 'name': 'memory'}, 'value'),  # memory checkbox
    Input({'type': 'numeric-input-inputbox', 'name': 'mother-daughter-memory'}, 'value'),  # mother-daughter mem. input
    Input({'type': 'numeric-input-inputbox', 'name': 'sister-sister-memory'}, 'value'),  # sister-sister mem. input
    Input({'type': 'div-selector-dropdown', 'name': 'signal'}, 'value'),  # Signal index in dropdown
    Input({'type': 'div-selector-child', 'parent-label': ALL, 'name': 'signal'}, 'children'),  # All signal data
    State({'type': 'div-selector-dropdown', 'name': 'signal'}, 'options'),  # Signal options in dropdown
    State('colonies-store', 'data'),
)
def update_colonies_store_parameters(
        radius_value: float,
        max_speed_value: float,
        memory_checked: bool,
        mother_daughter_memory: float,
        sister_sister_memory: float,
        signal_index: int | None,
        signal_data: list[str],
        signal_options: list[dict[str, str | int | None]],
        store_data: dict[str, Any],
) -> dict[str, Any]:
    """Updates the parameters in the colonies store's storage."""
    store_data['radius'] = radius_value
    store_data['max_speed'] = max_speed_value
    store_data['mother_daughter_memory'] = mother_daughter_memory if memory_checked is True else None
    store_data['sister_sister_memory'] = sister_sister_memory if memory_checked is True else None
    if signal_index is not None:
        signal_name = get_dropdown_label_from_index(dropdown_index=signal_index, dropdown_options=signal_options)
        store_data['signal'] = signal_name
        store_data['signal_data'] = signal_data[signal_index]
    else:
        store_data['signal'] = None
        store_data['signal_data'] = None
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
