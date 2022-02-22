import unittest
from pathlib import Path
from unittest import mock
from unittest.mock import MagicMock

from matplotlib import pyplot as plt

from clovars.bio import Treatment
from clovars.simulation import TreatmentDrawer
from tests import NotEmptyTestCase


class TestTreatmentDrawer(NotEmptyTestCase):
    """Class representing unit-tests for clovars.simulation.view.simulation_viewer.TreatmentDrawer class."""
    default_folder_path = Path('.')
    default_file_name = 'TEST'
    default_file_extension = 'png'

    def setUp(self) -> None:
        """Sets up the test case subject (a TreatmentDrawer instance)."""
        self.treatment_drawer = TreatmentDrawer(treatment_data={('1', 0): Treatment()})

    def test_treatment_drawer_has_treatment_attribute(self) -> None:
        """Tests whether the TreatmentDrawer has the "treatments" attribute (dictionary of integer-treatment pairs)."""
        self.assertTrue(hasattr(self.treatment_drawer, 'treatment_data'))
        self.assertIsInstance(self.treatment_drawer.treatment_data, dict)
        with self.assertSequenceNotEmpty(self.treatment_drawer.treatment_data):
            for key, value in self.treatment_drawer.treatment_data.items():
                self.assertIsInstance(key, tuple)
                self.assertIsInstance(key[0], str)
                self.assertIsInstance(key[1], int)
                self.assertIsInstance(value, Treatment)

    def test_show_gaussians_method_calls_plt_show(self) -> None:
        """Tests whether the "display" method calls "plt.show" (i.e. it displays a plot)."""
        with mock.patch('clovars.simulation.view.treatment_drawer.plt.show', side_effect=plt.close) as mock_plt_show:
            self.treatment_drawer.display(show_division=True, show_death=True)
        mock_plt_show.assert_called_once()
        plt.show()

    def test_render_method_saves_figure(self) -> None:
        """Tests whether the "render" method calls "plt.Figure.savefig" (i.e. it saves a figure)."""
        with mock.patch('clovars.simulation.view.treatment_drawer.plt.Figure.savefig') as mock_savefig:
            self.treatment_drawer.render(
                show_division=True,
                show_death=True,
                folder_path=self.default_folder_path,
                file_name=self.default_file_name,
                file_extension=self.default_file_extension,
            )
        mock_savefig.assert_called_once()

    def test_yield_curves_method_yields_tuple_of_figure_and_label(self) -> None:
        """Tests whether the "yield_curves" method yields a tuple containing a matplotlib Figure and a string."""
        return_value = list(self.treatment_drawer.yield_curves(show_division=True, show_death=True))
        with self.assertSequenceNotEmpty(return_value):
            for figure, label in return_value:
                self.assertIsInstance(figure, plt.Figure)
                self.assertIsInstance(label, str)
                plt.close()  # Do not keep the figure open

    def test_yield_curves_yields_one_tuple_per_treatment(self) -> None:
        """Tests whether the "yield_curves" method yields one tuple for each treatment."""
        self.treatment_drawer.treatment_data = {}
        for i in range(1, 10):
            self.treatment_drawer.treatment_data[(str(i+1), i)] = Treatment()
            with mock.patch('clovars.simulation.view.treatment_drawer.plt') as mock_plt:  # Do not draw on Axes
                mock_plt.subplots.return_value = (MagicMock(), MagicMock())
                return_value = list(self.treatment_drawer.yield_curves(show_division=True, show_death=True))
            self.assertEqual(len(return_value), i)

    def test_yield_curves_yields_empty_sequence_if_no_treatments_are_present(self) -> None:
        """Tests whether the "yield_curves" method yields nothing if no treatments are present."""
        self.treatment_drawer.treatment_data = {}
        return_value = list(self.treatment_drawer.yield_curves(show_division=True, show_death=True))
        self.assertEqual(len(return_value), 0)

    def test_yield_curves_calls_death_curve_plot_pdf_if_death_gaussian_is_true(self) -> None:
        """Tests whether the "yield_curves" method draws the death Curve if the "show_death" parameter is True."""
        return_value = list(self.treatment_drawer.yield_curves(show_division=True, show_death=False))
        with self.assertSequenceNotEmpty(return_value):
            for _, label in return_value:
                self.assertNotIn('death', label)
                plt.close()  # Do not keep the figure open
        return_value = list(self.treatment_drawer.yield_curves(show_division=True, show_death=True))
        with self.assertSequenceNotEmpty(return_value):
            for _, label in return_value:
                self.assertIn('death', label)
                plt.close()  # Do not keep the figure open

    def test_yield_curves_calls_division_curve_plot_pdf_if_division_gaussian_is_true(self) -> None:
        """
        Tests whether the "yield_gaussians" method draws the division Curve
        if the "show_division" parameter is True.
        """
        return_value = list(self.treatment_drawer.yield_curves(show_division=False, show_death=True))
        with self.assertSequenceNotEmpty(return_value):
            for _, label in return_value:
                self.assertNotIn('div', label)
                plt.close()  # Do not keep the figure open
        return_value = list(self.treatment_drawer.yield_curves(show_division=True, show_death=True))
        with self.assertSequenceNotEmpty(return_value):
            for _, label in return_value:
                self.assertIn('div', label)
                plt.close()  # Do not keep the figure open


if __name__ == '__main__':
    unittest.main()
