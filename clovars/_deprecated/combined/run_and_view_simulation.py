from __future__ import annotations

from typing import Any

from clovars._deprecated.settings import get_run_settings, get_view_settings
from clovars.simulation import run_simulation_function, view_simulation_function


def run_and_view_simulation(
        run_settings: dict[str, Any] | None = None,
        view_settings: dict[str, Any] | None = None,
) -> None:
    """Runs the Simulation with the given settings and then views its results."""
    if run_settings is None:
        run_settings = {}
    run_simulation_function(**run_settings)
    if view_settings is None:
        view_settings = {}
    view_simulation_function(**view_settings)


if __name__ == '__main__':
    run_and_view_simulation(run_settings=get_run_settings(), view_settings=get_view_settings())
