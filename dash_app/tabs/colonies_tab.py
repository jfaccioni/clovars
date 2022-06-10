from __future__ import annotations

from typing import Any

import dash_bootstrap_components as dbc
from dash import dcc, State, Input, Output, callback

from dash_app.utils import get_signals
from dash_app.classes import Param
from dash_app.components import CollapsableContainer, NumericInputGroup, SignalSelector


def get_colonies_tab() -> dbc.Container:
    """Returns a Container representing the colonies tab."""
    radius = Param(name='radius', value=20, min_=0, max_=1_000, step=0.5)
    max_speed = Param(name='Max Speed', value=0.02, min_=0, max_=10, step=0.01)
    memory = Param(name='Memory', value=0.2, min_=0, max_=1, step=0.05)
    return dbc.Container([
        dbc.Label('Cell Parameters', size='lg'),
        dbc.Container([
            NumericInputGroup(name='radius', prefix='Radius:', suffix='µm', input_kwargs=radius.to_dict()),
            NumericInputGroup(name='max-speed', prefix='Max Speed:', suffix='µm/s', input_kwargs=max_speed.to_dict()),
        ]),
        dbc.Label('Cell Memory', size='lg'),
        CollapsableContainer([
                NumericInputGroup(
                    name='mother-daughter-memory',
                    prefix='Mother/Daughter memory:',
                    input_kwargs=memory.to_dict(),
                ),
                NumericInputGroup(
                    name='sister-sister-memory',
                    prefix='Sister/Sister memory:',
                    input_kwargs=memory.to_dict(),
                ),
        ], name='memory', label='Link inheritance', checked=False),
        dbc.Label('Cell Signal', size='lg'),
        SignalSelector(signals=get_signals(), aio_id='colonies-signal-selector'),
        dcc.Store(id='colonies-store', data={}),
    ])


# ### PAGE-SPECIFIC CALLBACKS
@callback(
    Output('colonies-store', 'data'),
    Input({'type': 'numeric-input-inputbox', 'name': 'radius'}, 'value'),  # radius input
    Input({'type': 'numeric-input-inputbox', 'name': 'max-speed'}, 'value'),  # max_speed input
    Input({'type': 'collapsable-div-checkbox', 'name': 'memory'}, 'value'),  # memory checkbox
    Input({'type': 'numeric-input-inputbox', 'name': 'mother-daughter-memory'}, 'value'),  # md-dd memory input
    Input({'type': 'numeric-input-inputbox', 'name': 'sister-sister-memory'}, 'value'),  # sis-sis memory input
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
