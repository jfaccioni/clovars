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
    valid_layouts = [
        'family',
        'time',
        'age',
        'generation',
        'division',
        'death',
        'signal',
    ]

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
        self.validate_layout(layout=layout)
        self.layout = layout
        self.time_normalizer = self.get_normalizer(values=time_values)
        self.age_normalizer = self.get_normalizer(values=age_values)
        self.generation_normalizer = self.get_normalizer(values=generation_values)
        self.division_normalizer = self.get_normalizer(values=None)
        self.death_normalizer = self.get_normalizer(values=None)
        self.signal_normalizer = self.get_normalizer(values=signal_values)

    def validate_layout(
            self,
            layout: str,
    ) -> None:
        """Raises a ValueError if the given layout isn't a valid option."""
        if layout not in self.valid_layouts:
            raise ValueError(f'Invalid layout: {layout}')

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
            root_nodes: list[CellNode],
            display_well: bool,
            z_axis_ratio: float,
            well_radius: float,
    ) -> None:
        """Displays the trees as a matplotlib 3D plot."""
        self.plot_trees(
            root_nodes=root_nodes,
            display_well=display_well,
            z_axis_ratio=z_axis_ratio,
            well_radius=well_radius,
        )
        plt.show()

    def render_trees(
            self,
            root_nodes: list[CellNode],
            display_well: bool,
            z_axis_ratio: float,
            well_radius: float,
            folder_path: Path,
            file_name: str,
            file_extension: str,
    ) -> None:
        """Renders the trees as a matplotlib 3D plot."""
        figure = self.plot_trees(
            root_nodes=root_nodes,
            display_well=display_well,
            z_axis_ratio=z_axis_ratio,
            well_radius=well_radius,
        )
        fname = str(folder_path / f'{file_name}.{file_extension}')
        figure.savefig(fname)
        plt.close(figure)

    def plot_trees(
            self,
            root_nodes: list[CellNode],
            display_well: bool,
            z_axis_ratio: float,
            well_radius: float,
    ) -> plt.Figure:
        """Plots the trees in the Well as a 3D plot."""
        figure = plt.figure(figsize=(12, 12))
        ax = figure.add_subplot(projection='3d')
        ax.set_box_aspect((1.0, 1.0, z_axis_ratio))
        for root_node in root_nodes:
            self.draw_tree(ax=ax, root_node=root_node)
        ax.set_xlabel('X coordinate (µm)')
        ax.set_ylabel('Y coordinate (µm)')
        ax.set_zlabel('Time (h)')
        if self.layout not in ('family', 'time'):  # add colorbar for other layouts only
            self.add_colorbar(figure=figure, ax=ax)
        if display_well is True:
            self.draw_well(ax=ax, well_radius=well_radius)
            self.set_well_limits(ax=ax, well_radius=well_radius)
        figure.tight_layout()
        return figure

    def draw_tree(
            self,
            ax: plt.Axes,
            root_node: CellNode,
    ) -> None:
        """Draws the tree on a matplotlib 3D plot."""
        for branch in root_node.yield_branches():
            self.draw_branch(ax=ax, branch=branch)
        if self.layout == 'family':
            self.format_family_layout(ax=ax, root_node=root_node)
        else:
            self.format_non_family_layout(ax=ax, root_node=root_node)

    def draw_branch(
            self,
            ax: plt.Axes,
            branch: list[CellNode],
    ) -> None:
        """Draws the branch on a matplotlib 3D plot."""
        if self.layout == 'family':
            xs, ys, zs = self.get_xyz_from_cell_nodes(cell_nodes=branch)
            ax.plot(xs, ys, zs, color='0.7', alpha=0.7, linewidth=1, zorder=1)
        else:
            for i, _ in enumerate(branch):
                branch_segment = branch[i:i+2]
                self.draw_branch_segment(ax=ax, branch_segment=branch_segment)

    @staticmethod
    def get_xyz_from_cell_nodes(cell_nodes: list[CellNode]) -> tuple[list[float], list[float], list[float]]:
        """Returns the XYZ coordinates of each CellNode in the input list."""
        xs = [node.x for node in cell_nodes]
        ys = [node.y for node in cell_nodes]
        zs = [node.simulation_hours for node in cell_nodes]
        return xs, ys, zs

    def draw_branch_segment(
            self,
            ax: plt.Axes,
            branch_segment: list[CellNode],
    ) -> None:
        """Draws the branch segment on a matplotlib 3D plot."""
        xs, ys, zs = self.get_xyz_from_cell_nodes(cell_nodes=branch_segment)
        color = self.get_segment_color(branch_segment=branch_segment)
        ax.plot(xs, ys, zs, color=color, linewidth=2, zorder=1)

    def get_segment_color(
            self,
            branch_segment: list[CellNode],
    ) -> float:
        """Returns the color for the branch segment."""
        values = {
            'time': self.get_time_color,
            'age': self.get_age_color,
            'generation': self.get_generation_color,
            'division': self.get_division_color,
            'death': self.get_death_color,
            'signal': self.get_signal_color,
        }[self.layout](branch_segment=branch_segment)
        return self.colormap(np.mean(values))

    def get_time_color(
            self,
            branch_segment: list[CellNode],
    ) -> str:
        """Returns the branch color in the plot, when plotting the tree with the time layout."""
        return self.time_normalizer([node.simulation_hours for node in branch_segment])

    def get_age_color(
            self,
            branch_segment: list[CellNode],
    ) -> str:
        """Returns the branch color in the plot, when plotting the tree with the age layout."""
        return self.age_normalizer([node.seconds_since_birth / 3600 for node in branch_segment])  # in hours

    def get_generation_color(
            self,
            branch_segment: list[CellNode],
    ) -> str:
        """Returns the branch color in the plot, when plotting the tree with the generation layout."""
        return self.generation_normalizer([node.generation for node in branch_segment])

    def get_division_color(
            self,
            branch_segment: list[CellNode],
    ) -> str:
        """Returns the branch color in the plot, when plotting the tree with the division layout."""
        return self.division_normalizer([node.division_threshold for node in branch_segment])

    def get_death_color(
            self,
            branch_segment: list[CellNode],
    ) -> str:
        """Returns the branch color in the plot, when plotting the tree with the death layout."""
        return self.death_normalizer([node.death_threshold for node in branch_segment])

    def get_signal_color(
            self,
            branch_segment: list[CellNode],
    ) -> str:
        """Returns the branch color in the plot, when plotting the tree with the signal layout."""
        return self.signal_normalizer([node.signal_value for node in branch_segment])

    def format_family_layout(
            self,
            ax: plt.Axes,
            root_node: CellNode,
    ) -> None:
        """Formats the tree according to the family layout."""
        self.draw_root(ax=ax, root_node=root_node)
        parent_nodes = root_node.search_nodes(fate_at_next_frame='division')
        self.draw_parents(ax=ax, parent_nodes=parent_nodes)
        dead_nodes = root_node.search_nodes(fate_at_next_frame='death')
        self.draw_dead_cells(ax=ax, dead_nodes=dead_nodes)
        leaf_nodes = [node for node in root_node.get_leaves() if node not in dead_nodes]
        self.draw_leaf_cells(ax=ax, leaf_nodes=leaf_nodes)

    def format_non_family_layout(
            self,
            ax: plt.Axes,
            root_node: CellNode,
    ) -> None:
        """Formats the tree according to the non-family layout"""
        parent_nodes = root_node.search_nodes(fate_at_next_frame='division')
        self.draw_parents(ax=ax, parent_nodes=parent_nodes)

    @staticmethod
    def draw_root(
            ax: plt.Axes,
            root_node: CellNode,
    ) -> None:
        """Draws the root Cell on a matplotlib 3D plot"""
        ax.scatter(root_node.x, root_node.y, root_node.simulation_hours, color='blue', marker='s', zorder=2)

    def draw_parents(
            self,
            ax: plt.Axes,
            parent_nodes: list[CellNode],
    ) -> None:
        """Draws the parent Cells on a matplotlib 3D plot."""
        xs, ys, zs = self.get_xyz_from_cell_nodes(cell_nodes=parent_nodes)
        if self.layout == 'family':
            ax.scatter(xs, ys, zs, color='green', marker='^', zorder=2)
        else:
            ax.scatter(xs, ys, zs, color='black', marker='.', s=100, alpha=0.5, zorder=2)

    def draw_dead_cells(
            self,
            ax: plt.Axes,
            dead_nodes: list[CellNode],
    ) -> None:
        """Draws the dead Cells on a matplotlib 3D plot."""
        xs, ys, zs = self.get_xyz_from_cell_nodes(cell_nodes=dead_nodes)
        ax.scatter(xs, ys, zs, color='red', marker='x', zorder=2)

    def draw_leaf_cells(
            self,
            ax: plt.Axes,
            leaf_nodes: list[CellNode],
    ) -> None:
        """Draws the leaf Cells on a matplotlib 3D plot."""
        xs, ys, zs = self.get_xyz_from_cell_nodes(cell_nodes=leaf_nodes)
        ax.scatter(xs, ys, zs, color='orange', marker='*', zorder=2)

    def add_colorbar(
            self,
            figure: plt.Figure,
            ax: plt.Axes,
    ) -> None:
        """Adds a colorbar to the Figure."""
        norm = {
            'age': self.age_normalizer,
            'generation': self.generation_normalizer,
            'division': self.division_normalizer,
            'death': self.death_normalizer,
            'signal': self.signal_normalizer,
        }[self.layout]
        label = {
            'age': 'Cell Age (h)',
            'generation': 'Generation',
            'division': 'Division Threshold',
            'death': 'Death Threshold',
            'signal': 'Signal Value',
        }[self.layout]
        mappable = plt.cm.ScalarMappable(norm=norm, cmap=self.colormap)
        figure.colorbar(mappable=mappable, ax=ax, label=label, shrink=0.5)

    @staticmethod
    def draw_well(
            ax: plt.Axes,
            well_radius: float,
    ) -> None:
        """Draws the Well onto the bottom of the 3D plot."""
        well_patch = plt.Circle((well_radius, well_radius), well_radius, color='#232323', alpha=0.3)
        ax.add_patch(well_patch)
        art3d.pathpatch_2d_to_3d(well_patch, z=0, zdir="z")

    @staticmethod
    def set_well_limits(
            ax: plt.Axes,
            well_radius: float,
    ) -> None:
        """Sets the 3D plot limits based on the drawn Well."""
        ax.set_xlim(0, well_radius * 2)
        ax.set_ylim(0, well_radius * 2)
        ax.set_zlim(bottom=0)
