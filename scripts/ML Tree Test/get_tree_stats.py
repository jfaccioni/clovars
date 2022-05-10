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
    branch_length_mean, branch_length_sd = get_branch_length_mean_sd(branches=branches)
    # LEAVES
    leaves = node.get_leaves()
    n_leaves = len(leaves)
    leaf_generation_mean, leaf_generation_sd = get_nodes_mean_sd(nodes=leaves, param='generation')
    # PARENTS
    parents = node.get_parents()
    n_parents = len(parents)
    parent_generation_mean, parent_generation_sd = get_nodes_mean_sd(nodes=parents, param='generation')
    simulation_seconds_at_division_mean, simulation_seconds_at_division_sd = get_nodes_mean_sd(
        nodes=parents,
        param='simulation_seconds',
    )
    cell_seconds_at_division_mean, cell_seconds_at_division_sd = get_nodes_mean_sd(
        nodes=parents,
        param='seconds_since_birth',
    )
    # DEAD CELLS
    dead_cells = node.get_dead_nodes()
    n_dead_cells = len(dead_cells)
    dead_cell_generation_mean, dead_cell_generation_sd = get_nodes_mean_sd(nodes=dead_cells, param='generation')
    simulation_seconds_at_death_mean, simulation_seconds_at_death_sd = get_nodes_mean_sd(
        nodes=dead_cells,
        param='simulation_seconds',
    )
    cell_seconds_at_death_mean, cell_seconds_at_death_sd = get_nodes_mean_sd(
        nodes=dead_cells,
        param='seconds_since_birth',
    )
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


def get_branch_length_mean_sd(branches: list[list[CellNode]]) -> tuple[float, float]:
    """returns the mean and sd of branch lengths, evaluated for each branch (CellNode list) in the branches list."""
    if not branches:
        return np.nan, np.nan
    values = [len(branch) for branch in branches]
    return np.mean(values).item(), np.std(values).item()


def get_nodes_mean_sd(
        nodes: list[CellNode],
        param: str,
) -> tuple[float, float]:
    """Returns the mean and sd of the parameter, evaluated for each CellNode in the nodes list."""
    if not nodes:  # empty list
        return np.nan, np.nan
    values = [getattr(node, param) for node in nodes]
    return np.mean(values).item(), np.std(values).item()


if __name__ == '__main__':
    main(
        input_folder=SETTINGS['input_folder'],
        treatment_label=SETTINGS['treatment_label'],
        memory_label=SETTINGS['memory_label'],
        output_folder=SETTINGS['output_folder'],
        all_trees=SETTINGS['all_trees'],
    )
