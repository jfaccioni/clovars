import unittest
from unittest import mock
from unittest.mock import MagicMock

from clovars.scientific import (
    CellSignal,
    ConstantCellSignal,
    EMGaussianCellSignal,
    GaussianCellSignal,
    get_cell_signal,
    SinusoidalCellSignal,
    StochasticCellSignal,
    StochasticSinusoidalCellSignal,
)


class TestCellSignal(unittest.TestCase):
    """Class representing unit-tests for clovars.scientific.cell_signal.CellSignal class."""

    def setUp(self) -> None:
        """Sets up the test case subject (a CellSignal instance)."""
        self.signal = CellSignal()

    def test_signal_has_initial_value_and_value_attributes(self) -> None:
        """Tests whether a CellSignal has the "initial_value" and "value" attributes."""
        for attr_name in ('initial_value', 'value'):
            self.assertTrue(hasattr(self.signal, attr_name))
            self.assertIsInstance(getattr(self.signal, attr_name), (int, float))

    def test_initial_value_outside_minus_one_and_one_interval_raises_value_error(self) -> None:
        """Tests whether a CellSignal raises a ValueError when initialized with an initial value outside [-1, 1]."""
        for okay_initial_value in [-1.0, -0.5, 0.0, 0.5, 1.0]:
            try:
                CellSignal(initial_value=okay_initial_value)
            except ValueError:
                self.fail("ValueError was raised unexpectedly!")
        for bad_initial_value in [-1.01, 1.01]:
            with self.assertRaises(ValueError):
                CellSignal(initial_value=bad_initial_value)

    def test_split_method_returns_a_copy_of_the_signal(self) -> None:
        """Tests whether the "split" method returns a copy of the CellSignal instance."""
        new_signal = self.signal.split()
        self.assertIsInstance(new_signal, CellSignal)
        self.assertIsNot(new_signal, self.signal)

    @mock.patch('clovars.scientific.CellSignal.get_new_value', return_value=0.5)
    def test_oscillate_method_modifies_the_signal_value(
            self,
            _: MagicMock,
    ) -> None:
        """Tests whether the "oscillate" method modifies the CellSignal's value attribute."""
        value_before_oscillation = self.signal.value
        self.signal.oscillate()
        self.assertNotEqual(value_before_oscillation, self.signal.value)

    @mock.patch('clovars.scientific.CellSignal.get_new_value', return_value=0.5)
    def test_oscillate_method_passes_args_and_kwargs_to_get_new_value(
            self,
            mock_get_new_value: MagicMock,
    ) -> None:
        """Tests whether the "oscillate" method passes any args and kwargs to the "get_new_value" method."""
        self.signal.oscillate(1, 2, x='y')
        mock_get_new_value.assert_called_once_with(1, 2, x='y')

    def test_get_new_value_method_is_an_abstract_method(self) -> None:
        """Tests whether the "get_new_value" method is an abstract method of the CellSignal class."""
        with self.assertRaises(NotImplementedError):
            self.signal.get_new_value()


class TestSinusoidalCellSignal(unittest.TestCase):
    """Class representing unit-tests for clovars.scientific.cell_signal.SinusoidalCellSignal class."""
    default_current_seconds = 60

    def setUp(self) -> None:
        """Sets up the test case subject (a SinusoidalCellSignal instance)."""
        self.signal = SinusoidalCellSignal()

    def test_sinusoidal_signal_inherits_from_signal(self) -> None:
        """Tests whether a SinusoidalCellSignal inherits from CellSignal."""
        self.assertIsInstance(self.signal, CellSignal)

    def test_sinusoidal_signal_has_period_attributes(self) -> None:
        """Tests whether a SinusoidalCellSignal has the "period" attributes."""
        self.assertTrue(hasattr(self.signal, 'period'))
        self.assertIsInstance(self.signal.period, (int, float))

    def test_period_equal_to_or_less_than_zero_raises_value_error(self) -> None:
        """Tests whether a CellSignal raises a ValueError when initialized with a period <= 0."""
        for okay_period in [0.1, 10, 1_000]:
            try:
                SinusoidalCellSignal(period=okay_period)
            except ValueError:
                self.fail("ValueError was raised unexpectedly!")
        for bad_period in [0.0, -1.0, -200]:
            with self.assertRaises(ValueError):
                SinusoidalCellSignal(period=bad_period)

    @mock.patch('clovars.scientific.SinusoidalCellSignal.sine', return_value=0.05)
    def test_get_new_value_calls_sine_method_and_returns_it(
            self,
            mock_sine: MagicMock,
    ) -> None:
        """
        Tests whether a SinusoidalCellSignal returns the value from the "sine" method when
        the method "get_new_value" is called.
        """
        value = self.signal.get_new_value(current_seconds=self.default_current_seconds)
        mock_sine.assert_called_once_with(current_seconds=self.default_current_seconds)
        self.assertEqual(value, 0.05)

    def test_sine_method_returns_values_in_sine_wave_as_a_function_of_time(self) -> None:
        """Tests whether the "sine" method returns a value from a sine wave outputting values between [-1, 1]."""
        times = {
            int(self.signal.period * 0.000): 0.0,
            int(self.signal.period * 0.250): 1.0,
            int(self.signal.period * 0.500): 0.0,
            int(self.signal.period * 0.750): -1.0,
            int(self.signal.period * 1.000): 0.0,
        }
        for current_seconds, expected_sine in times.items():
            actual_sine = self.signal.sine(current_seconds=current_seconds)
            with self.subTest(current_seconds=current_seconds, expected_sine=expected_sine, actual_sine=actual_sine):
                self.assertAlmostEqual(expected_sine, actual_sine)  # Due to rounding errors on floats


