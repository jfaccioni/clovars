from __future__ import annotations

import math
import random


class Circle:
    """Class representing an abstract Circle."""
    def __init__(
            self,
            x: float,
            y: float,
            radius: float,
    ) -> None:
        """Initializes a Circle instance"""
        self.x = x
        self.y = y
        self.validate_radius(radius=radius)
        self._radius = radius

    @property
    def radius(self) -> float:
        """Returns the radius of the Circle."""
        return self._radius

    @radius.setter
    def radius(self, new_radius) -> None:
        """Sets a new radius to the Circle, validating it in the process."""
        self.validate_radius(radius=new_radius)
        self._radius = new_radius

    @staticmethod
    def validate_radius(radius: float) -> None:
        """Validates the radius by raising a ValueError if it is negative."""
        if radius < 0:
            raise ValueError(f"The radius of a Circle cannot be negative (radius = {radius})")

    @property
    def area(self) -> float:
        """Returns the area of the Circle."""
        return math.pi * (self.radius ** 2)

    @property
    def center(self) -> tuple[float, float]:
        """Returns the center of the Circle as a tuple of its (x, y) cartesian coordinates."""
        return self.x, self.y

    def distance_to(
            self,
            other: Circle
    ) -> float:
        """Returns the distance between two Circles."""
        return math.dist(self.center, other.center)

    def overlaps_with(
            self,
            other: Circle
    ) -> bool:
        """Returns whether two Circles overlap."""
        distance = self.distance_to(other)
        if (self.radius + other.radius) >= distance:
            return True
        return False

    def contains(
            self,
            other: Circle
    ) -> bool:
        """Returns whether the Circle entirely contains another Circle instance."""
        distance = self.distance_to(other)
        if self.radius >= (distance + other.radius):
            return True
        return False

    def is_inside(self, other: Circle) -> bool:
        """Returns whether the Circle is entirely contained by another Circle instance."""
        if other.contains(self):
            return True
        return False

    def random_point(self) -> tuple[float, float]:
        """Returns a random point inside the circle as a tuple of its (x, y) cartesian coordinates.
        source: https://stackoverflow.com/questions/5837572/50746409#50746409"""
        r = self.radius * math.sqrt(random.random())
        theta = random.random() * 2 * math.pi
        return self.x + (r * math.cos(theta)), self.y + (r * math.sin(theta))
