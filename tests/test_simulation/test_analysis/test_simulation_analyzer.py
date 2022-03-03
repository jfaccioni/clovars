import unittest

from tests import SKIP_TESTS


class TestSimulationAnalyzer(unittest.TestCase):
    """Class representing unit-tests of the clovars.simulation.analysis.SimulationAnalyzer class."""

    @unittest.skipIf(SKIP_TESTS is True, "SKIP TESTS is set to True")
    def test_(self) -> None:
        self.fail("Write the test!")


if __name__ == '__main__':
    unittest.main()
