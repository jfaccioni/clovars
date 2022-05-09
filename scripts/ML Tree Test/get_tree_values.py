from __future__ import annotations

from typing import TYPE_CHECKING

import numpy as np
import pandas as pd

from clovars import ROOT_PATH
from clovars.IO import SimulationLoader
from clovars.abstract import CellNode
from clovars.simulation import SimulationViewer

if TYPE_CHECKING:
    from pathlib import Path

SETTINGS = {
    'input_folder': ROOT_PATH / 'output' / 'ML Tree Test',
    'input_treatment': 'TMZ',  # Control, ControlTMZ, TMZ
    'input_memory': 'No Memory',  # No Memory, Almost No Memory, Half Memory, Almost Full Memory, Full Memory
    'output_folder': ROOT_PATH / 'scripts' / 'ML Tree Test',
}


def main(
        input_folder: Path,
        input_treatment: str,
        input_memory: str,
        output_folder: Path,
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
    dfs = []
    for i, root_node in enumerate(viewer.yield_roots()):
        df = get_tree_values(node=root_node, treatment_label=input_treatment, memory_label=input_memory, index=i)
        dfs.append(df)
    data = pd.concat(dfs)
    data.to_csv(str(output_folder / 'tree_data.csv'))


def get_tree_values(
        node: CellNode,
        treatment_label: str,
        memory_label: str,
        index: int,
) -> pd.DataFrame:
    """Gets the tree values and returns it as a DataFrame."""
    branches = node.get_branches()
    n_branches = len(branches)
    branch_lengths = [len(branch) for branch in branches]
    branch_length_mean = np.mean(branch_lengths)
    branch_length_sd = np.std(branch_lengths)

    leaves = node.get_leaves()
    n_leaves = len(leaves)
    leaf_generations = [leaf.generation for leaf in leaves]
    leaf_generation_mean = np.mean(leaf_generations)
    leaf_generation_sd = np.std(leaf_generations)

    parents = node.get_parents()
    n_parents = len(parents)
    parent_generations = [parent.generation for parent in parents]
    parent_generation_mean = np.mean(parent_generations)
    parent_generation_sd = np.std(parent_generations)
    simulation_seconds_at_division = [parent.simulation_seconds for parent in parents]
    simulation_seconds_at_division_mean = np.mean(simulation_seconds_at_division)
    simulation_seconds_at_division_sd = np.std(simulation_seconds_at_division)
    cell_seconds_at_division = [parent.seconds_since_birth for parent in parents]
    cell_seconds_at_division_mean = np.mean(cell_seconds_at_division)
    cell_seconds_at_division_sd = np.std(cell_seconds_at_division)

    dead_cells = node.get_dead_nodes()
    n_dead_cells = len(dead_cells)
    dead_cell_generations = [dead_cell.generation for dead_cell in dead_cells]
    dead_cell_generation_mean = np.mean(dead_cell_generations)
    dead_cell_generation_sd = np.std(dead_cell_generations)
    simulation_seconds_at_death = [dead_cell.simulation_seconds for dead_cell in dead_cells]
    simulation_seconds_at_death_mean = np.mean(simulation_seconds_at_death)
    simulation_seconds_at_death_sd = np.std(simulation_seconds_at_death)
    cell_seconds_at_death = [dead_cell.seconds_since_birth for dead_cell in dead_cells]
    cell_seconds_at_death_mean = np.mean(cell_seconds_at_death)
    cell_seconds_at_death_sd = np.std(cell_seconds_at_death)

    return pd.DataFrame({
        'treatment': treatment_label,
        'memory_label': memory_label,

        'n_branches': n_branches,
        'branch_length_mean': branch_length_mean,
        'branch_length_sd': branch_length_sd,

        'n_leaves': n_leaves,
        'leaf_generation_mean': leaf_generation_mean,
        'leaf_generation_sd': leaf_generation_sd,

        'n_parents': n_parents,
        'parent_generation_mean': parent_generation_mean,
        'parent_generation_sd': parent_generation_sd,
        'simulation_seconds_at_division_mean': simulation_seconds_at_division_mean,
        'simulation_seconds_at_division_sd': simulation_seconds_at_division_sd,
        'cell_seconds_at_division_mean': cell_seconds_at_division_mean,
        'cell_seconds_at_division_sd': cell_seconds_at_division_sd,

        'n_dead_cells': n_dead_cells,
        'dead_cell_generation_mean': dead_cell_generation_mean,
        'dead_cell_generation_sd': dead_cell_generation_sd,
        'simulation_seconds_at_death_mean': simulation_seconds_at_death_mean,
        'simulation_seconds_at_death_sd': simulation_seconds_at_death_sd,
        'cell_seconds_at_death_mean': cell_seconds_at_death_mean,
        'cell_seconds_at_death_sd': cell_seconds_at_death_sd,
    }, index=[index])


if __name__ == '__main__':
    main(
        input_folder=SETTINGS['input_folder'],
        input_treatment=SETTINGS['input_treatment'],
        input_memory=SETTINGS['input_memory'],
        output_folder=SETTINGS['output_folder']
    )
