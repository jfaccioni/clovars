import unittest
from pathlib import Path
from typing import Callable
from unittest import mock
from unittest.mock import MagicMock

import pandas as pd
from ete3 import TreeStyle
from matplotlib.colors import Normalize, Colormap

from clovars.abstract import CellNode
from clovars.simulation import TreeDrawer


class TestTreeDrawer(unittest.TestCase):
    """Class representing unit-tests of clovars.simulation.view.simulation_viewer.TreeDrawer objects."""
    default_delta = 100
    default_folder_path = Path('.')
    default_file_name = 'file_name'
    default_file_extension = '.png'
    default_dpi = 120
    default_well_radius = 100

    def setUp(self) -> None:
        """Sets up the test case subject (a TreeDrawer instance)."""
        self.tree_drawer = TreeDrawer()

    def test_tree_drawer_has_colormap_attribute(self) -> None:
        """Tests whether a TreeDrawer has the "colormap" attribute (a Colormap instance)."""
        self.assertTrue(hasattr(self.tree_drawer, 'colormap'))
        self.assertIsInstance(self.tree_drawer.colormap, Colormap)

    def test_tree_drawer_has_normalizer_attributes(self) -> None:
        """Tests whether a TreeDrawer has the expected normalizer attributes."""
        for normalizer_attr_name in ['signal_normalizer', 'time_normalizer', 'division_normalizer']:
            with self.subTest(normalizer_attr_name=normalizer_attr_name):
                self.assertTrue(hasattr(self.tree_drawer, normalizer_attr_name))
                self.assertIsInstance(getattr(self.tree_drawer, normalizer_attr_name), Normalize)

    def test_tree_drawer_has_tree_style_dict_attribute(self) -> None:
        """Tests whether a TreeDrawer has the "tree_style_dict" attribute (a dictionary)."""
        self.assertTrue(hasattr(self.tree_drawer, 'tree_style_dict'))
        self.assertIsInstance(self.tree_drawer.tree_style_dict, dict)
        for key, value in self.tree_drawer.tree_style_dict.items():
            self.assertIsInstance(key, str)
            self.assertIsInstance(value, Callable)

    def test_get_normalizer_method_returns_normalize_instance(self) -> None:
        """Tests whether the "get_normalizer" method returns a Normalize instance."""
        self.assertIsInstance(self.tree_drawer.get_normalizer(), Normalize)

    def test_get_normalizer_method_normalizes_signals_from_cells(self) -> None:
        """Tests whether the "get_normalizer" method normalizes the pandas Series values between 0 and 1."""
        values = pd.Series([0.20, 0.37, 0.55, 0.80])
        normalizer = self.tree_drawer.get_normalizer(values=values)
        self.assertEqual(normalizer(0.2), 0)
        self.assertEqual(normalizer(0.8), 1)

    @mock.patch('clovars.abstract.CellNode.show')
    @mock.patch('clovars.simulation.TreeDrawer.get_tree_style')
    def test_show_ete3_method_calls_show_on_well_node(
            self,
            mock_get_tree_style: MagicMock,
            mock_show: MagicMock,
    ) -> None:
        """
        Tests whether the "show_ete3" method calls the root CellNode's "show" method
        passing in the return value from "get_tree_style" method.
        """
        self.tree_drawer.show_ete3(root=CellNode(name='1a-1'))
        mock_get_tree_style.assert_called_once()
        mock_show.assert_called_once()
        self.assertIn(mock_get_tree_style.return_value, mock_show.call_args.kwargs.values())

    @mock.patch('clovars.abstract.CellNode.render')
    @mock.patch('clovars.simulation.TreeDrawer.get_tree_style')
    def test_render_ete3_method_calls_render_on_root_node(
            self,
            mock_get_tree_style: MagicMock,
            mock_render: MagicMock,
    ) -> None:
        """
        Tests whether the "render_ete3" method calls the root CellNode's "render" method
        passing in the return value from "get_tree_style" method.
        """
        self.tree_drawer.render_ete3(
            root=CellNode(name='1a-1'),
            folder_path=self.default_folder_path,
            file_name=self.default_file_name,
            file_extension=self.default_file_extension,
            dpi=self.default_dpi,
        )
        mock_get_tree_style.assert_called_once()
        mock_render.assert_called_once()
        self.assertIn(mock_get_tree_style.return_value, mock_render.call_args.kwargs.values())

    def test_get_tree_style_method_returns_a_tree_style_instance(self) -> None:
        """Tests whether the "get_tree_style" method returns a TreeStyle instance."""
        tree_style = self.tree_drawer.get_tree_style()
        self.assertIsInstance(tree_style, TreeStyle)

    def test_get_tree_style_method_sets_the_appropriate_layout_function(self) -> None:
        """Tests whether the "get_tree_style" method sets the appropriate layout function on the TreeStyle."""
        layout_test_cases = {
            'family': self.tree_drawer.family_layout_function,
            'signal': self.tree_drawer.signal_layout_function,
            'time': self.tree_drawer.time_layout_function,
            'division': self.tree_drawer.division_layout_function,
        }
        for tree_layout, expected_layout_function in layout_test_cases.items():
            tree_style = self.tree_drawer.get_tree_style(tree_layout=tree_layout)
            self.assertIn(expected_layout_function, tree_style.layout_fn)  # noqa

    def test_get_tree_style_method_raises_error_on_invalid_style(self) -> None:
        """Tests whether the "get_tree_style" method raises a ValueError if the "tree_layout" argument is not valid."""
        with self.assertRaises(ValueError):
            self.tree_drawer.get_tree_style(tree_layout='something wrong')

    @mock.patch('clovars.simulation.view.tree_drawer.add_face_to_node')
    def test_family_layout_function_calls_set_style(
            self,
            _: MagicMock,  # mocked add_face_to_node because it requires to be called from a TreeStyle layout function
    ) -> None:
        """Tests whether the "family_layout_function" method calls the Node's "set_style" method."""
        node = CellNode()
        with mock.patch('clovars.abstract.CellNode.set_style') as mock_set_style:
            self.tree_drawer.family_layout_function(node=node)
        mock_set_style.assert_called()

    @mock.patch('clovars.simulation.view.tree_drawer.add_face_to_node')
    def test_signal_layout_function_calls_set_style(
            self,
            _: MagicMock,  # mocked add_face_to_node because it requires to be called from a TreeStyle layout function
    ) -> None:
        """Tests whether the "signal_layout_function" method calls the Node's "set_style" method."""
        node = CellNode()
        with mock.patch('clovars.abstract.CellNode.set_style') as mock_set_style:
            self.tree_drawer.signal_layout_function(node=node)
        mock_set_style.assert_called()

    @mock.patch('clovars.simulation.view.tree_drawer.add_face_to_node')
    def test_time_layout_function_calls_set_style(
            self,
            _: MagicMock,  # mocked add_face_to_node because it requires to be called from a TreeStyle layout function
    ) -> None:
        """Tests whether the "time_layout_function" method calls the Node's "set_style" method."""
        node = CellNode()
        with mock.patch('clovars.abstract.CellNode.set_style') as mock_set_style:
            self.tree_drawer.time_layout_function(node=node)
        mock_set_style.assert_called()

    @mock.patch('clovars.simulation.view.tree_drawer.add_face_to_node')
    def test_division_layout_function_calls_set_style(
            self,
            _: MagicMock,  # mocked add_face_to_node because it requires to be called from a TreeStyle layout function
    ) -> None:
        """Tests whether the "division_layout_function" method calls the Node's "set_style" method."""
        node = CellNode()
        with mock.patch('clovars.abstract.CellNode.set_style') as mock_set_style:
            self.tree_drawer.division_layout_function(node=node)
        mock_set_style.assert_called()

    @mock.patch('clovars.simulation.view.tree_drawer.add_face_to_node')
    def test_color_layout_function_calls_set_style(
            self,
            _: MagicMock,  # mocked add_face_to_node because it requires to be called from a TreeStyle layout function
    ) -> None:
        """Tests whether the "set_color_layout" method calls the Node's "set_style" method."""
        node = CellNode()
        with mock.patch('clovars.abstract.CellNode.set_style') as mock_set_style:
            self.tree_drawer.color_layout_function(node=node, color='#ffffff')
        mock_set_style.assert_called()

    def test_show_trees_matplotlib_method_calls_plt_show(self) -> None:
        """Tests whether the "show_trees_matplotlib" method calls "plt.show" (i.e. it displays a plot)."""
        with mock.patch('clovars.simulation.view.tree_drawer.plt') as mock_plt:
            self.tree_drawer.show_trees_matplotlib(well_node=CellNode(), well_radius=self.default_well_radius)
        mock_plt.show.assert_called_once()

    def test_render_trees_matplotlib_method_calls_plt_show(self) -> None:
        """Tests whether the "render_trees_matplotlib" method calls "plt.Figure.savefig" (i.e. it saves a figure)."""
        with mock.patch('clovars.simulation.view.tree_drawer.plt.Figure.savefig') as mock_figure_savefig:
            self.tree_drawer.render_trees_matplotlib(
                well_node=CellNode(),
                well_radius=self.default_well_radius,
                folder_path=self.default_folder_path,
                file_name=self.default_file_name,
                file_extension=self.default_file_extension,
            )
        mock_figure_savefig.assert_called_once()

    def test_draw_well_method_calls_add_patch_on_the_axes_instance(self) -> None:
        """Tests whether the "draw_well" method calls the "add_patch" method on the plt.Axes instance."""
        mock_ax = MagicMock()
        self.tree_drawer.draw_well(ax=mock_ax, well_radius=self.default_well_radius)
        mock_ax.add_patch.assert_called_once()

    @mock.patch('clovars.simulation.TreeDrawer.draw_dead_cells')
    @mock.patch('clovars.simulation.TreeDrawer.draw_parents')
    @mock.patch('clovars.simulation.TreeDrawer.draw_branch')
    def test_draw_tree_method_calls_downstream_drawing_methods(
            self,
            *draw_mocks: MagicMock,
    ) -> None:
        """Tests whether the "draw_tree" method calls the related downstream "draw" methods."""
        root = CellNode()
        root.add_child()
        root.add_child()
        root.children[0].add_child()
        self.tree_drawer.draw_tree(ax=MagicMock(), root=root)
        for draw_mock in draw_mocks:
            draw_mock.assert_called()

    def test_draw_branch_method_calls_ax_plot(self) -> None:
        """Tests whether the "draw_branch" method calls the "plot" method on the plt.Axes instance."""
        mock_ax = MagicMock()
        self.tree_drawer.draw_branch(ax=mock_ax, branch=[CellNode(), CellNode(), CellNode()])
        mock_ax.plot.assert_called_once()

    def test_draw_parents_method_calls_ax_scatter(self) -> None:
        """Tests whether the "draw_parents" method calls the "scatter" method on the plt.Axes instance."""
        mock_ax = MagicMock()
        self.tree_drawer.draw_parents(ax=mock_ax, parent_nodes=[CellNode(), CellNode(), CellNode()])
        mock_ax.scatter.assert_called_once()

    def test_draw_dead_cells_method_calls_ax_scatter(self) -> None:
        """Tests whether the "draw_dead_cells" method calls the "scatter" method on the plt.Axes instance."""
        mock_ax = MagicMock()
        self.tree_drawer.draw_dead_cells(ax=mock_ax, dead_nodes=[CellNode(), CellNode(), CellNode()])
        mock_ax.scatter.assert_called_once()

    def test_get_xyz_from_cell_nodes_method_returns_tuple_of_values(self) -> None:
        """Tests whether the "get_xyz_from_cell_nodes" method returns a tuple of list of the XYZ values of each Node."""
        cell_nodes = [
            CellNode(x=10, y=5, simulation_hours=1),
            CellNode(x=12, y=4, simulation_hours=2),
            CellNode(x=14, y=3, simulation_hours=3),
        ]
        xs, ys, zs = self.tree_drawer.get_xyz_from_cell_nodes(cell_nodes=cell_nodes)
        self.assertSequenceEqual(xs, [10, 12, 14])
        self.assertSequenceEqual(ys, [5, 4, 3])
        self.assertSequenceEqual(zs, [1, 2, 3])

    def test_add_colorbar_method(self) -> None:
        """Tests whether the "add_colorbar" method calls the "colorbar" method on the plt.Figure instance."""
        mock_fig, mock_ax = MagicMock(), MagicMock()
        self.tree_drawer.add_colorbar(figure=mock_fig, ax=mock_ax)
        mock_fig.colorbar.assert_called_once()

    def test_set_limits_method(self) -> None:
        """Tests whether the "set_limits" method calls the "set_limit" methods on the plt.Axes instance."""
        mock_ax = MagicMock()
        self.tree_drawer.set_limits(ax=mock_ax, well_radius=self.default_well_radius)
        mock_ax.set_xlim.assert_called_once()
        mock_ax.set_ylim.assert_called_once()
        mock_ax.set_zlim.assert_called_once()


if __name__ == '__main__':
    unittest.main()
