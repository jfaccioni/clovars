from __future__ import annotations

import dash_bootstrap_components as dbc


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
