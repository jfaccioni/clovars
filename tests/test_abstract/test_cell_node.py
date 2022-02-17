import unittest
from typing import Generator

from ete3 import TreeNode

from clovars.abstract import CellNode


class TestCellNode(unittest.TestCase):
    """Class representing unit-tests of clovars.abstract.cell_node.CellNode objects."""

    def setUp(self) -> None:
        """Sets up the test case subject (a CellNode instance)."""
        self.cell_node = CellNode()

    @staticmethod
    def get_default_tree() -> CellNode:
        """
        Returns the root Cell of a pre-structured tree, to be used in the tests.
        Structure is as follows:

                    1             h = 0 (root)
                    |
                    1             h = 1
              ______|______
             |            |
            1.1          1.2      h = 2
             |            |
            1.1          1.2      h = 3
           __|___         |
          |     |         |
        1.1.1 1.1.2      1.2      h = 4
          |     |       __|___
          |     |      |     |
         XXX  1.1.2  1.2.1 1.2.2  h = 5

        """
        # h = 0 (root)
        root_h0 = CellNode(name='1')
        # h = 1
        root_h1 = root_h0.add_child(name='1')  # noqa
        # h = 2
        child_1_1_h2 = root_h1.add_child(name='1.1')
        child_1_2_h2 = root_h1.add_child(name='1.2')
        # h = 3
        child_1_1_h3 = child_1_1_h2.add_child(name='1.1')
        child_1_2_h3 = child_1_2_h2.add_child(name='1.2')
        # h = 4
        child_1_1_1_h4 = child_1_1_h3.add_child(name='1.1.1')
        child_1_1_2_h4 = child_1_1_h3.add_child(name='1.1.2')
        child_1_2_h4 = child_1_2_h3.add_child(name='1.2')
        # h = 5
        child_1_1_1_h4.fate_at_next_frame = 'death'
        child_1_1_2_h4.add_child(name='1.1.2')
        child_1_2_h4.add_child(name='1.2.1')
        child_1_2_h4.add_child(name='1.2.2')
        return root_h0

    def test_node_has_expected_class_attributes(self) -> None:
        """Tests whether a CellNode has the expected class attributes."""
        expected_class_attrs = {
            'branch_name': str,
            'colony_name': str,
            'x': float,
            'y': float,
            'signal_value': float,
            'simulation_seconds': int,
            'seconds_since_birth': int,
            'generation': int,
            'fate_at_next_frame': str,
        }
        for expected_attr_name, expected_attr_type in expected_class_attrs.items():
            with self.subTest(expected_attr_name=expected_attr_name, expected_attr_type=expected_attr_type):
                self.assertTrue(hasattr(self.cell_node, expected_attr_name))
                self.assertIsInstance(getattr(self.cell_node, expected_attr_name), expected_attr_type)

    def test_node_has_expected_instance_attributes(self) -> None:
        """Tests whether a CellNode has the expected instance attributes."""
        expected_instance_attrs = {
            'branch_name': str,
            'colony_name': str,
            'x': float,
            'y': float,
            'signal_value': float,
            'simulation_seconds': int,
            'seconds_since_birth': int,
            'generation': int,
            'fate_at_next_frame': str,
            'dist': (float, type(None)),
            'support': (float, type(None)),
            'name': (str, type(None)),
        }
        for expected_attr_name, expected_attr_type in expected_instance_attrs.items():
            with self.subTest(expected_attr_name=expected_attr_name, expected_attr_type=expected_attr_type):
                self.assertTrue(hasattr(self.cell_node, expected_attr_name))
                self.assertIsInstance(getattr(self.cell_node, expected_attr_name), expected_attr_type)

    def test_node_inherits_from_ete3_treenode(self) -> None:
        """Tests whether a CellNode inherits from ete3.TreeNode."""
        self.assertIsInstance(self.cell_node, TreeNode)

    def test_as_file_name_method_returns_file_name(self) -> None:
        """Tests whether the "as_file_name" method returns an appropriately formatted name of the CellNode."""
        for test_case_name, decimals, expected_result in zip(
                ['1a-1', '400000ab-17', '34xyz-689', '111fyq-900', '23bbc-230'],
                [2, 3, 5, 1, 6],
                ['01a01', '400000ab017', '00034xyz00689', '111fyq900', '000023bbc000230'],
        ):
            with self.subTest(test_case_name=test_case_name, decimals=decimals, expected_result=expected_result):
                actual_result = CellNode(name=test_case_name).as_file_name(decimals=decimals)
                self.assertEqual(expected_result, actual_result)

    def test_as_file_name_method_raises_error_on_bad_name(self) -> None:
        """Tests whether the "as_file_name" method raises a TypeError if the CellNode's name is not parsable."""
        for bad_name in ['', 'AAAAAAAAAAA', "???", '1111wq', 'wq123']:
            with self.subTest(bad_name=bad_name), self.assertRaises(ValueError):
                CellNode(name=bad_name).as_file_name()

    def test_is_parent_method_returns_whether_node_is_biological_parent(self) -> None:
        """Tests whether the "is_parent" method returns if the CellNode is a biological parent or not."""
        self.assertFalse(self.cell_node.is_parent())
        self.cell_node.add_child(CellNode())  # noqa
        self.assertFalse(self.cell_node.is_parent())
        self.cell_node.add_child(CellNode())  # noqa
        self.assertTrue(self.cell_node.is_parent())  # parent: more than one child

    def test_is_child_method_returns_whether_node_is_biological_child(self) -> None:
        """Tests whether the "is_child" method returns if the CellNode is a biological child or not."""
        parent = CellNode()
        self.assertFalse(self.cell_node.is_child())
        parent.add_child(self.cell_node)  # noqa
        self.assertFalse(self.cell_node.is_child())
        parent.add_child(CellNode())  # noqa
        self.assertTrue(self.cell_node.is_child())  # child: up Node has more than one child

    def test_is_dead_method_returns_whether_node_is_considered_dead(self) -> None:
        """Tests whether the "is_dead" method returns if the CellNode has "death" as its fate at the next frame."""
        for fate_at_next_frame in ['', 'migration', 'division']:
            self.cell_node.fate_at_next_frame = fate_at_next_frame
            self.assertFalse(self.cell_node.is_dead())
        self.cell_node.fate_at_next_frame = 'death'
        self.assertTrue(self.cell_node.is_dead())

    def test_yield_branches_yields_list_of_Cells_in_each_branch(self) -> None:
        """Tests whether the "yield_branches" method yields lists of CellNodes that are in each branch of the tree."""
        root_node = self.get_default_tree()
        branch_generator = root_node.yield_branches()
        self.assertIsInstance(branch_generator, Generator)
        for branch in branch_generator:
            self.assertIsInstance(branch, list)
            for node in branch:
                self.assertIsInstance(node, CellNode)

    def test_yield_branches_has_unique_name_for_each_branch(self) -> None:
        """Tests whether the "yield_branches" properly gathers CellNodes with the same branch name."""
        branch_names = []
        root_node = self.get_default_tree()
        for branch in root_node.yield_branches():
            first_node = branch[0]
            branch_names.append(first_node.name)
        self.assertEqual(len(branch_names), len(set(branch_names)))

    def test_get_branches_returns_a_list_of_branches(self) -> None:
        """Tests whether the "get_branches" returns a list of branches, (with each branch containing its CellNodes)."""
        root_cell = self.get_default_tree()
        branches = root_cell.get_branches()
        self.assertIsInstance(branches, list)
        self.assertIsInstance(branches[0], list)
        self.assertIsInstance(branches[0][0], CellNode)

    def test_yield_parents_yield_all_parent_nodes_in_the_tree(self) -> None:
        """Tests whether the "yield_parents" method yields all parent CellNodes in the tree."""
        root_cell = self.get_default_tree()
        parent_generator = root_cell.yield_parents()
        self.assertIsInstance(parent_generator, Generator)
        for parent in parent_generator:
            self.assertIsInstance(parent, CellNode)
            self.assertTrue(parent.is_parent())

    def test_get_parents_returns_a_list_of_all_parents_in_the_tree(self) -> None:
        """Tests whether the "get_parents" returns a list of all parent CellNodes in the tree."""
        root_cell = self.get_default_tree()
        parents = root_cell.get_parents()
        self.assertIsInstance(parents, list)
        for parent in parents:
            self.assertIsInstance(parent, CellNode)
            self.assertTrue(parent.is_parent())

    def test_yield_dead_nodes_yield_all_dead_cells_cells_in_the_tree(self) -> None:
        """Tests whether the "yield_dead_nodes" method yields all dead CellNodes in the tree."""
        root_cell = self.get_default_tree()
        dead_cell_generator = root_cell.yield_dead_nodes()
        self.assertIsInstance(dead_cell_generator, Generator)
        for dead_cell in dead_cell_generator:
            self.assertIsInstance(dead_cell, CellNode)
            self.assertTrue(dead_cell.is_dead())

    def test_get_dead_cells_returns_a_list_of_all_dead_cells_in_the_tree(self) -> None:
        """Tests whether the "get_dead_nodes" returns a list of all dead CellNodes in the tree."""
        root_cell = self.get_default_tree()
        dead_cells = root_cell.get_dead_nodes()
        self.assertIsInstance(dead_cells, list)
        for dead_cell in dead_cells:
            self.assertIsInstance(dead_cell, CellNode)
            self.assertTrue(dead_cell.is_dead())


if __name__ == '__main__':
    unittest.main()
