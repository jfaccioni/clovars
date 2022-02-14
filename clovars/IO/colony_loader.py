from __future__ import annotations

import itertools
from string import ascii_lowercase
from typing import Any

from clovars.bio import Cell, Colony, Treatment
from clovars.scientific import get_cell_signal, get_curve


class ColonyLoader:
    """Class responsible for validating and creating all starting Colonies in the Simulation."""
    default_cell_radius = 1.0
    default_cell_max_speed = 1.0
    default_fitness_memory = 1.0

    def __init__(
            self,
            colony_data: list[dict[str, Any]] = None,
    ) -> None:
        """Initializes a ColonyLoader instance."""
        self.colonies = []
        if colony_data:  # Checks if colony_list is None or empty list
            self.parse_colony_data(colony_data=colony_data)

    def parse_colony_data(
            self,
            colony_data: list[dict[str, Any]],
    ) -> None:
        """Parses data from colony_list into Colonies, appending them to the Colonies list."""
        for colony_index, colony_data in enumerate(colony_data, 1):
            treatment_regimen = self.get_colony_treatment_regimen(treatment_data=colony_data.get('treatment_data', {}))
            letters = self.iter_all_strings()
            for _ in range(colony_data.get('copies', 1)):
                colony = self.create_colony(
                    colony_index=colony_index,
                    repeat_label=next(letters),
                    cell_data=colony_data.get('cells', {}),
                    initial_size=colony_data.get('initial_size', 1),
                    treatment_regimen=treatment_regimen,
                )
                self.colonies.append(colony)

    @staticmethod
    def get_colony_treatment_regimen(treatment_data: dict[int, dict]) -> dict[int, Treatment]:
        """Initializes treatment instances and returns them in a dictionary as expected by Colony instances."""
        treatment_regimen = {}
        for treatment_frame, treatment_info in treatment_data.items():
            division_curve = get_curve(**treatment_info.get('division_curve', {}))
            death_curve = get_curve(**treatment_info.get('death_curve', {}))
            treatment = Treatment(
                name=treatment_info.get('name'),
                division_curve=division_curve,
                death_curve=death_curve,
                signal_disturbance=treatment_info.get('signal_disturbance', None),
                fitness_memory_disturbance=treatment_info.get('fitness_memory_disturbance', None),
            )
            treatment_regimen[treatment_frame] = treatment
        return treatment_regimen

    def create_colony(
            self,
            colony_index: int,
            repeat_label: str,
            cell_data: dict[str, Any],
            initial_size: int,
            treatment_regimen: dict[int, Treatment],
    ) -> Colony:
        """Creates a Colony based on the values in the input data and returns it."""
        cells = []
        for cell_index in range(1, initial_size + 1):
            cell = self.create_cell(
                cell_data=cell_data,
                colony_index=colony_index,
                repeat_label=repeat_label,
                cell_index=cell_index,
            )
            cells.append(cell)
        return Colony(cells=cells, treatment_regimen=treatment_regimen)

    def create_cell(
            self,
            cell_data: dict[str, Any],
            colony_index: int,
            repeat_label: str,
            cell_index: int,
    ) -> Cell:
        """Creates a Cell based on the values in the input data and returns it."""
        cell_kwargs = {
            'max_speed': cell_data.get('max_speed', self.default_cell_max_speed),
            'radius': cell_data.get('radius', self.default_cell_radius),
            'fitness_memory': cell_data.get('fitness_memory', self.default_fitness_memory),
            'signal': get_cell_signal(**cell_data.get('signal', {})),
        }
        return Cell(x=0, y=0, name=f"{colony_index}{repeat_label}-{cell_index}", **cell_kwargs)

    # Generates unique letter combinations -> 'a', 'b', 'c', ..., 'z', 'aa', 'ab', 'ac', ...
    # Source: https://stackoverflow.com/questions/29351492/
    @staticmethod
    def iter_all_strings():
        size = 1
        while True:
            for s in itertools.product(ascii_lowercase, repeat=size):
                yield "".join(s)
            size += 1
