from __future__ import annotations

import uuid
from typing import TYPE_CHECKING

import dash_bootstrap_components as dbc
from dash import dcc, callback, Output, Input, MATCH, ALL, callback_context, State

from dash_app.utils import get_dropdown_index

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
    components = []
    # PREFIX
    if with_checkbox is True:
        checkbox_id = {'type': 'numeric-input-checkbox', 'name': name}
        components.append(dbc.InputGroupText(dbc.Checkbox(id=checkbox_id, label=prefix or None, value=checked)))
    elif prefix:
        components.append(dbc.InputGroupText(children=prefix))
    # INPUTBOX
    input_id = {'type': 'numeric-input-inputbox', 'name': name}
    inputbox = dbc.Input(type="number", id=input_id, **numeric_input_params)
    components.append(inputbox)
    # SUFFIX
    if suffix:
        components.append(dbc.InputGroupText(children=suffix))
    return dbc.InputGroup(components, className="numeric-input-group flex-nowrap")


# ### COMPONENT-SPECIFIC CALLBACKS
@callback(
    Output({'type': 'numeric-input-inputbox', 'name': MATCH}, 'disabled'),
    Input({'type': 'numeric-input-checkbox', 'name': MATCH}, 'value'),
)
def set_inputbox_disabled(checkbox_enabled: bool) -> bool:
    """Disables the numeric inputbox whenever the checkbox is unchecked."""
    return not checkbox_enabled


#####


def CollapsableContainer(
        children: list[Component] | None = None,
        name: str = "",
        label: str = "",
        checked: bool = False,
) -> dbc.Container:
    """Returns a Container containing a checkbox that opens/closes a collapsable component."""
    name = name or str(uuid.uuid4())
    checkbox_id = {'type': 'collapsable-div-checkbox', 'name': name}
    collapse_id = {'type': 'collapsable-div-collapse', 'name': name}
    return dbc.Container([
        dbc.Checkbox(id=checkbox_id, label=label or None, value=checked),
        dbc.Collapse(id=collapse_id, children=children or [], is_open=checked)
    ])


# ### COMPONENT-SPECIFIC CALLBACKS
@callback(
    Output({'type': 'collapsable-div-collapse', 'name': MATCH}, 'is_open'),
    Input({'type': 'collapsable-div-checkbox', 'name': MATCH}, 'value'),
)
def toggle_collapsable_div(checkbox_checked: bool) -> bool:
    """Opens the collapsable div whenever its checkbox is checked."""
    return checkbox_checked


#####


def DivSelectorDropdown(
        children: dict[str, Component] | None = None,
        name: str = "",
) -> dbc.Container:
    """Returns a Container containing a selector that displays a given div in the children dictionary."""
    if children is None:
        return dbc.Container([])
    name = name or str(uuid.uuid4())
    elements = [dcc.Dropdown(
        id={'type': 'div-selector-dropdown', 'name': name},
        options=list(children),
        className='div-selector-dropdown',
    )]
    for index, (key, value) in enumerate(children.items()):
        value.id = {'type': 'div-selector-child', 'parent-label': key, 'name': name}
        elements.append(value)
        # if (index + 1) < len(children):  # add breaks between elements
        #     elements.append(html.Br())
    return dbc.Container(elements)


# ### COMPONENT-SPECIFIC CALLBACKS

@callback(
    Output({'type': 'div-selector-child', 'parent-label': ALL, 'name': MATCH}, 'style'),
    Input({'type': 'div-selector-dropdown', 'name': MATCH}, 'value'),
    State({'type': 'div-selector-dropdown', 'name': MATCH}, 'options'),
)
def change_div_selector_display(
        dropdown_value: str | None,
        dropdown_options: list[dict[str, str]],
) -> list[dict[str, str]]:
    values = [{'display': 'none'}] * len(callback_context.outputs_list)
    if dropdown_value:
        dropdown_index = get_dropdown_index(dropdown_value=dropdown_value, dropdown_options=dropdown_options)
        values[dropdown_index] = {'display': 'inline'}
    return values
