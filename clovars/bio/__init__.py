from clovars.abstract import CellMemory
from clovars.bio.treatment import Treatment, get_treatment
from clovars.scientific import CellSignal, Gaussian

DEFAULT_TREATMENT = Treatment(
        name="Control",
        division_curve=Gaussian(loc=24.0, scale=5),
        death_curve=Gaussian(loc=32, scale=5),
        signal_disturbance={
            'signal_type': 'Gaussian',
            'mean': 0.0,
            'std': 1e-3,
            'k': 1e-3,
        }
    )

DEFAULT_FITNESS_MEMORY = CellMemory()
DEFAULT_CELL_SIGNAL = CellSignal('gaussian')

from clovars.bio.well import Well
from clovars.bio.cell import Cell
from clovars.bio.colony import Colony
