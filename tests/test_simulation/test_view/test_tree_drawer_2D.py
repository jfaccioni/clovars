import unittest
from unittest.mock import MagicMock

import pandas as pd
from matplotlib.colors import Normalize, Colormap

from clovars.simulation import TreeDrawer2D
from tests import SKIP_TESTS


class TestTreeDrawer2D(unittest.TestCase):
    """Class representing unit-tests of clovars.simulation.view.simulation_viewer.TreeDrawer2D objects."""
    def setUp(self) -> None:
        """Sets up the test case subject (a TreeDrawer2D instance)."""
        self.tree_drawer_2D = TreeDrawer2D()

    def test_tree_drawer_has_valid_layouts_attribute(self) -> None:
        """Tests whether a TreeDrawer2D has the "valid_layouts" class attribute (a list of strings)."""
        self.assertTrue(hasattr(TreeDrawer2D, 'valid_layouts'))
        self.assertIsInstance(TreeDrawer2D.valid_layouts, list)
        for value in TreeDrawer2D.valid_layouts:
            self.assertIsInstance(value, str)

    def test_tree_drawer_has_colormap_attribute(self) -> None:
        """Tests whether a TreeDrawer2D has the "colormap" attribute (a Colormap instance)."""
        self.assertTrue(hasattr(self.tree_drawer_2D, 'colormap'))
        self.assertIsInstance(self.tree_drawer_2D.colormap, Colormap)

    def test_tree_drawer_has_layout_attribute(self) -> None:
        """Tests whether a TreeDrawer2D has the "layout" attribute (a string)."""
        self.assertTrue(hasattr(self.tree_drawer_2D, 'layout'))
        self.assertIsInstance(self.tree_drawer_2D.layout, str)

    def test_tree_drawer_has_normalizer_attributes(self) -> None:
        """Tests whether a TreeDrawer2D has the expected normalizer attributes."""
        for normalizer_attr_name in [
            'time_normalizer',
            'age_normalizer',
            'generation_normalizer',
            'division_normalizer',
            'death_normalizer',
            'signal_normalizer',
        ]:
            with self.subTest(normalizer_attr_name=normalizer_attr_name):
                self.assertTrue(hasattr(self.tree_drawer_2D, normalizer_attr_name))
                self.assertIsInstance(getattr(self.tree_drawer_2D, normalizer_attr_name), Normalize)

    def test_get_normalizer_method_returns_normalize_instance(self) -> None:
        """Tests whether the "get_normalizer" method returns a Normalize instance."""
        self.assertIsInstance(self.tree_drawer_2D.get_normalizer(), Normalize)

    def test_validate_layout_method_(self) -> None:
        """Docstring."""
        for valid_layout in TreeDrawer2D.valid_layouts:
            try:
                self.tree_drawer_2D.validate_layout(layout=valid_layout)
            except ValueError:
                self.fail(f'Test failed: layout "{valid_layout}" should have been a valid value.')
        with self.assertRaises(ValueError):
            self.tree_drawer_2D.validate_layout(layout='something wrong')

    def test_get_normalizer_method_normalizes_values(self) -> None:
        """Tests whether the "get_normalizer" method normalizes the pandas Series values between 0 and 1."""
        values = pd.Series([0.20, 0.37, 0.55, 0.80])
        normalizer = self.tree_drawer_2D.get_normalizer(values=values)
        self.assertEqual(normalizer(0.2), 0)
        self.assertEqual(normalizer(0.8), 1)

    @unittest.skipIf(SKIP_TESTS is True, "SKIP TESTS is set to True")
    def test_display_trees_method_(self) -> None:
        """Docstring."""
        self.fail("Write the test!")

    @unittest.skipIf(SKIP_TESTS is True, "SKIP TESTS is set to True")
    def test_render_trees_method_(self) -> None:
        """Docstring."""
        self.fail("Write the test!")

    @unittest.skipIf(SKIP_TESTS is True, "SKIP TESTS is set to True")
    def test_plot_tree_method_(self) -> None:
        """Docstring."""
        self.fail("Write the test!")

    @unittest.skipIf(SKIP_TESTS is True, "SKIP TESTS is set to True")
    def test_draw_branches_method_(self) -> None:
        """Docstring."""
        self.fail("Write the test!")

    @unittest.skipIf(SKIP_TESTS is True, "SKIP TESTS is set to True")
    def test_draw_cells_method_(self) -> None:
        """Docstring."""
        self.fail("Write the test!")

    @unittest.skipIf(SKIP_TESTS is True, "SKIP TESTS is set to True")
    def test_get_node_x_method_(self) -> None:
        """Docstring."""
        self.fail("Write the test!")

    @unittest.skipIf(SKIP_TESTS is True, "SKIP TESTS is set to True")
    def test_get_node_y_method(self) -> None:
        """Docstring."""
        self.fail("Write the test!")

    @unittest.skipIf(SKIP_TESTS is True, "SKIP TESTS is set to True")
    def test_get_height_from_name_method_(self) -> None:
        """Docstring."""
        self.fail("Write the test!")

    @unittest.skipIf(SKIP_TESTS is True, "SKIP TESTS is set to True")
    def test_get_node_color_method_(self) -> None:
        """Docstring."""
        self.fail("Write the test!")

    @unittest.skipIf(SKIP_TESTS is True, "SKIP TESTS is set to True")
    def test_get_family_color_method_(self) -> None:
        """Docstring."""
        self.fail("Write the test!")

    @unittest.skipIf(SKIP_TESTS is True, "SKIP TESTS is set to True")
    def test_get_age_color_method_(self) -> None:
        """Docstring."""
        self.fail("Write the test!")

    @unittest.skipIf(SKIP_TESTS is True, "SKIP TESTS is set to True")
    def test_get_generation_color_method_(self) -> None:
        """Docstring."""
        self.fail("Write the test!")

    @unittest.skipIf(SKIP_TESTS is True, "SKIP TESTS is set to True")
    def test_get_division_color_method_(self) -> None:
        """Docstring."""
        self.fail("Write the test!")

    @unittest.skipIf(SKIP_TESTS is True, "SKIP TESTS is set to True")
    def test_get_death_color_method_(self) -> None:
        """Docstring."""
        self.fail("Write the test!")

    @unittest.skipIf(SKIP_TESTS is True, "SKIP TESTS is set to True")
    def test_get_signal_color_method_(self) -> None:
        """Docstring."""
        self.fail("Write the test!")

    @unittest.skipIf(SKIP_TESTS is True, "SKIP TESTS is set to True")
    def test_get_node_marker_method_(self) -> None:
        """Docstring."""
        self.fail("Write the test!")

    @unittest.skipIf(SKIP_TESTS is True, "SKIP TESTS is set to True")
    def test_get_family_marker_method_(self) -> None:
        """Docstring."""
        self.fail("Write the test!")

    @unittest.skipIf(SKIP_TESTS is True, "SKIP TESTS is set to True")
    def test_get_node_size_method_(self) -> None:
        """Docstring."""
        self.fail("Write the test!")

    @unittest.skipIf(SKIP_TESTS is True, "SKIP TESTS is set to True")
    def test_hide_borders_method_(self) -> None:
        """Docstring."""
        self.fail("Write the test!")

    def test_add_legend_method_adds_legend_to_axes(self) -> None:
        """Tests whether the "add_legend" method calls the "legend" method on the plt.Axes instance."""
        mock_fig, mock_ax = MagicMock(), MagicMock()
        self.tree_drawer_2D.layout = 'generation'  # use a valid layout for this test
        self.tree_drawer_2D.add_legend(ax=mock_ax)
        mock_ax.legend.assert_called_once()

    def test_add_colorbar_method_adds_colorbar_to_figure(self) -> None:
        """Tests whether the "add_colorbar" method calls the "colorbar" method on the plt.Figure instance."""
        mock_fig, mock_ax = MagicMock(), MagicMock()
        self.tree_drawer_2D.layout = 'generation'  # use a valid layout for this test
        self.tree_drawer_2D.add_colorbar(figure=mock_fig, ax=mock_ax)
        mock_fig.colorbar.assert_called_once()

    @unittest.skipIf(SKIP_TESTS is True, "SKIP TESTS is set to True")
    def test_render_tree_videos_method_(self) -> None:
        """Docstring."""
        self.fail("Write the test!")

    @unittest.skipIf(SKIP_TESTS is True, "SKIP TESTS is set to True")
    def test_progress_callback_method_(self) -> None:
        """Docstring."""
        self.fail("Write the test!")

    @unittest.skipIf(SKIP_TESTS is True, "SKIP TESTS is set to True")
    def test_animate_tree_method_(self) -> None:
        """Docstring."""
        self.fail("Write the test!")

    @unittest.skipIf(SKIP_TESTS is True, "SKIP TESTS is set to True")
    def test_animate_frames_method_(self) -> None:
        """Docstring."""
        self.fail("Write the test!")


if __name__ == '__main__':
    unittest.main()
