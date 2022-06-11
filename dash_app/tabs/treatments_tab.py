from __future__ import annotations

import dash
import dash_bootstrap_components as dbc
from dash import dcc, callback, Output, Input, State

from dash_app.components.treatment_curve_selector import TreatmentCurveSelector
from dash_app.utils import get_treatment_curves


def get_treatments_tab() -> dbc.Container:
    """Returns a Container representing the treatments tab."""
    return dbc.Container([
        dbc.Label('Treatments', size='lg'),
        dbc.Row([
            dbc.Col([
                dbc.Button("Add treatment", id='add-treatment-button', class_name='button button-primary'),
            ]),
            dbc.Col([
                dbc.Button("Remove treatment", id='remove-treatment-button', class_name='button button-primary'),
            ]),
        ]),
        dbc.Row(id='treatment-row', children=get_treatment_cols(index=0)),
        dcc.Store(id='treatments-store', data={}),
    ])


def get_treatment_cols(
        index: int,
) -> list[dbc.Col]:
    return [
        dbc.Col(width=6, children=[
            TreatmentCurveSelector(
                curves=get_treatment_curves(),
                aio_id='treatment-curve-selector',
                treatment_index=index,
                curve_type='division',
            )
        ]),
        dbc.Col(width=6, children=[
            TreatmentCurveSelector(
                curves=get_treatment_curves(),
                aio_id='treatment-curve-selector',
                treatment_index=index,
                curve_type='death',
            ),
        ]),
    ]


@callback(
    Output('treatment-row', 'children'),
    Input('add-treatment-button', 'n_clicks'),
    Input('remove-treatment-button', 'n_clicks'),
    State('treatment-row', 'children'),
)
def modify_treatment_rows(
        n_clicks_add: int,
        n_clicks_remove: int,
        current_rows: list[dbc.Col],
) -> list[dbc.Col]:
    """Adds a new Treatment selector to the row Component's children."""
    if (triggered_id := dash.callback_context.triggered_id) is None:
        return current_rows
    elif triggered_id == 'add-treatment-button':
        if n_clicks_add is not None:
            current_rows.extend(get_treatment_cols(index=len(current_rows)))
    elif triggered_id == 'remove-treatment-button':
        if n_clicks_remove is not None and current_rows:
            current_rows.pop()
            current_rows.pop()
    else:
        raise ValueError(f"Unrecognized ID triggered the callback: {dash.callback_context.triggered_id}")
    return current_rows
