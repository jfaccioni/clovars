from __future__ import annotations

from collections import defaultdict
from typing import TYPE_CHECKING

import pandas as pd
import seaborn as sns
from ete3 import TreeNode as Node, TreeStyle

from clovars import ROOT_PATH

if TYPE_CHECKING:
    from pathlib import Path

sns.set()

SETTINGS = {
    'input_folder': ROOT_PATH / 'data' / 'esicancer_output' / 'trees',
    'output_folder': ROOT_PATH / 'scripts' / 'esiCancer Trees' / 'figures',
}


def main(
        input_folder: Path,
        output_folder: Path,
) -> None:
    """Main function of this script."""
    runs = defaultdict(dict)
    for csv_file_path in input_folder.glob("*.csv"):
        fitness_impact, _, result_type = csv_file_path.stem.split('_')
        runs[fitness_impact][result_type] = csv_file_path
    data = (
        pd
        .read_csv(runs['noImpact']['ancestralResults'], sep=';', index_col=None)
        .iloc[:, :-1]
        .drop(columns='Population')
        .melt(id_vars='Generation', var_name='Colony ID', value_name='Colony Size')
    )
    data['Colony ID'] = data['Colony ID'].str.strip()  # Remove surrounding whitespace in Colony ID column
    data = data.iloc[data.index > (len(data) % 2)]
    tree_root = Node()
    for colony_id, colony_data in data.groupby('Colony ID'):
        print(f'Processing Colony ID {colony_id}...')
        colony_root = Node(name=colony_id)
        tree_root.add_child(colony_root)  # noqa
        current_nodes = [colony_root]
        for named_tuple in (
                colony_data
                .iloc[1:, :]
                .itertuples()
        ):  # (Index, Generation, Colony ID, Colony Size)
            _, generation, _, colony_size = named_tuple
            children = []
            if colony_size < len(current_nodes):  # some cells died
                for i, node in enumerate(current_nodes):
                    if i == colony_size:
                        break
                    c = node.add_child()
                    children.append(c)
            elif colony_size > len(current_nodes):  # some cells divided
                for node in current_nodes:
                    c = node.add_child()
                    children.append(c)
                for i, node in enumerate(current_nodes):
                    if i == colony_size - len(current_nodes):
                        break
                    c = node.add_child()
                    children.append(c)
            else:  # no death, no divisions
                for node in current_nodes:
                    c = node.add_child()
                    children.append(c)
            current_nodes = children
    ts = TreeStyle()
    ts.branch_vertical_margin = 500
    tree_root.render(str(output_folder), tree_style=ts)


if __name__ == '__main__':
    main(**SETTINGS)
