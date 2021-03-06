from __future__ import annotations

from typing import Any

from clovars.IO import SimulationLoader
from clovars.simulation import SimulationViewer


def view_simulation_function(
        output_folder: str = 'view',
        simulation_loader_settings: dict[str, Any] | None = None,
        view_settings: dict[str, Any] | None = None,
        verbose: bool = False,
) -> None:
    """Views the result of a Simulation."""
    if simulation_loader_settings is None:
        simulation_loader_settings = {}
    if view_settings is None:
        view_settings = {}
    if verbose is True:
        print('Loading Simulation parameters and trees...')
    simulation_loader = SimulationLoader(settings=simulation_loader_settings)
    if verbose is True:
        print(f'loading simulations results from the following input folder:\n"{simulation_loader.input_folder}"\n')
        print('Visualizing Simulation trees...')
    simulation_viewer = SimulationViewer(
        cell_data=simulation_loader.cell_data,
        well_radius=simulation_loader.well_radius,
        treatment_data=simulation_loader.treatments,
        output_folder=output_folder,
        verbose=verbose,
    )
    simulation_viewer.generate_output(settings=view_settings)
    if verbose is True:
        if not simulation_viewer.is_empty:  # TODO: should check if render flags are on, not if dir is empty
            print(f'Output files written to the following output folder: {output_folder}')
        else:
            print('No output files were written (modify the settings file if you want to save output files)')
    simulation_viewer.delete_if_empty()
