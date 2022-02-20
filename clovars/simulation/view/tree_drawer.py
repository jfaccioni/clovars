from __future__ import annotations

from typing import TYPE_CHECKING

import numpy as np
import pandas as pd
from ete3 import TreeStyle, NodeStyle, AttrFace, add_face_to_node
from matplotlib import pyplot as plt
from matplotlib.cm import get_cmap
from matplotlib.colors import Normalize, to_hex
from mpl_toolkits.mplot3d import art3d

if TYPE_CHECKING:
    from pathlib import Path
    from clovars.abstract import CellNode


class TreeDrawer:
    """Class containing functions to draw and display Cell trees."""
    def __init__(
            self,
            colormap_name: str = 'viridis',
            signal_values: pd.Series | None = None,
            time_values: pd.Series | None = None,
            division_values: pd.Series | None = None,
    ) -> None:
        """Initializes a TreeDrawer instance."""
        self.colormap = get_cmap(colormap_name)
        self.signal_normalizer = self.get_normalizer(values=signal_values)
        self.time_normalizer = self.get_normalizer(values=time_values)
        self.division_normalizer = self.get_normalizer(values=division_values)
        self.tree_style_dict = {
            'family': self.family_layout_function,
            'signal': self.signal_layout_function,
            'time': self.time_layout_function,
            'division': self.division_layout_function,
        }

    @staticmethod
    def get_normalizer(values: pd.Series | None = None) -> Normalize:
        """Returns a Normalize instance that normalizes the values in the pandas Series between 0 and 1."""
        if values is None:
            return Normalize(vmin=0, vmax=1)
        if values.empty:
            return Normalize(vmin=0, vmax=1)
        return Normalize(vmin=values.min(), vmax=values.max())

    def show_ete3(
            self,
            root: CellNode,
            tree_layout: str = 'family',
    ) -> None:
        """Displays the tree from the cell root in the Well through the ete3 interface."""
        tree_style = self.get_tree_style(tree_layout=tree_layout)
        root.show(tree_style=tree_style)

    def render_ete3(
            self,
            root: CellNode,
            folder_path: Path,
            file_name: str,
            file_extension: str,
            dpi: int,
            tree_layout: str = 'family',
    ) -> None:
        """Renders the view of the SimulationViewer through the ete3 interface."""
        tree_style = self.get_tree_style(tree_layout=tree_layout)
        fname = str(folder_path / f'{file_name}_{root.as_file_name()}.{file_extension}')
        root.render(file_name=fname, tree_style=tree_style, dpi=dpi)

    def get_tree_style(
            self,
            tree_layout: str = 'family',
    ) -> TreeStyle:
        """Returns a TreeStyle to be used when formatting the ete3 trees."""
        tree_style = TreeStyle()
        tree_style.branch_vertical_margin = 10
        tree_style.optimal_scale_level = 'full'
        try:
            tree_style.layout_fn = self.tree_style_dict[tree_layout]
        except KeyError:
            raise ValueError(f'Invalid tree_layout: {tree_layout}.\nValid names: {list(self.tree_style_dict.keys())}')
        return tree_style

    @staticmethod
    def family_layout_function(node: CellNode) -> None:
        """Layouts the given Node instance as a family tree for the ete3 interface."""
        if node.is_root():
            node.set_style(NodeStyle(fgcolor='RoyalBlue', size=5))
            add_face_to_node(AttrFace("name"), node, column=0, position='float')
        elif node.is_parent():
            node.set_style(NodeStyle(fgcolor='MediumSeaGreen', size=5))
        elif node.is_child():
            add_face_to_node(AttrFace("name"), node, column=0, position='float')
        elif node.is_dead():
            node.set_style(NodeStyle(fgcolor='Tomato', size=5))
        elif node.is_leaf():
            node.set_style(NodeStyle(fgcolor='RoyalBlue', size=5))
        else:
            node.set_style(NodeStyle(fgcolor='Silver', size=3))

    def signal_layout_function(
            self,
            node: CellNode,
    ) -> None:
        """Layouts the given Node instance as a signal tree for the ete3 interface."""
        color = to_hex(self.colormap(self.signal_normalizer(node.signal_value)))
        self.color_layout_function(node=node, color=color)

    def time_layout_function(
            self,
            node: CellNode,
    ) -> None:
        """Layouts the given Node instance as a time tree for the ete3 interface."""
        color = to_hex(self.colormap(self.time_normalizer(node.simulation_seconds)))
        self.color_layout_function(node=node, color=color)

    def division_layout_function(
            self,
            node: CellNode,
    ) -> None:
        """Layouts the given Node instance as a time tree for the ete3 interface."""
        color = to_hex(self.colormap(self.division_normalizer(node.generation)))
        self.color_layout_function(node=node, color=color)

    @staticmethod
    def color_layout_function(
            node: CellNode,
            color: str,
    ) -> None:
        """Layouts the given Node instance as a colored tree for the ete3 interface."""
        if node.is_root():
            node.set_style(NodeStyle(fgcolor=color, size=5))
            add_face_to_node(AttrFace("name"), node, column=0, position='float')
        elif node.is_parent():
            node.set_style(NodeStyle(fgcolor=color, size=5))
        elif node.is_child():
            node.set_style(NodeStyle(fgcolor=color, size=5))
            add_face_to_node(AttrFace("name"), node, column=0, position='float')
        elif node.is_dead():
            node.set_style(NodeStyle(fgcolor=color, size=5))
        elif node.is_leaf():
            node.set_style(NodeStyle(fgcolor=color, size=5))
        else:
            node.set_style(NodeStyle(fgcolor=color, size=3))

    def show_trees_matplotlib_2D(
            self,
            well_node: CellNode,
            layout: str,
    ) -> None:
        """Displays the view of the SimulationViewer as a matplotlib 2D plot."""
        figure, ax = plt.subplots()
        self.draw_2D_scatter(well_node=well_node, layout=layout, ax=ax)
        for branch in well_node.yield_branches():
            self.draw_2D_branch(branch=branch, ax=ax)
        ax.set_xlabel('Simulation time (hours)')
        ax.set_ylabel('')
        self.add_colorbar(figure=figure, ax=ax)
        plt.show()

    def render_trees_matplotlib_2D(
            self,
            well_node: CellNode,
            layout: str,
            folder_path: Path,
            file_name: str,
            file_extension: str,
    ) -> None:
        """Renders the view of the SimulationViewer as a matplotlib 2D plot."""
        figure, ax = plt.subplots()
        self.draw_2D_scatter(well_node=well_node, layout=layout, ax=ax)
        for branch in well_node.yield_branches():
            self.draw_2D_branch(branch=branch, ax=ax)
        ax.set_xlabel('Simulation time (hours)')
        ax.set_ylabel('')
        self.add_colorbar(figure=figure, ax=ax)
        fname = str(folder_path / f'{file_name}.{file_extension}')
        figure.savefig(fname)
        plt.close(figure)

    def draw_2D_scatter(
            self,
            well_node: CellNode,
            layout: str,
            ax: plt.Axes,
    ) -> None:
        xs, ys, cs, ms = [], [], [], []
        for node in well_node.iter_descendants():
            xs.append(node.simulation_seconds)
            ys.append(self.get_height_from_name(name=node.name))
            if layout == 'family':
                cs.append(self.get_family_color(node=node))
            elif layout == 'time':
                cs.append(self.time_normalizer(node.simulation_seconds))
            elif layout == 'division':
                cs.append(self.division_normalizer(node.generation))
            elif layout == 'signal':
                cs.append(self.signal_normalizer(node.signal_value))
            else:
                raise ValueError(f'Invalid layout: {layout}')
            ms = '.' if layout != 'family' else self.get_family_marker(node=node)
        ax.scatter(xs, ys, c=cs, marker=ms)

    def draw_2D_branch(
            self,
            branch: list[CellNode],
            ax: plt.Axes,
    ) -> None:
        """Draws a branch onto the 2D tree."""
        xs = [node.simulation_seconds for node in branch]
        ys = [self.get_height_from_name(name=node.name) for node in branch]
        ax.plot(xs, ys, c='0.7', zorder=1)

    @staticmethod
    def get_family_color(node: CellNode) -> str:
        """Returns the proper color for the given CellNode, when plotting the 2D tree as a family."""
        if node.is_root():
            return 'blue'
        elif node.is_leaf():
            return 'orange'
        elif node.is_dead():
            return 'red'
        elif node.is_parent():
            return 'green'
        else:
            return 'gray'

    @staticmethod
    def get_family_marker(node: CellNode) -> str:
        """Returns the proper marker style for the given CellNode, when plotting the 2D tree as a family."""
        if node.is_root():
            return '*'
        elif node.is_leaf():
            return '.'
        elif node.is_dead():
            return 'x'
        elif node.is_parent():
            return '.'
        else:
            return '.'

    @staticmethod
    def get_height_from_name(name: str) -> float:
        """Returns the height of the CellNode in a 2D tree, given its name."""
        height = 0.0
        current_step = 0.5
        for number in name.split('.')[1:]:
            if number == '1':
                height += current_step
            elif number == '2':
                height -= current_step
            current_step /= 2
        return height

    def show_trees_matplotlib_3D(
            self,
            well_node: CellNode,
            well_radius: float,
    ) -> None:
        """Displays the view of the SimulationViewer as a matplotlib 3D plot."""
        figure = plt.figure()
        ax = figure.add_subplot(projection='3d')
        self.draw_well(ax=ax, well_radius=well_radius)
        for root_node in well_node.children:
            self.draw_tree(ax=ax, root=root_node)
        ax.set_xlabel('X coordinate (µm)')
        ax.set_ylabel('Y coordinate (µm)')
        ax.set_zlabel('Time (h)')
        self.add_colorbar(figure=figure, ax=ax)
        self.set_limits(ax=ax, well_radius=well_radius)
        plt.show()

    def render_trees_matplotlib_3D(
            self,
            well_node: CellNode,
            well_radius: float,
            folder_path: Path,
            file_name: str,
            file_extension: str,
    ) -> None:
        """Renders the view of the SimulationViewer as a matplotlib 3D plot."""
        figure = plt.figure()
        ax = figure.add_subplot(projection='3d')
        self.draw_well(ax=ax, well_radius=well_radius)
        for root_node in well_node.children:
            self.draw_tree(ax=ax, root=root_node)
        ax.set_xlabel('X coordinate (µm)')
        ax.set_ylabel('Y coordinate (µm)')
        ax.set_zlabel('Time (h)')
        self.add_colorbar(figure=figure, ax=ax)
        self.set_limits(ax=ax, well_radius=well_radius)
        fname = str(folder_path / f'{file_name}.{file_extension}')
        figure.savefig(fname)
        plt.close(figure)

    @staticmethod
    def draw_well(
            ax: plt.Axes,
            well_radius: float,
    ) -> None:
        """Draws the Well onto the bottom of the 3D plot."""
        well_patch = plt.Circle((well_radius, well_radius), well_radius, color='#232323', alpha=0.3)
        ax.add_patch(well_patch)
        art3d.pathpatch_2d_to_3d(well_patch, z=0, zdir="z")

    def draw_tree(
            self,
            ax: plt.Axes,
            root: CellNode,
    ) -> None:
        """Draws the tree on a matplotlib 3D plot."""
        for branch in root.yield_branches():
            self.draw_branch(ax=ax, branch=branch)
        parent_nodes = root.search_nodes(fate_at_next_frame='division')
        self.draw_parents(ax=ax, parent_nodes=parent_nodes)
        dead_nodes = root.search_nodes(fate_at_next_frame='death')
        self.draw_dead_cells(ax=ax, dead_nodes=dead_nodes)

    def draw_branch(
            self,
            ax: plt.Axes,
            branch: list[CellNode],
    ) -> None:
        """Draws the branch on a matplotlib 3D plot."""
        xs, ys, zs = self.get_xyz_from_cell_nodes(cell_nodes=branch)
        color = self.colormap(self.time_normalizer(np.median(zs)))
        ax.plot(xs, ys, zs, color=color, alpha=0.7)

    def draw_parents(
            self,
            ax: plt.Axes,
            parent_nodes: list[CellNode],
    ) -> None:
        """Draws the parent Cells on a matplotlib 3D plot."""
        xs, ys, zs = self.get_xyz_from_cell_nodes(cell_nodes=parent_nodes)
        ax.scatter(xs, ys, zs, color='black', marker='o', alpha=0.7)

    def draw_dead_cells(
            self,
            ax: plt.Axes,
            dead_nodes: list[CellNode],
    ) -> None:
        """Draws the dead Cells on a matplotlib 3D plot."""
        xs, ys, zs = self.get_xyz_from_cell_nodes(cell_nodes=dead_nodes)
        ax.scatter(xs, ys, zs, color='red', marker='x', alpha=0.7)

    @staticmethod
    def get_xyz_from_cell_nodes(cell_nodes: list[CellNode]) -> tuple[list[float], list[float], list[float]]:
        """Returns the XYZ coordinates of each CellNode in the input list."""
        xs = [node.x for node in cell_nodes]
        ys = [node.y for node in cell_nodes]
        zs = [node.simulation_hours for node in cell_nodes]
        return xs, ys, zs

    def add_colorbar(
            self,
            figure: plt.Figure,
            ax: plt.Axes,
    ) -> None:
        """Adds a colorbar to the Figure."""
        mappable = plt.cm.ScalarMappable(norm=self.division_normalizer, cmap=self.colormap)
        cbar = figure.colorbar(mappable=mappable, ax=ax, label='Number of divisions')
        cbar.set_ticks([tick for tick in cbar.get_ticks() if tick.is_integer()])

    @staticmethod
    def set_limits(
            ax: plt.Axes,
            well_radius: float,
    ) -> None:
        """Sets the 3D plot limits based on the drawn Well."""
        ax.set_xlim(0, well_radius * 2)
        ax.set_ylim(0, well_radius * 2)
        ax.set_zlim(bottom=0)
