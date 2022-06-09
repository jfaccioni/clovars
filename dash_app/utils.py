from __future__ import annotations


def get_dropdown_index(
        dropdown_label: str,
        dropdown_options: list[dict[str, str]] | list[str],
) -> int:
    """Returns the index of the dropdown label"""
    if isinstance(dropdown_options, dict):
        dropdown_options: list[str] = [op['label'] for op in dropdown_options]
    return dropdown_options.index(dropdown_label)
