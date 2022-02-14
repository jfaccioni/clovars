import unittest

from clovars.bio import Well
from clovars.IO import WellLoader


class TestCellLoader(unittest.TestCase):
    """Class representing unit-tests for clovars.simulation.well_loader.WellLoader class."""

    def setUp(self) -> None:
        """Sets up the test case subject (a WellLoader instance)."""
        well_settings = {
            'well_radius': 50,
        }
        self.well_loader = WellLoader(well_settings=well_settings)

    def test_well_loader_has_well_attribute(self) -> None:
        """Tests whether a WellLoader has a "well" attribute - a Well instance."""
        self.assertTrue(hasattr(self.well_loader, 'well'))
        self.assertIsInstance(self.well_loader.well, Well)

    def test_well_loader_uses_default_arguments_when_they_are_not_present_on_init(self) -> None:
        """Tests whether a WellLoader uses its default arguments when they are not passed in the "__init__" method."""
        well_settings = {}
        well_loader = WellLoader(well_settings=well_settings)
        self.assertEqual(well_loader.well.radius, well_loader.default_well_radius)


if __name__ == '__main__':
    unittest.main()
