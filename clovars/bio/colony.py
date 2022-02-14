from __future__ import annotations

import itertools
from typing import Iterator, TYPE_CHECKING

import numpy as np

from clovars.bio.treatment import Treatment
from clovars.scientific import Gaussian, get_cell_signal

if TYPE_CHECKING:
    from clovars.bio import Cell


class Colony:
    """Class representing a Colony formed by a group of single Cells."""
    colony_id_counter = itertools.count()
    default_treatment_regimen = {
        0: Treatment(
            name="Control",
            division_curve=Gaussian(loc=24.0, scale=5),
            death_curve=Gaussian(loc=32, scale=5),
            signal_disturbance=None,
        ),
    }

    def __init__(
            self,
            cells: list[Cell] | None = None,
            treatment_regimen: dict[int, Treatment] | None = None,
    ) -> None:
        """Initializes a Colony instance."""
        self.id = next(self.colony_id_counter)
        if cells is None:
            cells = []
        self.cells = cells
        self.seconds_since_birth = 0
        if treatment_regimen is None:
            treatment_regimen = self.default_treatment_regimen
        self.treatment_regimen = treatment_regimen

    def __eq__(
            self,
            other: Colony,
    ) -> bool:
        """Implements the Colony equality by checking whether two Colonies are comprised of the same Cell instances."""
        return set(self) == set(other)

    def __len__(self) -> int:
        """Implements the Colony length by returning the number of Cells in it."""
        return len(self.cells)

    def __iter__(self) -> Iterator:
        """Implements iteration over a Colony by iterating over its Cells."""
        return iter(self.cells)

    def __getitem__(self, item) -> Cell:
        """Implements getting the nth item the Colony by getting it from its Cells."""
        try:
            return self.cells[item]
        except IndexError as e:
            if not self:
                raise IndexError('No Cells in the Colony') from e
            elif isinstance(item, int):
                raise IndexError(f'Tried to get Cell at index {item}, but Colony only has {len(self)} Cells') from e
        except TypeError as e:
            raise TypeError(f'Colony only accepts integer as indices, not {item.__class__.__name__}') from e

    def __bool__(self) -> bool:
        """Implements evaluating a Colony as True or False by evaluating its Cell list."""
        return bool(self.cells)

    @property
    def name(self) -> str | None:
        """Returns the Colony's name (return None if Colony is empty)."""
        try:
            return self[0].colony_name
        except IndexError:
            return None

    @property
    def center(self) -> tuple[float, float] | None:
        """
        Returns the center XY coordinate of the Colony as the midway point of all Cell's XY coordinates
        (returns None if the Colony is empty).
        """
        if not self:  # No Cells in Colony
            return None
        return np.mean([cell.x for cell in self]).item(), np.mean([cell.y for cell in self]).item()

    def is_dead(self) -> bool:
        """Returns whether all Cells in the Colony are dead or not."""
        if not bool(self):
            return True
        return all(not cell.alive for cell in self)

    def signal_mean(self) -> float:
        """Returns the CellSignal mean across all Cells in the Colony."""
        return np.mean([cell.signal_value for cell in self.cells]).item()

    def signal_std(self) -> float:
        """Returns the CellSignal standard deviation across all Cells in the Colony."""
        return np.std([cell.signal_value for cell in self.cells]).item()

    def pass_time(
            self,
            delta: int,
            current_seconds: int,
    ) -> None:
        """Simulates the Colony for a given number of seconds (delta)."""
        cells_to_add = []
        cells_to_drop = []
        for cell in self:
            outcome = cell.pass_time(delta=delta, current_seconds=current_seconds)
            if outcome is None:  # Cell has died in the prior iteration, outcome is a None value
                cells_to_drop.append(cell)
            elif isinstance(outcome, tuple):  # Cell has divided, outcome is a tuple of child Cells
                cells_to_add.extend(outcome)
                cells_to_drop.append(cell)
            elif outcome is cell:  # Cell has migrated or has just died in this iteration, outcome is the Cell itself
                pass
            else:
                raise ValueError(f"Cell.pass_time returned an unexpected outcome: {outcome}")
        self.cells = [cell for cell in self.cells if cell not in cells_to_drop] + cells_to_add
        self.seconds_since_birth += delta

    def attempt_treatment_change(
            self,
            current_frame: int,
    ) -> None:
        """Checks if the Colony should change its Treatment regimen, and do so if positive."""
        if (new_treatment := self.treatment_regimen.get(current_frame)) is not None:
            for cell in self.cells:
                cell.treatment = new_treatment
                if (new_signal := new_treatment.signal_disturbance) is not None:
                    cell.signal = get_cell_signal(**new_signal)
                if (new_fitness_memory := new_treatment.fitness_memory_disturbance) is not None:
                    cell.fitness_memory = new_fitness_memory
