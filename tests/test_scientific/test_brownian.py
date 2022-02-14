import random
import unittest

from clovars.scientific import brownian_motion, bounded_brownian_motion, reflect_around_interval, triangular_wave


class TestBrownian(unittest.TestCase):
    """Class representing unit-tests for clovars.scientific.brownian_motion module."""
    def test_bounded_brownian_motion_returns_values_between_bounds(self) -> None:
        """
        Tests whether the "bounded_brownian_motion" function always returns values
        between the lower and upper bounds used.
        """
        for _ in range(30):
            current_value, scale = random.random(), random.random()
            lower_bound, upper_bound = random.random(), random.random() + 1
            value = bounded_brownian_motion(
                current_value=current_value,
                scale=scale,
                lower_bound=lower_bound,
                upper_bound=upper_bound,
            )
            with self.subTest(value=value, lower_bound=lower_bound, upper_bound=upper_bound):
                self.assertGreaterEqual(value, lower_bound)
                self.assertLessEqual(value, upper_bound)

    def test_brownian_motion_returns_values_close_to_the_input_value(self) -> None:
        """Tests whether the "brownian_motion" function returns new values within ~ 7 SDs of the input value."""
        for current_value in [0, 17.98, 999, 312, -73.4]:
            for scale in [0.2, 0.5, 0.8]:
                tolerance = 7 * scale
                with self.subTest(current_value=current_value, scale=scale, tolerance=tolerance):
                    result = brownian_motion(current_value=current_value, scale=scale)
                    self.assertGreaterEqual(result, current_value - tolerance)
                    self.assertLessEqual(result, current_value + tolerance)

    def test_brownian_motion_returns_input_value_if_scale_is_one(self) -> None:
        """Tests whether the "brownian_motion" function returns the exact input value if the scale argument is one."""
        for _ in range(30):
            current_value = random.random()
            with self.subTest(current_value=current_value):
                result = brownian_motion(current_value=current_value, scale=1.0)
                self.assertEqual(current_value, result)

    def test_reflect_around_interval_returns_input_value_reflected_between_bounds(self) -> None:
        """
        Tests whether the "reflect_around_interval" function returns the input value
        after reflecting it between two bounds.
        """
        reflect_test_cases = [
            (0.5, 0.0, 1.0, 0.5),
            (1.5, 0.0, 1.0, 0.5),
            (-.5, 0.0, 1.0, 0.5),
            (3.6, 2.0, 3.0, 2.4),
            (3.2, 1.0, 3.0, 2.8),
            (6.4, 4.0, 6.0, 5.6),
            (10., 5.0, 8.0, 6.0),
            (10., 1.0, 3.0, 2.0),
        ]
        for x, lower_bound, upper_bound, expected_x in reflect_test_cases:
            with self.subTest(x=x, lower_bound=lower_bound, upper_bound=upper_bound, expected_x=expected_x):
                actual_x = reflect_around_interval(x=x, lower_bound=lower_bound, upper_bound=upper_bound)
                self.assertAlmostEqual(expected_x, actual_x)

    def test_triangular_wave_behaves_as_a_triangular_wave(self) -> None:
        """Tests whether the "triangular_wave" function returns values as expected by a triangular wave function."""
        triangular_test_cases = [
            (0.0, 1.0, 1.0, 0.0),
            (.25, 1.0, 1.0, 1.0),
            (.50, 1.0, 1.0, 0.0),
            (.75, 1.0, 1.0, -1.),
            (1.0, 1.0, 1.0, 0.0),
        ]
        for x, period, amplitude, expected_y in triangular_test_cases:
            with self.subTest(x=x, period=period, amplitude=amplitude, expected_y=expected_y):
                actual_y = triangular_wave(x=x, period=period, amplitude=amplitude)
                self.assertEqual(expected_y, actual_y)

    def test_triangular_wave_scales_with_period(self) -> None:
        """Tests whether the "triangular_wave" function scales with its period argument properly."""
        triangular_test_cases = [
            (.25, 1.0, 1.0, 1.0),
            (.25, 2.0, 1.0, 0.5),
            (.25, 4.0, 1.0, .25),
            (.25, 0.5, 1.0, 0.0),
        ]
        for x, period, amplitude, expected_y in triangular_test_cases:
            with self.subTest(x=x, period=period, amplitude=amplitude, expected_y=expected_y):
                actual_y = triangular_wave(x=x, period=period, amplitude=amplitude)
                self.assertEqual(expected_y, actual_y)

    def test_triangular_wave_scales_with_amplitude(self) -> None:
        """Tests whether the "triangular_wave" function scales with its amplitude argument properly."""
        triangular_test_cases = [
            (0.25, 1.0, 1.0, 1.0),
            (0.25, 1.0, 2.0, 2.0),
            (0.25, 1.0, 4.0, 4.0),
            (0.25, 1.0, 5.0, 5.0),
            (0.75, 1.0, 1.0, -1.),
            (0.75, 1.0, 2.0, -2.),
            (0.75, 1.0, 4.0, -4.),
            (0.75, 1.0, 5.0, -5.),
        ]
        for x, period, amplitude, expected_y in triangular_test_cases:
            with self.subTest(x=x, period=period, amplitude=amplitude, expected_y=expected_y):
                actual_y = triangular_wave(x=x, period=period, amplitude=amplitude)
                self.assertEqual(expected_y, actual_y)


if __name__ == '__main__':
    unittest.main()
