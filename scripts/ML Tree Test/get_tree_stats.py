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
    'treatment_label': 'TMZ',  # Control, ControlTMZ, TMZ
    'memory_label': 'No Memory',  # No Memory, Almost No Memory, Half Memory, Almost Full Memory, Full Memory
    'output_folder': ROOT_PATH / 'scripts' / 'ML Tree Test' / 'results',
    'all_trees': True,
}


def main(
        all_trees: bool,
        input_folder: Path,
        treatment_label: str,
        memory_label: str,
        output_folder: Path,
) -> None:
    """Main function of this script."""
    if all_trees is True:
        data = get_stats_from_all_trees(input_folder=input_folder)
        data.to_csv(str(output_folder / f'tree_stats.csv'))
    else:
        data = get_stats_from_single_tree(
            input_folder=input_folder,
            treatment_label=treatment_label,
            memory_label=memory_label,
        )
        data.to_csv(str(output_folder / f'tree_stats{treatment_label}_{memory_label}.csv'))


def get_stats_from_all_trees(input_folder: Path) -> pd.DataFrame:
    """Gets the tree stats DataFrame from all folders under the input folder."""
    dfs = []
    for folder_path in input_folder.iterdir():
        folder_name = folder_path.stem
        print(f'Getting stats from trees in folder: {folder_name}')
        treatment_label, memory_label = folder_name.split('_')
        df = get_stats_from_single_tree(
            input_folder=input_folder,
            treatment_label=treatment_label,
            memory_label=memory_label,
        )
        dfs.append(df)
    return pd.concat(dfs, ignore_index=True)


def get_stats_from_single_tree(
        input_folder: Path,
        treatment_label: str,
        memory_label: str,
) -> pd.DataFrame:
    """Gets the tree stats DataFrame from a single folder."""
    settings = {
        'simulation_input_folder': input_folder / "_".join([treatment_label, memory_label]),
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
        df = get_tree_stats(node=root_node, treatment_label=treatment_label, memory_label=memory_label, index=i)
        dfs.append(df)
    return pd.concat(dfs)


def get_tree_stats(
        node: CellNode,
        treatment_label: str,
        memory_label: str,
        index: int,
) -> pd.DataFrame:
    """Gets the tree stats and returns it as a DataFrame."""
    # BRANCHES
    branches = node.get_branches()
    n_branches = len(branches)
    branch_lengths = [len(branch) for branch in branches]
    branch_length_mean = np.mean(branch_lengths)
    branch_length_sd = np.std(branch_lengths)
    # LEAVES
    leaves = node.get_leaves()
    n_leaves = len(leaves)
    leaf_generations = [leaf.generation for leaf in leaves]
    leaf_generation_mean = np.mean(leaf_generations)
    leaf_generation_sd = np.std(leaf_generations)
    # PARENTS
    parents = node.get_parents()
    n_parents = len(parents)
    parent_generations = [parent.generation for parent in parents]
    if parent_generations:
        parent_generation_mean = np.mean(parent_generations)
        parent_generation_sd = np.std(parent_generations)
    else:
        parent_generation_mean = np.nan
        parent_generation_sd = np.nan
    simulation_seconds_at_division = [parent.simulation_seconds for parent in parents]
    if simulation_seconds_at_division:
        simulation_seconds_at_division_mean = np.mean(simulation_seconds_at_division)
        simulation_seconds_at_division_sd = np.std(simulation_seconds_at_division)
    else:
        simulation_seconds_at_division_mean = np.nan
        simulation_seconds_at_division_sd = np.nan
    cell_seconds_at_division = [parent.seconds_since_birth for parent in parents]
    if cell_seconds_at_division:
        cell_seconds_at_division_mean = np.mean(cell_seconds_at_division)
        cell_seconds_at_division_sd = np.std(cell_seconds_at_division)
    else:
        cell_seconds_at_division_mean = np.nan
        cell_seconds_at_division_sd = np.nan
    # DEAD CELLS
    dead_cells = node.get_dead_nodes()
    n_dead_cells = len(dead_cells)
    dead_cell_generations = [dead_cell.generation for dead_cell in dead_cells]
    if dead_cell_generations:
        dead_cell_generation_mean = np.mean(dead_cell_generations)
        dead_cell_generation_sd = np.std(dead_cell_generations)
    else:
        dead_cell_generation_mean = np.nan
        dead_cell_generation_sd = np.nan
    simulation_seconds_at_death = [dead_cell.simulation_seconds for dead_cell in dead_cells]
    if simulation_seconds_at_death:
        simulation_seconds_at_death_mean = np.mean(simulation_seconds_at_death)
        simulation_seconds_at_death_sd = np.std(simulation_seconds_at_death)
    else:
        simulation_seconds_at_death_mean = np.nan
        simulation_seconds_at_death_sd = np.nan
    cell_seconds_at_death = [dead_cell.seconds_since_birth for dead_cell in dead_cells]
    if cell_seconds_at_death:
        cell_seconds_at_death_mean = np.mean(cell_seconds_at_death)
        cell_seconds_at_death_sd = np.std(cell_seconds_at_death)
    else:
        cell_seconds_at_death_mean = np.nan
        cell_seconds_at_death_sd = np.nan

    return pd.DataFrame({
        # LABELS
        'treatment': treatment_label,
        'memory': memory_label,
        # BRANCHES
        'n_branches': n_branches,
        'branch_length_mean': branch_length_mean,
        'branch_length_sd': branch_length_sd,
        # LEAVES
        'n_leaves': n_leaves,
        'leaf_generation_mean': leaf_generation_mean,
        'leaf_generation_sd': leaf_generation_sd,
        # PARENTS
        'n_parents': n_parents,
        'parent_generation_mean': parent_generation_mean,
        'parent_generation_sd': parent_generation_sd,
        'simulation_seconds_at_division_mean': simulation_seconds_at_division_mean,
        'simulation_seconds_at_division_sd': simulation_seconds_at_division_sd,
        'cell_seconds_at_division_mean': cell_seconds_at_division_mean,
        'cell_seconds_at_division_sd': cell_seconds_at_division_sd,
        # DEAD CELLS
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
        treatment_label=SETTINGS['treatment_label'],
        memory_label=SETTINGS['memory_label'],
        output_folder=SETTINGS['output_folder'],
        all_trees=SETTINGS['all_trees'],
    )
