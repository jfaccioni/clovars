from __future__ import annotations

import itertools
import random
from typing import TYPE_CHECKING

from clovars.abstract import Circle
from clovars.bio import DEFAULT_TREATMENT, DEFAULT_CELL_SIGNAL, DEFAULT_FITNESS_MEMORY
from clovars.utils import SimulationError

if TYPE_CHECKING:
    from clovars.abstract import CellMemory
    from clovars.scientific import CellSignal
    from clovars.bio import Treatment


class Cell:
    """Class representing a single Cell in a specific point in time and space."""
    cell_id_counter = itertools.count()
    min_time_to_division = 12 * 3600  # Wait at least 12h before dividing

    def __init__(
            self,
            name: str = '',
            max_speed: float = 1.0,
            x: float = 0.0,
            y: float = 0.0,
            radius: float = 1.0,
            linked_sister_inheritance: bool = False,
            division_threshold: float | None = None,
            death_threshold: float | None = None,
            fitness_memory: CellMemory | None = None,
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
        self.linked_sister_inheritance = linked_sister_inheritance
        self.division_threshold = random.random() if division_threshold is None else division_threshold
        if not 0 <= self.division_threshold <= 1:
            raise SimulationError(f"Division threshold value {self.division_threshold} not in [0, 1] interval.")
        self.death_threshold = random.random() if death_threshold is None else death_threshold
        if not 0 <= self.death_threshold <= 1:
            raise SimulationError(f"Death threshold value {self.death_threshold} not in [0, 1] interval.")
        # Composition
        self.circle = Circle(x=x, y=y, radius=radius)
        self.fitness_memory = fitness_memory if fitness_memory is not None else DEFAULT_FITNESS_MEMORY
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
        if random.random() >= 0.5:  # test death first
            if self.should_die(delta=delta):
                self.fate = 'death'
            elif self.should_divide(delta=delta):
                self.fate = 'division'
            else:
                self.fate = 'migration'
        else:  # test division first
            if self.should_divide(delta=delta):
                self.fate = 'division'
            elif self.should_die(delta=delta):
                self.fate = 'death'
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
        if self.seconds_since_birth < self.min_time_to_division:
            return False
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
            for child_cell in result:
                child_cell.fluctuate_signal(current_seconds=current_seconds, has_divided=True)
        elif self.fate == 'migration':
            result = self.migrate(delta=delta)
            result.fluctuate_signal(current_seconds=current_seconds)
        else:
            raise ValueError(f'Bad Cell fate: {self.fate}')
        return result

    def die(self) -> None:
        """Sets the Cell to a dead state."""
        self.alive = False

    def divide(
            self,
            delta: int
    ) -> tuple[Cell, Cell]:
        """Creates and returns two Cells from a parent Cell."""
        if self.linked_sister_inheritance is True:
            child_01 = self.get_child_cell(delta=delta, branch_name='1', fitness_source=('mother', self))
            child_02 = self.get_child_cell(delta=delta, branch_name='2', fitness_source=('sister', child_01))
        else:
            child_01 = self.get_child_cell(delta=delta, branch_name='1', fitness_source=('mother', self))
            child_02 = self.get_child_cell(delta=delta, branch_name='2', fitness_source=('mother', self))
        return child_01, child_02

    def get_child_cell(
            self,
            delta: int,
            branch_name: str,
            fitness_source: tuple[str, Cell],
    ) -> Cell:
        """Returns a new Cell from the current Cell."""
        new_x, new_y = self.get_new_xy_coordinates(delta=delta, event_name='division')
        new_division_threshold, new_death_threshold = self.inherit_fitness(fitness_source=fitness_source)
        new_name = f'{self.name}.{branch_name}'
        new_signal = self.signal.split()
        for _ in range(20):
            new_signal.oscillate(seconds=delta)
        child = self.__class__(
            name=new_name,
            max_speed=self.max_speed,
            x=new_x,
            y=new_y,
            radius=self.radius,
            linked_sister_inheritance=self.linked_sister_inheritance,
            division_threshold=new_division_threshold,
            death_threshold=new_death_threshold,
            fitness_memory=self.fitness_memory,
            signal=new_signal,
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

    def inherit_fitness(
            self,
            fitness_source: tuple[str, Cell],
    ) -> tuple[float, float]:
        """Returns a new death and division threshold by inheriting from the fitness source."""
        inheritance_type, cell_to_inherit = fitness_source
        try:
            inheritance_function = {
                'mother': self.fitness_memory.inherit_from_mother,
                'sister': self.fitness_memory.inherit_from_sister,
            }[inheritance_type]
        except KeyError:
            raise ValueError(f"Invalid inheritance type: {inheritance_type}")
        division_threshold = inheritance_function(cell_to_inherit.division_threshold)
        death_threshold = inheritance_function(cell_to_inherit.death_threshold)
        return division_threshold, death_threshold

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
            *args,
            **kwargs,
    ) -> None:
        """Fluctuates the CellSignal."""
        self.signal.oscillate(*args, **kwargs)
