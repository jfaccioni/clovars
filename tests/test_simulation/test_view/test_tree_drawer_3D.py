import unittest
from pathlib import Path
from unittest import mock
from unittest.mock import MagicMock

import pandas as pd
from ete3 import TreeStyle
from matplotlib.colors import Normalize, Colormap

from clovars.abstract import CellNode
from clovars.simulation import TreeDrawer3D
from tests import SKIP_TESTS


class TestTreeDrawer3D(unittest.TestCase):
    """Class representing unit-tests of clovars.simulation.view.simulation_viewer.TreeDrawer3D objects."""
    default_display_well = True
    default_z_axis_ratio = 1.0
    default_well_radius = 100
    default_folder_path = Path('.')
    default_file_name = 'file_name'
    default_file_extension = '.png'
    default_dpi = 120

    def setUp(self) -> None:
        """Sets up the test case subject (a TreeDrawer3D instance)."""
        self.tree_drawer_3D = TreeDrawer3D()

    def test_tree_drawer_has_valid_layouts_attribute(self) -> None:
        """Tests whether a TreeDrawer3D has the "valid_layouts" class attribute (a list of strings)."""
        self.assertTrue(hasattr(TreeDrawer3D, 'valid_layouts'))
        self.assertIsInstance(TreeDrawer3D.valid_layouts, list)
        for value in TreeDrawer3D.valid_layouts:
            self.assertIsInstance(value, str)

    def test_tree_drawer_has_colormap_attribute(self) -> None:
        """Tests whether a TreeDrawer3D has the "colormap" attribute (a Colormap instance)."""
        self.assertTrue(hasattr(self.tree_drawer_3D, 'colormap'))
        self.assertIsInstance(self.tree_drawer_3D.colormap, Colormap)

    def test_tree_drawer_has_layout_attribute(self) -> None:
        """Tests whether a TreeDrawer3D has the "layout" attribute (a string)."""
        self.assertTrue(hasattr(self.tree_drawer_3D, 'layout'))
        self.assertIsInstance(self.tree_drawer_3D.layout, str)

    def test_tree_drawer_has_normalizer_attributes(self) -> None:
        """Tests whether a TreeDrawer3D has the expected normalizer attributes."""
        for normalizer_attr_name in [
            'time_normalizer',
            'age_normalizer',
            'generation_normalizer',
            'division_normalizer',
            'death_normalizer',
            'signal_normalizer',
        ]:
            with self.subTest(normalizer_attr_name=normalizer_attr_name):
                self.assertTrue(hasattr(self.tree_drawer_3D, normalizer_attr_name))
                self.assertIsInstance(getattr(self.tree_drawer_3D, normalizer_attr_name), Normalize)

    def test_get_normalizer_method_returns_normalize_instance(self) -> None:
        """Tests whether the "get_normalizer" method returns a Normalize instance."""
        self.assertIsInstance(self.tree_drawer_3D.get_normalizer(), Normalize)

    def test_validate_layout_method_(self) -> None:
        """Docstring."""
        for valid_layout in TreeDrawer3D.valid_layouts:
            try:
                self.tree_drawer_3D.validate_layout(layout=valid_layout)
            except ValueError:
                self.fail(f'Test failed: layout "{valid_layout}" should have been a valid value.')
        with self.assertRaises(ValueError):
            self.tree_drawer_3D.validate_layout(layout='something wrong')

    def test_get_normalizer_method_normalizes_values(self) -> None:
        """Tests whether the "get_normalizer" method normalizes the pandas Series values between 0 and 1."""
        values = pd.Series([0.20, 0.37, 0.55, 0.80])
        normalizer = self.tree_drawer_3D.get_normalizer(values=values)
        self.assertEqual(normalizer(0.2), 0)
        self.assertEqual(normalizer(0.8), 1)

    def test_display_trees_method_calls_plt_show(self) -> None:
        """Tests whether the "display_trees" method calls "plt.show" (i.e. it displays a plot)."""
        with mock.patch('clovars.simulation.view.tree_drawer_3D.plt') as mock_plt:
            self.tree_drawer_3D.display_trees(
                root_nodes=[CellNode()],
                display_well=self.default_display_well,
                z_axis_ratio=self.default_z_axis_ratio,
                well_radius=self.default_well_radius,
            )
        mock_plt.show.assert_called_once()

    def test_render_trees_method_calls_plt_show(self) -> None:
        """Tests whether the "render_trees" method calls "plt.Figure.savefig" (i.e. it saves a figure)."""
        with mock.patch('clovars.simulation.view.tree_drawer_3D.plt.Figure.savefig') as mock_figure_savefig:
            self.tree_drawer_3D.render_trees(
                root_nodes=[CellNode()],
                display_well=self.default_display_well,
                z_axis_ratio=self.default_z_axis_ratio,
                well_radius=self.default_well_radius,
                folder_path=self.default_folder_path,
                file_name=self.default_file_name,
                file_extension=self.default_file_extension,
            )
        mock_figure_savefig.assert_called_once()

    @unittest.skipIf(SKIP_TESTS is True, "SKIP TESTS is set to True")
    def test_plot_trees_method_(self) -> None:
        """Docstring."""
        self.fail("Write the test!")

    @mock.patch('clovars.simulation.TreeDrawer3D.draw_branch')
    def test_draw_tree_method_calls_draw_branch_method(
            self,
            draw_branch_mock: MagicMock,
    ) -> None:
        """Tests whether the "draw_tree" method calls the "draw_branch" method."""
        self.tree_drawer_3D.draw_tree(ax=MagicMock(), root_node=CellNode())
        draw_branch_mock.assert_called()

    @mock.patch('clovars.simulation.TreeDrawer3D.format_family_layout')
    @mock.patch('clovars.simulation.TreeDrawer3D.format_non_family_layout')
    def test_draw_tree_method_calls_the_appropriate_formatting_method(
            self,
            format_non_family_layout_mock: MagicMock,
            format_family_layout_mock: MagicMock,
    ) -> None:
        """Tests whether the "draw_tree" method calls the appropriate layout method, depending on the layout."""
        self.tree_drawer_3D.layout = 'family'
        self.tree_drawer_3D.draw_tree(ax=MagicMock(), root_node=CellNode())
        format_non_family_layout_mock.assert_not_called()
        format_family_layout_mock.assert_called_once()
        self.tree_drawer_3D.layout = 'generation'
        self.tree_drawer_3D.draw_tree(ax=MagicMock(), root_node=CellNode())
        format_non_family_layout_mock.assert_called_once()
        format_family_layout_mock.assert_called_once()

    def test_draw_branch_method_calls_ax_plot_once_if_layout_is_family(self) -> None:
        """
        Tests whether the "draw_branch" method calls the "plot" method on the plt.Axes instance once
        if the current layout is family.
        """
        self.tree_drawer_3D.layout = 'family'
        mock_ax = MagicMock()
        self.tree_drawer_3D.draw_branch(ax=mock_ax, branch=[CellNode(), CellNode(), CellNode()])
        mock_ax.plot.assert_called_once()

    def test_draw_branch_method_calls_ax_plot_multiple_times_if_layout_is_not_family(self) -> None:
        """
        Tests whether the "draw_branch" method calls the "plot" method on the plt.Axes instance multiple times
        (once per branch segment) if the current layout is not family.
        """
        self.tree_drawer_3D.layout = 'generation'
        mock_ax = MagicMock()
        self.tree_drawer_3D.draw_branch(ax=mock_ax, branch=[CellNode(), CellNode(), CellNode()])
        self.assertGreater(len(mock_ax.plot.mock_calls), 1)  # called multiple times

    @mock.patch('clovars.simulation.TreeDrawer3D.draw_branch_segment')
    def test_draw_branch_method_calls_draw_branch_segment_only_if_layout_is_not_family(
            self,
            draw_branch_segment_mock: MagicMock,
    ) -> None:
        """
        Tests whether the "draw_branch" method calls the "draw_branch_segment" method
        only if the layout is not family.
        """
        mock_ax = MagicMock()
        self.tree_drawer_3D.layout = 'family'
        self.tree_drawer_3D.draw_branch(ax=mock_ax, branch=[CellNode(), CellNode(), CellNode()])
        draw_branch_segment_mock.assert_not_called()
        self.tree_drawer_3D.layout = 'generation'
        self.tree_drawer_3D.draw_branch(ax=mock_ax, branch=[CellNode(), CellNode(), CellNode()])
        draw_branch_segment_mock.assert_called()

    def test_get_xyz_from_cell_nodes_method_returns_tuple_of_values(self) -> None:
        """Tests whether the "get_xyz_from_cell_nodes" method returns a tuple of list of the XYZ values of each Node."""
        cell_nodes = [
            CellNode(x=10, y=5, simulation_hours=1),
            CellNode(x=12, y=4, simulation_hours=2),
            CellNode(x=14, y=3, simulation_hours=3),
        ]
        xs, ys, zs = self.tree_drawer_3D.get_xyz_from_cell_nodes(cell_nodes=cell_nodes)
        self.assertSequenceEqual(xs, [10, 12, 14])
        self.assertSequenceEqual(ys, [5, 4, 3])
        self.assertSequenceEqual(zs, [1, 2, 3])

    def test_draw_branch_segment_method_calls_ax_plot_once(self) -> None:
        """Tests whether the "draw_branch_segment" method calls the "plot" method on the plt.Axes instance once."""
        mock_ax = MagicMock()
        self.tree_drawer_3D.layout = 'generation'  # use a valid layout for this test
        self.tree_drawer_3D.draw_branch_segment(ax=mock_ax, branch_segment=[CellNode(), CellNode(), CellNode()])
        mock_ax.plot.assert_called_once()

    @unittest.skipIf(SKIP_TESTS is True, "SKIP TESTS is set to True")
    def test_get_segment_color_method_(self) -> None:
        """Docstring."""
        self.fail("Write the test!")

    @unittest.skipIf(SKIP_TESTS is True, "SKIP TESTS is set to True")
    def test_get_time_color_method_(self) -> None:
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
    def test_format_family_layout_method_(self) -> None:
        """Docstring."""
        self.fail("Write the test!")

    @unittest.skipIf(SKIP_TESTS is True, "SKIP TESTS is set to True")
    def test_format_non_family_layout_method_(self) -> None:
        """Docstring."""
        self.fail("Write the test!")

    def test_draw_root_method_calls_ax_scatter(self) -> None:
        """Tests whether the "draw_root" method calls the "scatter" method on the plt.Axes instance."""
        mock_ax = MagicMock()
        self.tree_drawer_3D.draw_root(ax=mock_ax, root_node=CellNode())
        mock_ax.scatter.assert_called_once()

    def test_draw_parents_method_calls_ax_scatter(self) -> None:
        """Tests whether the "draw_parents" method calls the "scatter" method on the plt.Axes instance."""
        mock_ax = MagicMock()
        self.tree_drawer_3D.draw_parents(ax=mock_ax, parent_nodes=[CellNode(), CellNode(), CellNode()])
        mock_ax.scatter.assert_called_once()

    def test_draw_dead_cells_method_calls_ax_scatter(self) -> None:
        """Tests whether the "draw_dead_cells" method calls the "scatter" method on the plt.Axes instance."""
        mock_ax = MagicMock()
        self.tree_drawer_3D.draw_dead_cells(ax=mock_ax, dead_nodes=[CellNode(), CellNode(), CellNode()])
        mock_ax.scatter.assert_called_once()

    def test_draw_leaf_cells_method_calls_ax_scatter(self) -> None:
        """Tests whether the "draw_leaf_cells" method calls the "scatter" method on the plt.Axes instance."""
        mock_ax = MagicMock()
        self.tree_drawer_3D.draw_leaf_cells(ax=mock_ax, leaf_nodes=[CellNode(), CellNode(), CellNode()])
        mock_ax.scatter.assert_called_once()

    def test_add_colorbar_method_adds_colorbar_to_figure(self) -> None:
        """Tests whether the "add_colorbar" method calls the "colorbar" method on the plt.Figure instance."""
        mock_fig, mock_ax = MagicMock(), MagicMock()
        self.tree_drawer_3D.layout = 'generation'  # use a valid layout for this test
        self.tree_drawer_3D.add_colorbar(figure=mock_fig, ax=mock_ax)
        mock_fig.colorbar.assert_called_once()

    def test_draw_well_method_calls_add_patch_on_the_axes_instance(self) -> None:
        """Tests whether the "draw_well" method calls the "add_patch" method on the plt.Axes instance."""
        mock_ax = MagicMock()
        self.tree_drawer_3D.draw_well(ax=mock_ax, well_radius=self.default_well_radius)
        mock_ax.add_patch.assert_called_once()

    def test_set_well_limits_method(self) -> None:
        """Tests whether the "set_well_limits" method calls the "set_limit" methods on the plt.Axes instance."""
        mock_ax = MagicMock()
        self.tree_drawer_3D.set_well_limits(ax=mock_ax, well_radius=self.default_well_radius)
        mock_ax.set_xlim.assert_called_once()
        mock_ax.set_ylim.assert_called_once()
        mock_ax.set_zlim.assert_called_once()


if __name__ == '__main__':
    unittest.main()