class TestStochasticCellSignal(unittest.TestCase):
    """Class representing unit-tests for clovars.scientific.cell_signal.StochasticCellSignal class."""
    current_seconds = 60

    def setUp(self) -> None:
        """Sets up the test case subject (a StochasticCellSignal instance)."""
        self.signal = StochasticCellSignal()

    def test_stochastic_signal_inherits_from_signal(self) -> None:
        """Tests whether a StochasticCellSignal inherits from CellSignal."""
        self.assertIsInstance(self.signal, CellSignal)

    def test_stochastic_signal_has_period_attributes(self) -> None:
        """Tests whether a StochasticCellSignal has the "noise" attributes."""
        self.assertTrue(hasattr(self.signal, 'noise'))
        self.assertIsInstance(self.signal.noise, (int, float))

    def test_noise_outside_zero_one_interval_raises_value_error(self) -> None:
        """Tests whether a CellSignal raises a ValueError when initialized with a noise outside [0, 1]."""
        for okay_noise in [0.0, 0.5, 1.0]:
            try:
                StochasticCellSignal(noise=okay_noise)
            except ValueError:
                self.fail("ValueError was raised unexpectedly!")
        for bad_noise in [-0.01, 1.01]:
            with self.assertRaises(ValueError):
                StochasticCellSignal(noise=bad_noise)

    @mock.patch('clovars.scientific.StochasticCellSignal.stochastic', return_value=0.55)
    def test_get_new_value_calls_stochastic_method(
            self,
            mock_stochastic: MagicMock,
    ) -> None:
        """
        Tests whether a StochasticCellSignal returns the value from the "stochastic" method when
        the method "get_new_value" is called.
        """
        value = self.signal.get_new_value()
        mock_stochastic.assert_called_once()
        self.assertEqual(value, 0.55)

    def test_stochastic_method_returns_values_inside_noise_range(self) -> None:
        """Tests whether the "stochastic" method returns a stochastic value inside the stochastic noise range."""
        expected_min = self.signal.initial_value - self.signal.noise
        expected_max = self.signal.initial_value + self.signal.noise
        for _ in range(50):
            stochastic_value = self.signal.stochastic()
            self.assertGreaterEqual(stochastic_value, expected_min)
            self.assertLessEqual(stochastic_value, expected_max)

    def test_stochastic_method_clips_values_between_minus_one_and_one(self) -> None:
        """Tests whether the "stochastic" method only returns values between [-1, 1], clipping anything below/above."""
        min_signal = StochasticCellSignal(initial_value=-1.0, noise=1.0)
        for _ in range(5):
            stochastic_value = min_signal.stochastic()
            self.assertGreaterEqual(stochastic_value, -1.0)
        max_signal = StochasticCellSignal(initial_value=1.0, noise=1.0)
        for _ in range(5):
            stochastic_value = max_signal.stochastic()
            self.assertLessEqual(stochastic_value, 1.0)


