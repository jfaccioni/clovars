from __future__ import annotations

from typing import Any

import dash_bootstrap_components as dbc
from dash import callback, html, Input, Output, dcc, State

from components import NumericInputGroup


def get_globals_tab() -> html.Div:
    """Returns a html div representing the globals tab."""
    delta_params = {
        'value': 3600,
        'min_': 0,
        'max_': 10_000,
        'step': 100,
    }
    frame_params = {
        'value': 144,
        'min_': 0,
        'max_': 10_000,
        'step': 1,
    }
    colony_one_params = {
        'value': 100,
        'min_': 0,
        'max_': 10_000,
        'step': 1,
    }
    colony_all_params = {
        'value': 50,
        'min_': 0,
        'max_': 10_000,
        'step': 1,
    }
    globals_card = dbc.Card([
        html.Div([dbc.Label('Simulation time', size='lg')]),
        html.Br(),
        get_time_controls(delta_params=delta_params, frame_params=frame_params),
        html.Br(),
        html.Div([dbc.Label('Early stopping', size='lg')]),
        html.Br(),
        get_early_stopping_controls(colony_one_params=colony_one_params, colony_all_params=colony_all_params),
    ])
    return html.Div([globals_card, dcc.Store(id='globals-store', data={})])


def get_time_controls(
        delta_params: dict | None = None,
        frame_params: dict | None = None,
) -> html.Div:
    """Returns a html div with the simulation time parameters (delta/frames)."""
    delta_params = delta_params or {}
    frame_params = frame_params or {}
    return html.Div([
        NumericInputGroup(
            name='delta',
            prefix='Delta between frames:',
            suffix='seconds',
            **delta_params,
        ),
        html.Br(),
        NumericInputGroup(
            name='frame',
            prefix='Run for:',
            suffix='frames',
            **frame_params,
        ),
        dbc.Label(id='time-label', children=""),
    ])


def get_early_stopping_controls(
        colony_one_params: dict | None = None,
        colony_all_params: dict | None = None,
) -> html.Div:
    """Returns a html div with the simulation early stopping parameters (one colony / all colonies)."""
    colony_one_params = colony_one_params or {}
    colony_all_params = colony_all_params or {}
    return html.Div([
        NumericInputGroup(
            name='colony-one',
            prefix='Stop when a colony reaches:',
            suffix='cells',
            with_checkbox=True,
            **colony_one_params,
        ),
        html.Br(),
        NumericInputGroup(
            name='colony-all',
            prefix='Stop when all colonies reach:',
            suffix='cells',
            with_checkbox=True,
            **colony_all_params,
        ),
    ])


# ### PAGE-SPECIFIC CALLBACKS
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
    Input({'type': 'numeric-input-inputbox', 'name': 'delta'}, 'value'),  # delta input
    Input({'type': 'numeric-input-inputbox', 'name': 'frame'}, 'value'),  # frame input
    Input({'type': 'numeric-input-inputbox', 'name': 'colony-one'}, 'value'),  # colony-one input
    Input({'type': 'numeric-input-inputbox', 'name': 'colony-one'}, 'disabled'),  # colony-one toggle
    Input({'type': 'numeric-input-inputbox', 'name': 'colony-all'}, 'value'),  # colony-all input
    Input({'type': 'numeric-input-inputbox', 'name': 'colony-all'}, 'disabled'),  # colony-all toggle
    State('globals-store', 'data'),
)
def update_globals_store_parameters(
        delta_value: int,
        frame_value: int,
        colony_one_value: int,
        colony_one_disabled: bool,
        colony_all_value: int,
        colony_all_disabled: bool,
        store_data: dict[str, Any],
) -> dict[str, Any]:
    """Updates the parameters in the globals store's storage."""
    store_data['delta'] = delta_value
    store_data['frame'] = frame_value
    store_data['colony_one'] = None if colony_one_disabled else colony_one_value
    store_data['colony_all'] = None if colony_all_disabled else colony_all_value
    return store_data
