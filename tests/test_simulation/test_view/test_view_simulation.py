import unittest
from unittest import mock
from unittest.mock import MagicMock

from clovars.simulation import view_simulation_function
from tests import SKIP_TESTS


@mock.patch('clovars.simulation.view.view_simulation.SimulationLoader')  # do not actually attempt to load data!
class TestViewSimulation(unittest.TestCase):
    """Class representing unit-tests of the view_simulation module."""

    def test_view_simulation_function_runs_without_arguments(
            self,
            _: MagicMock,
    ) -> None:
        """Tests whether the "view_simulation" function runs without any arguments."""
        try:
            view_simulation_function()
        except Exception as e:
            self.fail(f'function "view_simulation" could not execute, error raised: {e}')

    def test_view_simulation_function_instantiates_a_simulation_loader_instance(
            self,
            mock_simulation_loader: MagicMock,
    ) -> None:
        """Tests whether the "view_simulation" function instantiates a SimulationLoader instance."""
        view_simulation_function()
        mock_simulation_loader.assert_called_once()

    def test_view_simulation_function_instantiates_a_simulation_analyzer_instance(
            self,
            _: MagicMock,
    ) -> None:
        """Tests whether the "view_simulation" function instantiates a SimulationViewer instance."""
        with mock.patch('clovars.simulation.view.view_simulation.SimulationViewer') as mock_simulation_viewer:
            view_simulation_function()
        mock_simulation_viewer.assert_called_once()

    def test_view_simulation_function_calls_analyse_method(
            self,
            _: MagicMock,
    ) -> None:
        """Tests whether the "view_simulation" function calls the SimulationViewer's "generate_output" method."""
        with mock.patch('clovars.simulation.SimulationViewer.generate_output') as mock_gen_output:
            view_simulation_function()
        mock_gen_output.assert_called_once()

    @unittest.skipIf(SKIP_TESTS is True, "SKIP TESTS is set to True")
    def test_view_simulation_function_removes_view_dir_if_it_is_empty(self) -> None:
        self.fail("Write the test!")


if __name__ == '__main__':
    unittest.main()
