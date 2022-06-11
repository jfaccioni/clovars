from __future__ import annotations

from dash_app.utils.treatment_curves import get_treatment_curves, draw_treatment_curve
from dash_app.utils.cell_signals import get_signals, draw_signal


def get_dropdown_index(
        dropdown_value: str,
        dropdown_options: list[dict[str, str]] | list[str],
) -> int:
    """Returns the index of the dropdown value."""
    if isinstance(dropdown_options, dict):
        dropdown_options: list[str] = [op['value'] for op in dropdown_options]
    return dropdown_options.index(dropdown_value)
