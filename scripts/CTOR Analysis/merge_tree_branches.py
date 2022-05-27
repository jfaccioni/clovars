from __future__ import annotations

from pathlib import Path

import pandas as pd
import seaborn as sns
from ete3 import TreeStyle, NodeStyle

from clovars import ROOT_PATH
from clovars.abstract import CellNode
from clovars.simulation import SimulationViewer

sns.set()

SETTINGS = {
    'ctor_output_folder': ROOT_PATH / 'data' / 'ctor_analysis' / '2022-05-26 Gaussian Curves',
    'circular_tree': False,
    'dpi': 320,
}

DEFAULT_NODE_STYLE = NodeStyle({
    'fgcolor': '#aaaaaa',
    'shape': 'square',
    'size': 0,
})
INITIAL_NODE_STYLE = NodeStyle({
    'fgcolor': '#3e5199',
    'shape': 'square',
    'size': 5
})
DEAD_NODE_STYLE = NodeStyle({
    'fgcolor': '#993e50',
    'shape': 'circle',
    'size': 5
})
LEAF_NODE_STYLE = NodeStyle({
    'fgcolor': '#aabbee',
    'shape': 'square',
    'size': 5
})
PARENT_NODE_STYLE = NodeStyle({
    'fgcolor': '#50993e',
    'shape': 'circle',
    'size': 5
})


def main(
        ctor_output_folder: Path,
        circular_tree: bool,
        dpi: int,
) -> None:
    """Main function of this script."""
    for ctor_folder in (p for p in ctor_output_folder.iterdir() if p.is_dir()):
        print(f'reading from CTOR folder:\n{ctor_folder}')
        for colony_folder in (ctor_folder / 'data').iterdir():
            print(f'parsing data from colony folder:\n{colony_folder}')
            _, colony_num_str = colony_folder.stem.split('_')
            colony_num = int(colony_num_str)
            data = pd.read_csv(colony_folder / 'cell.csv', index_col=None)
            print(f'Parsing data into tree structure...')
            tree = get_tree(data=data)
            tree_style = get_tree_style(circular_tree=circular_tree)
            file_path = get_file_path(ctor_folder=ctor_folder, colony_num=colony_num, circular_tree=circular_tree)
            print(f'Drawing tree at {file_path}...\n')
            tree.render(file_name=file_path, tree_style=tree_style, dpi=dpi)


def get_tree(data: pd.DataFrame) -> CellNode:
    """Returns a tree from the given DataFrame."""
    simulation_viewer = SimulationViewer(cell_data=data, well_radius=1.0, treatment_data={})
    root = CellNode()
    for node in simulation_viewer.roots:
        for subnode in node.iter_descendants():
            if subnode.is_dead():
                subnode.set_style(node_style=DEAD_NODE_STYLE)
            elif subnode.is_leaf():  # proper leaf
                subnode.set_style(node_style=LEAF_NODE_STYLE)
            elif subnode.is_parent():
                subnode.set_style(node_style=PARENT_NODE_STYLE)
            else:
                subnode.set_style(node_style=DEFAULT_NODE_STYLE)
        node.set_style(node_style=INITIAL_NODE_STYLE)
        root.set_style(node_style=DEAD_NODE_STYLE)
        root.add_child(node)  # noqa
    return root


def get_tree_style(circular_tree: bool) -> TreeStyle:
    """Returns a TreeStyle object with set parameters."""
    tree_style = TreeStyle()
    tree_style.show_leaf_name = False
    tree_style.show_branch_length = False
    tree_style.show_branch_support = False
    tree_style.show_scale = False
    if circular_tree is True:
        tree_style.mode = "c"
        tree_style.arc_span = 360
    else:
        tree_style.rotation = 90
    return tree_style


def get_file_path(
        ctor_folder: Path,
        colony_num: int,
        circular_tree: bool,
) -> Path:
    """Returns the file path for writing the tree into."""
    folder_suffix = 'linear colony trees' if not circular_tree else 'circular colony trees'
    output_path = ctor_folder / 'figure' / folder_suffix
    output_path.mkdir(parents=True, exist_ok=True)
    file_path = output_path / f'Colony_{colony_num}.png'
    return file_path


if __name__ == '__main__':
    main(
        ctor_output_folder=SETTINGS['ctor_output_folder'],
        circular_tree=SETTINGS['circular_tree'],
        dpi=SETTINGS['dpi'],
    )
