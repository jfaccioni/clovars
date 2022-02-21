from __future__ import annotations

import re
from typing import Generator

from ete3 import TreeNode


class CellNode(TreeNode):
    """Class extending a TreeNode by adding methods specific to Cell lineage."""
    # Default values, also helps with linting
    index: int = 0
    id: int = 0
    branch_name: str = ''
    colony_name: str = ''
    generation: int = 0
    x: float = 0.0
    y: float = 0.0
    radius: float = 0.0
    signal_value: float = 0.0

    seconds_since_birth: int = 0
    fate_at_next_frame: str = ''
    treatment_name: str = ''
    death_threshold: float = 0.0
    division_threshold: float = 0.0
    fitness_memory: float = 0.0
    simulation_frames: int = 0
    simulation_seconds: int = 0
    simulation_hours: float = 0.0
    simulation_days: float = 0.0

    def __init__(
            self,
            dist: float | None = None,
            support: float | None = None,
            name: str | None = None,
            index: int = index,
            id: int = id,  # noqa
            branch_name: str = branch_name,
            colony_name: str = colony_name,
            generation: int = generation,
            x: float = x,
            y: float = y,
            radius: float = radius,
            signal_value: float = signal_value,
            seconds_since_birth: int = seconds_since_birth,
            fate_at_next_frame: str = fate_at_next_frame,
            treatment_name: str = treatment_name,
            death_threshold: float = death_threshold,
            division_threshold: float = division_threshold,
            fitness_memory: float = fitness_memory,
            simulation_frames: int = simulation_frames,
            simulation_seconds: int = simulation_seconds,
            simulation_hours: float = simulation_hours,
            simulation_days: float = simulation_days,

    ) -> None:
        """Initializes a CellNode instance."""
        super().__init__(dist=dist, support=support, name=name)
        for name, value in {
            'index': index,
            'id': id,
            'branch_name': branch_name,
            'colony_name': colony_name,
            'generation': generation,
            'x': x,
            'y': y,
            'radius': radius,
            'signal_value': signal_value,
            'seconds_since_birth': seconds_since_birth,
            'fate_at_next_frame': fate_at_next_frame,
            'treatment_name': treatment_name,
            'death_threshold': death_threshold,
            'division_threshold': division_threshold,
            'fitness_memory': fitness_memory,
            'simulation_frames': simulation_frames,
            'simulation_seconds': simulation_seconds,
            'simulation_hours': simulation_hours,
            'simulation_days': simulation_days,
        }.items():
            setattr(self, name, value)
            self.add_feature(name, value)

    def as_file_name(
            self,
            decimals: int = 3,
    ) -> str:
        """Returns a filesystem-compatible version of the CellNode's name."""
        try:
            colony_number = re.search(r'^\d+', self.name)[0].zfill(decimals)
            colony_copy_letter = re.search(r'[a-z]+', self.name)[0]
            branch_number = re.search(r'\d+$', self.name)[0].zfill(decimals)
        except TypeError:
            raise ValueError(f'Could not parse name: {self.name}')
        return f"{colony_number}{colony_copy_letter}{branch_number}"

    @property
    def parent(self) -> CellNode:
        """Alias property for returning the CellNode's parent node."""
        return self.up

    def is_parent(self) -> bool:
        """Returns whether the CellNode is considered to be a parent Cell, from a biological standpoint."""
        return len(self.children) > 1

    def is_child(self) -> bool:
        """Returns whether the CellNode is considered to be a child Cell, from a biological standpoint."""
        try:
            return len(self.parent.children) > 1
        except AttributeError:  # Happens when self.parent = None
            return False

    def is_initial_cell(self) -> bool:
        """Returns whether the CellNode appears at the very start of the simulation."""
        return self.simulation_seconds == 0

    def is_dead(self) -> bool:
        """Returns whether the CellNode is considered to be a dead Cell, from a biological standpoint."""
        return self.fate_at_next_frame == 'death'  # type: ignore

    def yield_branches(self) -> Generator[list[CellNode], None, None]:
        """Sequentially yields lists of CellNodes belonging to the same branch."""
        branch = []
        for node in self.traverse(strategy='preorder'):
            branch.append(node)
            if node.is_parent() or node.is_leaf():
                yield branch
                branch = []

    def get_branches(self) -> list[list[CellNode]]:
        """Returns a list of CellNode lists, each belonging to the same branch."""
        return list(self.yield_branches())

    def yield_parents(
            self,
            strategy: str = 'preorder',
    ) -> Generator[CellNode, None, None]:
        """Sequentially yields the parent CellNodes in the tree."""
        for node in self.traverse(strategy=strategy):
            if node.is_parent():
                yield node

    def get_parents(
            self,
            strategy: str = 'preorder',
    ) -> list[CellNode]:
        """Returns a list of parent CellNodes in the tree."""
        return list(self.yield_parents(strategy=strategy))

    def yield_dead_nodes(
            self,
            strategy: str = 'preorder',
    ) -> Generator[CellNode, None, None]:
        """Sequentially yields the dead CellNodes in the tree."""
        for node in self.traverse(strategy=strategy):
            if node.is_dead():
                yield node

    def get_dead_nodes(
            self,
            strategy: str = 'preorder',
    ) -> list[CellNode]:
        """Returns a list of dead CellNodes in the tree."""
        return list(self.yield_dead_nodes(strategy=strategy))
