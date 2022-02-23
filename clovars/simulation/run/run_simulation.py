from __future__ import annotations

from typing import Any

from clovars.IO import ColonyLoader, SimulationWriter, WellLoader
from clovars.simulation import SimulationRunner


def run_simulation_function(
        colony_data: list[dict[str, Any]] = None,
        well_settings: dict[str, Any] | None = None,
        simulation_writer_settings: dict[str, Any] | None = None,
        simulation_runner_settings: dict[str, Any] | None = None,
        verbose: bool = False,
) -> None:
    """Runs the Simulation with the given settings."""
    if colony_data is None:
        colony_data = []
    if well_settings is None:
        well_settings = {}
    if simulation_writer_settings is None:
        simulation_writer_settings = {}
    if simulation_runner_settings is None:
        simulation_runner_settings = {}
    if verbose is True:
        print('Loading Colonies and Well...')
    colony_loader = ColonyLoader(colony_data=colony_data)
    well_loader = WellLoader(well_settings=well_settings)
    well = well_loader.well
    well.set_initial_colonies(colony_loader.colonies)
    if verbose is True:
        print('Setting Simulation files...')
    simulation_writer = SimulationWriter(settings=simulation_writer_settings)
    if verbose is True:
        print(f'Using output folder:\n"{simulation_writer.path}"\n')
    simulation_writer.set_files()
    simulation_writer.write_params(
        colony_data=colony_data,
        well_settings=well_settings,
        simulation_writer_settings=simulation_writer_settings,
        simulation_runner_settings=simulation_runner_settings,
        verbose=verbose,
    )
    if verbose is True:
        print('Starting Simulation...')
    simulation_runner = SimulationRunner(verbose=verbose)
    simulation_runner.run(
        well=well,
        simulation_writer=simulation_writer,
        settings=simulation_runner_settings,
    )
    if verbose is True:
        print('Simulation has ended.')
