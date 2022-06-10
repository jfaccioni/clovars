from __future__ import annotations

import uuid
from typing import TYPE_CHECKING

import dash_bootstrap_components as dbc
from dash import callback, Output, Input, MATCH

if TYPE_CHECKING:
    from dash.development.base_component import Component


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
    return dbc.Container(
        [
            dbc.Checkbox(id=checkbox_id, label=label or None, value=checked),
            dbc.Collapse(id=collapse_id, children=children or [], is_open=checked)
        ]
    )


@callback(
    Output({'type': 'collapsable-div-collapse', 'name': MATCH}, 'is_open'),
    Input({'type': 'collapsable-div-checkbox', 'name': MATCH}, 'value'),
)
def toggle_collapsable_container(checkbox_checked: bool) -> bool:
    """Opens/closes the collapsable Container whenever its checkbox is checked."""
    return checkbox_checked
