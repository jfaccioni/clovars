from __future__ import annotations

import abc
from pathlib import Path
from typing import Any

import pandas as pd
from ete3 import TreeNode  # requires Python 3.8 env!

from clovars import ROOT_PATH

_CELL_INPUT_FILE = ROOT_PATH / 'output' / 'cell_output.csv'
_CELL_OUTPUT_PATH = ROOT_PATH / 'output' / 'Tree Loader Tests' / 'cell'
_CELL_OUTPUT_PATH.mkdir(exist_ok=True, parents=True)

_COLONY_INPUT_FILE = ROOT_PATH / 'output' / 'colony_output.csv'
_COLONY_OUTPUT_PATH = ROOT_PATH / 'output' / 'Tree Loader Tests' / 'colony'
_COLONY_OUTPUT_PATH.mkdir(exist_ok=True, parents=True)


class CellNode(TreeNode):
    """Class representing a single node in a Tree."""
    _ete3_features = {'dist', 'support', 'name'}

    def __init__(
            self,
            dist: float | None = None,
            support: float | None = None,
            name: str | None = None,
            **kwargs,
    ) -> None:
        """Initializes a CellNode instance."""
        super().__init__(dist=dist, support=support, name=name)
        for feature_name, feature_value in kwargs.items():
            self.add_feature(feature_name, feature_value)

    def get_features(self) -> dict[str, Any]:
        """Returns all features in the CellNode."""
        return {
            feature_name: getattr(self, feature_name)
            for feature_name in self.features
        }

    def get_clovars_features(self) -> dict[str, Any]:
        """
        Returns the features in the CellNode that do not derive from the ete3.TreeNode class
        (i.e. excluding dist, name and support).
        """
        return {
            feature_name: feature_value
            for feature_name, feature_value in self.get_features().items()
            if feature_name not in self._ete3_features
        }


class TreeLoader:
    """Base class responsible for loading CloVarS pandas dataframe into a tree structure."""
    _name_column_name = 'name'
    _seconds_column_name = 'simulation_seconds'

    def __init__(
            self,
            data: pd.DataFrame = None,
    ) -> None:
        """Initializes a TreeLoader instance."""
        self.trees = {}
        if data is not None:
            self.load_data(data)

    @abc.abstractmethod
    def load_data(
            self,
            data: pd.DataFrame,
    ) -> None:
        """Abstract method meant to be created by TreeLoader subclasses."""
        raise NotImplementedError

    def show(self) -> None:
        """Displays all trees."""
        for tree in self.trees.values():
            tree.show()

    def render(
            self,
            output_path: Path,
    ) -> None:
        """Renders all trees."""
        for tree in self.trees.values():
            file_name = f'{tree.name.replace(".", "_")}.png'
            tree.render(str(output_path / file_name))


class CellTreeLoader(TreeLoader):
    """Class responsible for loading a CloVarS cell dataframe into a tree structure."""
    def load_data(
            self,
            cell_data: pd.DataFrame,
    ) -> None:
        """Loads the cell data in the pandas DataFrame and puts it to the tree root."""
        for root_name, root_data in cell_data.groupby('branch_name', sort=False):
            branches = root_data.sort_values(by=[self._seconds_column_name]).groupby(self._name_column_name)
            root_node = self.build_tree(node_name=str(root_name), branches=branches)
            self.trees[root_name] = root_node

    def build_tree(
            self,
            node_name: str,
            branches: pd.DataFrameGroupBy,
            node: CellNode = None,
    ) -> CellNode | None:
        """Recursively builds the tree, one branch at a time, then returns its root Node."""
        current_node = node
        try:
            data = branches.get_group(node_name)
        except KeyError:  # No new branches below current branch -> end of tree
            return None
        for i, data in data.iterrows():
            next_node = CellNode(**data.to_dict())
            try:
                current_node.add_child(next_node)  # noqa
            except AttributeError:  # current_node is None -> start of tree
                node = next_node
            current_node = next_node
        self.build_tree(node_name=node_name + '.1', branches=branches, node=current_node)
        self.build_tree(node_name=node_name + '.2', branches=branches, node=current_node)
        return node


class ColonyTreeLoader(TreeLoader):
    """Class responsible for loading a CloVarS colony dataframe into a tree structure."""
    def load_data(
            self,
            colony_data: pd.DataFrame,
    ) -> None:
        """Loads the colony data in the pandas DataFrame and puts it to the tree root."""
        for colony_name, colony_data in colony_data.groupby(self._name_column_name, sort=False):
            current_node = None
            for i, data in colony_data.iterrows():
                next_node = CellNode(**data.to_dict())
                try:
                    current_node.add_child(next_node)  # noqa
                except AttributeError:  # current_node is None -> start of tree
                    self.trees[colony_name] = next_node
                current_node = next_node


if __name__ == '__main__':
    # Cell
    _cell_data = pd.read_csv(_CELL_INPUT_FILE)
    _tree_loader = CellTreeLoader(data=_cell_data)
    _tree_loader.show()
    _tree_loader.render(_CELL_OUTPUT_PATH)
    # Colony
    _colony_data = pd.read_csv(_COLONY_INPUT_FILE)
    _tree_loader = ColonyTreeLoader(data=_colony_data)
    _tree_loader.show()
    _tree_loader.render(_COLONY_OUTPUT_PATH)