class TestStochasticSinusoidalCellSignal(unittest.TestCase):
    """Class representing unit-tests for clovars.scientific.cell_signal.StochasticSinusoidalCellSignal class."""
    current_seconds = 60

    def setUp(self) -> None:
        """Sets up the test case subject (a StochasticSinusoidalCellSignal instance)."""
        self.signal = StochasticSinusoidalCellSignal()

    def test_stochastic_sinusoidal_signal_inherits_from_signal(self) -> None:
        """
        Tests whether a StochasticSinusoidalCellSignal inherits from both
        SinusoidalCellSignal and StochasticCellSignal.
        """
        self.assertIsInstance(self.signal, SinusoidalCellSignal)
        self.assertIsInstance(self.signal, StochasticCellSignal)

    def test_stochastic_sinusoidal_signal_has_period_attributes(self) -> None:
        """Tests whether a StochasticCellSignal has the "sinusoidal_weight" and "stochastic_weight" attributes."""
        for attr_name in ('stochastic_weight', 'sine_weight'):
            self.assertTrue(hasattr(self.signal, attr_name))
            self.assertIsInstance(getattr(self.signal, attr_name), (int, float))

    def test_stochastic_weight_outside_zero_one_interval_raises_value_error(self) -> None:
        """
        Tests whether a StochasticSinusoidalCellSignal raises a ValueError when initialized with a
        stochastic weight outside [0, 1].
        """
        for okay_stochastic_weight in [0.0, 0.5, 1.0]:
            try:
                StochasticSinusoidalCellSignal(stochastic_weight=okay_stochastic_weight)
            except ValueError:
                self.fail("ValueError was raised unexpectedly!")
        for bad_stochastic_weight in [-0.01, 1.01]:
            with self.assertRaises(ValueError):
                StochasticSinusoidalCellSignal(stochastic_weight=bad_stochastic_weight)

    def test_stochastic_weight_and_sine_weight_always_add_up_to_one(self) -> None:
        """
        Tests whether a StochasticSinusoidalCellSignal's "stochastic_weight" attribute and
        "sine_weight" attribute always add up to 1.
        """
        for stochastic_weight in [0.0, 0.1, 0.25, 0.5, 0.75, 0.9, 1.0]:
            signal = StochasticSinusoidalCellSignal(stochastic_weight=stochastic_weight)
            self.assertEqual(signal.stochastic_weight + signal.sine_weight, 1.0)

    @mock.patch('clovars.scientific.StochasticSinusoidalCellSignal.stochastic', return_value=0.49)
    @mock.patch('clovars.scientific.StochasticSinusoidalCellSignal.sine', return_value=0.33)
    def test_get_new_value_calls_both_sine_and_stochastic_methods(
            self,
            mock_sine: MagicMock,
            mock_stochastic: MagicMock,
    ) -> None:
        """
        Tests whether a StochasticSinusoidalCellSignal calls both the "sine" and "stochastic" methods when
        the method "get_new_value" is called.
        """
        value = self.signal.get_new_value(current_seconds=self.current_seconds)
        mock_sine.assert_called_once_with(current_seconds=self.current_seconds)
        mock_stochastic.assert_called_once()
        expected_value = (0.49 * 0.5) + (0.33 * 0.5)  # Default stochastic_weight and sine_weight -> 0.5
        self.assertEqual(value, expected_value)


class TestGaussianCellSignal(unittest.TestCase):
    """Class representing unit-tests for clovars.scientific.cell_signal.TestGaussianCellSignal class."""

    def setUp(self) -> None:
        """Sets up the test case subject (a TestGaussianCellSignal instance)."""
        self.signal = GaussianCellSignal()

    def test_gaussian_signal_inherits_from_signal(self) -> None:
        """Tests whether a GaussianCellSignal inherits from CellSignal."""
        self.assertIsInstance(self.signal, CellSignal)

    def test_gaussian_signal_has_mean_std_attributes(self) -> None:
        """Tests whether a GaussianCellSignal has the "mean" and "std" attributes."""
        for attr_name in ('mean', 'std'):
            self.assertTrue(hasattr(self.signal, attr_name))
            self.assertIsInstance(getattr(self.signal, attr_name), (int, float))

    def test_gaussian_std_less_equal_zero_raises_value_error(self) -> None:
        """
        Tests whether a GaussianCellSignal raises a ValueError when
        initialized with a std less or equal to zero.
        """
        for okay_std in [0.1, 5.55, 100]:
            try:
                GaussianCellSignal(std=okay_std)
            except ValueError:
                self.fail("ValueError was raised unexpectedly!")
        for bad_std in [0, -0.01, -100]:
            with self.assertRaises(ValueError):
                GaussianCellSignal(std=bad_std)

    def test_get_new_value_calls_normal_method(self) -> None:
        """Tests whether a GaussianCellSignal calls the "normal" method when the method "get_new_value" is called."""
        with mock.patch('clovars.scientific.GaussianCellSignal.normal') as mock_normal:
            self.signal.get_new_value()
        mock_normal.assert_called_once()

    def test_normal_method_gets_value_from_gaussian_distribution(self) -> None:
        """Tests whether the "normal" method gets a random gaussian value from scipy's norm.rvs."""
        with mock.patch('clovars.scientific.cell_signal.norm.rvs', return_value=0.5) as mock_gaussian_draw:
            self.signal.normal()
        mock_gaussian_draw.assert_called_once_with(loc=self.signal.mean, scale=self.signal.std)

    def test_normal_method_clips_values_between_zero_and_one(self) -> None:
        """Tests whether the "normal" method only returns values between [-1, 1], clipping anything below/above."""
        min_signal = GaussianCellSignal(initial_value=-1.0)
        for _ in range(5):
            gaussian_value = min_signal.normal()
            self.assertGreaterEqual(gaussian_value, -1.0)
        max_signal = GaussianCellSignal(initial_value=1.0)
        for _ in range(5):
            gaussian_value = max_signal.normal()
            self.assertLessEqual(gaussian_value, 1.0)


