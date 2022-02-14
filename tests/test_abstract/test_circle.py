import math
import unittest

from cellsim.abstract import Circle


class TestCircle(unittest.TestCase):
    """Class representing unit-tests of clovars.abstract.circle.Circle objects."""
    def test_negative_radius_on_init_raises_value_error(self) -> None:
        """Tests whether initializing a circle with radius < 0 raises a ValueError."""
        try:
            Circle(x=0.0, y=0.0, radius=1.0)
        except ValueError:
            self.fail("Circle raised ValueError unexpectedly!")
        try:
            Circle(x=0.0, y=0.0, radius=0.0)
        except ValueError:
            self.fail("Circle raised ValueError unexpectedly!")
        with self.assertRaises(ValueError):
            Circle(x=0.0, y=0.0, radius=-1.0)

    def test_getting_radius_property_returns_protected_attribute_radius(self) -> None:
        """Tests whether the "radius" property returns the "_radius" protected attribute."""
        c = Circle(x=5.0, y=5.0, radius=2.0)
        self.assertTrue(hasattr(c, '_radius'))
        self.assertEqual(c.radius, c._radius)

    def test_setting_negative_radius_raises_value_error(self) -> None:
        """Tests whether setting a negative radius to an existing Circle raises a ValueError."""
        c = Circle(x=5.0, y=5.0, radius=2.0)
        try:
            c.radius = 1.0
        except ValueError:
            self.fail("Circle raised ValueError unexpectedly!")
        try:
            c.radius = 0.0
        except ValueError:
            self.fail("Circle raised ValueError unexpectedly!")
        with self.assertRaises(ValueError):
            c.radius = -1.0

    def test_validate_radius_method(self) -> None:
        """Tests the "validate_radius" static method of Circles."""
        try:
            Circle.validate_radius(1.0)
        except ValueError:
            self.fail("Circle raised ValueError unexpectedly!")
        try:
            Circle.validate_radius(0.0)
        except ValueError:
            self.fail("Circle raised ValueError unexpectedly!")
        with self.assertRaises(ValueError):
            Circle.validate_radius(-1.0)

    def test_area_property(self) -> None:
        """Tests the "area" property of Circles."""
        circle_of_radius_zero = Circle(x=0.0, y=0.0, radius=0.0)
        expected_area = 0.0
        self.assertEqual(circle_of_radius_zero.area, expected_area)

        circle_of_radius_one = Circle(x=0.0, y=0.0, radius=1.0)
        expected_area = math.pi
        self.assertEqual(circle_of_radius_one.area, expected_area)

        circle_of_radius_two = Circle(x=0.0, y=0.0, radius=2.0)
        expected_area = math.pi * (2 ** 2)
        self.assertEqual(circle_of_radius_two.area, expected_area)

        circle_of_radius_ten = Circle(x=0.0, y=0.0, radius=10.0)
        expected_area = math.pi * (10 ** 2)
        self.assertEqual(circle_of_radius_ten.area, expected_area)

    def test_center_property(self) -> None:
        """Tests the "center" property of Circles."""
        xs = [1.2, 0.0, -6.9, 2.3]
        ys = [4.7, 9.8, 0.0, -1.2]
        for x, y in zip(xs, ys):
            c = Circle(x=x, y=y, radius=1.0)
            with self.subTest(x=x, y=y):
                self.assertEqual(c.center, (x, y))

    def test_distance_to_method(self) -> None:
        """Tests the "distance_to" method of Circles."""
        circle_on_origin = Circle(x=0.0, y=0.0, radius=1.0)
        circle_on_3_4 = Circle(x=3.0, y=4.0, radius=1.0)
        self.assertEqual(circle_on_origin.distance_to(circle_on_3_4), 5.0)
        self.assertEqual(circle_on_3_4.distance_to(circle_on_origin), 5.0)

    def test_overlaps_with(self) -> None:
        """Tests the "overlaps_with" method of Circles."""
        circle_on_origin = Circle(x=0.0, y=0.0, radius=1.0)
        contained_circle = Circle(x=0.2, y=0.0, radius=0.5)
        self.assertTrue(circle_on_origin.overlaps_with(contained_circle))
        self.assertTrue(contained_circle.overlaps_with(circle_on_origin))
        overlapping_circle = Circle(x=1.5, y=0.0, radius=1.0)
        self.assertTrue(circle_on_origin.overlaps_with(overlapping_circle))
        self.assertTrue(overlapping_circle.overlaps_with(circle_on_origin))
        distant_circle = Circle(x=10.0, y=0.0, radius=1.0)
        self.assertFalse(circle_on_origin.overlaps_with(distant_circle))
        self.assertFalse(distant_circle.overlaps_with(circle_on_origin))

    def test_contains(self) -> None:
        """Tests the "contains" method of Circles."""
        circle_on_origin = Circle(x=0.0, y=0.0, radius=1.0)
        contained_circle = Circle(x=0.2, y=0.0, radius=0.5)
        self.assertTrue(circle_on_origin.contains(contained_circle))
        self.assertFalse(contained_circle.contains(circle_on_origin))
        overlapping_circle = Circle(x=1.5, y=0.0, radius=1.0)
        self.assertFalse(circle_on_origin.contains(overlapping_circle))
        self.assertFalse(overlapping_circle.contains(circle_on_origin))
        distant_circle = Circle(x=10.0, y=0.0, radius=1.0)
        self.assertFalse(circle_on_origin.contains(distant_circle))
        self.assertFalse(distant_circle.contains(circle_on_origin))

    def test_is_inside(self) -> None:
        """Tests the "is_inside" method of Circles."""
        circle_on_origin = Circle(x=0.0, y=0.0, radius=1.0)
        contained_circle = Circle(x=0.2, y=0.0, radius=0.5)
        self.assertFalse(circle_on_origin.is_inside(contained_circle))
        self.assertTrue(contained_circle.is_inside(circle_on_origin))
        overlapping_circle = Circle(x=1.5, y=0.0, radius=1.0)
        self.assertFalse(circle_on_origin.is_inside(overlapping_circle))
        self.assertFalse(overlapping_circle.is_inside(circle_on_origin))
        distant_circle = Circle(x=10.0, y=0.0, radius=1.0)
        self.assertFalse(circle_on_origin.is_inside(distant_circle))
        self.assertFalse(distant_circle.is_inside(circle_on_origin))

    def test_random_point(self) -> None:
        """Tests the "random_point" method of Circles."""
        circle_on_origin = Circle(x=0.0, y=0.0, radius=1.0)
        for _ in range(10):  # test 10 random circles
            x, y = circle_on_origin.random_point()
            random_point = Circle(x=x, y=y, radius=0.0)
            self.assertTrue(circle_on_origin.contains(random_point))


if __name__ == '__main__':
    unittest.main()
