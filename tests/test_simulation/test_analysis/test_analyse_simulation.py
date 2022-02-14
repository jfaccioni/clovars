import unittest
from unittest import mock
from unittest.mock import MagicMock

from clovars.simulation import analyse_simulation_function


@mock.patch('clovars.simulation.analysis.analyse_simulation.SimulationLoader')  # do not actually attempt to load data!
class TestAnalyseSimulation(unittest.TestCase):
    """Class representing unit-tests of the clovars.analyse_simulation module."""

    def test_analyse_simulation_function_runs_without_any_arguments(
            self,
            _: MagicMock,
    ) -> None:
        """Tests whether the "analyse_simulation" function runs without_any_arguments."""
        try:
            analyse_simulation_function()
        except Exception as e:
            self.fail(f'function "analyse_simulation" could not execute, error raised: {e}')

    def test_analyse_simulation_function_instantiates_a_simulation_loader_instance(
            self,
            mock_simulation_loader: MagicMock,
    ) -> None:
        """Tests whether the "analyse_simulation" function instantiates a SimulationLoader instance."""
        analyse_simulation_function()
        mock_simulation_loader.assert_called_once()

    def test_analyse_simulation_function_instantiates_a_simulation_analyzer_instance(
            self,
            _: MagicMock,
    ) -> None:
        """Tests whether the "analyse_simulation" function instantiates a SimulationAnalyzer instance."""
        with mock.patch('clovars.simulation.analysis.analyse_simulation.SimulationAnalyzer') as mock_sim_analyzer:
            analyse_simulation_function()
        mock_sim_analyzer.assert_called_once()

    def test_analyse_simulation_function_calls_analyse_method(
            self,
            _: MagicMock,
    ) -> None:
        """Tests whether the "analyse_simulation" function calls the SimulationAnalyzer's "analyse" method."""
        with mock.patch('clovars.simulation.analysis.analyse_simulation.SimulationAnalyzer.analyse') as mock_analyse:
            analyse_simulation_function()
        mock_analyse.assert_called_once()


if __name__ == '__main__':
    unittest.main()
