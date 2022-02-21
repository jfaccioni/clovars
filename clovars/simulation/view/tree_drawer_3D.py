from __future__ import annotations

from typing import TYPE_CHECKING

import numpy as np
import pandas as pd
from matplotlib import pyplot as plt
from matplotlib.cm import get_cmap
from matplotlib.colors import Normalize
from mpl_toolkits.mplot3d import art3d

if TYPE_CHECKING:
    from pathlib import Path
    from clovars.abstract import CellNode


class TreeDrawer3D:
    """Class containing functions to draw and display Cell trees in 3D."""
    def __init__(
            self,
            colormap_name: str = 'viridis',
            layout: str = 'family',
            signal_values: pd.Series | None = None,
            age_values: pd.Series | None = None,
            time_values: pd.Series | None = None,
            generation_values: pd.Series | None = None,
    ) -> None:
        """Initializes a TreeDrawer instance."""
        self.colormap = get_cmap(colormap_name)
        self.layout = layout  # not being used for anything now
        self.time_normalizer = self.get_normalizer(values=time_values)
        self.age_normalizer = self.get_normalizer(values=age_values)
        self.generation_normalizer = self.get_normalizer(values=generation_values)
        self.signal_normalizer = self.get_normalizer(values=signal_values)

    @staticmethod
    def get_normalizer(values: pd.Series | None = None) -> Normalize:
        """Returns a Normalize instance that normalizes the values in the pandas Series between 0 and 1."""
        if values is None:
            return Normalize(vmin=0, vmax=1)
        if values.empty:
            return Normalize(vmin=0, vmax=1)
        return Normalize(vmin=values.min(), vmax=values.max())

    def display_trees(
            self,
            well_node: CellNode,
            well_radius: float,
    ) -> None:
        """Displays the trees as a matplotlib 3D plot."""
        self.plot_trees(well_node=well_node, well_radius=well_radius)
        plt.show()

    def render_trees(
            self,
            well_node: CellNode,
            well_radius: float,
            folder_path: Path,
            file_name: str,
            file_extension: str,
    ) -> None:
        """Renders the trees as a matplotlib 3D plot."""
        figure = self.plot_trees(well_node=well_node, well_radius=well_radius)
        fname = str(folder_path / f'{file_name}.{file_extension}')
        figure.savefig(fname)
        plt.close(figure)

    def plot_trees(
            self,
            well_node: CellNode,
            well_radius: float
    ) -> plt.Figure:
        """Plots the trees in the Well as a 3D plot."""
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
        return figure

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
        mappable = plt.cm.ScalarMappable(norm=self.generation_normalizer, cmap=self.colormap)
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
