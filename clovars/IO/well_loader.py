from __future__ import annotations

from typing import Any

from clovars.bio import Well


class WellLoader:
    """Class responsible for validating and creating the Well in the Simulation."""
    default_well_radius = 1.0

    def __init__(
            self,
            well_settings: dict[str, Any],
    ) -> None:
        """Initializes a WellLoader instance."""
        well_radius = well_settings.get('well_radius', self.default_well_radius)
        self.well = Well(x=well_radius, y=well_radius, radius=well_radius)
