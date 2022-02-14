import unittest
from pathlib import Path
from unittest import mock

from clovars.bio import Cell, Colony, Well
from clovars.IO import SimulationWriter
from clovars.utils import PathCreatorMixin


class TestSimulationWriter(unittest.TestCase):
    """Class representing unit-tests for clovars.IO.simulation_writer.SimulationWriter class."""
    default_output_folder = Path('SimulationWriter_TEST_FOLDER')
    default_delta = 3600
    default_current_frame = 1
    default_stop_conditions = {}

    @classmethod
    def setUpClass(cls) -> None:
        """Sets up the entire test suite by instantiating a Well."""
        well = Well(x=100, y=100, radius=100)
        colony = Colony(cells=[Cell() for _ in range(3)])
        well.set_initial_colonies(initial_colonies=[colony])
        cls.well = well

    @classmethod
    def tearDownClass(cls) -> None:
        """Tears down the entire test suite by deleting the test output folder."""
        if cls.default_output_folder.exists():
            cls.default_output_folder.rmdir()

    def setUp(self) -> None:
        """Sets up the test case subject (a SimulationWriter instance)."""
        settings = {
            'output_folder': self.default_output_folder,
            'warn_on_overwrite': False,  # Do not warn during tests
        }
        self.simulation_writer = SimulationWriter(settings=settings)

    def tearDown(self) -> None:
        """Tears down each test case by deleting the contents of the output folder."""
        if self.default_output_folder.exists():
            for sub_path in self.default_output_folder.iterdir():
                sub_path.unlink()

    def test_simulation_writer_inherits_from_path_creator_mixin(self) -> None:
        """Tests whether an SimulationWriter is an instance of PathCreatorMixin."""
        self.assertIsInstance(self.simulation_writer, PathCreatorMixin)

    def test_simulation_writer_instance_has_expected_class_attributes(self) -> None:
        """Tests whether an SimulationWriter instance has the expected class attributes (strings)."""
        for expected_class_attr in [
            'cell_csv_header',
            'colony_csv_header',
            'default_output_folder',
            'default_cell_csv_file_name',
            'default_colony_csv_file_name',
            'default_parameters_file_name',
        ]:
            self.assertTrue(hasattr(SimulationWriter, expected_class_attr))
            self.assertIsInstance(getattr(SimulationWriter, expected_class_attr), str)

    def test_simulation_writer_instance_has_path_attributes(self) -> None:
        """Tests whether an SimulationWriter instance has the expected attributes (Path instances)."""
        for expected_class_attr in ['cell_csv_path', 'colony_csv_path', 'parameters_path']:
            self.assertTrue(hasattr(self.simulation_writer, expected_class_attr))
            self.assertIsInstance(getattr(self.simulation_writer, expected_class_attr), Path)

    def test_simulation_writer_instance_has_confirm_overwrite_flag_attribute(self) -> None:
        """Tests whether an SimulationWriter instance has the "confirm_overwrite_flag" attribute (a boolean value)."""
        self.assertTrue(hasattr(self.simulation_writer, 'confirm_overwrite_flag'))
        self.assertIsInstance(self.simulation_writer.confirm_overwrite_flag, bool)

    def test_set_files_calls_refresh_paths_method(self) -> None:
        """Tests whether the "set_files" method calls the "refresh_paths" method."""
        with mock.patch.object(self.simulation_writer, 'refresh_paths') as mock_refresh_paths:
            self.simulation_writer.set_files()
        mock_refresh_paths.assert_called_once()

    def test_set_files_calls_write_cell_csv_header_method(self) -> None:
        """Tests whether the "set_files" method calls the "write_cell_csv_header" method."""
        with mock.patch.object(self.simulation_writer, 'write_cell_csv_header') as mock_write_cell_csv_header:
            self.simulation_writer.set_files()
        mock_write_cell_csv_header.assert_called_once()

    def test_set_files_calls_write_colony_csv_header_method(self) -> None:
        """Tests whether the "set_files" method calls the "write_colony_csv_header" method."""
        with mock.patch.object(self.simulation_writer, 'write_colony_csv_header') as mock_write_colony_csv_header:
            self.simulation_writer.set_files()
        mock_write_colony_csv_header.assert_called_once()

    def test_refresh_paths_does_not_call_refresh_path_if_no_paths_exist_yet(self) -> None:
        """
        Tests whether the "refresh_paths" method does not call the "refresh_path" method if all
        SimulationWriter paths do not point to an existing file in the filesystem.
        """
        self.simulation_writer.cell_csv_path = Path('This_Path/Does_Not/Exist!')
        self.simulation_writer.colony_csv_path = Path('This_Path/Does_Not/Exist?')
        self.simulation_writer.params_path = Path('This_Path/Does_Not/Exist_')
        with mock.patch.object(self.simulation_writer, 'refresh_path') as mock_refresh_path:
            self.simulation_writer.refresh_paths()
        mock_refresh_path.assert_not_called()

    def test_refresh_paths_calls_confirm_overwrite_and_refresh_path_at_least_one_path_exist(self) -> None:
        """
        Tests whether the "refresh_paths" method calls "confirm_overwrite" and "refresh_path" methods
        if at least one SimulationWriter path points to an existing file in the filesystem.
        """
        self.simulation_writer.cell_csv_path = self.default_output_folder / Path('.')
        self.simulation_writer.colony_csv_path = Path('.')
        self.simulation_writer.params_path = Path('.')
        with mock.patch.object(self.simulation_writer, 'refresh_path') as mock_refresh_path:
            with mock.patch.object(self.simulation_writer, 'confirm_overwrite') as mock_confirm_overwrite:
                self.simulation_writer.refresh_paths()
        mock_refresh_path.assert_called()
        mock_confirm_overwrite.assert_called()

    def test_refresh_paths_skips_confirm_overwrite_if_confirm_overwrite_flag_is_false(self) -> None:
        """
        Tests whether the "refresh_paths" skips the call to "confirm_overwrite" if the "confirm_overwrite_flag"
        is set to False.
        """
        self.simulation_writer.cell_csv_path = self.default_output_folder / Path('.')
        self.simulation_writer.colony_csv_path = Path('.')
        self.simulation_writer.params_path = Path('.')
        self.simulation_writer.confirm_overwrite_flag = False
        with mock.patch.object(self.simulation_writer, 'refresh_path') as mock_refresh_path:
            with mock.patch.object(self.simulation_writer, 'confirm_overwrite') as mock_confirm_overwrite:
                self.simulation_writer.refresh_paths()
        mock_refresh_path.assert_called()
        mock_confirm_overwrite.assert_not_called()

    def test_confirm_overwrite_returns_none_if_input_is_y(self) -> None:
        """Tests whether the "confirm_overwrite" method returns None if the input value is "y"."""
        with mock.patch('clovars.IO.simulation_writer.input', return_value='y'):
            self.assertIsNone(self.simulation_writer.confirm_overwrite(existing_paths=[]))

    def test_confirm_overwrite_calls_sys_exit_if_input_is_n(self) -> None:
        """Tests whether the "confirm_overwrite" method calls SystemExit if the input value is "n"."""
        with mock.patch('clovars.IO.simulation_writer.input', return_value='n'):
            with self.assertRaises(SystemExit):
                self.simulation_writer.confirm_overwrite(existing_paths=[])

    def test_confirm_overwrite_keeps_running_until_input_is_valid(self) -> None:
        """Tests whether the "confirm_overwrite" keeps executing until the input is either "y" or "n"."""
        class MockLoopError(Exception):
            pass

        mock_input_return_values = ('invalid', 'DUUUH', '', MockLoopError)
        with mock.patch('clovars.IO.simulation_writer.input', side_effect=mock_input_return_values):
            with self.assertRaises(MockLoopError):  # input was called until MockLoopError was found
                self.simulation_writer.confirm_overwrite(existing_paths=[])

    def test_refresh_path_calls_unlinks_and_touches_path(self) -> None:
        """Tests whether the "refresh_path" properly refreshes the file in the Path object."""
        path = self.default_output_folder / Path('some_file.txt')
        with open(path, 'w') as mock_file:
            mock_file.write('Some content goes here')
        self.simulation_writer.refresh_path(path=path)
        with open(path) as mock_file:
            self.assertEqual(mock_file.read(), '')
        path.unlink()

    def test_write_params_writes_a_json_file_to_the_output_folder(self) -> None:
        """Tests whether the "write_params" method writes a JSON file to the output folder."""
        self.simulation_writer.write_params(
            colony_data=[],
            well_settings={},
            simulation_writer_settings={},
            simulation_runner_settings={},
            verbose=True,
        )
        expected_file_path = self.default_output_folder / self.simulation_writer.default_parameters_file_name
        self.assertTrue(expected_file_path.exists())

    def test_write_cell_csv_header_writes_single_header_row(self) -> None:
        """Tests whether the "write_cell_csv_header" method writes the Cell csv header to a file."""
        self.simulation_writer.write_cell_csv_header()
        with open(self.simulation_writer.cell_csv_path) as csv_file:
            self.assertEqual(self.simulation_writer.cell_csv_header, csv_file.readline())

    def test_write_cells_writes_a_csv_file_to_the_output_folder(self) -> None:
        """Tests whether the "write_cells" method writes a csv file to the output folder."""
        self.assertFalse(self.simulation_writer.cell_csv_path.exists())
        self.simulation_writer.write_cells(
            well=self.well,
            simulation_seconds=self.default_delta,
            current_frame=self.default_current_frame,
        )
        self.assertTrue(self.simulation_writer.cell_csv_path.exists())

    def test_write_cells_method_writes_one_row_per_cell(self) -> None:
        """Tests whether the "write_cells" method writes a csv with one row per each Cell."""
        expected_cell_number = 3
        self.simulation_writer.write_cells(
            well=self.well,
            simulation_seconds=self.default_delta,
            current_frame=self.default_current_frame,
        )
        with open(self.simulation_writer.cell_csv_path) as csv_file:
            self.assertEqual(expected_cell_number, len(csv_file.readlines()))

    def test_cell_as_csv_row_returns_row_with_equal_number_of_columns_to_cell_header(self) -> None:
        """Tests whether the "cell_as_csv_row" method returns a string of equal length to the cell csv header."""
        row = self.simulation_writer.cell_as_csv_row(
            cell=Cell(),
            simulation_seconds=self.default_delta,
            current_frame=self.default_current_frame,
        )
        self.assertIsInstance(row, str)
        self.assertEqual(len(row.split(',')), len(self.simulation_writer.cell_csv_header.split(',')))

    def test_write_colony_csv_header_writes_single_header_row(self) -> None:
        """Tests whether the "write_colony_csv_header" method writes the Colony csv header to a file."""
        self.simulation_writer.write_colony_csv_header()
        with open(self.simulation_writer.colony_csv_path) as csv_file:
            self.assertEqual(self.simulation_writer.colony_csv_header, csv_file.readline())

    def test_write_colonies_writes_a_csv_file_to_the_output_folder(self) -> None:
        """Tests whether the "write_colonies" method writes a csv file to the output folder."""
        self.assertFalse(self.simulation_writer.colony_csv_path.exists())
        self.simulation_writer.write_colonies(
            well=self.well,
            simulation_seconds=self.default_delta,
            current_frame=self.default_current_frame,
        )
        self.assertTrue(self.simulation_writer.colony_csv_path.exists())

    def test_write_colonies_method_writes_one_row_per_colony(self) -> None:
        """Tests whether the "write_colonies" method writes a csv with one row per each Cell."""
        expected_colony_number = 1
        self.simulation_writer.write_colonies(
            well=self.well,
            simulation_seconds=self.default_delta,
            current_frame=self.default_current_frame,
        )
        with open(self.simulation_writer.colony_csv_path) as csv_file:
            self.assertEqual(expected_colony_number, len(csv_file.readlines()))

    def test_colony_as_csv_row_returns_row_with_equal_number_of_columns_to_colony_header(self) -> None:
        """Tests whether the "colony_as_csv_row" method returns a string of equal length to the colony csv header."""
        row = self.simulation_writer.colony_as_csv_row(
            colony=Colony(),
            simulation_seconds=self.default_delta,
            current_frame=self.default_current_frame,
        )
        self.assertIsInstance(row, str)
        self.assertEqual(len(row.split(',')), len(self.simulation_writer.colony_csv_header.split(',')))


if __name__ == '__main__':
    unittest.main()
