from clovars.bio.treatment import Treatment, get_treatment
from clovars.scientific import ConstantCellSignal, Gaussian

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

DEFAULT_CELL_SIGNAL = ConstantCellSignal()

from clovars.bio.well import Well
from clovars.bio.cell import Cell
from clovars.bio.colony import Colony
