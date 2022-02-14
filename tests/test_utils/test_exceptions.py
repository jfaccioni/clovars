import unittest

from clovars.utils import SimulationError


class TestExceptions(unittest.TestCase):
    """Class representing unit-tests of the clovars.exceptions module."""
    def test_simulation_error_is_an_exception(self) -> None:
        """Tests whether the SimulationError is a proper Python Exception."""
        self.assertTrue(issubclass(SimulationError, Exception))


if __name__ == '__main__':
    unittest.main()
