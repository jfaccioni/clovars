from __future__ import annotations

from typing import Any

import dash_bootstrap_components as dbc
from dash import dcc, callback, Output, Input, State, ALL

from dash_app.components import CollapsableContainer, DivSelectorDropdown, NumericInputGroup
from dash_app.utils import get_dropdown_index


def get_colonies_tab() -> dbc.Container:
    """Returns a Container representing the colonies tab."""
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
    signal_param_types = {
        'Noise': lambda name: NumericInputGroup(name=name, prefix='Noise', value=0.2, min_=0.0, max_=1.0, step=0.05),
        'Period': lambda name: NumericInputGroup(name=name, prefix='Period', value=3600, min_=0.0, max_=1_000_000.0, step=100),
        'Stochastic Weight': lambda name: NumericInputGroup(name=name, prefix='Stochastic weight', value=0.2, min_=0.0, max_=1.0, step=0.05),
        'Mean': lambda name: NumericInputGroup(name=name, prefix='Mean', value=0.0, min_=-1_000.0, max_=1_000.0, step=0.5),
        'Standard Dev.': lambda name: NumericInputGroup(name=name, prefix='Standard deviation', value=0.05, min_=0.0, max_=1_000.0, step=0.05),
        'K': lambda name: NumericInputGroup(name=name, prefix='K', value=1.0, min_=0.0, max_=1_000.0, step=0.05),
    }
    signal_selector_components = {
        'Stochastic': dbc.Container(
            className='signal-param-container',
            children=[
                signal_param_types['Noise']('stoch-noise'),
            ],
        ),
        'Sinusoidal': dbc.Container(
            className='signal-param-container',
            children=[
                signal_param_types['Period']('sin-period'),
            ],
        ),
        'Stochastic-Sinusoidal': dbc.Container(
            className='signal-param-container',
            children=[
                signal_param_types['Noise']('stochsin-noise'),
                signal_param_types['Period']('stochsin-period'),
                signal_param_types['Stochastic Weight']('stochsin-stochweight'),
            ],
        ),
        'Gaussian': dbc.Container(
            className='signal-param-container',
            children=[
                signal_param_types['Mean']('gaussian-mean'),
                signal_param_types['Standard Dev.']('gaussian-std'),
            ],
        ),
        'E.M. Gaussian': dbc.Container(
            className='signal-param-container',
            children=[
                signal_param_types['Mean']('emgaussian-mean'),
                signal_param_types['Standard Dev.']('emgaussian-std'),
                signal_param_types['K']('emgaussian-k'),
            ],
        ),
    }
    return dbc.Container([
        dbc.Label('Cell Parameters', size='lg'),
        dbc.Container([
            NumericInputGroup(name='radius', prefix='Radius:', suffix='µm', **radius_params),
            NumericInputGroup(name='max-speed', prefix='Max Speed:', suffix='µm/s', **max_speed_params),
        ]),
        dbc.Label('Cell Memory', size='lg'),
        CollapsableContainer([
                NumericInputGroup(name='mother-daughter-memory', prefix='Mother/Daughter memory:', **memory_params),
                NumericInputGroup(name='sister-sister-memory', prefix='Sister/Sister memory:', **memory_params),
        ], name='memory', label='Link inheritance', checked=False),
        dbc.Label('Cell Signal', size='lg'),
        DivSelectorDropdown(name='signal', children=signal_selector_components),
        dcc.Store(id='colonies-store', data={})
    ])


# ### PAGE-SPECIFIC CALLBACKS
@callback(
    Output('colonies-store', 'data'),
    # RADIUS
    Input({'type': 'numeric-input-inputbox', 'name': 'radius'}, 'value'),  # radius input
    # MAX SPEED
    Input({'type': 'numeric-input-inputbox', 'name': 'max-speed'}, 'value'),  # max_speed input
    # MEMORY
    Input({'type': 'collapsable-div-checkbox', 'name': 'memory'}, 'value'),  # memory checkbox
    Input({'type': 'numeric-input-inputbox', 'name': 'mother-daughter-memory'}, 'value'),  # mother-daughter mem. input
    Input({'type': 'numeric-input-inputbox', 'name': 'sister-sister-memory'}, 'value'),  # sister-sister mem. input
    # SIGNAL
    Input({'type': 'div-selector-dropdown', 'name': 'signal'}, 'value'),  # Signal name in dropdown
    Input({'type': 'div-selector-child', 'parent-label': ALL, 'name': 'signal'}, 'children'),  # All signal data
    State({'type': 'div-selector-dropdown', 'name': 'signal'}, 'options'),  # Signal options in dropdown
    # STORE
    State('colonies-store', 'data'),
)
def update_colonies_store_parameters(
        radius_value: float | None,
        max_speed_value: float | None,
        memory_checked: bool,
        mother_daughter_memory: float | None,
        sister_sister_memory: float | None,
        signal_name: str | None,
        signal_data: dict,
        signal_options: list[str],
        store_data: dict[str, Any],
) -> dict[str, Any]:
    """Updates the parameters in the colonies store's storage."""
    store_data['radius'] = radius_value
    store_data['max_speed'] = max_speed_value
    store_data['mother_daughter_memory'] = mother_daughter_memory if memory_checked is True else None
    store_data['sister_sister_memory'] = sister_sister_memory if memory_checked is True else None
    store_data['signal'] = signal_label
    store_data['signal_data'] = None
    if signal_label is not None:
        signal_index = get_dropdown_index(dropdown_label=signal_label, dropdown_options=signal_options)
        store_data['signal_data'] = signal_data[signal_index]
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
