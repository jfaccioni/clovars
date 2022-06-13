from __future__ import annotations

import dash
import dash_bootstrap_components as dbc
from dash import dcc, callback, Output, Input, State, ALL

from dash_app.components.treatment_selector import TreatmentSelector
from dash_app.utils import get_treatment_curves


def get_treatments_tab() -> dbc.Container:
    """Returns a Container representing the treatments tab."""
    return dbc.Container([
        dbc.Label('Treatments', size='lg'),
        dbc.Container(id='treatment-container', children=[]),
        dbc.Row([
            dbc.Button("Add treatment", id='add-treatment-button', class_name='button button-primary', size='lg'),
        ], align='end'),
        dcc.Store(id='treatment-regimen-store', data={}),
    ])


def get_treatment_selector(
        index: int,
) -> TreatmentSelector:
    return TreatmentSelector(
        curves=get_treatment_curves(),
        # No AIO_ID in order to keep each instance unique, even if they end up sharing the same index.
        aio_index=index,
    )


@callback(
    Output('treatment-container', 'children'),
    Input('add-treatment-button', 'n_clicks'),
    Input({
        'component': ALL,
        'subcomponent': 'remove-treatment-button',
        'aio_id': ALL,
        'aio_index': ALL,
    }, 'n_clicks'),
    State('treatment-container', 'children'),
)
def modify_treatment_selectors(
        n_clicks_add: int,
        n_clicks_remove: int,
        current_treatments: list[TreatmentSelector],
) -> list[TreatmentSelector]:
    """Adds a new Treatment selector to the row Component's children."""
    if (triggered_id := dash.callback_context.triggered_id) is None:
        return current_treatments
    add_button, remove_buttons = dash.callback_context.inputs_list
    if triggered_id == add_button['id']:
        if n_clicks_add is not None:
            current_treatments.append(get_treatment_selector(index=len(current_treatments)))
    else:
        try:
            index_to_remove = remove_buttons.index(triggered_id)
            current_treatments = current_treatments[:index_to_remove] + current_treatments[index_to_remove+1:]
        except ValueError:
            raise ValueError(f"Unrecognized ID triggered the callback: {dash.callback_context.triggered_id}")
    return current_treatments


@callback(
    Output('treatment-regimen-store', 'data'),
    Input({
        'component': 'TreatmentCurveSelector',
        'subcomponent': 'division-store',
        'aio_id': ALL,
        'aio_index': ALL,
    }, 'data'),
    Input({
        'component': 'TreatmentCurveSelector',
        'subcomponent': 'death-store',
        'aio_id': ALL,
        'aio_index': ALL,
        }, 'data'),
    State('treatment-regimen-store', 'data')
)
def update_treatment_regimen(
        division_treatments_data: list[dict],
        death_treatments_data: list[dict],
        treatment_regimen_data: dict,
) -> dict:
    """Updates the treatment regimen Store whenever a division/death treatment store is modified."""
    # print("DIVISION TREATMENTS:", division_treatments_data)
    # print("DEATH TREATMENTS:", death_treatments_data)
    # print("TREATMENT REGIMEN:", treatment_regimen_data)
    return treatment_regimen_data
