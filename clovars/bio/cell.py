from __future__ import annotations

import itertools
import random
from typing import TYPE_CHECKING

from clovars.abstract import Circle
from clovars.scientific import bounded_brownian_motion
from clovars.utils import SimulationError
from clovars.bio import DEFAULT_TREATMENT, DEFAULT_CELL_SIGNAL

if TYPE_CHECKING:
    from clovars.scientific import CellSignal
    from clovars.bio import Treatment


class Cell:
    """Class representing a single Cell in a specific point in time and space."""
    cell_id_counter = itertools.count()

    def __init__(
            self,
            name: str = '',
            max_speed: float = 1.0,
            fitness_memory: float = 0.0,
            x: float = 0.0,
            y: float = 0.0,
            radius: float = 1.0,
            division_threshold: float | None = None,
            death_threshold: float | None = None,
            signal: CellSignal | None = None,
            treatment: Treatment | None = None,
    ) -> None:
        """Initializes a Cell instance."""
        # Basic Attributes
        self.id = next(self.cell_id_counter)
        self.name = name
        self.max_speed = max_speed
        self.fate = 'migration'
        self.seconds_since_birth = 0
        # State flags
        self.alive = True
        self.senescent = False
        # Fitness-related attributes
        if not 0 <= fitness_memory <= 1:
            raise SimulationError(f"Fitness memory value {fitness_memory} not in [0, 1] interval.")
        self.fitness_memory = fitness_memory
        self.division_threshold = random.random() if division_threshold is None else division_threshold
        if not 0 <= self.division_threshold <= 1:
            raise SimulationError(f"Division threshold value {self.division_threshold} not in [0, 1] interval.")
        self.death_threshold = random.random() if death_threshold is None else death_threshold
        if not 0 <= self.death_threshold <= 1:
            raise SimulationError(f"Death threshold value {self.death_threshold} not in [0, 1] interval.")
        # Composition
        self.circle = Circle(x=x, y=y, radius=radius)
        self.signal = signal if signal is not None else DEFAULT_CELL_SIGNAL
        self.treatment = treatment if treatment is not None else DEFAULT_TREATMENT

    def __str__(self) -> str:
        """Returns a user-friendly string representation of the Cell."""
        return repr(self)

    def __repr__(self) -> str:
        """Returns a string representation of the Cell."""
        return f'Cell({self.name=}, {self.max_speed=}, {self.x=}, {self.y=})'

    def calculate_division_chance(
            self,
            delta: int,
    ) -> float:
        """Returns the chance that the Cell has to divide at the next moment in time."""
        return self.treatment.division_chance(x=self.hours_since_birth + (delta / 3600))

    def calculate_death_chance(
            self,
            delta: int,
    ) -> float:
        """Returns the chance that the Cell has to die at the next moment in time."""
        return self.treatment.death_chance(x=self.hours_since_birth + (delta / 3600))

    @property
    def x(self) -> float:
        """Returns the x coordinate of the Cell (through the underlying Circle instance)."""
        return self.circle.x

    @x.setter
    def x(
        self,
        new_x: float,
    ) -> None:
        """Sets the x coordinate of the Cell (through the underlying Circle instance)."""
        self.circle.x = new_x

    @property
    def y(self) -> float:
        """Returns the y coordinate of the Cell (through the underlying Circle instance)."""
        return self.circle.y

    @y.setter
    def y(
        self,
        new_y: float,
    ) -> None:
        """Sets the y coordinate of the Cell (through the underlying Circle instance)."""
        self.circle.y = new_y

    @property
    def center(self) -> tuple[float, float]:
        """Returns a tuple of the (x, y) coordinates of the Cell (through the underlying Circle instance)."""
        return self.circle.center

    @property
    def radius(self) -> float:
        """Returns the radius of the Cell (in the underlying Circle instance)."""
        return self.circle.radius

    @radius.setter
    def radius(
            self,
            new_radius: float,
    ) -> None:
        """Sets the radius of the Cell (in the underlying Circle instance)."""
        self.circle.radius = new_radius

    @property
    def area(self) -> float:
        """Returns the area of the Cell (in the underlying Circle instance)."""
        return self.circle.area

    def distance_to(
            self,
            other_cell: Cell,
    ) -> float:
        """Returns the distance between two Cells (through the Circle interface)."""
        if not isinstance(other_cell, Cell):
            raise TypeError(
                f"Cannot calculate distance between instances of "
                f"{self.__class__.__name__} and {other_cell.__class__.__name__}, only between Cells."
            )
        return self.circle.distance_to(other_cell.circle)

    @property
    def hours_since_birth(self) -> float:
        """Returns the hours of Simulation since the Cell's birth."""
        return self.seconds_since_birth / 3600

    @property
    def branch_name(self) -> str:
        """Returns the name of the Cell's Branch in the Colony, ex: 1b-5.1.2 -> 1b-5."""
        return self.name.split('.')[0]

    @property
    def colony_name(self) -> str:
        """Returns the name of the Cell's Colony, ex: 1b-5.1.2 -> 1b."""
        return self.name.split('.')[0].split('-')[0]

    @property
    def generation(self) -> int:
        """Returns the number of times that this Cell has divided since its tree's root Cell."""
        return self.name.count('.')

    @property
    def signal_value(self) -> float:
        """Returns the value of the CellSignal in this Cell."""
        return self.signal.value

    def set_cell_fate(
            self,
            delta: int,
    ) -> None:
        """Sets the Cell fate for the next frame."""
        if self.should_die(delta=delta):
            self.fate = 'death'
        elif self.should_divide(delta=delta):
            self.fate = 'division'
        else:
            self.fate = 'migration'

    def should_die(
            self,
            delta: int,
    ) -> bool:
        """Returns whether the Cell should die at this point in time or not."""
        return self.calculate_death_chance(delta=delta) > self.death_threshold

    def should_divide(
            self,
            delta: int,
    ) -> bool:
        """Returns whether the Cell should die at this point in time or not."""
        return self.calculate_division_chance(delta=delta) > self.division_threshold

    def pass_time(
            self,
            delta: int,
            current_seconds: int,
    ) -> Cell | tuple[Cell, Cell] | None:
        """Simulates the Cell for a given number of seconds (delta)."""
        if self.fate == 'death':
            self.die()
            return None
        elif self.fate == 'division':
            result = self.divide(delta=delta)
        elif self.fate == 'migration':
            result = self.migrate(delta=delta)
        else:
            raise ValueError(f'Bad Cell fate: {self.fate}')
        self.fluctuate_signal(current_seconds=current_seconds)
        return result

    def die(self) -> None:
        """Sets the Cell to a dead state."""
        self.alive = False

    def divide(
            self,
            delta: int
    ) -> tuple[Cell, Cell]:
        """Creates and returns two Cells from a parent Cell."""
        child_01 = self.get_child_cell(delta=delta, branch_name='1')
        child_02 = self.get_child_cell(delta=delta, branch_name='2')
        return child_01, child_02

    def get_child_cell(
            self,
            delta: int,
            branch_name: str,
    ) -> Cell:
        """Returns a new Cell from the current Cell."""
        new_x, new_y = self.get_new_xy_coordinates(delta=delta, event_name='division')
        new_division_threshold, new_death_threshold = self.get_child_fitness()
        new_name = f'{self.name}.{branch_name}'
        child = self.__class__(
            name=new_name,
            max_speed=self.max_speed,
            fitness_memory=self.fitness_memory,
            x=new_x,
            y=new_y,
            division_threshold=new_division_threshold,
            death_threshold=new_death_threshold,
            radius=self.radius,
            signal=self.signal.split(),
            treatment=self.treatment,
        )
        return child

    def get_new_xy_coordinates(
            self,
            delta: int,
            event_name: str,
    ) -> tuple[float, float]:
        """Returns the XY coordinates for a Cell in the next frame, given the time delta and event."""
        if event_name == 'migration':
            search_radius = self.max_speed * delta
        elif event_name == 'division':
            search_radius = self.max_speed * delta / 100
        else:
            raise ValueError(f"Invalid event name: {event_name}")
        return Circle(x=self.x, y=self.y, radius=search_radius).random_point()

    def get_child_fitness(self) -> tuple[float, float]:
        """Returns a new death and division threshold using a brownian motion scaled by the Cell's fitness memory."""
        child_division_threshold = bounded_brownian_motion(
            current_value=self.division_threshold,
            scale=self.fitness_memory,
        )
        child_death_threshold = bounded_brownian_motion(
            current_value=self.death_threshold,
            scale=self.fitness_memory,
        )
        return child_division_threshold, child_death_threshold

    def migrate(
            self,
            delta: int,
    ) -> Cell:
        """Modifies the Cell in-place for simulating Cell migration."""
        self.x, self.y = self.get_new_xy_coordinates(delta=delta, event_name='migration')
        self.seconds_since_birth += delta
        return self

    def fluctuate_signal(
            self,
            current_seconds: int,
    ) -> None:
        """Fluctuates the CellSignal."""
        self.signal.oscillate(current_seconds=current_seconds)
