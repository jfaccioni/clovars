import unittest
from pathlib import Path
from typing import Generator
from unittest import mock
from unittest.mock import MagicMock

import pandas as pd

from clovars.abstract import CellNode
from clovars.bio import Treatment
from clovars.simulation import SimulationViewer
from clovars.utils import PathCreatorMixin, QuietPrinterMixin
from tests import NotEmptyTestCase, SKIP_TESTS


class TestSimulationViewer(NotEmptyTestCase):
    """Class representing unit-tests for clovars.simulation.view.simulation_viewer.SimulationViewer class."""
    default_output_folder = Path('SimulationViewer_TEST_FOLDER')
    default_well_radius = 100
    default_cell_data = pd.DataFrame({  # a Cell that divides into two between 60s and 120s
        'signal_value': [0.0, 0.1, 0.2, 0.05],
        'simulation_seconds': [0, 3600, 7200, 10800],
        'simulation_hours': [0, 1, 2, 3],
        'seconds_since_birth': [0, 3600, 0, 3600],
        'generation': [0, 0, 1, 1],
        'name': ['1a-1', '1a-1', '1a-1.1', '1a-1.2'],
        'branch_name': ['1a-1', '1a-1', '1a-1', '1a-1'],
        'colony_name': ['1a', '1a', '1a', '1a'],
    })

    @classmethod
    def tearDownClass(cls) -> None:
        """Tears down the entire test suite by deleting the test output folder."""
        if cls.default_output_folder.exists():
            cls.default_output_folder.rmdir()

    def setUp(self) -> None:
        """Sets up the test case subject (a SimulationViewer instance)."""
        settings = {
            'cell_data': self.default_cell_data,
            'treatment_data': {('1', 0): Treatment()},
            'output_folder': self.default_output_folder,
            'well_radius': self.default_well_radius,
            'verbose': False,
        }
        self.simulation_viewer = SimulationViewer(**settings)

    def tearDown(self) -> None:
        """Tears down each test case by deleting the contents of the output folder."""
        if self.default_output_folder.exists():
            for sub_path in self.default_output_folder.iterdir():
                sub_path.unlink()

    def test_simulation_viewer_inherits_from_quiet_printer_mixin(self) -> None:
        """Tests whether a SimulationViewer inherits from QuietPrinterMixin."""
        self.assertTrue(isinstance(self.simulation_viewer, QuietPrinterMixin))

    def test_simulation_viewer_inherits_from_path_creator_mixin(self) -> None:
        """Tests whether a SimulationViewer inherits from PathCreatorMixin."""
        self.assertTrue(isinstance(self.simulation_viewer, PathCreatorMixin))

    def test_simulation_has_default_class_attributes(self) -> None:
        """Tests whether a Simulation has the expected default class attribute for its settings."""
        expected_attr_dict = {
            "default_colormap_name": str,
            "default_dpi": int,
            "default_layout": str,
            "default_2D_file_name": str,
            "default_2D_file_extension": str,
            "default_video_file_name": str,
            "default_video_file_extension": str,
            "default_3D_file_name": str,
            "default_3D_file_extension": str,
            "default_treatments_file_name": str,
            "default_treatments_file_extension": str,
        }
        for expected_attr, expected_type in expected_attr_dict.items():
            with self.subTest(expected_attr=expected_attr, expected_type=expected_type):
                self.assertTrue(hasattr(SimulationViewer, expected_attr))
                self.assertIsInstance(getattr(SimulationViewer, expected_attr), expected_type)

    def test_simulation_viewer_has_cell_data_attribute(self) -> None:
        """Tests whether a SimulationViewer has the "cell_data" attribute (a pandas DataFrame)."""
        self.assertTrue(hasattr(self.simulation_viewer, 'cell_data'))
        self.assertIsInstance(self.simulation_viewer.cell_data, pd.DataFrame)

    def test_simulation_viewer_has_well_radius_attribute(self) -> None:
        """Tests whether a SimulationViewer has the "well_radius" attribute (a float)."""
        self.assertTrue(hasattr(self.simulation_viewer, 'well_radius'))
        self.assertIsInstance(self.simulation_viewer.well_radius, int)

    def test_simulation_viewer_has_treatment_data_attribute(self) -> None:
        """Tests whether a SimulationViewer has the "treatment_data" attribute (a dictionary)."""
        self.assertTrue(hasattr(self.simulation_viewer, 'treatment_data'))
        self.assertIsInstance(self.simulation_viewer.treatment_data, dict)

    def test_simulation_viewer_has_protected_attributes(self) -> None:
        """Tests whether a SimulationViewer has the expected protected attributes starting as None values."""
        for protected_attr in ['_well_node', '_roots']:
            with self.subTest(protected_attr=protected_attr):
                self.assertTrue(hasattr(self.simulation_viewer, protected_attr))
                self.assertIsNone(getattr(self.simulation_viewer, protected_attr))

    @mock.patch('clovars.simulation.view.simulation_viewer.TreeDrawer2D')
    def test_generate_output_method_creates_tree_drawer_2D(
            self,
            mock_tree_drawer_2D: MagicMock,
    ) -> None:
        """Tests whether the "generate_output" method instantiates a TreeDrawer2D instance."""
        self.simulation_viewer.generate_output(settings={})
        mock_tree_drawer_2D.assert_called_once()

    @mock.patch('clovars.simulation.TreeDrawer2D.display_trees')
    def test_generate_output_method_calls_display_trees_method_on_tree_drawer_2D(
            self,
            mock_display_trees: MagicMock,
    ) -> None:
        """Tests whether the "generate_output" method calls the TreeDrawer2D's "display_trees" method."""
        self.simulation_viewer.generate_output(settings={'display_2D': False})
        mock_display_trees.assert_not_called()
        with mock.patch.object(self.simulation_viewer, 'yield_roots', return_value=[MagicMock()]):
            self.simulation_viewer.generate_output(settings={'display_2D': True})
        mock_display_trees.assert_called()

    @mock.patch('clovars.simulation.TreeDrawer2D.render_trees')
    def test_generate_output_method_calls_render_trees_method_on_tree_drawer_2D(
            self,
            mock_render_trees: MagicMock,
    ) -> None:
        """Tests whether the "generate_output" method calls the TreeDrawer2D's "render_trees" method."""
        self.simulation_viewer.generate_output(settings={'render_2D': False})
        mock_render_trees.assert_not_called()
        with mock.patch.object(self.simulation_viewer, 'yield_roots', return_value=[MagicMock()]):
            self.simulation_viewer.generate_output(settings={'render_2D': True})
        mock_render_trees.assert_called()

    @mock.patch('clovars.simulation.TreeDrawer2D.render_tree_videos')
    def test_generate_output_method_calls_render_tree_videos_method_on_tree_drawer_2D(
            self,
            mock_render_tree_videos: MagicMock,
    ) -> None:
        """Tests whether the "generate_output" method calls the TreeDrawer2D's "render_tree_videos" method."""
        self.simulation_viewer.generate_output(settings={'render_video_2D': False})
        mock_render_tree_videos.assert_not_called()
        with mock.patch.object(self.simulation_viewer, 'yield_roots', return_value=[MagicMock()]):
            self.simulation_viewer.generate_output(settings={'render_video_2D': True})
        mock_render_tree_videos.assert_called()

    @mock.patch('clovars.simulation.view.simulation_viewer.TreeDrawer3D')
    def test_generate_output_method_creates_tree_drawer_3D(
            self,
            mock_tree_drawer_3D: MagicMock,
    ) -> None:
        """Tests whether the "generate_output" method instantiates a TreeDrawer3D instance."""
        self.simulation_viewer.generate_output(settings={})
        mock_tree_drawer_3D.assert_called_once()

    @mock.patch('clovars.simulation.TreeDrawer3D.display_trees')
    def test_generate_output_method_calls_display_trees_method_on_tree_drawer_3D(
            self,
            mock_display_trees: MagicMock,
    ) -> None:
        """Tests whether the "generate_output" method calls the TreeDrawer3D's "display_trees" method."""
        self.simulation_viewer.generate_output(settings={'display_3D': False})
        mock_display_trees.assert_not_called()
        with mock.patch.object(self.simulation_viewer, 'yield_roots', return_value=[MagicMock()]):
            self.simulation_viewer.generate_output(settings={'display_3D': True})
        mock_display_trees.assert_called()

    @mock.patch('clovars.simulation.TreeDrawer3D.render_trees')
    def test_generate_output_method_calls_render_trees_method_on_tree_drawer_3D(
            self,
            mock_render_trees: MagicMock,
    ) -> None:
        """Tests whether the "generate_output" method calls the TreeDrawer3D's "render_trees" method."""
        self.simulation_viewer.generate_output(settings={'render_3D': False})
        mock_render_trees.assert_not_called()
        with mock.patch.object(self.simulation_viewer, 'yield_roots', return_value=[MagicMock()]):
            self.simulation_viewer.generate_output(settings={'render_3D': True})
        mock_render_trees.assert_called()

    @mock.patch('clovars.simulation.view.simulation_viewer.TreatmentDrawer')
    def test_generate_output_method_creates_treatment_drawer(
            self,
            mock_treatment_drawer: MagicMock,
    ) -> None:
        """Tests whether the "generate_output" method instantiates a TreatmentDrawer instance."""
        self.simulation_viewer.generate_output(settings={})
        mock_treatment_drawer.assert_called_once()

    @mock.patch('clovars.simulation.TreatmentDrawer.display')
    def test_generate_output_method_calls_display_method_on_treatment_drawer(
            self,
            mock_show_gaussians: MagicMock,
    ) -> None:
        """Tests whether the "generate_output" method calls the TreatmentDrawer's "display" method."""
        self.simulation_viewer.generate_output(settings={'display_treatments': False})
        mock_show_gaussians.assert_not_called()
        self.simulation_viewer.generate_output(settings={'display_treatments': True})
        mock_show_gaussians.assert_called()

    @mock.patch('clovars.simulation.TreatmentDrawer.render')
    def test_generate_output_method_calls_render_method_on_treatment_drawer(
            self,
            mock_render_gaussians: MagicMock,
    ) -> None:
        """Tests whether the "generate_output" method calls the TreatmentDrawer's "display" method."""
        self.simulation_viewer.generate_output(settings={'render_treatments': False})
        mock_render_gaussians.assert_not_called()
        self.simulation_viewer.generate_output(settings={'render_treatments': True})
        mock_render_gaussians.assert_called()

    def test_well_node_property_returns_cell_node_instance(self) -> None:
        """Tests whether the "well_node" property returns a CellNode instance."""
        self.assertIsInstance(self.simulation_viewer.well_node, CellNode)

    def test_well_node_avoids_calling_get_well_node_if_value_is_not_none(self) -> None:
        """Tests whether the "well_node" property avoids calling the "get_well_node" method if its value is not None."""
        with mock.patch.object(self.simulation_viewer, 'get_well_node') as mock_get_well_node:
            self.simulation_viewer._well_node = "Not None!"
            self.simulation_viewer.well_node  # noqa
        mock_get_well_node.assert_not_called()
        with mock.patch.object(self.simulation_viewer, 'get_well_node') as mock_get_well_node:
            self.simulation_viewer._well_node = None
            self.simulation_viewer.well_node  # noqa
        mock_get_well_node.assert_called_once()

    def test_roots_property_returns_list_of_node_instances(self) -> None:
        """Tests whether the "roots" property returns a list of CellNode instances."""
        self.assertIsInstance(self.simulation_viewer.roots, list)
        with self.assertSequenceNotEmpty(self.simulation_viewer.roots):
            for root in self.simulation_viewer.roots:
                self.assertIsInstance(root, CellNode)

    def test_roots_avoids_calling_yield_roots_if_value_is_not_none(self) -> None:
        """Tests whether the "roots" property avoids calling the "yield_roots" method if its value is not None."""
        with mock.patch.object(self.simulation_viewer, 'yield_roots') as mock_yield_roots:
            self.simulation_viewer._roots = "Not None!"
            self.simulation_viewer.roots  # noqa
        mock_yield_roots.assert_not_called()
        with mock.patch.object(self.simulation_viewer, 'yield_roots') as mock_yield_roots:
            self.simulation_viewer._roots = None
            self.simulation_viewer.roots  # noqa
        mock_yield_roots.assert_called_once()

    def test_get_well_node_method_returns_cell_node_instance(self) -> None:
        """Tests whether the "ge_well_node" method returns a CellNode instance."""
        self.assertIsInstance(self.simulation_viewer.get_well_node(), CellNode)

    def test_get_well_node_method_places_every_root_node_as_child(self) -> None:
        """Tests whether the "get_well_node" method places every root Node as a child to the Well Node."""
        expected_roots = [CellNode(), CellNode(), CellNode()]
        expected_roots[0].add_child(CellNode())  # This child Node should not appear as a Well Node child  # noqa
        self.simulation_viewer._roots = expected_roots
        actual_roots = self.simulation_viewer.get_well_node().children
        self.assertEqual(len(expected_roots), len(actual_roots))
        for expected_root, actual_root in zip(expected_roots, actual_roots):
            self.assertEqual(expected_root, actual_root)

    def test_yield_roots_method_returns_a_generator(self) -> None:
        """Tests whether the "yield_roots" method returns a generator instance."""
        self.assertIsInstance(self.simulation_viewer.yield_roots(), Generator)

    def test_yield_roots_sequentially_yields_nodes(self) -> None:
        """Tests whether the "yield_roots" method sequentially yields root CellNodes from the dataset."""
        roots = list(self.simulation_viewer.yield_roots())
        self.assertEqual(len(roots), 1)  # Default test case, only one root CellNode
        for i, suffix in enumerate('bcde', 2):
            self.simulation_viewer.cell_data = pd.concat([
                self.simulation_viewer.cell_data,
                pd.DataFrame({
                    'signal_value': 0.0,
                    'simulation_seconds': 0,
                    'generation': 0,
                    'name': f'1{suffix}-1',
                    'branch_name': f'1{suffix}-1',
                    'colony_name': f'1{suffix}',
                }, index=[0])
            ], ignore_index=True)
            roots = list(self.simulation_viewer.yield_roots())
            self.assertEqual(len(roots), i)  # adds one new root CellNode at a time

    def test_get_root_data_returns_a_node_instance(self) -> None:
        """Tests whether the "get_root_data" method returns a CellNode instance."""
        root = self.simulation_viewer.get_root_data(root_name='1a-1', root_data=self.default_cell_data)
        self.assertIsInstance(root, CellNode)

    def test_get_root_data_raises_error_if_name_is_invalid(self) -> None:
        """
        Tests whether the "get_root_data" method raises a ValueError if the provided root name does not exist
        in the DataFrame's "name" column.
        """
        valid_names = ['1a-1', '2a-b', '3e-12']
        mock_dataframe = pd.DataFrame({'name': valid_names, 'simulation_seconds': [0, 0, 0]})
        for invalid_name in ['', 'AAAAAAAAA', '???']:
            with self.subTest(invalid_name=invalid_name), self.assertRaises(ValueError):
                self.simulation_viewer.get_root_data(root_name=invalid_name, root_data=mock_dataframe)
        for valid_name in valid_names:
            with self.subTest(valid_name=valid_name):
                try:
                    self.simulation_viewer.get_root_data(root_name=valid_name, root_data=mock_dataframe)
                except ValueError:
                    self.fail(f'Valid name {valid_name} unexpectedly raised a ValueError!')

    def test_get_root_data_returns_node_with_tree_structure(self) -> None:
        """Tests whether the Node returned by the "get_root_data" has a defined tree structure."""
        expected_cells_in_tree = len(self.default_cell_data)
        root = self.simulation_viewer.get_root_data(root_name='1a-1', root_data=self.simulation_viewer.cell_data)
        actual_cells_in_tree = len([node for node in root.traverse()])
        self.assertEqual(actual_cells_in_tree, expected_cells_in_tree)  # At the start, all data is from the same root
        for suffix in 'bcde':
            self.simulation_viewer.cell_data = pd.concat([
                self.simulation_viewer.cell_data,
                pd.DataFrame({
                    'signal_value': 0.0,
                    'simulation_seconds': 0,
                    'generation': 0,
                    'name': f'1{suffix}-1',
                    'branch_name': f'1{suffix}-1',
                    'colony_name': f'1{suffix}',
                }, index=[0])
            ], ignore_index=True)  # Adds unrelated CellNodes to the data
            root = self.simulation_viewer.get_root_data(root_name='1a-1', root_data=self.simulation_viewer.cell_data)
            actual_cells_in_tree = len([node for node in root.traverse()])
            self.assertEqual(actual_cells_in_tree, expected_cells_in_tree)  # Tree should not change
            new_root = self.simulation_viewer.get_root_data(
                root_name=f'1{suffix}-1',
                root_data=self.simulation_viewer.cell_data,
            )
            actual_cells_in_new_tree = len([node for node in new_root.traverse()])
            self.assertEqual(actual_cells_in_new_tree, 1)  # Tree has a single CellNode in it

    def test_build_tree_returns_a_node_instance(self) -> None:
        """Tests whether the "build_tree" returns a CellNode instance."""
        root = self.simulation_viewer.build_tree(root_name='1a-1', groups=self.default_cell_data.groupby('name'))
        self.assertIsInstance(root, CellNode)

    @unittest.skipIf(SKIP_TESTS is True, "SKIP TESTS is set to True")
    def test_build_tree_returns_node_with_tree_structure(self) -> None:
        """Tests whether the Node returned by the "build_tree" has a defined tree structure."""
        self.fail('Write the test!')  # TODO: revise the code used for this test, currently kinda confusing


if __name__ == '__main__':
    unittest.main()
