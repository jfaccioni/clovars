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
    store_data['signal'] = signal_name
    store_data['signal_data'] = None
    if signal_name is not None:
        signal_index = get_dropdown_index(dropdown_value=signal_name, dropdown_options=signal_options)
        store_data['signal_data'] = parse_signal_parameters(data=signal_data[signal_index])  # TODO: values are not updated!
    return store_data


def parse_signal_parameters(data: dict) -> dict:
    """Parses the data dictionary into the desired structure for the signal's parameters."""
    result = {}
    for container_data in data:
        label_data, inputbox_data = container_data['props']['children']
        parameter_name = label_data['props']['children']
        parameter_value = inputbox_data['props']['value']
        result[parameter_name] = parameter_value
    return result
