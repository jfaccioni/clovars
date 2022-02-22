from __future__ import annotations

from typing import Generator, TYPE_CHECKING

from matplotlib import pyplot as plt

if TYPE_CHECKING:
    from pathlib import Path
    from clovars.bio import Treatment


class TreatmentDrawer:
    """Class containing functions to draw and display Treatments."""
    def __init__(
            self,
            treatment_data: dict[tuple[str, int], Treatment],
    ) -> None:
        """Initializes a TreeDrawer instance."""
        self.treatment_data = treatment_data

    def display(
            self,
            show_division: bool,
            show_death: bool,
    ) -> None:
        """Displays the Division and Death Gaussians for each Treatment in the Simulation."""
        for figure, _ in self.yield_curves(show_death=show_death, show_division=show_division):
            plt.show()

    def render(
            self,
            show_division: bool,
            show_death: bool,
            folder_path: Path,
            file_name: str,
            file_extension: str,
    ) -> None:
        """Renders the Division and Death Gaussians for each Treatment in the Simulation."""
        for figure, label in self.yield_curves(show_death=show_death, show_division=show_division):
            fname = folder_path / f'{file_name}_{label}.{file_extension}'
            figure.savefig(fname)
            plt.close(figure)

    def yield_curves(
            self,
            show_death: bool,
            show_division: bool,
    ) -> Generator[tuple[plt.Figure, str], None, None]:
        """Sequentially yields gaussian Figures from the Simulation view."""
        for (colony_name, treatment_frame), treatment in self.treatment_data.items():
            fig, ax = plt.subplots()
            suffix = ''
            if show_death is True:
                suffix += 'death'
                treatment.death_curve.plot_pdf(ax=ax, x_steps=100_000, color='#E96F00', label='Death')
            if show_division is True:
                suffix += 'div'
                treatment.division_curve.plot_pdf(ax=ax, x_steps=100_000, color='#0098B1', label='Division')
            label = f'{treatment.name}_{suffix}'
            fig.suptitle(
                f'Treatment {treatment.name} added on frame {treatment_frame}'
                f'\nfor colonies starting with {colony_name}'
            )
            plt.legend()
            yield fig, label
