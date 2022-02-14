import unittest
from unittest import mock

from clovars.bio import Cell, Colony, Treatment
from clovars.IO import ColonyLoader
from tests import NotEmptyTestCase


class TestColonyLoader(NotEmptyTestCase):
    """Class representing unit-tests for clovars.IO.colony_loader.ColonyLoader class."""

    def setUp(self) -> None:
        """Sets up the test case subject (a ColonyLoader instance)."""
        self.colony_loader = ColonyLoader()

    def test_colony_loader_has_default_class_attribute(self) -> None:
        """Tests whether a ColonyLoader has the expected default class attributes."""
        for class_attr_name in ['default_cell_radius', 'default_cell_max_speed', 'default_fitness_memory']:
            self.assertTrue(hasattr(ColonyLoader, class_attr_name))
            self.assertIsInstance(getattr(ColonyLoader, class_attr_name), float)

    def test_colony_loader_has_colonies_attribute(self) -> None:
        """Tests whether a ColonyLoader has a "colonies" attribute (a list)."""
        self.assertTrue(hasattr(self.colony_loader, 'colonies'))
        self.assertIsInstance(self.colony_loader.colonies, list)

    def test_colony_loader_instantiation_calls_parse_colony_data_if_colony_data_is_truthy(self) -> None:
        """
        Tests whether a ColonyLoader calls the "parse_colony_data" upon initialization
        if the "colony_data" argument is truthy.
        """
        for falsy_value in [[], None]:
            with mock.patch('clovars.IO.ColonyLoader.parse_colony_data') as mock_parse_colony_data:
                ColonyLoader(colony_data=falsy_value)
                mock_parse_colony_data.assert_not_called()
        for truthy_value in [[{'colonies_here': 0}], [{'colonies_here': 1, 'more colonies!': 2}]]:
            with mock.patch('clovars.IO.ColonyLoader.parse_colony_data') as mock_parse_colony_data:
                ColonyLoader(colony_data=truthy_value)
                mock_parse_colony_data.assert_called_once_with(colony_data=truthy_value)

    def test_parse_colony_data_appends_to_the_colony_list(self) -> None:
        """Tests whether the "parse_colony_data" method appends Colonies to the Colonies list."""
        self.assertEqual(len(self.colony_loader.colonies), 0)
        with mock.patch('clovars.IO.ColonyLoader.create_colony'):
            self.colony_loader.parse_colony_data(colony_data=[{'copies': 1}])
        self.assertEqual(len(self.colony_loader.colonies), 1)

    def test_parse_colony_data_appends_multiple_copies(self) -> None:
        """Tests whether the "parse_colony_data" method appends one Colony for each copy in the "colony_data"."""
        with mock.patch('clovars.IO.ColonyLoader.create_colony'):
            for i in range(5):
                with self.subTest(i=i):
                    colony_loader = ColonyLoader()
                    colony_loader.parse_colony_data(colony_data=[{'copies': i}])
                    self.assertEqual(len(colony_loader.colonies), i)

    def test_parse_colony_data_appends_all_colonies_in_list(self) -> None:
        """Tests whether the "parse_colony_data" method appends one Colony for each dictionary in the "colony_data"."""
        with mock.patch('clovars.IO.ColonyLoader.create_colony'):
            for i in range(1, 5):
                colony_loader = ColonyLoader()
                colony_loader.parse_colony_data(colony_data=[{'copies': i}, {'copies': i*2}, {'copies': i*3}])
                self.assertEqual(len(colony_loader.colonies), i + (i*2) + (i*3))

    def test_get_colony_treatment_regimen_returns_a_dictionary(self) -> None:
        """
        Tests whether the "get_colony_treatment_regimen" method returns a dictionary
        with integers as keys and Treatment instances as values.
        """
        treatment_data = {
            0: {}
        }
        return_value = self.colony_loader.get_colony_treatment_regimen(treatment_data=treatment_data)
        self.assertIsInstance(return_value, dict)
        with self.assertSequenceNotEmpty(return_value):
            for key, value in return_value.items():
                self.assertIsInstance(key, int)
                self.assertIsInstance(value, Treatment)

    def test_get_colony_treatment_regimen_instantiates_one_treatment_per_pair(self) -> None:
        """
        Tests whether the "get_colony_treatment_regimen" method creates one treatment
        for each key-value pair in the treatment_data dictionary.
        """
        treatment_data = {}
        for i in range(5):
            treatment_data[i] = {}
            return_value = self.colony_loader.get_colony_treatment_regimen(treatment_data=treatment_data)
            self.assertEqual(len(return_value), i+1)

    def test_get_colony_treatment_regimen_returns_empty_dict_when_treatment_data_is_empty(self) -> None:
        """
        Tests whether the "get_colony_treatment_regimen" method returns an empty dictionary
        when the provided treatment data is empty.
        """
        return_value = self.colony_loader.get_colony_treatment_regimen(treatment_data={})
        self.assertEqual(return_value, {})

    def test_create_colony_returns_a_colony(self) -> None:
        """Tests whether the "create_colony" method returns a Colony instance."""
        with mock.patch('clovars.IO.ColonyLoader.create_cell'):
            return_value = self.colony_loader.create_colony(
                colony_index=0,
                repeat_label='',
                cell_data={},
                initial_size=1,
                treatment_regimen={},
            )
        self.assertIsInstance(return_value, Colony)

    def test_create_colony_initial_size_determines_colony_size(self) -> None:
        """Tests whether the "create_colony" method returns a Colony with "initial_size" number of Cells."""
        with mock.patch('clovars.IO.ColonyLoader.create_cell'):
            for i in range(5):
                created_colony = self.colony_loader.create_colony(
                    colony_index=0,
                    repeat_label='',
                    cell_data={},
                    initial_size=i,
                    treatment_regimen={},
                )
            self.assertEqual(len(created_colony), i)

    def test_create_cell_returns_a_cell(self) -> None:
        """Tests whether the "create_cell" method returns a Cell instance."""
        return_value = self.colony_loader.create_cell(cell_data={}, colony_index=0, repeat_label='', cell_index=0)
        self.assertIsInstance(return_value, Cell)

    def test_create_cell_uses_default_values(self) -> None:
        """Tests whether the "create_cell" properly uses default values if they're not in the "cell_data" dictionary."""
        returned_cell = self.colony_loader.create_cell(cell_data={}, colony_index=0, repeat_label='', cell_index=0)
        for attr_name in ['max_speed', 'radius']:
            with self.subTest(attr_name=attr_name):
                self.assertEqual(getattr(returned_cell, attr_name), getattr(ColonyLoader, f'default_cell_{attr_name}'))

    def test_create_cell_uses_values_from_cell_data(self) -> None:
        """Tests whether the "create_cell" properly uses the values from the "cell_data" dictionary, when provided."""
        for cell_data in [
            {'max_speed': 0.5},
            {'radius': 1.5},
            {'max_speed': 2.5, 'radius': 3.5},
            {'max_speed': 2.5, 'fitness_memory': 0.2},
            {'max_speed': 2.5, 'radius': 4.7, 'fitness_memory': 0.49},
        ]:
            returned_cell = self.colony_loader.create_cell(
                cell_data=cell_data,
                colony_index=0,
                repeat_label='',
                cell_index=0,
            )
            for attr_name, attr_value in cell_data.items():
                with self.subTest(cell_data=cell_data, attr_name=attr_name, attr_value=attr_value):
                    self.assertEqual(getattr(returned_cell, attr_name), attr_value)

    def test_create_cell_uses_signal_dict_for_calling_get_cell_signal(self) -> None:
        """Tests whether the "create_cell" properly uses the "signal" subdict for calling "get_cell_signal"."""
        for cell_data in [
            {'max_speed': 0.5, 'signal': {'thing': 1, 'another stuff': False}},
            {'radius': 1.5, 'signal': {'thing': 0, 'another!!!': None}},
            {'max_speed': 2.5, 'radius': 3.5, 'fitness_memory': 0.35, 'signal': {'thing': 1.05, '???': True}},
        ]:
            with mock.patch('clovars.IO.colony_loader.get_cell_signal') as mock_get_cell_signal:
                self.colony_loader.create_cell(cell_data=cell_data, colony_index=0, repeat_label='', cell_index=0)
                mock_get_cell_signal.assert_called_once_with(**cell_data['signal'])

    def test_create_cell_combines_arguments_into_cell_name(self) -> None:
        """Tests whether the "create_cell" properly uses its arguments to define the Cell name."""
        cell = self.colony_loader.create_cell(cell_data={}, colony_index=1, repeat_label='Foo', cell_index=2)
        self.assertEqual(cell.name, '1Foo-2')


if __name__ == '__main__':
    unittest.main()
