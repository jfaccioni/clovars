from __future__ import annotations

from typing import TYPE_CHECKING

from clovars import ROOT_PATH
from clovars.IO import SimulationLoader
from clovars.simulation import SimulationViewer, TreeDrawer3D

if TYPE_CHECKING:
    from pathlib import Path

SETTINGS = {
    'input_folder': ROOT_PATH / 'output' / 'ML Tree Test',
    'input_treatment': 'TMZ',  # Control, ControlTMZ, TMZ
    'input_memory': 'No Memory',  # No Memory, Almost No Memory, Half Memory, Almost Full Memory, Full Memory
    'tree_index': 11,
}


def main(
        input_folder: Path,
        input_treatment: str,
        input_memory: str,
        tree_index: int | None,
) -> None:
    """Main function of this script."""
    settings = {
        'simulation_input_folder': input_folder / "_".join([input_treatment, input_memory]),
    }
    loader = SimulationLoader(settings=settings)
    viewer = SimulationViewer(
        cell_data=loader.cell_data,
        well_radius=loader.well_radius,
        treatment_data=loader.treatments,
        output_folder='.',
        verbose=True,
    )
    tree_drawer_settings = {
        'colormap_name': 'viridis',
        'layout': 'family',
        'signal_values': viewer.cell_data['signal_value'],
        'time_values': viewer.cell_data['simulation_hours'],
        'age_values': viewer.cell_data['seconds_since_birth'] / 3600,  # in hours
        'generation_values': viewer.cell_data['generation'],
    }
    tree_drawer_3D = TreeDrawer3D(**tree_drawer_settings)
    called = False
    for i, root_node in enumerate(viewer.yield_roots()):
        if tree_index is None or tree_index == i:
            tree_drawer_3D.display_trees(
                root_nodes=[root_node],
                display_well=False,
                z_axis_ratio=1.0,
                well_radius=viewer.well_radius,
            ),
            called = True
    if called is False:
        print('Did not call display trees method - tree index out of range.')


if __name__ == '__main__':
    main(
        input_folder=SETTINGS['input_folder'],
        input_treatment=SETTINGS['input_treatment'],
        input_memory=SETTINGS['input_memory'],
        tree_index=SETTINGS['tree_index'],
    )
