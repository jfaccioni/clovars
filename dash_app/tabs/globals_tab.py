from __future__ import annotations

from typing import Any

import dash_bootstrap_components as dbc
from dash import callback, Input, Output, dcc, State

from dash_app.classes import Param
from dash_app.components import NumericInputGroup


def get_globals_tab() -> dbc.Container:
    """Returns a Container representing the globals tab."""
    return dbc.Container([
        dbc.Label('Simulation time', size='lg'),
        get_time_controls(),
        dbc.Label('Early stopping', size='lg'),
        get_early_stopping_controls(),
        dcc.Store(id='globals-store', data={})
    ])


def get_time_controls() -> dbc.Container:
    """Returns a Container with the simulation time parameters (delta/frames)."""
    frames = Param(name='frames', value=144, min_=0, max_=10_000, step=1)
    delta = Param(name='delta', value=3600, min_=0, max_=10_000, step=60)
    return dbc.Container([
        NumericInputGroup(
            name='frame',
            prefix='Run for:',
            suffix='frames',
            input_kwargs=frames.to_dict(),
        ),
        NumericInputGroup(
            name='delta',
            prefix='Delta between frames:',
            suffix='seconds',
            input_kwargs=delta.to_dict(),
        ),
        dbc.Label(id='time-label', children="", className='time-label note secondary text-secondary'),
    ])


def get_early_stopping_controls() -> dbc.Container:
    """Returns a Container with the simulation early stopping parameters (one colony / all colonies)."""
    colony_one = Param(name='colony-one', value=100, min_=0, max_=10_000, step=1)
    colony_all = Param(name='colony-all', value=50, min_=0, max_=10_000, step=1)
    return dbc.Container([
        NumericInputGroup(
            name='colony-one',
            prefix='Stop when a colony reaches:',
            suffix='cells',
            with_checkbox=True,
            input_kwargs=colony_one.to_dict(),
        ),
        NumericInputGroup(
            name='colony-all',
            prefix='Stop when all colonies reach:',
            suffix='cells',
            with_checkbox=True,
            input_kwargs=colony_all.to_dict(),
        ),
    ])


@callback(
    Output('time-label', 'children'),
    Input({'type': 'numeric-input-inputbox', 'name': 'delta'}, 'value'),
    Input({'type': 'numeric-input-inputbox', 'name': 'frame'}, 'value'),
)
def set_total_runtime_label(
        delta: int,
        frames: int | None,
) -> str:
    """Updates the label of the total simulation time, whenever the delta/frames parameters change."""
    if frames is None or delta is None:
        return ""
    else:
        total_seconds = (delta * frames)
        total_hours = total_seconds / (60 * 60)
        total_days = total_hours / 24
        return f"Simulation will run for {round(total_hours, 2)} hours ({round(total_days, 2)} days)"


@callback(
    Output('globals-store', 'data'),
    Input({'type': 'numeric-input-inputbox', 'name': 'frame'}, 'value'),  # frame input
    Input({'type': 'numeric-input-inputbox', 'name': 'delta'}, 'value'),  # delta input
    Input({'type': 'numeric-input-inputbox', 'name': 'colony-one'}, 'value'),  # colony-one input
    Input({'type': 'numeric-input-inputbox', 'name': 'colony-one'}, 'disabled'),  # colony-one toggle
    Input({'type': 'numeric-input-inputbox', 'name': 'colony-all'}, 'value'),  # colony-all input
    Input({'type': 'numeric-input-inputbox', 'name': 'colony-all'}, 'disabled'),  # colony-all toggle
    State('globals-store', 'data'),
)
def update_globals_store_parameters(
        frame_value: int,
        delta_value: int,
        colony_one_value: int,
        colony_one_disabled: bool,
        colony_all_value: int,
        colony_all_disabled: bool,
        store_data: dict[str, Any],
) -> dict[str, Any]:
    """Updates the parameters in the globals store's storage."""
    store_data['frame'] = frame_value
    store_data['delta'] = delta_value
    store_data['colony_one'] = None if colony_one_disabled else colony_one_value
    store_data['colony_all'] = None if colony_all_disabled else colony_all_value
    return store_data