class TestEMGaussianCellSignal(unittest.TestCase):
    """Class representing unit-tests for clovars.scientific.cell_signal.EMGaussianCellSignal class."""

    def setUp(self) -> None:
        """Sets up the test case subject (an EMGaussianCellSignal instance)."""
        self.signal = EMGaussianCellSignal()

    def test_emgaussian_signal_inherits_from_signal(self) -> None:
        """Tests whether an EMGaussianCellSignal inherits from CellSignal."""
        self.assertIsInstance(self.signal, CellSignal)

    def test_emgaussian_signal_has_k_attribute(self) -> None:
        """Tests whether a GaussianCellSignal has the "mean", "std", and "k" attributes."""
        for attr_name in ('mean', 'std', 'k'):
            self.assertTrue(hasattr(self.signal, attr_name))
            self.assertIsInstance(getattr(self.signal, attr_name), (int, float))

    def test_get_new_value_calls_em_normal_method(self) -> None:
        """
        Tests whether an EMGaussianCellSignal calls the "em_normal" method when
        the method "get_new_value" is called.
        """
        with mock.patch('clovars.scientific.EMGaussianCellSignal.em_normal') as mock_em_normal:
            self.signal.get_new_value()
        mock_em_normal.assert_called_once()

    def test_em_normal_method_gets_value_from_gaussian_distribution(self) -> None:
        """Tests whether the "em_normal" method gets a random gaussian value from scipy's exponnorm.rvs."""
        with mock.patch('clovars.scientific.cell_signal.exponnorm.rvs', return_value=0.5) as mock_gaussian_draw:
            self.signal.em_normal()
        mock_gaussian_draw.assert_called_once_with(loc=self.signal.mean, scale=self.signal.std, K=self.signal.k)

    def test_em_normal_method_clips_values_between_zero_and_one(self) -> None:
        """Tests whether the "em_normal" method only returns values between [-1, 1], clipping anything below/above."""
        min_signal = EMGaussianCellSignal(initial_value=-1.0)
        for _ in range(5):
            gaussian_value = min_signal.em_normal()
            self.assertGreaterEqual(gaussian_value, -1.0)
        max_signal = EMGaussianCellSignal(initial_value=1.0)
        for _ in range(5):
            gaussian_value = max_signal.em_normal()
            self.assertLessEqual(gaussian_value, 1.0)


class TestConstantCellSignal(unittest.TestCase):
    """Class representing unit-tests for clovars.scientific.cell_signal.ConstantCellSignal class."""

    def setUp(self) -> None:
        """Sets up the test case subject (a ConstantCellSignal instance)."""
        self.signal = ConstantCellSignal()

    def test_constant_signal_inherits_from_signal(self) -> None:
        """Tests whether a ConstantCellSignal inherits from CellSignal."""
        self.assertIsInstance(self.signal, CellSignal)

    @mock.patch('clovars.scientific.ConstantCellSignal.constant', return_value=0.99)
    def test_get_new_value_calls_constant_method(
            self,
            mock_constant: MagicMock,
    ) -> None:
        """
        Tests whether a ConstantCellSignal returns the value from the "constant" method when
        the method "get_new_value" is called.
        """
        value = self.signal.get_new_value()
        mock_constant.assert_called_once_with()
        self.assertEqual(value, 0.99)

    def test_constant_method_returns_initial_value(self) -> None:
        """Tests whether the "constant" method simply returns the CellSignal's initial value when called."""
        initial_value = self.signal.initial_value
        for _ in range(5):
            constant_value = self.signal.constant()
            self.assertEqual(constant_value, initial_value)


