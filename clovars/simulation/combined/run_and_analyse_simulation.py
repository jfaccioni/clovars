from __future__ import annotations

from typing import Any

from clovars._deprecated.settings import get_run_settings, get_analysis_settings
from clovars.simulation import analyse_simulation_function, run_simulation_function


def run_and_analyse_simulation(
        run_settings: dict[str, Any] | None = None,
        analysis_settings: dict[str, Any] | None = None,
) -> None:
    """Runs the Simulation with the given settings and then analyses its results."""
    if run_settings is None:
        run_settings = {}
    run_simulation_function(**run_settings)
    if analysis_settings is None:
        analysis_settings = {}
    analyse_simulation_function(**analysis_settings)


if __name__ == '__main__':
    run_and_analyse_simulation(run_settings=get_run_settings(), analysis_settings=get_analysis_settings())
