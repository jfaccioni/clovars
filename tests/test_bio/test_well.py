import unittest
from unittest import mock
from unittest.mock import MagicMock

from clovars.abstract import Circle
from clovars.bio import Cell, Colony, Well


class TestWell(unittest.TestCase):
    """Class representing unit-tests of clovars.bio.well.Well objects."""
    default_delta = 100

    def setUp(self) -> None:
        """Sets up the test case subject (a Well instance)."""
        self.well = Well(x=100.0, y=100.0, radius=100.0)

    def get_tree_with(
            self,
            n_frames: int,
            n_divisions: int,
    ) -> Cell:
        """Returns a tree with the specified number of frames and divisions."""
        root = Cell()
        cell = root
        for _ in range(n_divisions):
            cell, _ = cell.divide(delta=self.default_delta)
        for _ in range(n_frames - n_divisions):
            cell = cell.migrate(delta=self.default_delta)
        return root

    def test_well_is_a_circle_instance(self) -> None:
        """Tests whether the Well is an instance of Circle."""
        self.assertIsInstance(self.well, Circle)

    def test_well_has_attributes_of_a_circle(self) -> None:
        """Tests whether the Well has the expected attributes of a Circle."""
        for attr_name in ['x', 'y', 'radius']:
            self.assertTrue(hasattr(self.well, attr_name))

    def test_well_has_colonies_attribute(self) -> None:
        """Tests whether the Well has a "root_cells" attribute (an empty List)."""
        self.assertIsInstance(self.well.colonies, list)
        self.assertSequenceEqual(self.well.colonies, [])

    def test_well_length_returns_number_of_colonies_in_the_well(self) -> None:
        """Tests whether the Well length corresponds to the number of Colonies in it."""
        self.assertEqual(len(self.well), 0)
        self.well.colonies = [Colony(), Colony(), Colony()]
        self.assertEqual(len(self.well), 3)

    def test_well_getitem_returns_the_cell_at_the_index(self) -> None:
        """Tests whether calling the Well's "__getitem__" special method returns the Colony at the i-th index."""
        with self.assertRaises(IndexError):
            self.well[0]  # noqa
        for i in range(5):
            self.well.colonies.append(Colony())
            self.assertIs(self.well[i], self.well.colonies[i])

    def test_well_iteration_yields_cells_from_the_root_cells_list(self) -> None:
        """Tests whether iterating over the Well yields Colonies in it."""
        self.well.colonies = [Colony(), Colony(), Colony()]

        for colony in self.well:
            self.assertIsInstance(colony, Colony)

    def test_cells_property_returns_list_of_all_cells_across_colonies(self) -> None:
        """Tests whether the "cells" property returns a list of all Cells across all Colonies in the Well."""
        self.well.colonies = [Colony(cells=[Cell(), Cell(), Cell()]), Colony(cells=[Cell()]), Colony(cells=[Cell()])]
        for cell in self.well.cells:
            self.assertIsInstance(cell, Cell)

    def test_colony_sizes_property_returns_number_of_cells_in_each_colony(self) -> None:
        """Tests whether the "colony_sizes" property returns the number of Cells in each Colony."""
        self.well.colonies = [Colony(cells=[Cell()]), Colony(cells=[Cell(), Cell(), Cell()]), Colony()]
        self.assertEqual(self.well.colony_sizes, [1, 3, 0])

    def test_colony_sizes_property_returns_empty_list_when_no_cells_are_present(self) -> None:
        """Tests whether the "colony_sizes" property returns an empty list when no Cells are in the Well."""
        self.well.colonies = []
        self.assertEqual(self.well.colony_sizes, [])

    def test_largest_colony_size_property_returns_the_number_of_cells_in_the_largest_colony(self) -> None:
        """Tests whether the "colony_sizes" property returns the number of Cells in the largest Colony."""
        self.well.colonies = [Colony(cells=[Cell()]), Colony(cells=[Cell(), Cell(), Cell()]), Colony()]
        self.assertEqual(self.well.largest_colony_size, 3)

    def test_largest_colony_size_property_returns_none_when_no_cells_are_present(self) -> None:
        """Tests whether the "largest_colony_size" property returns None when no Cells are in the Well."""
        self.well.colonies = []
        self.assertIsNone(self.well.largest_colony_size)

    @mock.patch('clovars.bio.Well.add_colony')
    @mock.patch('clovars.bio.Well.place_colony_inside')
    def test_set_initial_colonies_calls_methods_for_each_colony(
            self,
            mock_place_colony_inside: MagicMock,
            mock_add_colony: MagicMock,
    ) -> None:
        """Tests whether the "set_initial_colonies" method calls the downstream methods for each input Colony."""
        colonies = [Colony(), Colony(), Colony()]
        self.well.set_initial_colonies(colonies)
        for colony in colonies:
            mock_place_colony_inside.assert_any_call(colony=colony)
            mock_add_colony.assert_any_call(colony=colony)

    def test_place_colony_inside_method_places_colonies_inside_the_well(self) -> None:
        """Tests whether the "place_colony_inside" method places each cell of the Colony inside the Well."""
        colony = Colony(cells=[Cell(x=-10, y=-10, radius=0.05), Cell(x=-10, y=-10, radius=0.05)])
        for cell in colony:
            self.assertFalse(self.well.contains(cell.circle))
        self.well.place_colony_inside(colony)
        for cell in colony:
            self.assertTrue(self.well.contains(cell.circle))  # Fails rarely (random point + jitter ends out of Well)

    def test_add_colony_method_adds_colonies_to_the_well(self) -> None:
        """Tests whether the "add_colony" method adds the Colony to the Well."""
        self.assertSequenceEqual(self.well.colonies, [])
        colony = Colony()
        self.well.add_colony(colony)
        self.assertSequenceEqual(self.well.colonies, [colony])

    def test_pass_time_method_(self) -> None:
        """docstring."""
        self.fail('Write the test!')

    def test_set_cell_fate_method_calls_set_cell_fate_method(self) -> None:
        """Tests whether the "set_cell_fate" method calls the "set_cell_fate" of each Cell in the Well."""
        cells = [Cell(), Cell(), Cell(), Cell()]
        for cell in cells:
            cell.set_cell_fate = MagicMock()
        cells_in_well = cells[2:]
        self.well.colonies = [Colony(cells=cells_in_well)]
        self.well.set_cell_fate(delta=self.default_delta)
        for cell in cells:
            if cell in cells_in_well:
                cell.set_cell_fate.assert_called_once_with(delta=self.default_delta)
            else:
                cell.set_cell_fate.assert_not_called()

    def test_modify_colony_treatment_regimen_method_calls_attempt_treatment_change_method(self) -> None:
        """
        Tests whether the "modify_colony_treatment_regimen" method calls the
        "attempt_treatment_change" of each Colony in the Well.
        """
        colonies = [Colony(), Colony(), Colony(), Colony()]
        for colony in colonies:
            colony.attempt_treatment_change = MagicMock()
        colonies_in_well = colonies[2:]
        self.well.colonies = colonies
        self.well.modify_colony_treatment_regimens(current_frame=0)
        for colony in colonies:
            if colony in colonies_in_well:
                colony.attempt_treatment_change.assert_called_once_with(current_frame=0)
            else:
                colony.attempt_treatment_change.assert_not_called()


if __name__ == '__main__':
    unittest.main()
