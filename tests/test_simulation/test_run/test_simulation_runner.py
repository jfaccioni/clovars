import unittest
from itertools import product
from typing import List
from unittest import mock
from unittest.mock import MagicMock

from clovars.simulation import SimulationRunner
from clovars.utils import QuietPrinterMixin, SimulationError


class TestSimulationRunner(unittest.TestCase):
    """Class representing unit-tests for clovars.simulation_runner.simulation_runner.SimulationRunner class."""

    def setUp(self) -> None:
        """Sets up the test case subject (a SimulationRunner instance)."""
        self.run_kwargs = {
            'simulation_writer': MagicMock(),
            'well': MagicMock(),
            'settings': {
                'delta': 3600,
                'stop_conditions': {
                    'stop_at_frame': 5,
                    'stop_at_single_colony_size': None,
                    'stop_at_all_colonies_size': None,
                },
            },
        }
        self.simulation_runner = SimulationRunner()

    def test_simulation_runner_inherits_from_quiet_printer_mixin(self) -> None:
        """Tests whether a SimulationRunner inherits from QuietPrinterMixin."""
        self.assertIsInstance(self.simulation_runner, QuietPrinterMixin)

    def test_simulation_runner_has_max_iteration_class_attributes(self) -> None:
        """Tests whether a SimulationRunner has the "max_iteration" class attribute (an integer)."""
        self.assertTrue(hasattr(SimulationRunner, 'max_iteration'))
        self.assertIsInstance(SimulationRunner.max_iteration, int)

    def test_run_method_calls_validate_settings_method(self) -> None:
        """Tests whether the "run" method calls the "validate_settings" method."""
        with mock.patch.object(self.simulation_runner, 'validate_settings') as mock_validate_settings:
            mock_validate_settings.return_value = (
                self.run_kwargs['settings']['delta'],
                self.run_kwargs['settings']['stop_conditions'],
            )  # needs to return a tuple
            self.simulation_runner.run(**self.run_kwargs)
        mock_validate_settings.assert_called()

    def test_run_method_calls_get_simulation_hours_method(self) -> None:
        """Tests whether the "run" method calls the "get_simulation_hours" method."""
        with mock.patch.object(self.simulation_runner, 'get_simulation_hours') as mock_get_simulation_seconds:
            self.simulation_runner.run(**self.run_kwargs)
        mock_get_simulation_seconds.assert_called()

    def test_run_method_calls_get_simulation_seconds_method(self) -> None:
        """Tests whether the "run" method calls the "get_simulation_seconds" method."""
        with mock.patch.object(self.simulation_runner, 'get_simulation_seconds') as mock_get_simulation_seconds:
            self.simulation_runner.run(**self.run_kwargs)
        mock_get_simulation_seconds.assert_called()

    def test_run_method_calls_modify_colony_treatment_regimens_method(self) -> None:
        """Tests whether the "run" method calls the Well's "modify_colony_treatment_regimens"."""
        self.simulation_runner.run(**self.run_kwargs)
        self.run_kwargs['well'].modify_colony_treatment_regimens.assert_called()

    def test_run_method_calls_set_cell_fate_method(self) -> None:
        """Tests whether the "run" method calls the Well's "set_cell_fate"."""
        self.simulation_runner.run(**self.run_kwargs)
        self.run_kwargs['well'].set_cell_fate.assert_called()

    def test_run_method_calls_write_simulation_status_method(self) -> None:
        """Tests whether the "run" method calls the "write_simulation_status" method."""
        with mock.patch.object(self.simulation_runner, 'write_simulation_status') as mock_write_simulation_status:
            self.simulation_runner.run(**self.run_kwargs)
        mock_write_simulation_status.assert_called()

    def test_run_method_calls_reached_stop_condition_method(self) -> None:
        """Tests whether the "run" method calls the "reached_stop_condition" method."""
        with mock.patch.object(self.simulation_runner, 'reached_stop_condition') as mock_reached_stop_condition:
            self.simulation_runner.run(**self.run_kwargs)
        mock_reached_stop_condition.assert_called()

    def test_run_method_calls_pass_time_method_when_stop_condition_is_not_met(self) -> None:
        """Tests whether the "run" method continues its loop while a stop condition is not met."""
        with mock.patch.object(self.simulation_runner, 'reached_stop_condition', return_value=False):
            self.simulation_runner.run(**self.run_kwargs)
        self.run_kwargs['well'].pass_time.assert_called()

    def test_run_method_does_not_call_pass_time_method_when_stop_condition_is_not_met(self) -> None:
        """Tests whether the "run" method breaks its loop when a stop condition is met."""
        with mock.patch.object(self.simulation_runner, 'reached_stop_condition', return_value=True):
            self.simulation_runner.run(**self.run_kwargs)
        self.run_kwargs['well'].pass_time.assert_not_called()

    def test_validate_settings_method_returns_delta_and_stop_conditions(self) -> None:
        """Tests whether the "validate_settings" method returns the delta and stop conditions."""
        return_value = self.simulation_runner.validate_settings(settings=self.run_kwargs['settings'])
        self.assertEqual(return_value[0], self.run_kwargs['settings']['delta'])
        self.assertEqual(return_value[1], self.run_kwargs['settings']['stop_conditions'])

    def test_validate_settings_raises_exception_if_delta_is_not_in_settings(self) -> None:
        """Tests whether the "validate_settings" method raises a SimulationError if the "delta" key is missing."""
        self.run_kwargs['settings'].pop('delta')
        with self.assertRaises(SimulationError):
            self.simulation_runner.validate_settings(settings=self.run_kwargs)

    def test_validate_settings_raises_exception_if_delta_is_not_integer(self) -> None:
        """
        Tests whether the "validate_settings" method raises a SimulationError
        if the "delta" key is not associated to an integer.
        """
        self.run_kwargs['settings']['delta'] = "Not an integer!"  # noqa
        with self.assertRaises(SimulationError):
            self.simulation_runner.validate_settings(settings=self.run_kwargs)

    def test_validate_settings_raises_exception_if_stop_conditions_is_not_in_settings(self) -> None:
        """
        Tests whether the "validate_settings" method raises a SimulationError
        if the "stop_conditions" key is missing.
        """
        self.run_kwargs['settings'].pop('stop_conditions')
        with self.assertRaises(SimulationError):
            self.simulation_runner.validate_settings(settings=self.run_kwargs)

    def test_validate_settings_raises_exception_if_stop_conditions_is_not_dictionary(self) -> None:
        """
        Tests whether the "validate_settings" method raises a SimulationError
        if the "stop_conditions" key is not associated to a dictionary.
        """
        self.run_kwargs['settings']['stop_conditions'] = "Not a dictionary!"  # noqa
        with self.assertRaises(SimulationError):
            self.simulation_runner.validate_settings(settings=self.run_kwargs)

    def test_get_simulation_hours_method_returns_the_correct_simulation_hours(self) -> None:
        """Tests whether the "get_simulation_hours" method properly returns the Simulation time in hours."""
        hour_test_cases = [  # tuples in the order: (delta, current_frame, expected_time)
            (0, 0, 0),
            (1800, 1, 0.5),
            (3600, 2, 2.0),
            (7200, 3, 6.0),
            (180, 10, 0.5),
        ]
        for delta, current_frame, expected_hours in hour_test_cases:
            with self.subTest(delta=delta, current_frame=current_frame, expected_hours=expected_hours):
                actual_hours = self.simulation_runner.get_simulation_hours(delta=delta, current_frame=current_frame)
                self.assertEqual(expected_hours, actual_hours)

    def test_get_simulation_seconds_method_returns_the_correct_simulation_hours(self) -> None:
        """Tests whether the "get_simulation_seconds" method properly returns the Simulation time in seconds."""
        seconds_test_cases = [  # tuples in the order: (delta, current_frame, expected_time)
            (0, 0, 0),
            (1800, 1, 1800),
            (3600, 2, 7200),
            (7200, 3, 21600),
            (180, 10, 1800),
        ]
        for delta, current_frame, expected_seconds in seconds_test_cases:
            with self.subTest(delta=delta, current_frame=current_frame, expected_seconds=expected_seconds):
                actual_seconds = self.simulation_runner.get_simulation_seconds(delta=delta, current_frame=current_frame)
                self.assertEqual(expected_seconds, actual_seconds)

    def test_write_simulation_status_method_calls_write_cells(self) -> None:
        """Tests whether the "write_simulation_status" method calls the SimulationWriter's "write_cells" method."""
        self.simulation_runner.write_simulation_status(
            simulation_writer=self.run_kwargs['simulation_writer'],
            well=self.run_kwargs['well'],
            simulation_seconds=0,
        )
        self.run_kwargs['simulation_writer'].write_cells.assert_called_once_with(
            well=self.run_kwargs['well'],
            simulation_seconds=0,
        )

    def test_write_simulation_status_method_calls_write_colonies(self) -> None:
        """Tests whether the "write_simulation_status" method calls the SimulationWriter's "write_colonies" method."""
        self.simulation_runner.write_simulation_status(
            simulation_writer=self.run_kwargs['simulation_writer'],
            well=self.run_kwargs['well'],
            simulation_seconds=0,
        )
        self.run_kwargs['simulation_writer'].write_colonies.assert_called_once_with(
            well=self.run_kwargs['well'],
            simulation_seconds=0,
        )

    @mock.patch('clovars.simulation.SimulationRunner.reached_all_colonies_size_limit')
    @mock.patch('clovars.simulation.SimulationRunner.reached_single_colony_size_limit')
    @mock.patch('clovars.simulation.SimulationRunner.reached_frame_limit')
    def test_reached_stop_condition_method_returns_true_if_at_least_one_stop_condition_is_met(
            self,
            *mocks: List[MagicMock],
    ) -> None:
        """Tests if the "reached_stop_condition" method returns True if at least one stop condition is met."""
        bool_values_grid = list(product([True, False], repeat=3))
        for bool_values in bool_values_grid:
            with self.subTest(bool_values=bool_values, mocks=mocks):
                for return_value, method_mock in zip(bool_values, mocks):
                    method_mock.return_value = return_value
                answer = self.simulation_runner.reached_stop_condition(
                    well=self.run_kwargs['well'],
                    current_frame=0,
                    stop_conditions=self.run_kwargs['settings']['stop_conditions'],
                )
                if all(value is False for value in bool_values):  # no stop condition was met
                    self.assertFalse(answer)
                else:
                    self.assertTrue(answer)

    def test_reached_reached_frame_limit_returns_boolean_value(self) -> None:
        """Tests whether the "reached_frame_limit" method returns True or False according to the input parameters."""
        limit = 1
        current_frame_test_cases = [
            (0, False),  # Current frame below limit
            (1, True),  # Current frame at limit
            (2, True),  # Current frame above limit
        ]
        for test_case, expected_value in current_frame_test_cases:
            with self.subTest(test_case=test_case, expected_value=expected_value):
                actual_value = self.simulation_runner.reached_frame_limit(current_frame=test_case, frame_limit=limit)
                self.assertEqual(expected_value, actual_value)

    def test_reached_single_colony_size_limit_returns_boolean_value(self) -> None:
        """
        Tests whether the "reached_single_colony_size_limit" method returns True or False
        according to the input parameters.
        """
        limit = 1
        single_colony_size_test_cases = [
            (0, False),  # Largest colony size below limit
            (1, True),  # Largest colony size at limit
            (2, True),  # Largest colony size above limit
        ]
        for test_case, expected_value in single_colony_size_test_cases:
            with self.subTest(test_case=test_case, expected_value=expected_value):
                actual_value = self.simulation_runner.reached_single_colony_size_limit(
                    largest_colony_size=test_case,
                    single_colony_size_limit=limit,
                )
                self.assertEqual(expected_value, actual_value)

    def test_reached_reached_all_colonies_size_limit_returns_boolean_value(self) -> None:
        """
        Tests whether the "reached_all_colonies_size_limit" method returns True or False
        according to the input parameters.
        """
        limit = 1
        all_colonies_size_test_cases = [
            ([0, 0, 0], False),  # All colony sizes below limit
            ([1, 1, 0], False),  # At least one colony size at limit
            ([1, 1, 1], True),  # All colony sizes at limit
            ([1, 2, 1], True),  # All colony sizes at or above limit
            ([2, 2, 2], True),  # All colony sizes above limit
        ]
        for test_case, expected_value in all_colonies_size_test_cases:
            with self.subTest(test_case=test_case, expected_value=expected_value):
                actual_value = self.simulation_runner.reached_all_colonies_size_limit(
                    all_colony_sizes=test_case,
                    all_colonies_size_limit=limit,
                )
                self.assertEqual(expected_value, actual_value)


if __name__ == '__main__':
    unittest.main()
