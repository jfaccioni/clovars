import unittest
from unittest import mock
from unittest.mock import MagicMock

from clovars._deprecated.combined.run_and_analyse_simulation import run_and_analyse_simulation


@unittest.skip("Deprecated module")
class TestRunAndAnalyseSimulation(unittest.TestCase):
    """Class representing unit-tests of the clovars.simulation.combined.run_and_analyse_simulation module."""

    @mock.patch('clovars.simulation.combined.run_and_analyse_simulation.analyse_simulation_function')
    @mock.patch('clovars.simulation.combined.run_and_analyse_simulation.run_simulation_function')
    def test_run_and_analyse_simulation_function_calls_run_simulation_and_analyse_simulation_functions(
            self,
            mock_run_simulation_function: MagicMock,
            mock_analyse_simulation_function: MagicMock,
    ) -> None:
        """
        Tests whether the "run_and_analyse_simulation" function calls both the
        "run_simulation" and "analyse_simulation" functions.
        """
        run_and_analyse_simulation()
        mock_run_simulation_function.assert_called_once()
        mock_analyse_simulation_function.assert_called_once()


if __name__ == '__main__':
    unittest.main()
