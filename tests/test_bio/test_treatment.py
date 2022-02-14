import unittest
from unittest import mock
from unittest.mock import MagicMock

from clovars.bio import Treatment, get_treatment
from clovars.scientific import Gaussian


class TestTreatment(unittest.TestCase):
    """Class representing unit-tests for clovars.bio.treatment.Treatment class."""
    default_delta = 100

    def setUp(self) -> None:
        """Sets up the test case subject (a Treatment instance)."""
        self.treatment = Treatment(
            name="Treatment Name",
            division_curve=Gaussian(loc=24.0, scale=1e-3),
            death_curve=Gaussian(loc=300.0, scale=1e-3),
        )

    def test_treatment_has_name_attribute(self) -> None:
        """Tests whether a Treatment has a "name" attribute (a string)."""
        self.assertTrue(hasattr(self.treatment, 'name'))
        self.assertIsInstance(self.treatment.name, str)

    def test_treatment_has_division_curve_attribute(self) -> None:
        """Tests whether a Treatment has a "division_curve" attribute (a Gaussian instance)."""
        self.assertTrue(hasattr(self.treatment, 'division_curve'))
        self.assertIsInstance(self.treatment.division_curve, Gaussian)

    def test_treatment_has_death_curve_attribute(self) -> None:
        """Tests whether a Treatment has a "death_curve" attribute (a Gaussian instance)."""
        self.assertTrue(hasattr(self.treatment, 'death_curve'))
        self.assertIsInstance(self.treatment.death_curve, Gaussian)

    def test_treatment_has_signal_disturbance_attribute(self) -> None:
        """Tests whether a Treatment has a "signal_disturbance" attribute (a dictionary or None type)."""
        self.assertTrue(hasattr(self.treatment, 'signal_disturbance'))
        self.assertIsInstance(self.treatment.signal_disturbance, (type(None), dict))

    def test_division_chance_calls_the_division_curve(self) -> None:
        """Tests whether the "division_chance" method calls the division curve with the provided argument."""
        self.treatment.division_curve = MagicMock()
        self.treatment.death_curve = MagicMock()
        self.treatment.division_chance(x=50)
        self.treatment.division_curve.assert_called_once_with(x=50)
        self.treatment.death_curve.assert_not_called()

    def test_death_chance_calls_the_death_curve(self) -> None:
        """Tests whether the "death_chance" method calls the death curve with the provided argument."""
        self.treatment.division_curve = MagicMock()
        self.treatment.death_curve = MagicMock()
        self.treatment.death_chance(x=50)
        self.treatment.division_curve.assert_not_called()
        self.treatment.death_curve.assert_called_once_with(x=50)

    def test_plot_method_calls_the_division_curve_plot_cdf_methods(self) -> None:
        """Tests whether the "plot" method conditionally calls the division curve's "plot_pdf" methods."""
        with mock.patch.object(self.treatment.division_curve, 'plot_pdf') as mock_division_curve_plot_pdf:
            self.treatment.plot(plot_division=False, plot_death=False, foo='bar')
            mock_division_curve_plot_pdf.assert_not_called()
            self.treatment.plot(plot_division=True, plot_death=False, foo='bar')
            mock_division_curve_plot_pdf.assert_called_once_with(label='Division', foo='bar')

    def test_plot_method_calls_the_death_curve_plot_cdf_methods(self) -> None:
        """Tests whether the "plot" method conditionally calls the death curve's "plot_pdf" methods."""
        with mock.patch.object(self.treatment.death_curve, 'plot_pdf') as mock_death_curve_plot_pdf:
            self.treatment.plot(plot_division=False, plot_death=False, foo='bar')
            mock_death_curve_plot_pdf.assert_not_called()
            self.treatment.plot(plot_division=False, plot_death=True, foo='bar')
            mock_death_curve_plot_pdf.assert_called_once_with(label='Death', foo='bar')


class TestTreatmentFunctions(unittest.TestCase):
    """Class representing unit-tests for clovars.bio.treatment free functions."""

    def test_get_treatment_function_returns_treatment_instance(self) -> None:
        """Tests whether the "get_treatment" function returns a Treatment instance."""
        self.assertIsInstance(get_treatment(), Treatment)


if __name__ == '__main__':
    unittest.main()
