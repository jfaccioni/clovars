import unittest
from pathlib import Path
from unittest import mock
from unittest.mock import MagicMock

import pandas as pd

from clovars.bio import Treatment
from clovars.IO import SimulationLoader
from tests import NotEmptyTestCase


class TestSimulationLoader(NotEmptyTestCase):
    """Class representing unit-tests for clovars.IO.simulation_loader.SimulationLoader class."""
    mock_dataframe = pd.DataFrame({'colony_name': [1, 2, 3], 'name': [4, 5, 6]})
    mock_treatment_data = {
        0: {
            'name': 'Control',
            'division_curve': {
                'name': 'Gamma',
                'mean': 0.00,
                'std': 0.90,
                'a': 28.47,
            },
            'death_curve': {
                'name': 'Gaussian',
                'mean': 100.00,
                'std': 1.00,
            },
            'signal_disturbance': None,
        },
    }
    mock_params = {
        'simulation_runner_settings': {
            'delta': 3600,
        },
        'colony_data': [
            {
                'treatment_data': mock_treatment_data,
            }
        ],
        'well_settings': {
            'well_radius': 10.0,
        },
    }

    def setUp(self) -> None:
        """Sets up the test case subject (a SimulationLoader instance)."""
        self.simulation_loader = SimulationLoader()

    def test_simulation_loader_has_default_class_attribute(self) -> None:
        """Tests whether a SimulationLoader has the expected default class attributes."""
        for class_attr_name in [
            'default_simulation_input_folder',
            'default_cell_csv_file_name',
            'default_colony_csv_file_name',
            'default_parameters_file_name',
        ]:
            self.assertTrue(hasattr(SimulationLoader, class_attr_name))
            self.assertIsInstance(getattr(SimulationLoader, class_attr_name), str)

    def test_simulation_loader_has_expected_path_attributes(self) -> None:
        """Tests whether a SimulationLoader has the expected path attributes (Path instances)."""
        for attr_name in ['cell_data_path', 'colony_data_path', 'params_path']:
            self.assertTrue(hasattr(self.simulation_loader, attr_name))
            self.assertIsInstance(getattr(self.simulation_loader, attr_name), Path)

    def test_simulation_loader_protected_attributes_start_as_none(self) -> None:
        """Tests whether a SimulationLoader has the expected protected attributes (that start as None)."""
        for attr_name in ['_cell_data', '_colony_data', '_params']:
            self.assertTrue(hasattr(self.simulation_loader, attr_name))
            self.assertIsInstance(getattr(self.simulation_loader, attr_name), type(None))

    def test_cell_data_property_returns_a_pandas_dataframe(self) -> None:
        """Tests whether the "cell_data" property returns a pandas DataFrame."""
        with mock.patch('clovars.IO.simulation_loader.pd.read_csv', return_value=self.mock_dataframe.copy()):
            returned_value = self.simulation_loader.cell_data
            self.assertIsInstance(returned_value, pd.DataFrame)

    def test_cell_data_property_only_calls_load_cell_data_if_it_is_none(self) -> None:
        """Tests whether the "cell_data" property only calls "load_cell_data" if its protected value is None."""
        self.simulation_loader._cell_data = "This value is not None!"
        with mock.patch('clovars.IO.SimulationLoader.load_cell_data') as mock_load_cell_data:
            self.simulation_loader.cell_data  # noqa
        mock_load_cell_data.assert_not_called()
        self.simulation_loader._cell_data = None
        with mock.patch('clovars.IO.SimulationLoader.load_cell_data') as mock_load_cell_data:
            self.simulation_loader.cell_data  # noqa
        mock_load_cell_data.assert_called_once()

    def test_load_cell_data_returns_a_pandas_dataframe(self) -> None:
        """Tests whether the "load_cell_data" method returns a pandas DataFrame."""
        with mock.patch('clovars.IO.simulation_loader.pd.read_csv', return_value=self.mock_dataframe.copy()):
            returned_value = self.simulation_loader.load_cell_data()
            self.assertIsInstance(returned_value, pd.DataFrame)

    def test_load_cell_data_changes_dtype_of_colony_name_column(self) -> None:
        """Tests whether the "load_cell_data" method converts the "colony_name" column to string."""
        df = self.mock_dataframe.copy()
        for element in df['colony_name']:
            self.assertIsInstance(element, int)
        with mock.patch('clovars.IO.simulation_loader.pd.read_csv', return_value=df):
            self.simulation_loader.load_cell_data()
        for element in df['colony_name']:
            self.assertIsInstance(element, str)

    def test_colony_data_property_returns_a_pandas_dataframe(self) -> None:
        """Tests whether the "colony_data" property returns a pandas DataFrame."""
        with mock.patch('clovars.IO.simulation_loader.pd.read_csv', return_value=self.mock_dataframe.copy()):
            returned_value = self.simulation_loader.colony_data
            self.assertIsInstance(returned_value, pd.DataFrame)

    def test_colony_data_property_only_calls_load_colony_data_if_it_is_none(self) -> None:
        """Tests whether the "colony_data" property only calls "load_colony_data" if its protected value is None."""
        self.simulation_loader._colony_data = "This value is not None!"
        with mock.patch('clovars.IO.SimulationLoader.load_colony_data') as mock_load_colony_data:
            self.simulation_loader.colony_data  # noqa
        mock_load_colony_data.assert_not_called()
        self.simulation_loader._colony_data = None
        with mock.patch('clovars.IO.SimulationLoader.load_colony_data') as mock_load_colony_data:
            self.simulation_loader.colony_data  # noqa
        mock_load_colony_data.assert_called_once()

    def test_load_colony_data_returns_a_pandas_dataframe(self) -> None:
        """Tests whether the "load_colony_data" method returns a pandas DataFrame."""
        with mock.patch('clovars.IO.simulation_loader.pd.read_csv', return_value=self.mock_dataframe.copy()):
            returned_value = self.simulation_loader.load_colony_data()
            self.assertIsInstance(returned_value, pd.DataFrame)

    def test_load_colony_data_changes_dtype_of_name_column(self) -> None:
        """Tests whether the "load_colony_data" method converts the "name" column to string."""
        df = self.mock_dataframe.copy()
        for element in df['name']:
            self.assertIsInstance(element, int)
        with mock.patch('clovars.IO.simulation_loader.pd.read_csv', return_value=df):
            self.simulation_loader.load_colony_data()
        for element in df['name']:
            self.assertIsInstance(element, str)

    @mock.patch('clovars.IO.simulation_loader.open')  # do not attempt to open the file!
    def test_params_property_returns_a_dictionary(
            self,
            _: MagicMock,
    ) -> None:
        """Tests whether the "params" property returns a dictionary."""
        with mock.patch('clovars.IO.simulation_loader.json.loads', return_value=self.mock_params):
            returned_value = self.simulation_loader.params
            self.assertIsInstance(returned_value, dict)

    @mock.patch('clovars.IO.simulation_loader.open')  # do not attempt to open the file!
    def test_params_property_only_calls_load_params_if_it_is_none(
            self,
            _: MagicMock,
    ) -> None:
        """Tests whether the "params" property only calls "load_params" if its protected value is None."""
        self.simulation_loader._params = "This value is not None!"
        with mock.patch('clovars.IO.SimulationLoader.load_params') as mock_load_params:
            self.simulation_loader.params  # noqa
        mock_load_params.assert_not_called()
        self.simulation_loader._params = None
        with mock.patch('clovars.IO.SimulationLoader.load_params') as mock_load_params:
            self.simulation_loader.params  # noqa
        mock_load_params.assert_called_once()

    @mock.patch('clovars.IO.simulation_loader.open')  # do not attempt to open the file!
    def test_load_params_returns_a_dictionary(
            self,
            _: MagicMock,
    ) -> None:
        """Tests whether the "load_params" method returns a dictionary."""
        with mock.patch('clovars.IO.simulation_loader.json.loads', return_value=self.mock_params):
            returned_value = self.simulation_loader.load_params()
            self.assertIsInstance(returned_value, dict)

    @mock.patch('clovars.IO.simulation_loader.open')  # do not attempt to open the file!
    def test_delta_property_returns_int_from_params_dictionary(
            self,
            _: MagicMock,
    ) -> None:
        """Tests whether the "delta" property returns an int from the "params" dictionary."""
        with mock.patch('clovars.IO.simulation_loader.json.loads', return_value=self.mock_params):
            self.assertIsInstance(self.simulation_loader.delta, int)
            self.assertEqual(self.simulation_loader.delta, 3600)

    def test_treatments_property_only_calls_load_treatments_if_it_is_none(self) -> None:
        """Tests whether the "treatments" property only calls "load_treatments" if its protected value is None."""
        self.simulation_loader._treatments = "This value is not None!"
        with mock.patch('clovars.IO.SimulationLoader.load_treatments') as mock_load_treatments:
            self.simulation_loader.treatments  # noqa
        mock_load_treatments.assert_not_called()
        self.simulation_loader._treatments = None
        with mock.patch('clovars.IO.SimulationLoader.load_treatments') as mock_load_treatments:
            self.simulation_loader.treatments  # noqa
        mock_load_treatments.assert_called_once()

    @mock.patch('clovars.IO.simulation_loader.open')  # do not attempt to open the file!
    def test_load_treatments_returns_dict_with_proper_structure(
            self,
            _: MagicMock,
    ) -> None:
        """
        Tests whether the "load_treatments" method returns a dictionary with the expected structure:
        { (colony_name_prefix, treatment_frame): Treatment_instance }.
        """
        with mock.patch('clovars.IO.simulation_loader.json.loads', return_value=self.mock_params):
            with mock.patch('clovars.IO.simulation_loader.pd.read_csv', return_value=self.mock_dataframe.copy()):
                self.assertIsInstance(self.simulation_loader.treatments, dict)
                with self.assertSequenceNotEmpty(self.simulation_loader.treatments):
                    for key, value in self.simulation_loader.treatments.items():
                        self.assertIsInstance(key, tuple)
                        self.assertIsInstance(key[0], str)
                        self.assertIsInstance(key[1], int)
                        self.assertIsInstance(value, Treatment)

    @mock.patch('clovars.IO.simulation_loader.open')  # do not attempt to open the file!
    def test_well_radius_property_returns_float_from_params_dictionary(
            self,
            _: MagicMock,
    ) -> None:
        """Tests whether the "well_radius" property returns a float from the "params" dictionary."""
        with mock.patch('clovars.IO.simulation_loader.json.loads', return_value=self.mock_params):
            self.assertIsInstance(self.simulation_loader.well_radius, float)
            self.assertEqual(self.simulation_loader.well_radius, 10.0)


if __name__ == '__main__':
    unittest.main()
