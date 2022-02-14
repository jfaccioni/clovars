from __future__ import annotations

from typing import Iterator, TYPE_CHECKING

from clovars.abstract import Circle

if TYPE_CHECKING:
    from clovars.bio import Cell, Colony


class Well(Circle):
    """Class representing a Well in which Cells can grow."""
    def __init__(
            self,
            x: float,
            y: float,
            radius: float,
    ) -> None:
        """Initializes a Well instance."""
        super().__init__(x=x, y=y, radius=radius)
        self.colonies: list[Colony] = []

    def __len__(self) -> int:
        """
        Implements the length protocol for Well instances by returning the number of Cells in it
        (i.e. allows the syntax "len(well)" to be used).
        """
        return len(self.colonies)

    def __getitem__(
            self,
            i: int,
    ) -> Colony:
        """
        Implements the getitem protocol for Well instances by getting the Cell at a specific index
        (i.e. allows the syntax "well[0]" to be used).
        """
        return self.colonies[i]

    def __iter__(self) -> Iterator:
        """
        Implements the iterator protocol for Well instances by iterating over its Cells
        (i.e. allows the syntax "for cell in well" to be used).
        """
        return iter(self.colonies)

    @property
    def cells(self) -> list[Cell]:
        """Returns the Cells in the Well across all colonies."""
        return [cell for colony in self for cell in colony]

    @property
    def colony_sizes(self) -> list[int]:
        """
        Returns a list of the sizes of all Cell colonies inside the Well.
        The list may be empty if no Cells are in the Well.
        """
        if not self.colonies:  # No Colonies in Well
            return []
        return [len(colony) for colony in self]

    @property
    def largest_colony_size(self) -> int | None:
        """Returns the size of the largest Cell colony inside the Well."""
        try:
            return max(map(len, self.colonies))
        except ValueError:  # no Colonies in Well
            return None

    def set_initial_colonies(
            self,
            initial_colonies: list[Colony],
    ) -> None:
        """Adds the Cells in the list as initial Cells of the Well."""
        for colony in initial_colonies:
            self.place_colony_inside(colony=colony)
            self.add_colony(colony=colony)

    def place_colony_inside(
            self,
            colony: Colony,
    ) -> None:
        """Moves the Cell to a random position inside the Well."""
        colony_x, colony_y = self.random_point()
        for cell in colony:
            x_jitter, y_jitter = [coord / 100 for coord in self.random_point()]
            cell.x = colony_x + x_jitter
            cell.y = colony_y + y_jitter

    def add_colony(
            self,
            colony: Colony,
    ) -> None:
        """Adds a Colony instance to the Well's Colonies list."""
        self.colonies.append(colony)

    def pass_time(
            self,
            delta: int,
            current_seconds: int,
    ) -> None:
        """Simulates the Cells in the Well for a given number of seconds."""
        dead_colonies = []
        for colony in self.colonies:
            colony.pass_time(delta=delta, current_seconds=current_seconds)
            if colony.is_dead():
                dead_colonies.append(colony)
        self.colonies = [
            colony
            for colony in self.colonies
            if colony not in dead_colonies
        ]

    def set_cell_fate(
            self,
            delta: int,
    ) -> None:
        """Sets the fate of each Cell for the next simulation frame."""
        for cell in self.cells:
            cell.set_cell_fate(delta=delta)

    def modify_colony_treatment_regimens(
            self,
            current_frame: int,
    ) -> None:
        """Adds a treatment to all Cells in the Well (through the Cell's corresponding class method)."""
        for colony in self.colonies:
            colony.attempt_treatment_change(current_frame=current_frame)
