from __future__ import annotations

from typing import Any

from clovars.IO import SimulationLoader
from clovars.simulation import SimulationAnalyzer


def analyse_simulation_function(
        output_folder: str = 'analysis',
        simulation_loader_settings: dict[str, Any] | None = None,
        analysis_settings: dict[str, Any] | None = None,
        verbose: bool = False,
) -> None:
    """Analyses the result of a Simulation."""
    if simulation_loader_settings is None:
        simulation_loader_settings = {}
    if analysis_settings is None:
        analysis_settings = {}
    if verbose:
        print('Loading Simulation parameters and trees...')
    simulation_loader = SimulationLoader(settings=simulation_loader_settings)
    if verbose is True:
        print(f'loading from input folder:\n"{simulation_loader.input_folder}"\n')
        print('Analyzing Simulation trees...')
    simulation_analyzer = SimulationAnalyzer(
        cell_data=simulation_loader.cell_data,
        colony_data=simulation_loader.colony_data,
        delta=simulation_loader.delta,
        treatment_data=simulation_loader.treatments,
        verbose=verbose,
        output_folder=output_folder,
    )
    # TODO: display an informative message if no output will be generated!
    simulation_analyzer.analyse(settings=analysis_settings)
    simulation_analyzer.delete_if_empty()
