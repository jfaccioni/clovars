from __future__ import annotations

import itertools
import json
import sys
from pathlib import Path
from typing import TYPE_CHECKING, Any

from clovars.utils import PathCreatorMixin

if TYPE_CHECKING:
    from clovars.bio import Cell, Colony, Well


class SimulationWriter(PathCreatorMixin):
    """Class responsible for writing Simulation data to output files."""
    cell_index_counter = itertools.count()
    cell_csv_header = (
        'index,'
        'id,'
        'name,'
        'branch_name,'
        'colony_name,'
        'generation,'
        'x,'
        'y,'
        'radius,'
        'signal_value,'
        'seconds_since_birth,'
        'fate_at_next_frame,'
        'treatment_name,'
        'death_threshold,'
        'division_threshold,'
        'fitness_memory,'
        'simulation_frames,'
        'simulation_seconds,'
        'simulation_hours,'
        'simulation_days\n'
    )
    colony_index_counter = itertools.count()
    colony_csv_header = (
        'index,'
        'id,'
        'name,'
        'size,'
        'seconds_since_birth,'
        'signal_mean,'
        'signal_std,'
        'simulation_frames,'
        'simulation_seconds,'
        'simulation_hours,'
        'simulation_days\n'
    )
    default_output_folder = '.'
    default_cell_csv_file_name = 'cells.csv'
    default_colony_csv_file_name = 'colonies.csv'
    default_parameters_file_name = 'params.json'

    def __init__(
            self,
            settings: dict[str, any] = None,
    ) -> None:
        """Initializes a SimulationWriter."""
        if settings is None:
            settings = {}
        super().__init__(folder=settings.get('output_folder', self.default_output_folder))
        self.cell_csv_path = self.path / settings.get('cell_csv_file_name', self.default_cell_csv_file_name)
        self.colony_csv_path = self.path / settings.get('colony_csv_file_name', self.default_colony_csv_file_name)
        self.parameters_path = self.path / settings.get('parameters_file_name', self.default_parameters_file_name)
        self.confirm_overwrite_flag = settings.get('confirm_overwrite', True)

    def set_files(self) -> None:
        """Sets up the files for writing into them."""
        self.refresh_paths()
        self.write_cell_csv_header()
        self.write_colony_csv_header()

    def refresh_paths(self) -> None:
        """Refreshes the files whose Path already exist in the filesystem."""
        if not (existing_paths := [
            path
            for path in (self.cell_csv_path, self.colony_csv_path, self.parameters_path)
            if path.exists()
        ]):  # No conflicts with the file Path are present
            return
        if self.confirm_overwrite_flag is True:
            self.confirm_overwrite(existing_paths=existing_paths)
        for path in existing_paths:
            self.refresh_path(path=path)

    @staticmethod
    def confirm_overwrite(existing_paths: list[Path]) -> None:
        """Prompts the user to confirm whether to overwrite the files in the "existing_paths" list or not."""
        paths_str = "\n".join([f'"{str(existing_path)}"' for existing_path in existing_paths])
        answer = input(f'The following files\n{paths_str}\nalready exist. Ok to overwrite? (y/n)').lower()
        while True:
            if answer == 'y':
                return
            elif answer == 'n':
                print(f'User did not want to overwrite\n{paths_str}.\nExiting simulation...')
                sys.exit(0)
            else:
                answer = input(f'Could not understand answer {answer}, please type "y" or "n" only')

    @staticmethod
    def refresh_path(path: Path):
        """Refreshes the file by deleting it and touching it afterwards."""
        path.unlink(missing_ok=True)
        path.touch()

    def write_params(
            self,
            colony_data: list[dict],
            well_settings: dict[str, Any],
            simulation_writer_settings: dict[str, Any],
            simulation_runner_settings: dict[str, Any],
            verbose: float,
    ) -> None:
        """Serializes the parameters into the JSON parameters file."""
        params = {
            'colony_data': colony_data,
            'well_settings': well_settings,
            'simulation_writer_settings': simulation_writer_settings,
            'simulation_runner_settings': simulation_runner_settings,
            'verbose': verbose,
        }
        with open(self.parameters_path, "w") as file:
            file.write(json.dumps(params, indent=4))

    def write_cell_csv_header(self) -> None:
        """Writes the header to the cell output csv file."""
        with open(self.cell_csv_path, 'a') as cell_output_csv:
            cell_output_csv.write(self.cell_csv_header)

    def write_cells(
            self,
            well: Well,
            current_frame: int,
            simulation_seconds: int,
    ) -> None:
        """Writes the current Cell information to the cell output csv file."""
        with open(self.cell_csv_path, 'a') as cell_output_csv:
            for cell in well.cells:
                cell_row = self.cell_as_csv_row(
                    cell=cell,
                    current_frame=current_frame,
                    simulation_seconds=simulation_seconds,
                )
                cell_output_csv.write(cell_row)

    def cell_as_csv_row(
            self,
            cell: Cell,
            current_frame: int,
            simulation_seconds: int,
    ) -> str:
        """Returns a string representing the Cell as a row in a csv file."""
        return (
            f'{next(self.cell_index_counter)},'
            f'{cell.id},'
            f'{cell.name},'
            f'{cell.branch_name},'
            f'{cell.colony_name},'
            f'{cell.generation},'
            f'{cell.x},'
            f'{cell.y},'
            f'{cell.radius},'
            f'{cell.signal_value},'
            f'{cell.seconds_since_birth},'
            f'{cell.fate},'
            f'{cell.treatment.name},'
            f'{cell.death_threshold},'
            f'{cell.division_threshold},'
            f'{cell.fitness_memory},'
            f'{current_frame},'
            f'{simulation_seconds},'
            f'{simulation_seconds / 3600},'
            f'{simulation_seconds / (3600 * 24)}\n'
        )

    def write_colony_csv_header(self) -> None:
        """Writes the header to the colony output csv file."""
        with open(self.colony_csv_path, 'a') as colony_output_csv:
            colony_output_csv.write(self.colony_csv_header)

    def write_colonies(
            self,
            well: Well,
            current_frame: int,
            simulation_seconds: int,
    ) -> None:
        """Writes the current Colony information to the colony output csv file."""
        with open(self.colony_csv_path, 'a') as colony_output_csv:
            for colony in well:
                colony_row = self.colony_as_csv_row(
                    colony=colony,
                    current_frame=current_frame,
                    simulation_seconds=simulation_seconds,
                )
                colony_output_csv.write(colony_row)

    def colony_as_csv_row(
            self,
            colony: Colony,
            current_frame: int,
            simulation_seconds: int,
    ) -> str:
        """Returns a string representing the Colony as a row in a csv file."""
        return (
            f'{next(self.colony_index_counter)},'
            f'{colony.id},'
            f'{colony.name},'
            f'{len(colony)},'
            f'{colony.seconds_since_birth},'
            f'{colony.signal_mean()},'
            f'{colony.signal_std()},'
            f'{current_frame},'
            f'{simulation_seconds},'
            f'{simulation_seconds / 3600},'
            f'{simulation_seconds / (3600 * 24)}\n'
        )
