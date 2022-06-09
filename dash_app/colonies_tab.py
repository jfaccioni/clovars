from __future__ import annotations

from typing import Any

import dash_bootstrap_components as dbc
from dash import dcc, State, Input, Output, callback

from dash_app.cell_signals import get_signals
from dash_app.components import CollapsableContainer, NumericInputGroup, SignalSelector


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
        SignalSelector(signals=get_signals(), aio_id='colonies-signal-selector'),
        dcc.Store(id='colonies-store', data={}),
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
    Input(
        {'type': 'numeric-input-inputbox', 'name': 'mother-daughter-memory'}, 'value'),  # mother-daughter mem. input
    Input({'type': 'numeric-input-inputbox', 'name': 'sister-sister-memory'}, 'value'),  # sister-sister mem. input
    # STATES
    State('colonies-store', 'data'),
)
def update_colonies_store_parameters(
        radius_value: float | None,
        max_speed_value: float | None,
        memory_checked: bool,
        mother_daughter_memory: float | None,
        sister_sister_memory: float | None,
        store_data: dict[str, Any],
) -> dict[str, Any]:
    """Updates the parameters in the colonies store's storage."""
    store_data['radius'] = radius_value
    store_data['max_speed'] = max_speed_value
    store_data['mother_daughter_memory'] = mother_daughter_memory if memory_checked is True else None
    store_data['sister_sister_memory'] = sister_sister_memory if memory_checked is True else None
    return store_data
