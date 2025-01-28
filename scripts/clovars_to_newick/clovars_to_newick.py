from pathlib import Path

import pandas as pd
from pandas.core.groupby import DataFrameGroupBy


from clovars import ROOT_PATH
from clovars.abstract import CellNode

SETTINGS = {
    'input_folder': ROOT_PATH / 'data' / 'clovars_output' / 'batch_FitnessMemory_treatCurveMean',
    'input_file': '0.1mem_35.09mean_cell_output.csv',
    # Newick format as defined in the link below:
    # http://etetoolkit.org/docs/latest/tutorial/tutorial_trees.html#reading-and-writing-newick-trees
    'newick_format': 0,
}


def main(
        input_folder: Path | str,
        input_file: Path | str,
        newick_format: int,
) -> None:
    """Main function of this script."""
    # Inputs
    input_folder = Path(input_folder)
    input_file = Path(input_file)
    input_path = input_folder / input_file
    # Outputs
    output_folder = input_folder / 'newick'
    output_folder.mkdir(exist_ok=True, parents=True)
    # Data
    df = pd.read_csv(input_path, index_col='index')
    for root_name, root_data in df.groupby('branch_name', sort=False):
        groups = root_data.sort_values(by=['simulation_seconds']).groupby('name')
        root_node = build_tree(root_name=root_name, groups=groups)  # noqa
        output_file = f'{input_file.stem}_{root_name}.nw'
        output_path = output_folder / output_file
        root_node.write(outfile=output_path, format=newick_format)


def build_tree(
        groups: DataFrameGroupBy,
        root_name: str,
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


if __name__ == '__main__':
    main(**SETTINGS)
