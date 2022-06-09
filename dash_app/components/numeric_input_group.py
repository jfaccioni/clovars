from __future__ import annotations

import uuid

import dash_bootstrap_components as dbc
from dash import callback, Output, Input, MATCH


def NumericInputGroup(
        name: str | dict = "",
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
    if not name:
        name = {'name': str(uuid.uuid4())}
    elif isinstance(name, str):
        name = {'name': name}
    numeric_input_params = {
        'value': value or 5,
        'min': min_ or 0,
        'max': max_ or 10,
        'step': step or 1,
    }
    components = []
    # PREFIX
    if with_checkbox is True:
        checkbox_id = {'type': 'numeric-input-checkbox'}
        checkbox_id.update(name)
        components.append(dbc.InputGroupText(dbc.Checkbox(id=checkbox_id, label=prefix or None, value=checked)))
    elif prefix:
        components.append(dbc.InputGroupText(children=prefix))
    # INPUTBOX
    input_id = {'type': 'numeric-input-inputbox'}
    input_id.update(name)
    inputbox = dbc.Input(id=input_id, type="number", autofocus=True, **numeric_input_params)
    components.append(inputbox)
    # SUFFIX
    if suffix:
        components.append(dbc.InputGroupText(children=suffix))
    return dbc.InputGroup(components, class_name="numeric-input-group flex-nowrap")


# ### COMPONENT-SPECIFIC CALLBACKS
@callback(
    Output({'type': 'numeric-input-inputbox', 'name': MATCH}, 'disabled'),
    Input({'type': 'numeric-input-checkbox', 'name': MATCH}, 'value'),
)
def set_inputbox_disabled(checkbox_enabled: bool) -> bool:
    """Disables the numeric inputbox whenever the checkbox is unchecked."""
    return not checkbox_enabled
