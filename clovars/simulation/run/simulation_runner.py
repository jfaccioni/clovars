from __future__ import annotations

from typing import Any, TYPE_CHECKING

from clovars.IO import SimulationWriter
from clovars.utils import QuietPrinterMixin, SimulationError

if TYPE_CHECKING:
    from clovars.bio import Well


class SimulationRunner(QuietPrinterMixin):
    """Class representing a Simulation with fluctuating cell features."""
    max_iteration = 10_000  # max number of iterations, no matter the stop conditions used

    def __init__(
            self,
            verbose: bool = False,
    ) -> None:
        """Initializes a Simulation instance."""
        super().__init__(verbose=verbose)

    def run(
            self,
            simulation_writer: SimulationWriter,
            well: Well,
            settings: dict[str, Any],
    ) -> None:
        """Runs the settings main loop, checking for stop conditions after every iteration."""
        delta, stop_conditions = self.validate_settings(settings=settings)
        for current_frame in range(self.max_iteration):
            # Output current simulation_runner time
            simulation_hours = self.get_simulation_hours(delta=delta, current_frame=current_frame)
            simulation_seconds = self.get_simulation_seconds(delta=delta, current_frame=current_frame)
            message = f'Current frame: {current_frame} ({round(simulation_hours, 2)} h)'
            self.quiet_print(len(message) * '\b' + message, end='', flush=True)
            # Attempt to modify the treatment regimens in each colony
            well.modify_colony_treatment_regimens(current_frame=current_frame)
            # Define fate for each Cell (for the next iteration)
            well.set_cell_fate(delta=delta)
            # Output current simulation_runner status
            self.write_simulation_status(
                simulation_writer=simulation_writer,
                well=well,
                current_frame=current_frame,
                simulation_seconds=simulation_seconds,
            )
            # Check for stop conditions
            if self.reached_stop_condition(well=well, current_frame=current_frame, stop_conditions=stop_conditions):
                print('---*---*---')  # Proper format to end of simulation message
                break
            # Simulate Cells for one frame
            well.pass_time(delta=delta, current_seconds=simulation_seconds)

        else:  # no stop condition was met -> self.default_max_iters reached
            print('---*---*---')  # Proper format to end of simulation message
            self.quiet_print(f"No stop condition met, program ran for {self.max_iteration} iterations.")

    @staticmethod
    def validate_settings(settings: dict[str, Any]) -> tuple[int, dict[str, int | None]]:
        """Raises a SimulationError if the run_settings are not properly formatted."""
        # Validates delta
        try:
            delta = settings['delta']
        except KeyError:
            raise SimulationError("Delta parameter not found in run settings dictionary")
        if not isinstance(delta, int):
            raise SimulationError(f"Delta parameter must be an integer, not {type(delta)}")
        # Validates stop conditions
        try:
            stop_conditions = settings['stop_conditions']
        except KeyError:
            raise SimulationError("Stop conditions parameter not found in run settings dictionary")
        if not isinstance(stop_conditions, dict):
            raise SimulationError(f"Stop conditions parameter must be a dict, not {type(stop_conditions)}")
        return delta, stop_conditions

    @staticmethod
    def get_simulation_hours(
            delta: int,
            current_frame: int,
    ) -> float:
        """Returns the Simulation's current time, in hours."""
        return (delta * current_frame) / 3600

    @staticmethod
    def get_simulation_seconds(
            delta: int,
            current_frame: int,
    ) -> int:
        """Returns the Simulation's current time, in seconds."""
        return delta * current_frame

    @staticmethod
    def write_simulation_status(
            simulation_writer: SimulationWriter,
            well: Well,
            current_frame: int,
            simulation_seconds: int,
    ) -> None:
        """Writes the current status of the Simulation to csv files (through the CSVTableWriter instance)."""
        simulation_writer.write_cells(well=well, current_frame=current_frame, simulation_seconds=simulation_seconds)
        simulation_writer.write_colonies(well=well, current_frame=current_frame, simulation_seconds=simulation_seconds)

    def reached_stop_condition(
            self,
            well: Well,
            current_frame: int,
            stop_conditions: dict[str, int | None],
    ) -> bool:
        """Returns whether the settings should stop at this iteration, given the stop conditions."""
        frame_limit = stop_conditions.get('stop_at_frame', None)
        if self.reached_frame_limit(current_frame=current_frame, frame_limit=frame_limit):
            self.quiet_print(f'\nReached stop condition: the current simulation_runner frame is >= {frame_limit}')
            return True
        single_colony_size_limit = stop_conditions.get('stop_at_single_colony_size', None)
        if self.reached_single_colony_size_limit(
                largest_colony_size=well.largest_colony_size,
                single_colony_size_limit=single_colony_size_limit
        ):
            self.quiet_print(f'\nReached stop condition: a colony size is >= {single_colony_size_limit}')
            return True
        all_colonies_size_limit = stop_conditions.get('stop_at_all_colonies_size', None)
        if self.reached_all_colonies_size_limit(
                all_colony_sizes=well.colony_sizes,
                all_colonies_size_limit=all_colonies_size_limit
        ):
            self.quiet_print(f'\nReached stop condition: all colony sizes are >= {all_colonies_size_limit}')
            return True
        else:
            return False

    @staticmethod
    def reached_frame_limit(
            current_frame: int,
            frame_limit: int | None,
    ) -> bool:
        """Returns whether the Simulation has reached its allowed iteration limit or not."""
        return frame_limit is not None and current_frame >= frame_limit

    @staticmethod
    def reached_single_colony_size_limit(
            largest_colony_size: int | None,
            single_colony_size_limit: int | None,
    ) -> bool:
        """Returns whether the Simulation has reached its allowed size limit or not."""
        if largest_colony_size is None:  # all Colonies have no Cells in them
            return False
        return single_colony_size_limit is not None and largest_colony_size >= single_colony_size_limit

    @staticmethod  # TOREVIEW: check if this method includes colonies where all cells are dead!
    def reached_all_colonies_size_limit(
            all_colony_sizes: list[int],
            all_colonies_size_limit: int | None,
    ) -> bool:
        """Returns whether the Simulation has reached its allowed size limit or not."""
        return all_colonies_size_limit is not None and all(
            colony_size >= all_colonies_size_limit
            for colony_size in all_colony_sizes
        )