class TestCellSignalFunctions(unittest.TestCase):
    """Class representing unit-tests for clovars.scientific.cell_signal free functions."""

    def test_get_cell_signal_function_returns_stochastic_signal_if_name_argument_is_stochastic(self) -> None:
        """
        Tests whether the "get_cell_signal" function returns a StochasticCellSignal instance
        when the "name" argument is the string "Stochastic".
        """
        self.assertIsInstance(get_cell_signal(name='Stochastic'), StochasticCellSignal)

    def test_get_cell_signal_function_returns_sinusoidal_signal_if_name_argument_is_sinusoidal(self) -> None:
        """
        Tests whether the "get_cell_signal" function returns a SinusoidalCellSignal instance
        when the "name" argument is the string "Sinusoidal".
        """
        self.assertIsInstance(get_cell_signal(name='Sinusoidal'), SinusoidalCellSignal)

    def test_get_cell_signal_function_returns_stocsin_signal_if_name_argument_is_stocsin(self) -> None:
        """
        Tests whether the "get_cell_signal" function returns a StochasticSinusoidalCellSignal instance
        when the "name" argument is the string "StochasticSinusoidal".
        """
        self.assertIsInstance(get_cell_signal(name='StochasticSinusoidal'), StochasticSinusoidalCellSignal)

    def test_get_cell_signal_function_returns_constant_signal_if_name_argument_is_constant(self) -> None:
        """
        Tests whether the "get_cell_signal" function returns a ConstantCellSignal instance
        when the "name" argument is the string "Constant".
        """
        self.assertIsInstance(get_cell_signal(name='Constant'), ConstantCellSignal)

    def test_get_cell_signal_function_returns_random_signal_if_name_argument_is_random(self) -> None:
        """
        Tests whether the "get_cell_signal" function returns a random signal instance
        when the "name" argument is the string "Random".
        """
        signals = (
            SinusoidalCellSignal,
            StochasticCellSignal,
            StochasticSinusoidalCellSignal,
            GaussianCellSignal,
            EMGaussianCellSignal,
            ConstantCellSignal,
        )
        for _ in range(30):
            self.assertIsInstance(get_cell_signal(name='Random'), signals)

    def test_get_cell_signal_function_returns_gaussian_signal_if_name_argument_is_falsy(self) -> None:
        """
        Tests whether the "get_cell_signal" function returns a GaussianCellSignal instance
        when the "name" argument is a falsy value."""
        for falsy_value in ['', None, False, 0]:
            signal = get_cell_signal(name=falsy_value)
            self.assertIsInstance(signal, GaussianCellSignal)

    def test_get_cell_signal_function_raises_value_error_if_any_other_name_argument_is_given(self) -> None:
        """
        Tests whether the "get_cell_signal" function raises a ValueError if any other value
        for the "name" argument is used.
        """
        invalid_signal_types = ['Hello', 'sinusoidal', 'ecstatic', '!!!', 1.0, True]
        for invalid_signal_type in invalid_signal_types:
            with self.assertRaises(ValueError):
                get_cell_signal(name=invalid_signal_type)

    def test_get_cell_signal_function_returns_a_signal_with_the_arguments_provided(self) -> None:
        """
        Tests whether the "get_cell_signal" function returns a CellSignal with the arguments passed on to it
        as the correct attributes in the CellSignal instance.
        """
        kwargs = {
            'name': 'Random',
            'initial_value': 0.4,
            'period': 0.1,
            'noise': 0.8,
            'stochastic_weight': 0.2,
            'mean': 0.3,
            'std': 0.7,
            'k': 0.9,
        }
        potential_attrs = ['period', 'noise', 'stochastic_weight', 'mean', 'std', 'k']
        for _ in range(10):
            signal = get_cell_signal(**kwargs)
            self.assertEqual(signal.initial_value, kwargs['initial_value'])
            for potential_attr in potential_attrs:
                if hasattr(signal, potential_attr):
                    self.assertEqual(getattr(signal, potential_attr), kwargs[potential_attr])


if __name__ == '__main__':
    unittest.main()
