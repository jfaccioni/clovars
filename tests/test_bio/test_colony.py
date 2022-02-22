import unittest

import numpy as np

from clovars.bio import Cell, Colony, Treatment
from clovars.scientific import ConstantCellSignal
from tests import SKIP_TESTS


class TestColony(unittest.TestCase):
    """Class representing unit-tests for clovars.bio.colony.Colony class."""
    default_delta = 100

    def setUp(self) -> None:
        """Sets up the test case subject (a Colony instance)."""
        self.colony = Colony()

    def test_colony_has_default_treatment_regimen_attribute(self) -> None:
        """Tests whether a Colony has a "default_treatment_regimen" attribute (a dictionary)."""
        self.assertTrue(hasattr(self.colony, 'default_treatment_regimen'))
        self.assertIsInstance(self.colony.default_treatment_regimen, dict)
        for key, value in self.colony.default_treatment_regimen.items():
            self.assertIsInstance(key, int)
            self.assertIsInstance(value, Treatment)

    def test_colony_has_cells_attribute(self) -> None:
        """Tests whether a Colony has a "cells" attribute (a list)."""
        self.assertTrue(hasattr(self.colony, 'cells'))
        self.assertIsInstance(self.colony.cells, list)

    def test_cells_attribute_is_empty_list_when_cells_argument_is_none(self) -> None:
        """Tests whether the "cells" attribute is an empty list when a Colony is initialized with cells=None."""
        self.assertEqual(Colony(cells=None).cells, [])

    def test_colony_has_seconds_since_birth_attribute(self) -> None:
        """Tests whether a Colony has a "seconds_since_birth" attribute (an int)."""
        self.assertTrue(hasattr(self.colony, 'seconds_since_birth'))
        self.assertIsInstance(self.colony.seconds_since_birth, int)

    def test_colony_has_treatment_regimen_attribute(self) -> None:
        """Tests whether a Colony has a "treatment_regimen" attribute (a dictionary)."""
        self.assertTrue(hasattr(self.colony, 'treatment_regimen'))
        self.assertIsInstance(self.colony.treatment_regimen, dict)

    def test_treatment_regimen_attribute_is_the_default_when_treatment_regimen_argument_is_none(self) -> None:
        """
        Tests whether the "treatment_regimen" attribute is set to the default Treatment regimen
        when a Colony is initialized with treatment_regimen=None.
        """
        self.assertEqual(Colony(treatment_regimen=None).treatment_regimen, Colony.default_treatment_regimen)

    def test_colony_equality_compares_the_cell_lists(self) -> None:
        """Tests whether comparing two Colonies for equality compares each Colony's Cells list."""
        other_colony = Colony()
        self.assertEqual(self.colony, other_colony)
        other_colony.cells = [Cell()]
        self.assertNotEqual(self.colony, other_colony)

    def test_colony_length_returns_number_of_cells_in_the_colony(self) -> None:
        """Tests whether the Colony length corresponds to the number of Cells in it."""
        self.assertEqual(len(self.colony), 0)
        self.colony.cells = [Cell(), Cell(), Cell()]
        self.assertEqual(len(self.colony), 3)

    def test_colony_iteration_yields_cells_from_colony(self) -> None:
        """Tests whether iterating over the Colony yields Cells from the Cells list."""
        cells = [Cell(), Cell(), Cell()]
        self.colony.cells = cells
        for cell, cell_from_colony in zip(cells, self.colony):
            self.assertIs(cell, cell_from_colony)

    def test_colony_getitem_returns_the_cell_at_the_index(self) -> None:
        """Tests whether calling the Colony's "__getitem__" special method returns the Cell at the i-th index."""
        with self.assertRaises(TypeError):
            self.colony['abc']  # noqa
        with self.assertRaises(IndexError):
            self.colony[0]  # noqa
        self.colony.cells = [Cell(), Cell(), Cell()]
        self.assertIs(self.colony[0], self.colony.cells[0])
        self.assertIs(self.colony[1], self.colony.cells[1])
        self.assertIs(self.colony[2], self.colony.cells[2])
        with self.assertRaises(IndexError):
            self.colony[3]  # noqa

    def test_colony_boolean_returns_whether_there_are_cells_in_the_colony(self) -> None:
        """Tests whether the Colony is considered to be True if there are Cells in it, and False otherwise."""
        self.assertFalse(self.colony)
        self.colony.cells = [Cell()]
        self.assertTrue(self.colony)

    def test_name_property_returns_name_from_the_first_cell(self) -> None:
        """Tests whether the Colony's "name" property returns the first Cell's "colony_name"."""
        self.colony.cells = [Cell(name='1.2.1')]
        self.assertEqual(self.colony.name, '1')
        self.colony.cells = [Cell(name='19.1.1')]
        self.assertEqual(self.colony.name, '19')
        self.colony.cells.append(Cell(name='1.2.1'))
        self.assertEqual(self.colony.name, '19')

    def test_name_property_returns_none_if_colony_is_empty(self) -> None:
        """Tests whether the "name" property returns None if the Colony has no Cells in it."""
        self.assertIsNone(Colony().name)

    def test_center_property_returns_the_colony_average_xy_coordinate(self) -> None:
        """Tests whether the "center" property returns the Colony's  "average" XY coordinate, considering its Cells."""
        self.colony.cells.append(Cell(x=0, y=10))
        self.assertEqual(self.colony.center, (0, 10))
        self.colony.cells.append(Cell(x=10, y=32))
        self.assertEqual(self.colony.center, (5, 21))
        self.colony.cells.append(Cell(x=50, y=21))
        self.assertEqual(self.colony.center, (20, 21))

    def test_center_property_returns_none_if_colony_is_empty(self) -> None:
        """Tests whether the "center" property returns None if the Colony has no Cells in it."""
        self.assertIsNone(Colony().center)

    def test_is_dead_returns_true_if_colony_is_empty(self) -> None:
        """Tests whether the "is_dead" method returns False if the Colony has no Cells in it."""
        self.assertTrue(Colony(cells=[]).is_dead())

    def test_is_dead_returns_true_when_all_cells_in_it_are_dead(self) -> None:
        """Tests whether the "is_dead" method returns True only if all Cells in the Colony are dead."""
        for _ in range(5):
            cell = Cell()
            self.colony.cells.append(cell)
            self.assertFalse(self.colony.is_dead())
            cell.die()
            self.assertTrue(self.colony.is_dead())

    def test_signal_mean_method_returns_the_mean_across_all_cell_signals(self) -> None:
        """Tests whether the Colony "signal_mean" property returns the Signal mean across all Cells in the Colony."""
        signal_values = [1.0, 0.5, 0.0, -0.5, -1.0]
        self.colony.cells = [
            Cell(signal=ConstantCellSignal(initial_value=initial_value))
            for initial_value in signal_values
        ]
        self.assertEqual(self.colony.signal_mean(), np.mean(signal_values))

    def test_signal_std_method_returns_the_mean_across_all_cell_signals(self) -> None:
        """
        Tests whether the Colony "signal_std" property returns the Signal standard deviation
        across all Cells in the Colony.
        """
        signal_values = [1.0, 0.5, 0.0, -0.5, -1.0]
        self.colony.cells = [
            Cell(signal=ConstantCellSignal(initial_value=initial_value))
            for initial_value in signal_values
        ]
        self.assertEqual(self.colony.signal_std(), np.std(signal_values))

    @unittest.skipIf(SKIP_TESTS is True, "SKIP TESTS is set to True")
    def test_pass_time_method_(self) -> None:
        """Docstring."""
        self.fail('Write the test!')


if __name__ == '__main__':
    unittest.main()
