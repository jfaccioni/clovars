import unittest
from unittest import mock
from unittest.mock import MagicMock

from clovars.simulation import run_simulation_function
from clovars.utils import SimulationError


@mock.patch('clovars.simulation.run.run_simulation.SimulationWriter')  # do not write output!
class TestRunSimulation(unittest.TestCase):
    """Class representing unit-tests of the run_simulation module."""
    mock_run_settings = {
        'delta': 3600,
        'stop_conditions': {}
    }

    def test_run_simulation_function_runs_with_run_settings(
            self,
            _: MagicMock,
    ) -> None:
        """
        Tests whether the "run_simulation" function runs as long as the
        "run_settings" dictionary has appropriate values.
        """
        try:
            run_simulation_function(simulation_runner_settings=self.mock_run_settings)
        except Exception as e:
            self.fail(f'function "run_simulation" could not execute, error raised: {e}')

    def test_run_simulation_function_raises_exception_if_proper_run_settings_are_not_provided(
            self,
            _: MagicMock,
    ) -> None:
        """
        Tests whether the "run_simulation" function raises a SimulationError Exception
        if one of the necessary arguments in "run_settings" are not present.
        """
        for bad_kwargs in [
            {},
            {'delta': 'NOT AN INTEGER'},
            {'stop_conditions': 'NOT A DICT'},
            {'delta': 'NOT AN INTEGER', 'stop_conditions': {}},
            {'delta': 3600, 'stop_conditions': 'NOT A DICT'},
            {'delta': 'NOT AN INTEGER', 'stop_conditions': 'NOT A DICT'},
        ]:
            with self.subTest(bad_kwargs=bad_kwargs):
                with self.assertRaises(SimulationError):
                    run_simulation_function(simulation_runner_settings=bad_kwargs)

    def test_run_simulation_function_instantiates_a_cell_loader_instance(
            self,
            _: MagicMock,
    ) -> None:
        """Tests whether the "run_simulation" function instantiates a ColonyLoader instance."""
        with mock.patch('clovars.simulation.run.run_simulation.ColonyLoader') as mock_colony_loader:
            run_simulation_function(simulation_runner_settings=self.mock_run_settings)
        mock_colony_loader.assert_called_once()

    def test_run_simulation_function_instantiates_a_well_loader_instance(
            self,
            _: MagicMock,
    ) -> None:
        """Tests whether the "run_simulation" function instantiates a WellLoader instance."""
        with mock.patch('clovars.simulation.run.run_simulation.WellLoader') as mock_well_loader:
            run_simulation_function(simulation_runner_settings=self.mock_run_settings)
        mock_well_loader.assert_called_once()

    @mock.patch('clovars.simulation.run.run_simulation.ColonyLoader')
    def test_run_simulation_function_calls_set_initial_colonies_method(
            self,
            mock_colony_loader: MagicMock,
            _: MagicMock,
    ) -> None:
        """
        Tests whether the "run_simulation" function calls the Well's "set_initial_colonies" method
        with the ColonyLoader's colonies.
        """
        with mock.patch('clovars.bio.Well.set_initial_colonies') as mock_set_initial_colonies:
            run_simulation_function(simulation_runner_settings=self.mock_run_settings)
        mock_set_initial_colonies.assert_called_once_with(mock_colony_loader.return_value.colonies)

    def test_run_simulation_function_instantiates_a_simulation_writer_instance(
            self,
            mock_simulation_writer: MagicMock,
    ) -> None:
        """Tests whether the "run_simulation" function instantiates a SimulationWriter instance."""
        run_simulation_function(simulation_runner_settings=self.mock_run_settings)
        mock_simulation_writer.assert_called_once()

    def test_run_simulation_function_calls_set_files_method(
            self,
            mock_simulation_writer: MagicMock,
    ) -> None:
        """Tests whether the "run_simulation" function calls the SimulationWriter's "set_files" method."""
        run_simulation_function(simulation_runner_settings=self.mock_run_settings)
        mock_simulation_writer.return_value.set_files.assert_called_once()

    def test_run_simulation_function_calls_write_params_method(
            self,
            mock_simulation_writer: MagicMock,
    ) -> None:
        """Tests whether the "run_simulation" function calls the SimulationWriter's "write_params" method."""
        run_simulation_function(simulation_runner_settings=self.mock_run_settings)
        mock_simulation_writer.return_value.write_params.assert_called_once()

    def test_run_simulation_function_instantiates_a_simulation_runner_instance(
            self,
            _: MagicMock,
    ) -> None:
        """Tests whether the "run_simulation" function instantiates a SimulationRunner instance."""
        with mock.patch('clovars.simulation.run.run_simulation.SimulationRunner') as mock_simulation_runner:
            run_simulation_function(simulation_runner_settings=self.mock_run_settings)
        mock_simulation_runner.assert_called_once()

    def test_run_simulation_function_calls_run_method(
            self,
            _: MagicMock,
    ) -> None:
        """Tests whether the "run_simulation" function calls the SimulationRunner's "run" method."""
        with mock.patch('clovars.simulation.SimulationRunner.run') as mock_run:
            run_simulation_function(simulation_runner_settings=self.mock_run_settings)
        mock_run.assert_called_once()


if __name__ == '__main__':
    unittest.main()
