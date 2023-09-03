from __future__ import annotations

from pathlib import Path

import pandas as pd

from clovars.IO import SimulationLoader
from clovars.abstract import CellNode

LOADER_SETTINGS = {
    'simulation_input_folder': Path('/') / 'home' / 'juliano' / 'output',
    'cell_csv_file_name': 'cell_output.csv',
    'colony_csv_file_name': 'colony_output.csv',
    'parameters_file_name': 'params.json',
}


def get_roots(
        simulation_input_folder: str | Path,
        cell_csv_file_name: str = 'cell_output.csv',
        colony_csv_file_name: str = 'colony_output.csv',
        parameters_file_name: str = 'params.json',
) -> list[CellNode]:
    """Returns a list of the root nodes from an experiment folder."""
    loader = SimulationLoader(settings={
        'simulation_input_folder': simulation_input_folder,
        'cell_csv_file_name': cell_csv_file_name,
        'colony_csv_file_name': colony_csv_file_name,
        'parameters_file_name': parameters_file_name,
    })
    roots = list(yield_roots(cell_data=loader.cell_data))
    return roots


def yield_roots(cell_data: pd.DataFrame):
    """Returns the root CellNodes of each tree, parsed from the cell_data DataFrame."""
    for root_name, root_data in cell_data.groupby('branch_name', sort=False):
        root_node = get_root_data(
            root_name=root_name,  # noqa
            root_data=root_data,
        )
        yield root_node


def get_root_data(
        root_name: str,
        root_data: pd.DataFrame,
) -> CellNode:
    """
    Builds the entire CellNode tree of a given colony name and returns its root Node.
    Raises ValueError if the given root_name is not present in the DataFrame.
    """
    if root_name not in root_data['name'].values:
        raise ValueError(f'Root name {root_name} not present in the "Name" column!')
    groups = root_data.sort_values(by=['simulation_seconds']).groupby('name')
    root_node = build_tree(
        root_name=root_name,
        groups=groups,
    )
    return root_node


def build_tree(
        root_name: str,
        groups: pd.DataFrameGroupBy,
        node: CellNode | None = None,
) -> CellNode:
    """Recursively builds the CellNode tree from the groups DataFrameGroupBy."""
    try:
        data = groups.get_group(root_name)
    except KeyError:  # Stop condition
        return node
    current_node = node
    for i, data in data.iterrows():
        next_node = CellNode(name=root_name)
        next_node.add_features(**data.to_dict())
        try:
            current_node.add_child(next_node)  # noqa
        except AttributeError:  # current_node is None
            node = next_node  # next_node is actually the root Node
        current_node = next_node
    build_tree(root_name=root_name + '.1', groups=groups, node=current_node)
    build_tree(root_name=root_name + '.2', groups=groups, node=current_node)
    return node
