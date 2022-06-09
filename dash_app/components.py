from __future__ import annotations

import uuid
from typing import TYPE_CHECKING

import dash_bootstrap_components as dbc
from dash import html, dcc, callback, Output, Input, MATCH, ALL, callback_context, State

from utils import get_dropdown_index

if TYPE_CHECKING:
    from dash.development.base_component import Component


def NumericInputGroup(
        name: str,
        prefix: str = "",
        suffix: str = "",
        with_checkbox: bool = False,
        checked: bool = False,
        value: int | float | None = None,
        min_: int | float | None = None,
        max_: int | float | None = None,
        step: int | float | None = None,
) -> dbc.InputGroup:
    """
    Convenience function that returns an InputGroup with a numeric input box, along with some formatting options.
    The parameters are:

      - name: defines the ID of each element inside the InputGroup (see below).
      - prefix: text that appears in an InputGroupText before / to the left of the Input component.
      - suffix: text that appears in an InputGroupText after / to the right of the Input component.
      - with_checkbox: if True, the prefix InputGroupText includes a Checkbox element.
      - checked: defines the checked state of the Checkbox (does nothing if with_checkbox is False).
      - value/min_/max_/step: passed onto the Input component, defining its limits and single step value.

    The IDs of the internal elements are:
      - inputbox: { 'type': 'numeric-input-inputbox', 'name': <name-parameter> }
      - checkbox (only if with_checkbox=True): { 'type': 'numeric-input-checkbox', 'name': <name-parameter> }
    """
    numeric_input_params = {
        'value': value or 5,
        'min': min_ or 0,
        'max': max_ or 10,
        'step': step or 1,
    }
    input_id = {'type': 'numeric-input-inputbox', 'name': name}
    inputbox = dbc.Input(type="number", id=input_id, **numeric_input_params)
    suffix = dbc.InputGroupText(children=suffix) if suffix else None
    if with_checkbox is True:
        checkbox_id = {'type': 'numeric-input-checkbox', 'name': name}
        prefix = dbc.InputGroupText(dbc.Checkbox(id=checkbox_id, label=prefix or None, value=checked))
    else:
        prefix = dbc.InputGroupText(children=prefix) if prefix else None
    return dbc.InputGroup([prefix, inputbox, suffix])


def CollapsableDiv(
        children: list[Component] | None = None,
        name: str = "",
        label: str = "",
        checked: bool = False,
) -> html.Div:
    """Returns a html div containing a checkbox that opens/closes a collapsable component."""
    name = name or str(uuid.uuid4())
    checkbox_id = {'type': 'collapsable-div-checkbox', 'name': name}
    collapse_id = {'type': 'collapsable-div-collapse', 'name': name}
    return html.Div([
        dbc.Checkbox(id=checkbox_id, label=label or None, value=checked),
        dbc.Collapse(id=collapse_id, children=children or [], is_open=checked)
    ])


@callback(
    Output({'type': 'collapsable-div-collapse', 'name': MATCH}, 'is_open'),
    Input({'type': 'collapsable-div-checkbox', 'name': MATCH}, 'value'),
)
def toggle_collapsable_div(checkbox_checked: bool) -> bool:
    """Opens the collapsable div whenever its checkbox is checked."""
    return checkbox_checked


def DivSelectorDropdown(
        children: dict[str, Component] | None = None,
        name: str = "",
) -> html.Div:
    """Returns a html div containing a selector that displays a given div in the children dictionary."""
    if children is None:
        return html.Div([])
    name = name or str(uuid.uuid4())
    choices = []
    elements = []
    for index, (key, value) in enumerate(children.items()):
        choices.append(key)
        value.id = {'type': 'div-selector-child', 'parent-label': key, 'name': name}
        elements.append(value)
    dropdown_id = {'type': 'div-selector-dropdown', 'name': name}
    dropdown = dcc.Dropdown(id=dropdown_id, options=choices)
    return html.Div([dropdown, *elements])


@callback(
    Output({'type': 'div-selector-child', 'parent-label': ALL, 'name': MATCH}, 'style'),
    Input({'type': 'div-selector-dropdown', 'name': MATCH}, 'value'),
    State({'type': 'div-selector-dropdown', 'name': MATCH}, 'options'),
)
def change_display_widget(
        dropdown_label: str | None,
        dropdown_options: list[dict[str, str]],
) -> list[dict[str, str]]:
    values = [{'display': 'none'}] * len(callback_context.outputs_list)
    if dropdown_label:
        dropdown_index = get_dropdown_index(dropdown_label=dropdown_label, dropdown_options=dropdown_options)
        values[dropdown_index] = {'display': 'inline'}
    return values

