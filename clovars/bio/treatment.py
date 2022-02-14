from __future__ import annotations

from typing import TYPE_CHECKING, Any

from clovars.scientific import Gaussian, get_curve

if TYPE_CHECKING:
    from clovars.scientific import Curve


class Treatment:
    """Class representing a Treatment that influences Cells."""

    def __init__(
            self,
            name: str | None = None,
            division_curve: Curve | None = None,
            death_curve: Curve | None = None,
            signal_disturbance: dict | None = None,
            fitness_memory_disturbance: int | None = None,
    ) -> None:
        """Initializes a Treatment instance."""
        if name is None:
            name = "Treatment"
        if division_curve is None:
            division_curve = Gaussian()
        self.division_curve = division_curve
        if death_curve is None:
            death_curve = Gaussian()
        self.name = name
        self.death_curve = death_curve
        self.signal_disturbance = signal_disturbance
        self.fitness_memory_disturbance = fitness_memory_disturbance

    def division_chance(
            self,
            x: float,
    ) -> float:
        """Returns the division curve PDF evaluated at x."""
        return self.division_curve(x=x)

    def death_chance(
            self,
            x: float,
    ) -> float:
        """Returns the death curve PDF evaluated at x."""
        return self.death_curve(x=x)

    def plot(
            self,
            plot_division: bool = True,
            plot_death: bool = True,
            *args,
            **kwargs,
    ) -> None:
        """Plots the Treatment's curves."""
        if plot_division is True:
            self.division_curve.plot_pdf(label='Division', *args, **kwargs)
        if plot_death is True:
            self.death_curve.plot_pdf(label='Death', *args, **kwargs)


def get_treatment(
        name: str = '',
        division_curve: dict[str, Any] | None = None,
        death_curve: dict[str, Any] | None = None,
        signal_disturbance: dict[str, Any] | None = None,
        fitness_memory_disturbance: int | None = None,
) -> Treatment:
    """Returns a Treatment instance based on the input parameters."""
    division_curve = division_curve if division_curve is not None else {}
    death_curve = death_curve if death_curve is not None else {}
    return Treatment(
        name=name,
        division_curve=get_curve(**division_curve),
        death_curve=get_curve(**death_curve),
        signal_disturbance=signal_disturbance,
        fitness_memory_disturbance=fitness_memory_disturbance,
    )
