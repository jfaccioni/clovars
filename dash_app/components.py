from __future__ import annotations

import uuid
from typing import TYPE_CHECKING

import dash
import dash_bootstrap_components as dbc
from dash import html, dcc, callback, Output, ALL, MATCH, Input

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
    dropdown_id = {'type': 'div-selector-dropdown', 'name': name}
    for index, (key, value) in enumerate(children.items()):
        choices.append(key)
        child_id = {'type': 'div-selector-child', 'label': key, 'index': index, 'name': name}
        value.id = child_id
        elements.append(value)
    options = [
        {'label': choice, 'value': index}
        for index, choice in enumerate(choices)
    ]
    return html.Div([dcc.Dropdown(id=dropdown_id, options=options), *elements])


@callback(
    Output({'type': 'div-selector-child', 'parent-label': ALL, 'name': MATCH}, 'style'),
    Input({'type': 'div-selector-dropdown', 'name': MATCH}, 'value'),
)
def change_display_widget(dropdown_index: int | None) -> list[dict[str, str]]:
    values = [{'display': 'none'}] * len(dash.callback_context.outputs_list)
    if dropdown_index is not None:
        values[dropdown_index] = {'display': 'inline'}
    return values
    # outputs = dash.callback_context.outputs_list
    # if not dropdown_value:
    #     return [{'display': 'none'}] * len(outputs)
    # return [
    #     {'display': 'inline'}
    #     if output['id']['parent'] == dropdown_value
    #     else {'display': 'none'}
    #     for output in dash.callback_context.outputs_list
    # ]
