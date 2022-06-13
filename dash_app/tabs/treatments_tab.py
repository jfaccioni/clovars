from __future__ import annotations

import dash
import dash_bootstrap_components as dbc
from dash import dcc, callback, Output, Input, State, ALL

from dash_app.components.treatment_selector import TreatmentSelector


def get_treatments_tab() -> dbc.Container:
    """Returns a Container representing the treatments tab."""
    return dbc.Container([
        dbc.Label('Treatments', size='lg'),
        dbc.Container(id='treatment-container', children=[]),
        dbc.Row(align='end', children=[
            dbc.Button("Add treatment", id='add-treatment-button', class_name='button button-primary', size='lg'),
        ]),
        dcc.Store(id='treatment-regimen-store', data={}),
    ])


@callback(
    Output('treatment-container', 'children'),
    Input('add-treatment-button', 'n_clicks'),
    Input({'component': 'TreatmentSelector', 'subcomponent': 'remove-treatment-button', 'aio_id': ALL}, 'n_clicks'),
    State('treatment-container', 'children'),
)
def modify_treatment_selectors(
        _: int,
        __: int,
        current_treatments: list[TreatmentSelector],
) -> list[TreatmentSelector]:
    """Adds a new Treatment selector to the row Component's children."""
    # No button clicked
    if (triggered_id := dash.callback_context.triggered_id) is None:
        return current_treatments
    # Add button clicked
    add_button, remove_buttons = dash.callback_context.inputs_list
    if triggered_id == add_button['id']:
        current_treatments.append(TreatmentSelector())
        return current_treatments
    # Delete button clicked
    try:
        index_to_remove = [btn['id'] for btn in remove_buttons].index(triggered_id)
        return current_treatments[:index_to_remove] + current_treatments[index_to_remove+1:]
    except ValueError:
        if current_treatments:  # List not empty, unknown ID
            raise ValueError(f"Unrecognized ID triggered the callback: {dash.callback_context.triggered_id}")
    return []


@callback(
    Output('treatment-regimen-store', 'data'),
    Input({'component': 'TreatmentSelector', 'subcomponent': 'division-store', 'aio_id': ALL}, 'data'),
    Input({'component': 'TreatmentSelector', 'subcomponent': 'death-store', 'aio_id': ALL}, 'data'),
    State('treatment-regimen-store', 'data')
)
def update_treatment_regimen(
        division_treatments_data: list[dict],
        death_treatments_data: list[dict],
        treatment_regimen_data: dict,
) -> dict:
    """Updates the treatment regimen Store whenever a division/death treatment store is modified."""
    print("DIVISION TREATMENTS:", division_treatments_data)
    print("DEATH TREATMENTS:", death_treatments_data)
    print("TREATMENT REGIMEN:", treatment_regimen_data)
    return treatment_regimen_data
