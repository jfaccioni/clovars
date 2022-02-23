import unittest
from unittest import mock
from unittest.mock import MagicMock

from clovars._deprecated.combined.run_and_view_simulation import run_and_view_simulation


@unittest.skip("Deprecated module")
class TestRunAndViewSimulation(unittest.TestCase):
    """Class representing unit-tests of the clovars.simulation.combined.run_and_view_simulation module."""

    @mock.patch('clovars.simulation.combined.run_and_view_simulation.view_simulation_function')
    @mock.patch('clovars.simulation.combined.run_and_view_simulation.run_simulation_function')
    def test_run_and_view_simulation_function_calls_run_simulation_and_view_simulation_functions(
            self,
            mock_run_simulation: MagicMock,
            mock_view_simulation: MagicMock,
    ) -> None:
        """
        Tests whether the "run_and_view_simulation" function calls both the
        "run_simulation" and "view_simulation" functions.
        """
        run_and_view_simulation()
        mock_run_simulation.assert_called_once()
        mock_view_simulation.assert_called_once()


if __name__ == '__main__':
    unittest.main()
