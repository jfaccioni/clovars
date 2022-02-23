import unittest
from unittest import mock
from unittest.mock import MagicMock

from clovars._deprecated.combined.run_view_analyse_simulation import run_view_analyse_simulation


@unittest.skip("Deprecated module")
class TestRunViewAnalyseSimulation(unittest.TestCase):
    """Class representing unit-tests of the clovars.simulation.combined.run_view_analyse_simulation module."""

    @mock.patch('clovars.simulation.combined.run_view_analyse_simulation.analyse_simulation_function')
    @mock.patch('clovars.simulation.combined.run_view_analyse_simulation.view_simulation_function')
    @mock.patch('clovars.simulation.combined.run_view_analyse_simulation.run_simulation_function')
    def test_run_view_analyse_simulation_function_calls_run_simulation_view_simulation_and_analyse_simulation_functions(
            self,
            mock_run_simulation: MagicMock,
            mock_view_simulation: MagicMock,
            mock_analyse_simulation: MagicMock,
    ) -> None:
        """
        Tests whether the "run_and_analyse_simulation" function calls the
        "run_simulation", "view_simulation" and "analyse_simulation" functions.
        """
        run_view_analyse_simulation()
        mock_run_simulation.assert_called_once()
        mock_view_simulation.assert_called_once()
        mock_analyse_simulation.assert_called_once()


if __name__ == '__main__':
    unittest.main()
